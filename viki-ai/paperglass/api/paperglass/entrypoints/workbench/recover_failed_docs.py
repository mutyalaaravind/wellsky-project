import asyncio
import sys, os
import json
from collections import OrderedDict
from pathlib import Path
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import GCP_FIRESTORE_DB
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    MedispanDrug,
    DocumentOperationInstanceLog
)

from paperglass.usecases.commands import StartOrchestration

from paperglass.infrastructure.ports import (
    IPromptAdapter,
    IQueryPort,
    IRelevancyFilterPort,
)


from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

import logging
from paperglass.log import getLogger
LOGGER = getLogger(__name__)

LOGGER.setLevel(logging.DEBUG)
logging.getLogger('google.auth._default').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('grpc._cython.cygrpc').setLevel(logging.INFO)
logging.getLogger('google.auth.transport.requests').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

DOCUMENT_OPERATION_TYPE = "medication_extraction"

START_DATE = "2025-06-12T17:56:00.000-05:00"
END_DATE = "2025-06-12T17:57:00.000-05:00"

async def do_something():
    # Create output directory one level up
    default_output_dir = Path("../../data/outage/2025-06-12/recovery/default")
    default_output_dir.mkdir(parents=True, exist_ok=True)
    high_output_dir = Path("../../data/outage/2025-06-12/recovery/high")
    high_output_dir.mkdir(parents=True, exist_ok=True)    
    LOGGER.info(f"Created output directory: {default_output_dir} and {high_output_dir}")
    
    # Create Firestore client connection to default database
    db = firestore.Client(database="viki-prod")
    #db = firestore.Client()
    
    # Get reference to paperglass_document collection
    collection_ref = db.collection('paperglass_documents')
    
    # Query for documents where created_at is between START_DATE and END_DATE
    # Since created_at is stored as ISO-8601 string, compare directly as strings
    
    # Query documents with created_at between the date range (string comparison)
    query = collection_ref.where(filter=firestore.FieldFilter('created_at', '>=', START_DATE)).where(filter=firestore.FieldFilter('created_at', '<=', END_DATE))

    # Execute the query and count documents
    docs = query.stream()
    
    # Count the documents
    count = 0
    saved_count = 0
    default_failed_count = 0
    high_failed_count = 0

    results = []
    for doc in docs:
        doc_dict = doc.to_dict()
        app_id = doc_dict.get("app_id")
        tenant_id = doc_dict.get("tenant_id")
        patient_id = doc_dict.get("patient_id")
        status = doc_dict.get("operation_status", {}).get(DOCUMENT_OPERATION_TYPE, {}).get("status")
        priority = doc_dict.get("priority")
        created_at = doc_dict.get("created_at")

        count += 1

        if status == "COMPLETED":
            #LOGGER.debug(f"Skipping completed document: {doc_dict.get('id')}  created_at: {created_at}  priority: {priority}")
            continue        

        
        if status == "FAILED" and priority == "default":
            default_failed_count += 1
            continue
        elif status == "FAILED" and priority == "high":
            high_failed_count += 1

        if status == "FAILED":
            
            id = doc_dict.get("id")
            
            LOGGER.debug(f"Found {status} document: {id}  priority: {priority} created_at: {created_at}")
            results.append(doc_dict)

            command = StartOrchestration(
                document_operation_type=DOCUMENT_OPERATION_TYPE,
                document_id=id,
                priority=priority
            )

            # Serialize command to JSON file
            try:
                output_dir = high_output_dir if priority == "high" else default_output_dir

                filename = f"{app_id}_{tenant_id}_{patient_id}_{command.id}.json"
                filepath = output_dir / filename
                
                with open(filepath, 'w') as f:
                    json.dump(command.dict(), f, cls=DateTimeEncoder, indent=2)
                
                saved_count += 1
                LOGGER.debug(f"Saved command to: {filepath}")
                
            except Exception as e:
                LOGGER.error(f"Failed to save command for document {id}: {e}")
                raise e

            # if count > 1000:
            #     LOGGER.warning("More than 1000 documents found, stopping to avoid excessive logging.")
            #     break
    
    LOGGER.info(f"Total documents assessed: {count}")
    LOGGER.info(f"Total documents with default priority and failed status: {default_failed_count}")
    LOGGER.info(f"Total documents with high priority and failed status: {high_failed_count}")
    LOGGER.info(f"Total commands saved: {saved_count}")
    return {"count": count, "saved_count": saved_count, "start_date": START_DATE, "end_date": END_DATE}

async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()
