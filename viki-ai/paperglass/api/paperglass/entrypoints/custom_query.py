
import sys,os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio,os
from google.cloud import firestore

from paperglass.settings import GCP_PROJECT_ID, GCP_FIRESTORE_DB

async def get_medications_by_name(search_term: str):
    db = firestore.Client(project=GCP_PROJECT_ID, database=GCP_FIRESTORE_DB)
    print(f'Connected to Firestore {GCP_PROJECT_ID} {GCP_FIRESTORE_DB}')

    search_term_lower = search_term.lower()
    print(f'Searching for {search_term_lower}')

    # Define the collection and document
    collection_name = "medications_extracted_medications"                       

    # Create a new document with a generated ID
    coll = db.collection(collection_name)

    docs = coll.get()
    print(f'Found {len(docs)} documents')

    idx = 0
    results = []
    for doc in docs:
        med = doc.to_dict()

        medication = med.get('medication')

        name = medication.get('name')
        if name is not None:
            name_lower = name.lower()
        else:
            continue

        if search_term_lower in name_lower:
            print(f'Found {name} in {name_lower}')
            #print(f'{json.dumps(med, indent=2)}')

            results.append(med)
            

        idx += 1

    print(json.dumps(results, indent=2))
    print(f'Found {len(results)} medications out of {idx}')


async def get_operation_instance_log_api(id:str):
    # Connect to Firestore
    db = firestore.Client(project=os.environ.get("GCP_PROJECT_ID"))

    # Define the collection and document
    collection_name = "paperglass_document_operation_instance_log"

    # Create a new document with a generated ID
    doc_ref = db.collection(collection_name).document(id).get()
    print(doc_ref.to_dict())

if __name__ == "__main__":
    id="089907004dd211efb8b342004e494300"
    value = "insulin"
    asyncio.run(get_medications_by_name(value))