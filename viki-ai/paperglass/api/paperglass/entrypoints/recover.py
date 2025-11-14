import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict, List
import uuid, csv
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import CLOUD_PROVIDER, CLOUD_TASK_QUEUE_NAME, GCP_LOCATION_2, SELF_API, SERVICE_ACCOUNT_EMAIL
from paperglass.domain.utils.auth_utils import get_token
from paperglass.usecases.orchestrator import PageClassificationAgent,MedicationExtractionAgent, recover
from paperglass.usecases.document_operation_instance_log import DocumentOperationInstanceLogService
from paperglass.domain.models import ClassifiedPage, DocumentOperation, DocumentOperationInstanceLog, PageOperation
from paperglass.domain.values import DocumentOperationStatus, DocumentOperationStep, DocumentOperationType, OrchestrationPriority, Page, PageOperationStatus
from paperglass.infrastructure.ports import ICloudTaskPort, IQueryPort

from kink import inject

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

ERROR_REASON_DEFAULT = "Unknown"

async def get_errored_pages(document_id: str):
    url = f"https://ai-paperglass-api-cocynqqo6a-uk.a.run.app//api/documents/{document_id}/page-logs"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjAwNyIsInRlbmFudElkIjoiNTQzMjEiLCJwYXRpZW50SWQiOiIyOTQzN2RkMjRmZmU0NjVlYjYxMWE2MWIwYjYyZjYwOCIsImFtdXNlcmtleSI6IjEyMzQ1In0.nNHPgG08X_YqaBN1spIKq2j0xTRT3vQmXhv-rOZ8JAU"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    errored_pages = []
    for log in data:
        if log["extraction_status"] == "FAILED":
            errored_pages.append(log["page_number"])
            
    LOGGER.debug(data)

    return errored_pages


async def get_error_details(document_id:str):
    
    url = f"https://ai-paperglass-api-cocynqqo6a-uk.a.run.app//api/documents/{document_id}/logs"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjAwNyIsInRlbmFudElkIjoiNTQzMjEiLCJwYXRpZW50SWQiOiIyOTQzN2RkMjRmZmU0NjVlYjYxMWE2MWIwYjYyZjYwOCIsImFtdXNlcmtleSI6IjEyMzQ1In0.nNHPgG08X_YqaBN1spIKq2j0xTRT3vQmXhv-rOZ8JAU"
    }
    response = requests.get(url, headers=headers)
    d0 = response.json()

    data = d0["MEDICATION_EXTRACTION"]

    error_class = ERROR_REASON_DEFAULT
    error_classes = {}
    error_details = []
    error_step_ids = []

    for details in data:        
        try:
            if details["status"] == "FAILED":            
                error_details.append(details)
                step_id = details["step_id"]
                if step_id not in error_step_ids:
                    error_step_ids.append(step_id)

                page_number = details["page_number"] if "page_number" in details else "unknown"
                if page_number is None:
                    page_number = "unknown"
                
                if "Aborted: 409" in str(error_details):
                    error_classes["page_" + str(page_number)] = "Firestore: Transaction Expired"

                if "409 The referenced transaction has expired" in str(error_details):
                    error_classes["page_" + str(page_number)] = "Firestore: Transaction Expired"

                if "ValueError: One or more components is not a string or is empty" in str(error_details):                
                    error_classes["page_" + str(page_number)] = "Firestore: Value Error"

                if "firestore/async_client.py" in str(error_details):                        
                    if "400 Invalid transaction" in str(error_details):
                        error_classes["page_" + str(page_number)] = "Firestore: Invalid Transaction"
                        

                if "extract_json() missing 1 required positional argument" in str(error_details):
                    error_classes["page_" + str(page_number)] = "VertexAI: Incomplete json returned from model"

                elif "value is not a valid list" in str(error_details):
                    error_classes["page_" + str(page_number)] = "VertexAI: Value is not a valid list"

                elif "Content has no parts" in str(error_details):
                    error_classes["page_" + str(page_number)] = "VertexAI: Content has no parts"

                if "429 Quota exceeded" in str(error_details):
                    error_classes["page_" + str(page_number)] = "VertexAI: Quota exceeded"

                elif "429 Resource exhausted" in str(error_details):
                    error_classes["page_" + str(page_number)] = "VertexAI: Resource exhausted"

                elif "429 Unable to submit request because the service is temporarily out of capacity" in str(error_details):
                    error_classes["page_" + str(page_number)] = "VertexAI: Service out of capacity"                    

                elif "vertexai/generative_models/_generative_models.py" in str(error_details):
                    if "exceptions.from_grpc_error(rpc_error)" in str(error_details):
                        error_classes["page_" + str(page_number)] = "VertexAI: RPC Error"
                    elif "Response has no candidates" in str(error_details):
                        error_classes["page_" + str(page_number)] = "VertexAI: Response has no candidates"
                


                if "PERFORM_OCR" in error_step_ids:
                    if "KeyError" in str(error_details):
                        error_classes["page_" + str(page_number)] = "OCR Error: KeyError"
                    else:
                        error_classes["page_" + str(page_number)] = "OCR Error: Other"                

        except Exception as e:
            LOGGER.error(f"Error processing error details: {e}")
            error_classes.append("Script Error")            

        


        LOGGER.debug(error_classes)

        if len(error_classes.values()) > 0:
            ec = list(error_classes.values())
            error_class = ec[0]    

        return {
            "error_class": error_class,
            "error_classes": error_classes,
            "error_step_ids": error_step_ids,
            "error_details": error_details
        }


