import asyncio
from collections import defaultdict
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime

import paperglass.usecases.documents as documents

from paperglass.infrastructure.adapters.external_medications import HHHAdapter
from paperglass.domain.values import HostFreeformMedicationAddModel


from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from google.cloud import firestore

"""
How many medications did the service extract?
How many medications did the user select to include in the medication profile?
How many additional medications did the user add?
"""
async def get_tenant_data(tenant_id:str):
    
    client = firestore.Client(database="viki-prod")
    
    docs = client.collection("paperglass_documents").where("tenant_id", "==", tenant_id).stream()
    
    docs = [x.to_dict() for x in docs]
    
    patient_docs = {}
    for doc in docs:
        doc_operations = client.collection("paperglass_document_operation").where("document_id", "==", doc.get("id")).stream()
        doc_operations = [x.to_dict() for x in doc_operations]
        doc_stats = {
            "document_id":doc.get("id"),
            "created_at":doc.get("created_at"),
            "document_operation_instance_id":doc_operations[0].get("active_document_operation_instance_id") if doc_operations else None
        }
        if patient_docs.get(doc.get("patient_id")) and isinstance(patient_docs.get(doc.get("patient_id")),list):
            patient_docs.get(doc.get("patient_id")).append(doc_stats)
        else:
            patient_docs[doc.get("patient_id")] = [doc_stats]
        
    open("./.logs/stats/patient_docs.json", "w+").write(json.dumps(patient_docs))
    
async def get_extracted_medications_count():
    patient_docs = open("./.logs/stats/patient_docs.json").read()
    
    patient_docs = json.loads(patient_docs)
    
    patient_medications = {}
    for patient_id,docs in patient_docs.items():
        # get all extracted medications count
        client = firestore.Client(database="viki-prod")
        for doc in docs:
            
            extracted_medications = client.collection("medications_extracted_medications").where("document_operation_instance_id","==",doc.get("document_operation_instance_id")).stream()
            extracted_medications = [x.to_dict() for x in extracted_medications]
            if patient_medications.get(patient_id):
                if not patient_medications[patient_id].get("documents_with_extracted_medications_count"):
                    patient_medications[patient_id]["documents_with_extracted_medications_count"]={}
                patient_medications[patient_id]["documents_with_extracted_medications_count"][doc.get("document_id")] = len(extracted_medications)
            else:
                patient_medications[patient_id] = {
                    "documents_with_extracted_medications_count":{doc.get("document_id"):len(extracted_medications)}
                }

        # get medication profile
        medication_profile = client.collection("medications_medication_profile").where("patient_id", "==", patient_id).stream()
        
        medication_profile = [x.to_dict() for x in medication_profile]
        
        medication_profile = medication_profile[0] if medication_profile else None
        
        synced_medications = [x for x in medication_profile.get("medications") if x.get("host_medication_sync_status")]
        
        imported_medications_but_not_extracted = [x for x in medication_profile.get("medications") if x.get("imported_medication") and not x.get("extracted_medication_reference")]
        
        user_added_medications = [x for x in medication_profile.get("medications") if x.get("user_entered_medication") and x.get("user_entered_medication").get("edit_type") == "added"]
        user_edited_medications = [x for x in medication_profile.get("medications") if x.get("user_entered_medication") and x.get("user_entered_medication").get("edit_type") == "updated"]
        
        patient_medications[patient_id]["total_extracted_medications"] = sum([x for x in patient_medications[patient_id]["documents_with_extracted_medications_count"].values()])
        patient_medications[patient_id]["synced_to_hhh_medications_count"] = len(synced_medications)
        patient_medications[patient_id]["user_added_medications_count"] = len(user_added_medications)
        patient_medications[patient_id]["user_edited_medications_count"] = len(user_edited_medications)
        patient_medications[patient_id]["imported_medications_but_not_extracted_count"] = len(imported_medications_but_not_extracted)
        
    open("./.logs/stats/patient_medications.json", "w+").write(json.dumps(patient_medications))


async def get_total_pages_and_medications(tenant_id:str):
    client = firestore.Client(database="viki-prod",project="viki-prod-app-wsky")
    docs = client.collection("paperglass_documents").stream()
    docs = [x.to_dict() for x in docs if x.get("created_at") < datetime.strptime("2024-10-31","%Y-%m-%d").isoformat() and x.get("created_at") > datetime.strptime("2024-10-01","%Y-%m-%d").isoformat()]
    
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
    
    open("./.logs/stats/total_pages_and_medications.json", "w+").write(json.dumps({"total_pages":total_pages,"total_medications":total_medications}))

