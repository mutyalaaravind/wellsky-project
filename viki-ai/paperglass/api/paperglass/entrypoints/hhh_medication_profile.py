import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.infrastructure.ports import IHHHAdapter,IQueryPort

from kink import inject

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)


@inject
async def test_medication_profile_api(medication_profile_adapter: IHHHAdapter):
    imported_medications = await medication_profile_adapter.get_medications("7899148","2BE65B49-AB63-5F71-851C477E745BB877")
    print(imported_medications)

@inject
async def get_medication_profile(medication_profile_adapter: IQueryPort, patient_id: str="7571693"):
    from google.cloud import firestore
    print(os.environ.get("GCP_PROJECT_ID"))
    db = firestore.Client(project=os.environ.get("GCP_PROJECT_ID"))

    # Define the collection and document
    collection_name = "medications_medication_profile"

    # Create a new document with a generated ID
    doc_ref = db.collection(collection_name).document("4f5f28485c0c11efa54042004e494300").get()
    print(doc_ref.to_dict())
    print( await medication_profile_adapter.get_medication_profile_by_patient_id(patient_id))

if __name__ == "__main__":
    asyncio.run(get_medication_profile())