async def get_active_failed_doc_ids(tenant_id):
    from google.cloud import firestore
    failed_docs = []
    success_docs =[]
    in_progress_docs = []
    db = firestore.Client(database="viki-prod")
    
    LOGGER.debug("Processing Tenant ID: %s", tenant_id)
    active_ops_instances = db.collection("paperglass_document_operation").where("tenant_id","==",tenant_id).where("operation_type","==",DocumentOperationType.MEDICATION_EXTRACTION.value).get()
    
    if active_ops_instances:
        for active_ops_instance in active_ops_instances:
            LOGGER.debug("Processing Active Ops Instance: %s", active_ops_instance.id)
            active_ops_instance = active_ops_instance.to_dict()
            active_document_operation_instance_id = active_ops_instance.get("active_document_operation_instance_id")
            doc = db.collection("paperglass_document_operation_instance").document(active_document_operation_instance_id).get()
            if doc.exists:
                document = {
                    "document_id": doc.to_dict().get("document_id"),
                    "created_at": doc.to_dict().get("created_at"),
                    "tenant_id": doc.to_dict().get("tenant_id"),
                    "patient_id": doc.to_dict().get("patient_id"),
                    "elapsed_time": (datetime.datetime.fromisoformat(doc.to_dict().get("end_date")) - datetime.datetime.fromisoformat(doc.to_dict().get("start_date"))).total_seconds() / 60,
                }
                    
                
                if doc.to_dict().get("status") == DocumentOperationStatus.FAILED.value:
                    document["status"] = "FAILED"
                    failed_docs.append(document)
                if doc.exists and doc.to_dict().get("status") == DocumentOperationStatus.COMPLETED.value:
                    document["status"] = "COMPLETED"
                    success_docs.append(document)
                if doc.exists and doc.to_dict().get("status") == DocumentOperationStatus.IN_PROGRESS.value:
                    document["status"] = "IN_PROGRESS"
                    in_progress_docs.append(document)
            
    
    failed_docs.sort(key=lambda x: x["created_at"],reverse=True)
    success_docs.sort(key=lambda x: x["created_at"],reverse=True)
    in_progress_docs.sort(key=lambda x: x["created_at"],reverse=True)
    # print(f"Tenant ID: {tenant_id}")
    # print(len(failed_docs))
    # print(len(success_docs))
    # print(len(in_progress_docs))
    
    # Define the headers for the CSV file
    headers = ["document_id", "created_at", "tenant_id", "patient_id","status", "elapsed_time", "error_reason", "error_pages", "error_steps", "error_reasons", "error_details"]

    # Combine all documents into a single list
    all_docs = failed_docs + success_docs + in_progress_docs
    
    all_docs.sort(key=lambda x: x["created_at"],reverse=True)

    # Define the file path for the CSV file
    csv_file_path = f"./.logs/stats/{tenant_id}_doc_status_{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().year}-iteration-{datetime.datetime.now().hour}.csv"

    # Write the data to the CSV file
    with open(csv_file_path, mode='w+', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for doc in all_docs:
            document_id = doc.get("document_id")
            if doc.get("status") == "FAILED":
                try:
                    error_pages = await get_errored_pages(document_id)
                except Exception as e:
                    LOGGER.error(f"Error getting errored pages: {e}")
                    error_pages = []

                try:
                    error_details = await get_error_details(document_id)
                    error_class = error_details["error_class"]
                    error_classes = error_details["error_classes"]
                    error_step_ids = error_details["error_step_ids"]
                except Exception as e1:
                    LOGGER.error(f"Error getting error details: {e1}")
                    error_class = "Script Error"
                    error_classes = {}
                    error_step_ids = []
                    error_details = f"{str(e1)}"
                
                LOGGER.debug(json.dumps(error_details, indent=2))

                doc["error_reason"] = error_class
                doc["error_pages"] = json.dumps(error_pages)
                doc["error_steps"] = json.dumps(error_step_ids)
                doc["error_reasons"] = json.dumps(error_classes)
                doc["error_details"] = json.dumps(error_details)                    

            writer.writerow(doc)

async def get_doc_with_no_ops(tenant_id):
    from google.cloud import firestore
    db = firestore.Client(database="viki-prod")
    docs = db.collection("paperglass_documents").where("tenant_id","==",tenant_id).get()
    not_started_docs=[]
    if docs:
        docs = [doc.to_dict() for doc in docs]
        for doc in docs:
            doc_ops = db.collection("paperglass_document_operation").where("document_id","==",doc.get("id")).get()
            doc_ops = [doc_op.to_dict() for doc_op in doc_ops]
            if not doc_ops:
                not_started_docs.append(doc)
    
    # Define the headers for the CSV file
    headers = ["document_id","created_at","app_id","tenant_id","patient_id","page_count","active"]

    # Define the file path for the CSV file
    csv_file_path = f"./.logs/stats/{tenant_id}_docs_with_no_ops_{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().year}-iteration-{datetime.datetime.now().hour}.csv"

    # Write the data to the CSV file
    with open(csv_file_path, mode='w+', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for doc in not_started_docs:
            writer.writerow({
                "document_id": doc.get("id"),
                "created_at": doc.get("created_at"),
                "app_id": doc.get("app_id"),
                "tenant_id": doc.get("tenant_id"),
                "patient_id": doc.get("patient_id"),
                "page_count": len(doc.get("pages")),
                "active": doc.get("active")
            })

async def get_failed_doc_ids(tenant_id="54321"):
    from google.cloud import firestore
    
    db = firestore.Client(database="viki-prod")
    docs = db.collection("paperglass_document_operation_instance").where("tenant_id","==",tenant_id).where("status","==",DocumentOperationStatus.FAILED.value).get()
    if docs:
        docs = [doc.to_dict().get("document_id") for doc in docs]
        print(docs)
    print("no docs found")
    
async def run_recovery_for_docs():
    #doc_ids_14143 = ['d9c77f60961f11efa72042004e494300', '63e1a748962011efa72042004e494300', '98d458f0969911efaed942004e494300', '98de990a969911ef939142004e494300', '95a4f658969911efb47242004e494300', '95b33394969911ef939142004e494300', 'd2c3fa04961f11efa72042004e494300', '78693726962011efa72042004e494300', '6cdcca8a962011efa72042004e494300', 'e4bb3dd0961f11efa72042004e494300', 'f69fc4e2954a11efb12a42004e494300', 'db24d6aa961f11efa72042004e494300', '6c8862a6962011efa72042004e494300', '6dbdfbfe962011efa72042004e494300', '4bbd134e960411efa72042004e494300', '95d52116969911efabe542004e494300', '98f90dbc969911efa4b642004e494300', '4d466968960411efa72042004e494300', '95c4c438969911ef9fd342004e494300', '60a7e6be962011efa72042004e494300', 'd24435c6961f11efa72042004e494300', '95c6ac80969911efbef842004e494300', '6b78b302962011efa72042004e494300', '72e52850962011efa72042004e494300', '95fd50f0969911ef908742004e494300', '962e53b2969911ef908742004e494300', 'cfe4011c961f11efa72042004e494300', '98fb0586969911ef9fd342004e494300', '98ebb57c969911efa66142004e494300', '95ec9012969911efbef842004e494300', '9623580e969911ef9ab542004e494300', '62427656962011efa72042004e494300', '95c21242969911ef870342004e494300', '1df04c9a960111efbed442004e494300', '47824056960411efa72042004e494300', '96257ee0969911efbef842004e494300', '718ad842962011efa72042004e494300', '4dd72f5c960411efa72042004e494300', 'd47b1d46961f11efa72042004e494300', '992e1a16969911ef929f42004e494300', '98745c20969911ef9ab542004e494300', 'cc3359f0961f11efa72042004e494300', '515d6baa960411efa72042004e494300', '98365920969911ef801442004e494300', '989c2034969911efa3ae42004e494300', '98b46694969911efbef842004e494300', '98b414e6969911ef888542004e494300', '4e47ab74960411efa72042004e494300', '68449804962011efa72042004e494300', '98b5377c969911ef932442004e494300', '649bd8de962011efa72042004e494300', 'ff936124960011efbed442004e494300', '991213a2969911ef9b6c42004e494300', '4fab9d5e960411efa72042004e494300', 'cb8996b8961f11efa72042004e494300', '76ea9a52962011efa72042004e494300', '77bc0452962011efa72042004e494300', '6ecc7ce6962011efa72042004e494300', '48ed9cd8960411efa72042004e494300', '47da6682960411efa72042004e494300', '9837e75e969911ef949a42004e494300', '663fdf0a962011efa72042004e494300', '628f0d04962011efa72042004e494300', '5f9ca548962011efa72042004e494300', '5d4b9ad4962e11efbed442004e494300', '98eb0744969911efaa3242004e494300', 'e98ea6da961f11efa72042004e494300', '9839b750969911efb47242004e494300', '4a04e7e8960411efa72042004e494300', '4d0a3718960411efa72042004e494300', '49408e66960411efa72042004e494300', '4a398aac960411efa72042004e494300', '46ef647a960411efa72042004e494300', '4e126504960411efa72042004e494300', '4f42077c960411efa72042004e494300', '9808fe6c969911efaced42004e494300', '71bef082962011efa72042004e494300', '98ed450e969911efaced42004e494300', '5d29d0ce962011efa72042004e494300', '991377ec969911ef80ea42004e494300', 'cbd3eea2961f11efa72042004e494300', 'd20ab256961f11efa72042004e494300', '4b0b32d2960411efa72042004e494300', '9829782c969911efaced42004e494300', '472757c2960411efa72042004e494300', 'f2f6453295ea11ef860d42004e494300', '47afd91c960411efa72042004e494300', '98d061fa969911efbaa042004e494300', '989df350969911ef93c942004e494300', '49d49c28960411efa72042004e494300', 'd6f005dc961f11efa72042004e494300', 'd0d9ff9a961f11efa72042004e494300', '4f7e9db8960411efa72042004e494300', '7679e44c962011efa72042004e494300', 'e7270220961f11efa72042004e494300', 'd41c14a4961f11efa72042004e494300', '988838a8969911ef949a42004e494300', '98e09f70969911ef872942004e494300', '4e68cec6960411efa72042004e494300', '518b85da960411efa72042004e494300', 'd95d54b4960611ef8e4142004e494300', 'd66176b4961f11efa72042004e494300', 'd2fa568a961f11efa72042004e494300', '98ddc57a969911efae9a42004e494300', '95c300d0969911ef870342004e494300', '69aaaeea962011efa72042004e494300', '762c5830962011efa72042004e494300', '9827d4ae969911efad9942004e494300', '98d6457a969911efa89142004e494300', '6ef336e2962011efa72042004e494300', 'cf255816961f11efa72042004e494300', '9809bdde969911efaa3242004e494300', 'a9b85b3e960411efa72042004e494300', 'e55c70e2961f11efa72042004e494300', '97f5ba14969911ef84f842004e494300', '97faf13c969911ef9fd342004e494300', '98720c7c969911efb8b642004e494300', 'e5b58a10961f11efa72042004e494300', '9898b160969911efa02e42004e494300', 'dde4e47a961f11efa72042004e494300', 'd3c47640961f11efa72042004e494300', '6805f3d8962011efa72042004e494300', 'd5b4d7d8961f11efa72042004e494300', '69658ae0962011efa72042004e494300', '7785b4ec962011efa72042004e494300', '7c6c615e962011efa72042004e494300', 'a89ef42e960411efa72042004e494300', '99219232969911ef93c942004e494300', 'a9e6d414960411efa72042004e494300', '98d1dcd8969911ef9f4d42004e494300', '97fdd802969911ef9ab542004e494300', '98002062969911ef84f842004e494300', '983e0616969911ef890542004e494300', '98b0f5cc969911ef93c942004e494300', '97dfb976969911ef84f842004e494300', '98011f76969911efabe542004e494300', '98101d0a969911efafd342004e494300', '4fecde04960411efa72042004e494300', '98ec6f4e969911efa95a42004e494300', 'e28e49c6961f11efa72042004e494300', '98745a72969911ef90de42004e494300', 'dc8c992e961f11efa72042004e494300', '987336d8969911ef8b9b42004e494300', '667b5972962011efa72042004e494300', 'dfc4a4ce961f11efa72042004e494300', 'd98cc4ba961f11efa72042004e494300', 'aafebe98960411efa72042004e494300', 'cc632da6961f11efa72042004e494300', 'e84d7350961f11efa72042004e494300', '4500a01c962611efbed442004e494300', '7bc4f180962011efa72042004e494300', '752dace0962011efa72042004e494300', '712eef1e962011efa72042004e494300', '63b01d40962011efa72042004e494300', '98af6978969911efa34242004e494300', 'e9c362a8961f11efa72042004e494300', 'd26fd744961f11efa72042004e494300', '98b9b0b8969911efa89142004e494300', '98779d36969911efad9942004e494300', '733065ae962011efa72042004e494300', '98fb659e969911efa7bc42004e494300', 'cea28096955a11efb12a42004e494300', '61702a7a962011efa72042004e494300', '9870c970969911ef869442004e494300', '97d34db2969911efb86642004e494300', '99176b72969911efae9a42004e494300', 'dbe9efb2961f11efa72042004e494300', '4f99effa960411efa72042004e494300', 'd6356e98961f11efa72042004e494300', '98b587b8969911ef869442004e494300', '4e1d275a960411efa72042004e494300', '98d9fb0c969911efbef842004e494300', '98a56d42969911ef90de42004e494300', 'de7e8d8c961f11efa72042004e494300', '63821350962011efa72042004e494300', 'd959900e961f11efa72042004e494300', '97d6f7be969911efabe542004e494300', 'de4a391a961f11efa72042004e494300', '79d46914962011efa72042004e494300', 'e5e2efc8961f11efa72042004e494300', '505f8ff8960411efa72042004e494300', '988dce58969911ef905542004e494300', '4df7d2b6960411efa72042004e494300', 'f5a4f7dc955f11efb12a42004e494300', '783a87be962011efa72042004e494300', '7bfb6742962011efa72042004e494300']
    files_to_recover_by_pages = [
                                    #"./.logs/stats/6110_doc_status_11-26-2024-iteration-21.csv",
                                 "./.logs/stats/14299_doc_status_11-26-2024-iteration-21.csv",
                                 "./.logs/stats/8536_doc_status_11-26-2024-iteration-21.csv",
                                 "./.logs/stats/14300_doc_status_11-26-2024-iteration-21.csv",
                                 "./.logs/stats/12142_doc_status_11-26-2024-iteration-21.csv",
                                 "./.logs/stats/14143_doc_status_11-26-2024-iteration-21.csv",
                                 "./.logs/stats/2506_doc_status_11-26-2024-iteration-21.csv"
                                 ]
    files_to_reprocess =  [
                                # "./.logs/stats/6110_docs_with_no_ops_11-26-2024-iteration-23.csv",
                                #  "./.logs/stats/14299_docs_with_no_ops_11-26-2024-iteration-23.csv",
                                #  "./.logs/stats/8536_docs_with_no_ops_11-26-2024-iteration-23.csv",
                                 "./.logs/stats/14300_docs_with_no_ops_11-26-2024-iteration-23.csv",
                                #  "./.logs/stats/12142_docs_with_no_ops_11-26-2024-iteration-21.csv",
                                #  "./.logs/stats/14143_docs_with_no_ops_11-26-2024-iteration-21.csv",
                                #  "./.logs/stats/2506_docs_with_no_ops_11-26-2024-iteration-21.csv"
    ]
    for file_to_recover_by_pages in files_to_recover_by_pages:
        doc_ids=[]
        with open(file_to_recover_by_pages, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "FAILED" in line and ("2024-11-27" in line or "2024-11-26" in line):
                    doc_id = line.split(",")[0]
                    doc_ids.append(doc_id)
            deduped_doc_ids = list(set(doc_ids))
            for doc_id in deduped_doc_ids:
                await run_recover(doc_id)
    
    for file_to_reprocess in files_to_reprocess:
        doc_ids = []
        with open(file_to_reprocess, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "document_id" not in line and ("2024-11-26" in line or "2024-11-27" in line):
                    doc_id = line.split(",")[0]
                    doc_ids.append(doc_id)
            for doc_id in list(set(doc_ids)):
                await re_process(doc_id)

async def re_process(doc_id):
    from usecases.orchestrator import orchestrate
    await orchestrate(doc_id,force_new_instance=True,priority=OrchestrationPriority.HIGH)

@inject
async def run_recover(doc_id, query:IQueryPort, cloud_task_adapter:ICloudTaskPort):
    classification_step_group_steps = [DocumentOperationStep.SPLIT_PAGES, 
                                       DocumentOperationStep.CREATE_PAGE, 
                                       DocumentOperationStep.TEXT_EXTRACTION,
                                       DocumentOperationStep.CLASSIFICATION
                                    ]
    medication_step_group_steps = [DocumentOperationStep.MEDICATIONS_EXTRACTION,
                                   DocumentOperationStep.MEDICATION_PROFILE_CREATION,
                                   DocumentOperationStep.MEDISPAN_MATCHING,
                                   DocumentOperationStep.NORMALIZE_MEDICATIONS,
                                   DocumentOperationStep.PERFORM_OCR
                                   ]
    
    
    doc_op:DocumentOperation  = await query.get_document_operation_by_document_id(doc_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)
    
    
    if not doc_op or not (doc_op and doc_op.active_document_operation_instance_id):
        await re_process(doc_id)
        return 

    doc_operation_instance_id= doc_op.active_document_operation_instance_id
    
    doc_logger = DocumentOperationInstanceLogService()
    doc_instance_logs:List[DocumentOperationInstanceLog] = await doc_logger.list(doc_id,doc_operation_instance_id)
    #doc_instance_logs:List[DocumentOperationInstanceLog] = await query.get_document_operation_instance_logs_by_document_id(doc_id,doc_operation_instance_id)
    
    failed_logs_without_page_number = [x for x in doc_instance_logs if x.status == DocumentOperationStatus.FAILED and x.page_number is None]
    
    if failed_logs_without_page_number:
        await re_process(doc_id)
    """
    {"unqiue_identifier":{PERFORM_OCR:{"pagenumber":DocumentOperationInstanceLog}}}
    """
    deduped_failed_log = {}
    
    print(f"Processing {doc_id}")
    print(f"Total Failed Logs: {len(doc_instance_logs)}")
    for failed_log in doc_instance_logs:
        if failed_log.unique_identifier() not in deduped_failed_log.keys():
            deduped_failed_log[failed_log.unique_identifier()] = {}
            deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number] = {}
            deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number][failed_log.step_id] = failed_log
        else:
            if deduped_failed_log[failed_log.unique_identifier()].get(failed_log.page_number) is None:
                deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number] = {}
                deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number][failed_log.step_id] = failed_log
            else:
                if deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number].get(failed_log.step_id):
                    if deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number][failed_log.step_id].created_at < failed_log.created_at:
                        deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number] = {}
                        deduped_failed_log[failed_log.unique_identifier()][failed_log.page_number][failed_log.step_id] = failed_log
        
    
    print(f"Total Unique Failed Logs: {len(deduped_failed_log)}")
    
    for k,page_number_dict in deduped_failed_log.items():
        if page_number_dict:
            for page_number,step_id_dict in page_number_dict.items():
                for step_id, log in step_id_dict.items():
                    log:DocumentOperationInstanceLog = log
                    if log.status == DocumentOperationStatus.FAILED:
                        
                        if log.page_number:
                            print(f"Recovering {log.id} for {log.step_id} on page {log.page_number}")
                            
                            if CLOUD_PROVIDER == "local":
                                await recover(log.id)
                            else:
                                print(await cloud_task_adapter.create_task(
                                    token=get_token(log.app_id, log.tenant_id, log.patient_id),
                                    location=GCP_LOCATION_2,
                                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                                    queue=CLOUD_TASK_QUEUE_NAME,
                                    url=f"{SELF_API}/orchestrate_v3_recover",
                                    payload={
                                        "failed_doc_operation_instance_log_id": log.id
                                    }
                                ))
                        else:
                            print(f"reprocessing {log.document_id}")
                            await re_process(log.document_id)
                            return

         
