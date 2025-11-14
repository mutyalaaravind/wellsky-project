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

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

async def _get_token():
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

@inject
async def generate_documents_csv():
    firestore_client = firestore.Client()
    docs = firestore_client.collection("paperglass_documents").stream()
    docs = [x for x in docs]
    with open(f'./.logs/documents.csv', mode='a+') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["id","app_id","tenant_id", "patient_id", "created_at","page_count","file_name","storage_uri"])
        for doc in docs:
            doc = doc.to_dict()
            writer.writerow([doc["id"],doc["app_id"],doc["tenant_id"], doc["patient_id"], doc["created_at"],doc["page_count"],doc["file_name"],doc["storage_uri"]])

@inject
async def process_documents():
    with open(f'./.logs/documents.csv',mode='r') as file:
        reader = csv.DictReader(file)
        with open(f'./.logs/processed_documents.csv', mode='a+') as log_file:
            for row in reader:
                doc_id = row["id"]
                log_file.seek(0)
                if doc_id in log_file.read():
                    print(f"Already processed document {doc_id}")
                    continue
                await process(row["id"])
                log_file.write(f"{row['id']},{datetime.datetime.now()}\n")
                time.sleep(60)
        

@inject
async def process(document_id,query_port:IQueryPort,command_handler:ICommandHandlingPort):
    await _get_token()
    # read csv file and get patients list
    
    doc = await query_port.get_document(document_id)
    if doc is None:
        print(f"Document {document_id} not found")
        return
    doc:Document = Document(**doc)
    print(doc)
    from orchestrator import orchestrate_with_default_document_operations
    await orchestrate_with_default_document_operations(doc,command_handler,query_port)

@inject
async def process_custom_prompt(document_id, query_port:IQueryPort,command_handler:ICommandHandlingPort):
    LOGGER.info("Running custom prompt pipeline for documentId %s",document_id)
    await _get_token()
    # read csv file and get patients list

    metric_starttime = time.time()

    docs = []
    if document_id == "*" or document_id == "all":
        epoc_date = "2000-01-01T00:00:00Z"
        LOGGER.info("Getting all documents since %s", epoc_date)        
        docs = await query_port.get_documents_by_created(epoc_date)
    else:
        LOGGER.info("Getting one document: %s", document_id)
        doc = await query_port.get_document(document_id)
        if doc is None:
            LOGGER.error(f"Document {document_id} not found")
            return    
        d:Document = Document(**doc)
        docs.append(d)

    LOGGER.info("Processing %s documents", len(docs))
    
    for doc in docs:        
        #LOGGER.debug("Document: %s", doc)

        LOGGER.debug("Orchestrating for custom prompt")

        from orchestrator import orchestrate_for_custom_prompt
        await orchestrate_for_custom_prompt(doc,command_handler,query_port)

        LOGGER.debug("Orchestrating for custom prompt done")
    
    LOGGER.info("Processed %s documents", len(docs))

    metric_endtime = time.time()
    metric_duration = metric_endtime - metric_starttime
    LOGGER.info("Process took %s seconds", metric_duration)

PIPELINE_NAME_DEFAULT = "default"

pipeline_registry = {
    PIPELINE_NAME_DEFAULT: process,
    "toc": process_custom_prompt    
}

DEFAULT_DOCUMENT_ID = "442ec7b224f811ef8a5542004e494300"

if __name__ == "__main__":
    # run in shell:
    # dev
    # gcloud auth application-default login --impersonate-service-account=viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com 
    # stage:
    # gcloud auth application-default login --impersonate-service-account=viki-ai-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com
    
    if len(sys.argv) > 1:        
        pipeline = sys.argv[1]                
    else:
        pipeline = PIPELINE_NAME_DEFAULT
    print(f"Running pipeline: {pipeline}")

    if pipeline not in pipeline_registry:
        print(f"Pipeline {pipeline} not found")
        sys.exit(1)

    if len(sys.argv) > 2:
        documentId = sys.argv[2]
    else:
        documentId = DEFAULT_DOCUMENT_ID
    print(f"with Document ID: {documentId}")

    asyncio.run(pipeline_registry[pipeline](documentId))    

    #asyncio.run(process("442ec7b224f811ef8a5542004e494300"))
    #asyncio.run(process_custom_prompt("442ec7b224f811ef8a5542004e494300"))
    pass