async def get_page_operation(document_id:str):
    client = firestore.Client(database="viki-prod",project="viki-prod-app-wsky")
    page_operations = client.collection("paperglass_page_operation").where("document_id", "==", document_id).stream()
    page_operations = [x.to_dict() for x in page_operations]
    
    for page_operation in page_operations:
        processed_time = (datetime.fromisoformat(page_operation.get("modified_at")) - datetime.fromisoformat(page_operation.get("created_at")))
        page_operation["processed_time_in_seconds"] = processed_time.total_seconds()
    import csv
    with open("./.logs/stats/page_operations.csv", "w", newline="") as f:
        w = csv.DictWriter(f, page_operations[0].keys())
        w.writeheader()
        w.writerows(page_operations)
    
    #open("./.logs/stats/page_operations.csv", "w+").write(json.dumps(page_operations))

async def get_tokens_by_query(document_id: str):
    import vertexai
    from vertexai.generative_models import GenerativeModel
    vertexai.init(project="viki-prod-app-wsky", location="us-central1")
    
    
    
    
    client = firestore.Client(database="viki-prod",project="viki-prod-app-wsky")
    doc_ops_instance_logs_docs = client.collection("paperglass_document_operation_instance_log").where("document_id", "==", document_id).stream()
    doc_ops_instance_logs = [x.to_dict() for x in doc_ops_instance_logs_docs]
    
    
    tokens_by_query = {}
    for log in doc_ops_instance_logs:
        flash_model = GenerativeModel("gemini-1.5-flash-001")
        pro_model = GenerativeModel("gemini-1.5-pro-001")
        #import pdb;pdb.set_trace()
        if log.get("step_id") in ["CLASSIFICATION","TEXT_EXTRACTION","MEDICATIONS_EXTRACTION","NORMALIZE_MEDICATIONS","MEDISPAN_MATCHING"]:
            context = log.get("context")
            if log.get("step_id") in ["MEDICATIONS_EXTRACTION","TEXT_EXTRACTION","CLASSIFICATION"]:
                print(log.get("step_id"))
                
                if log.get("step_id") == "TEXT_EXTRACTION":
                    model = pro_model
                else:
                    model = flash_model
                
                prompt_input_length = 0
                prompt_output_length = 0
                
                if context.get("llm_prompt") and isinstance(context.get("llm_prompt"),list):
                    for x in context.get("llm_prompt"):
                        model_response = model.count_tokens(x)
                        prompt_input_length += model_response.total_billable_characters
                    for x in context.get("model_response"):
                        prompt_output_length += len(x)
                        
                if log.get("step_id") == "TEXT_EXTRACTION":
                    # TEXT EXTRACTION takes pdf as input so we taking 1024 as fixed input characters for the same
                    prompt_input_length = prompt_input_length + 1024
                
                if not tokens_by_query.get(log.get("step_id")):
                    tokens_by_query[log.get("step_id")] = {}
                tokens_by_query[log.get("step_id")][log.get("page_number")] = {}
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt_input_length"] = prompt_input_length
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt_output_length"] = prompt_output_length
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt"] = context.get("llm_prompt")
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt_response"] = context.get("model_response")
                
            
            if log.get("step_id") in ["NORMALIZE_MEDICATIONS"]:
                print(log.get("step_id"))
                model = flash_model
                prompt_input_length = 0
                prompt_output_length = 0
                
                
                model_response = model.count_tokens(context.get("prompt"))
                prompt_input_length += model_response.total_billable_characters
                prompt_output_length += len(context.get("llm_raw_response"))
                # model_response = model.count_tokens(x)
                # prompt_output_length += model_response.total_billable_characters
                    
                if not tokens_by_query.get(log.get("step_id")):
                    tokens_by_query[log.get("step_id")] = {}
                tokens_by_query[log.get("step_id")][log.get("id")] = {}
                tokens_by_query[log.get("step_id")][log.get("id")]["prompt_input_length"] = prompt_input_length
                tokens_by_query[log.get("step_id")][log.get("id")]["prompt_output_length"] = prompt_output_length
                tokens_by_query[log.get("step_id")][log.get("id")]["prompt"] = context.get("prompt")
                tokens_by_query[log.get("step_id")][log.get("id")]["prompt_response"] = context.get("model_response")
                
            
            if log.get("step_id") in ["MEDISPAN_MATCHING"]:
                print(log.get("step_id"))
                medispan_prompt = """
                For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
                1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match
                2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
                3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
                4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
                5) Otherwise, return "{}" and specific what attributes were not found

                Only return the best match from the list. If no match is found, return "{}"

                Only return the best match from the list. If no match is found, return "{}"

                GIVEN MEDICATION:
                {SEARCH_TERM}

                MATCH LIST:
                """
                
                model = pro_model
                prompt_input_length = 0
                prompt_output_length = 0
                for x in context.get("medications"):
                    model_response = model.count_tokens(medispan_prompt.replace("{SEARCH_TERM}",x.get("medication").get("name")))
                    prompt_input_length += model_response.total_billable_characters
                for x in context.get("step_results"):
                    prompt_output_length += len(str(x))
                if not tokens_by_query.get(log.get("step_id")):
                    tokens_by_query[log.get("step_id")] = {}
                tokens_by_query[log.get("step_id")][log.get("page_number")] = {}
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt_input_length"] = len(medispan_prompt) + prompt_input_length
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt_output_length"] = prompt_output_length
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt"] = [ medispan_prompt.replace("{SEARCH_TERM}",x.get("medication").get("name")) for x in context.get("medications")]
                tokens_by_query[log.get("step_id")][log.get("page_number")]["prompt_response"] =  [len(str(x)) for x in context.get("step_results")]
    
    tokens_by_query["Summary"] = {}
    
    for step_id,page_values in tokens_by_query.items():
        if step_id == "Summary":
            continue
        tokens_by_query["Summary"][step_id] = {}
        prompt_input_length_values = [x.get("prompt_input_length") for x in page_values.values() if x.get("prompt_input_length")]
        prompt_output_length_values = [x.get("prompt_output_length") for x in page_values.values() if x.get("prompt_output_length")]
        
        tokens_by_query["Summary"][step_id]["input_length"] = {"min":min(prompt_input_length_values),"max":max(prompt_input_length_values),"avg":sum(prompt_input_length_values)/len(prompt_input_length_values)}
        tokens_by_query["Summary"][step_id]["output_length"] = {"min":min(prompt_output_length_values),"max":max(prompt_output_length_values),"avg":sum(prompt_output_length_values)/len(prompt_output_length_values)}
    
    text_extraction_input_values = tokens_by_query["Summary"]["TEXT_EXTRACTION"]["input_length"] 
    text_extraction_output_values = tokens_by_query["Summary"]["TEXT_EXTRACTION"]["output_length"]
    
    medispan_matching_input_values = tokens_by_query["Summary"]["MEDISPAN_MATCHING"]["input_length"]
    medispan_matching_output_values = tokens_by_query["Summary"]["MEDISPAN_MATCHING"]["output_length"]
    
    classification_input_values = tokens_by_query["Summary"]["CLASSIFICATION"]["input_length"]
    classification_output_values = tokens_by_query["Summary"]["CLASSIFICATION"]["output_length"]
    
    normalize_medications_input_values = tokens_by_query["Summary"]["NORMALIZE_MEDICATIONS"]["input_length"]
    normalize_medications_output_values = tokens_by_query["Summary"]["NORMALIZE_MEDICATIONS"]["output_length"]
    
    medication_extraction_input_values = tokens_by_query["Summary"]["MEDICATIONS_EXTRACTION"]["input_length"]
    medication_extraction_output_values = tokens_by_query["Summary"]["MEDICATIONS_EXTRACTION"]["output_length"]
    
    pro_001_values = {"input":{"min": min(text_extraction_input_values.get("min"),medispan_matching_input_values.get("min")),
                               "max":max(text_extraction_input_values.get("max"),medispan_matching_input_values.get("max")),
                               "avg":(text_extraction_input_values.get("avg")+medispan_matching_input_values.get("avg"))/2},
                      "output":{"min": min(text_extraction_output_values.get("min"),medispan_matching_output_values.get("min")),
                                "max":max(text_extraction_output_values.get("max"),medispan_matching_output_values.get("max")),
                                "avg":(text_extraction_output_values.get("avg")+medispan_matching_output_values.get("avg"))/2}}
    
    
    flash_001_values = {"input":{"min": min(classification_input_values.get("min"),normalize_medications_input_values.get("min"),medication_extraction_input_values.get("min")),
                                "max":max(classification_input_values.get("max"),normalize_medications_input_values.get("max"),medication_extraction_input_values.get("max")),
                                "avg":(classification_input_values.get("avg")+normalize_medications_input_values.get("avg")+medication_extraction_input_values.get("avg"))/3},
                        "output":{"min": min(classification_output_values.get("min"),normalize_medications_output_values.get("min"),medication_extraction_output_values.get("min")),
                                "max":max(classification_output_values.get("max"),normalize_medications_output_values.get("max"),medication_extraction_output_values.get("max")),
                                "avg":(classification_output_values.get("avg")+normalize_medications_output_values.get("avg")+medication_extraction_output_values.get("avg"))/3
                            }
                        }
     
    tokens_by_query["model_summary"] = {}
    tokens_by_query["model_summary"]["pro_001_values"] = pro_001_values
    tokens_by_query["model_summary"]["flash_001_values"] = flash_001_values
    
    
    open(f"./.logs/stats/tokens_by_query_{document_id}.json", "w+").write(json.dumps(tokens_by_query))

if __name__ == "__main__":
    #asyncio.run(get_tenant_data("54321"))
    #asyncio.run(get_tenant_data("11575"))
    #asyncio.run(get_extracted_medications_count())
    #asyncio.run(get_page_operation("742b965a85ad11ef9a7442004e494300"))
    #asyncio.run(get_total_pages_and_medications())
    asyncio.run(get_tokens_by_query(document_id="c44925ee9c6e11efb53942004e494300"))