async def get_total_pages_and_medications(tenant_id:str):
    print("======")
    print(tenant_id)
    from google.cloud import firestore
    client = firestore.Client(database="viki-prod",project="viki-prod-app-wsky")
    docs = client.collection("paperglass_documents").where("tenant_id","==",tenant_id).get()
    #docs = [x.to_dict() for x in docs if x.get("created_at") < datetime.strptime("2024-10-31","%Y-%m-%d").isoformat() and x.get("created_at") > datetime.strptime("2024-10-01","%Y-%m-%d").isoformat()]
    
    total_pages = sum([x.get("page_count") for x in docs])
    print(total_pages)
    
    total_medications = 0
    for doc in docs:
        doc_operations = client.collection("paperglass_document_operation").where("document_id", "==", doc.get("id")).stream()
        doc_operations = [x.to_dict() for x in doc_operations]
        doc_stats = {
            "document_id":doc.get("id"),
            "created_at":doc.get("created_at"),
            "document_operation_instance_id":doc_operations[0].get("active_document_operation_instance_id") if doc_operations else None
        }
        extracted_medications = client.collection("medications_extracted_medications").where("document_operation_instance_id","==",doc_stats.get("document_operation_instance_id")).stream()
        extracted_medications = [x.to_dict() for x in extracted_medications]
        total_medications += len(extracted_medications)
    print(total_medications)
    
