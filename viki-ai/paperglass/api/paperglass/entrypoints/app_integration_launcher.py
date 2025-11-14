import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kink import inject
from paperglass.settings import APPLICATION_INTEGRATION_TRIGGER_ID, CLOUD_TASK_QUEUE_NAME, INTEGRATION_PROJECT_NAME, SELF_API, SERVICE_ACCOUNT_EMAIL
from paperglass.usecases.commands import TriggerExtraction
from paperglass.infrastructure.ports import IApplicationIntegration, IQueryPort
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.models import Document
from paperglass.domain.values import DocumentStatusType
from google.cloud import storage
from mktoken import mktoken, mktoken2
import csv

import math
from google.cloud import firestore
import csv
import csv

async def _get_token(self):
    import google.auth
    import google.auth.transport.requests
    SCOPE = "https://www.googleapis.com/auth/cloud-platform"
    credentials, project_id = google.auth.default(scopes=[SCOPE])
    # getting request object
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)  # refresh token
    token = credentials.token
    return token, project_id

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

async def generate_source_docs_csv():
    # parse gcs folders for patient id and tenant id and generate a csv file
    gcs_bucket = "viki-ai-provisional-stage"
    ignore_paths = ["paperglass","hhdocs"]

    # Create a client to interact with GCS
    client = storage.Client(project="viki-stage-app-wsky")

    # Get the bucket and list all blobs (files) in the bucket

    bucket = client.get_bucket(gcs_bucket)
    blobs = bucket.list_blobs()

    # Specify the path and filename for the CSV file
    csv_file = "./files_to_process.csv"

    # Open the CSV file in write mode
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(["tenant_id", "patient_id", "file_name", "source_gcs_uri","size"])

        # Iterate through the blobs and write the data to the CSV file
        for blob in blobs:
            if any(ignore_path in blob.name for ignore_path in ignore_paths):
                continue
            tenant_id = blob.name.split("-")[0]
            patient_id = blob.name.split("-")[1].split("/")[0]
            file_name = blob.name.split("/")[-1]
            source_gcs_uri = blob.name
            size = convert_size(blob.size)
            writer.writerow([tenant_id, patient_id, file_name, source_gcs_uri,size])

    # Print a message indicating that the CSV file has been written
    print(f"CSV file '{csv_file}' has been written.")

    # from json file, kick off the app integration batch by batch
    pass

get_patient_unique_id = lambda app_id, tenant_id, patient_id: f"{app_id}-{tenant_id}-{patient_id}"