async def get_medication_profile(tenant_id:str):
    print("======")
    print(tenant_id)
    from google.cloud import firestore
    client = firestore.Client(database="viki-prod",project="viki-prod-app-wsky")
    docs = client.collection("medications_medication_profile").where("tenant_id","==",tenant_id).get()
    #docs = [x.to_dict() for x in docs if x.get("created_at") < datetime.strptime("2024-10-31","%Y-%m-%d").isoformat() and x.get("created_at") > datetime.strptime("2024-10-01","%Y-%m-%d").isoformat()]
    hhh_inserted_medication = 0
    for doc in docs:
        medications = doc.to_dict().get("medications")
        if medications:
            for medication in medications:
                if medication.get("host_medication_sync_status"):
                    hhh_inserted_medication = hhh_inserted_medication + 1
    print(hhh_inserted_medication)
    
        
if __name__ == '__main__':
    #tenant_ids = ["363","11575","14143"]
    tenant_ids = ["6110","14299","8536","14300","12142","14143","2506"]
    #tenant_ids = ["6110","14299", "8536", "14300"]
    for tenant_id in tenant_ids:
        asyncio.run(get_active_failed_doc_ids(tenant_id))
        asyncio.run(get_doc_with_no_ops(tenant_id))
    # for tenant_id in tenant_ids:
    #     asyncio.run(get_total_pages_and_medications(tenant_id))
    # asyncio.run(run_recovery_for_docs())
    # for tenant_id in tenant_ids:
    #     asyncio.run(get_medication_profile(tenant_id))
    asyncio.run(recover("5fb0cf20b2ca11ef91ac0242ac120007"))