@inject
async def create_patients(project:str, file_to_process:str):
    # read csv file and get patients list
    patients = []
    with open(file_to_process, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            patients.append(row)

    for patient in patients:
        
        first_name = patient.get("patient_id")
        last_name = patient["patient_id"]
        dob = ""
        created_at = datetime.datetime.now().isoformat()
        updated_at = created_at
        active=True
        app_id="007"
        tenant_id = patient.get("tenant_id")
        id = get_patient_unique_id(app_id, tenant_id, patient.get("patient_id"))

        # Define the data to be written
        patient_dict = dict(id=id, app_id=app_id,tenant_id=tenant_id, first_name=first_name, last_name=last_name, dob=dob, created_at=created_at, updated_at=updated_at, active=active)

        def create_patient(data: Dict):
            # Connect to Firestore
            db = firestore.Client(project=project)

            # Define the collection and document
            collection_name = "demo_patients"

            # Create a new document with a generated ID
            doc_ref = db.collection(collection_name).document(data["id"])

            # Write the data to Firestore
            doc_ref.set(data)

            print(f"Patient record created with ID: {data['id']}")

        create_patient(patient_dict)

@inject
async def create_documents(bucket_name:str, file_to_process:str,query:IQueryPort,command_handler:ICommandHandlingPort,app_integration_adapter:IApplicationIntegration,start_index=0,end_index=10,force_retrigger=False):
    # read csv file and get patients list
    docs = []
    with open(file_to_process, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            docs.append(row)
    
    status_file = open("execution_status.json", 'a')
    docs = docs[start_index:end_index]

    for doc in docs:
        app_id="007"
        tenant_id = doc.get("tenant_id")
        patient_id = get_patient_unique_id(app_id, tenant_id, doc.get("patient_id"))
        source_gcs_uri = f'gs://{bucket_name}/{doc.get("source_gcs_uri")}'
        file_name = doc.get("file_name")

        if ".jpg" in file_name or ".jpeg" in file_name:
            print("skipping due to unsupported fileformat")
            continue
        
        status = {"patient_id":patient_id,"app_id":app_id,"tenant_id":tenant_id,"source_gcs_uri":source_gcs_uri}
        

        ## TriggerExtraction calls CreateDocument based on raw binary from gcs storage
        # it has logic to not create document if already exists (based on source_document_storage_uri)
        doc:Document = await command_handler.handle_command(TriggerExtraction(patient_id=patient_id, app_id=app_id, tenant_id=tenant_id, source_document_storage_uri=source_gcs_uri))
        status.update({"document_id":doc.id})
        
        # below trigger is needed for local. IN cloud, this would have been automatically called on DocumentCreated Event
        if doc:
            doc_statuses= await query.get_document_statuses(doc.id, doc.execution_id)
            # find the status of the document and if failed or not started, trigger the orchestration else skip
            if not force_retrigger and doc_statuses and any([x.get("status") in [DocumentStatusType.DOCUMENT_UPLOADED.value] for x in doc_statuses]):
                # document is created and orchestration has started (maybe its over) 
                # in future we need to find all failed state and retry
                continue
                
        integration_project_name=INTEGRATION_PROJECT_NAME
        json_payload={
            "START_CLOUD_TASK_API":f"{SELF_API}/start_cloud_task",
            "CLOUD_TASK_ARGS":{
                "location":"us-east4",
                "url":f"{SELF_API}/orchestrate",
                "queue":CLOUD_TASK_QUEUE_NAME,
                "service_account_email":SERVICE_ACCOUNT_EMAIL,
                "payload":{"document_id": doc.id}
            },
            "TOKEN":f"Bearer {mktoken2(app_id, tenant_id,patient_id)}"
        }
        trigger_id = APPLICATION_INTEGRATION_TRIGGER_ID
        result = await app_integration_adapter.start(integration_project_name, json_payload, trigger_id)
        status.update({"app_integration_status":json.dumps(result)})

        # update status file
        status_file.write(json.dumps(status))
        status_file.write("\n")
        
        time.sleep(3*60) # sleep for 3 minutes

@inject
async def get_patient_documents(project:str):
    
    async def get_docs():
        # Connect to Firestore
        db = firestore.Client(project=project)

        # Define the collection and document
        collection_name = "paperglass_documents"

        # Create a new document with a generated ID
        doc_ref = db.collection(collection_name).get()
        docs = [doc.to_dict() for doc in doc_ref]
        return docs 
    
    docs = await get_docs()
    open("documents.json","w").write(json.dumps(docs))

@inject
async def get_docs_by_patients():
    docs = json.loads(open("documents.json").read())

    patient_docs = {}

    for doc in docs:
        patient_id = doc.get("patient_id")
        if patient_id not in patient_docs:
            patient_docs[patient_id] = []
        patient_docs[patient_id].append(doc)

    open("patient_docs.json","w").write(json.dumps(patient_docs))

@inject
async def get_doc_and_page_count_by_patients():
    docs = json.loads(open("documents.json").read())

    patient_docs = {}

    for doc in docs:
        patient_id = doc.get("patient_id")
        if patient_id not in patient_docs:
            patient_docs[patient_id] = {"doc_count":0,"page_count":0}
        patient_docs[patient_id]["doc_count"] += 1
        patient_docs[patient_id]["page_count"] += len(doc.get("pages"))

    with open("patient_docs_count.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["patient_id", "doc_count", "page_count"])
        for patient_id, counts in patient_docs.items():
            writer.writerow([patient_id, counts["doc_count"], counts["page_count"]])


if __name__ == "__main__":
    # run in shell: 
    # gcloud auth application-default login --impersonate-service-account=viki-ai-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com
    
    
    #asyncio.run(start_app_integration_execution_for_gcs_files())
    #asyncio.run(create_patients("viki-stage-app-wsky","./files_to_process.csv"))
    # asyncio.run(create_documents("viki-ai-provisional-stage","./files_to_process.csv",start_index=30,end_index=60))
    #asyncio.run(create_documents("viki-ai-provisional-stage","./files_to_process.csv",start_index=1,end_index=30,force_retrigger=False))
    #asyncio.run(get_patient_documents(project="viki-stage-app-wsky"))
    #asyncio.run(get_docs_by_patients())
    asyncio.run(get_doc_and_page_count_by_patients())
    pass