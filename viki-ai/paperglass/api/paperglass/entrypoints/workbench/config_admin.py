import asyncio
import sys, os
import json
import uuid
from collections import OrderedDict
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter
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

DATABASE = "viki-prod"  # GCP_FIRESTORE_DB

CONFIG = """
{
  "created_at": "2025-06-30T19:18:06.640164+00:00",
  "app_id": "ltc",
  "active": true,
  "modified_by": "eric.coiner@wellsky.com",
  "id": "9c2923594b654f668ba71f9d90f57615",
  "created_by": "eric.coiner@wellsky.com",
  "config": {
    "use_extract_and_classify_strategy": true,
    "token_validation": {
      "enabled": true
    },
    "use_v3_orchestration_engine": true,
    "enable_ocr": true,
    "ui_hide_medication_tab": true,
    "orchestration_confirm_evidence_linking_enabled": true,
    "meddb_catalog": "merative",
    "evidence_weak_matching_firsttoken_enabled": true,
    "ui_document_action_extract_enable": true,
    "use_async_document_status": true,
    "ui_classification_enable": false,
    "on_demand_external_files_config": {
      "enabled": true,
      "uploaded_date_cut_off_window_in_days": 10
    },
    "evidence_weak_matching_enabled": true,
    "ui_longstanding_enable": false,
    "extract_immunizations": false,
    "medispan_matching_version": "2",
    "extract_conditions": false,
    "orchestration_engine_version": "v4",
    "ui_host_linked_delete_enable": false,
    "extract_allergies": false,
    "ocr_trigger_config": {
      "enabled": true,
      "processing_mode_async": false,
      "disable_orchestration_processing": true,
      "touch_points": {
        "page_click": false,
        "bubble_click": false,
        "evidence_link_click": true
      }
    },
    "ui_nonstandard_dose_enable": false,
    "medispan_match_config": {
      "v2_enabled_globally": true,
      "catalog": "merative",
      "v2_enabled_tenants": []
    },
    "use_ordered_events": false,
    "integration": {
      "base_url": "https://medextract.experience.care",
      "endpoints": {
        "list_medications": "/api/v1/medex/clients/{tenantId}/patients/{patientId}/medications",
        "list_attachments": "/api/v1/medex/clients/{tenantId}/patients/{patientId}/attachments",
        "create_medication": "/api/v1/medex/clients/{tenantId}/patients/{patientId}/medications"
      }
    },
    "extraction_persisted_to_medication_profile": false,
    "ui_document_action_upsert_goldendataset_test_enable": true,
    "validation_rules": {
      "skipImportedValidation": true,
      "validateDates": false,
      "errorMessages": {
        "classification": [
          "Classification is missing."
        ],
        "dosage": [
          "Amount/Dose is missing."
        ],
        "medispanId": [
          "Please either select unlisted or search and select medication."
        ],
        "statusReason": [
          "Please fill/update the reason for none of the above status. If already filled, please ignore"
        ],
        "startDateWithEndDate": [
          "Start Date is required if End Date is provided"
        ],
        "startDate": [
          "Start Date is missing."
        ],
        "name": [
          "Medication name is missing."
        ]
      },
      "validateName": true,
      "validateMedispanId": true,
      "validateStatusReason": true,
      "validateDosage": false,
      "validateClassification": false
    }
  },
  "modified_at": "2025-06-30T19:18:06.640164+00:00"
}

"""

async def get_config(app_id: str):
    # Initialize Firestore client
    db = firestore.Client(database=DATABASE)
    
    # Query the paperglass_app_config collection
    config_ref = db.collection('paperglass_app_config')
    query = config_ref.where(filter=FieldFilter('app_id', '==', app_id)).limit(1)
    docs = query.stream()
    
    # Get the first matching document
    config = None
    for doc in docs:
        config = doc.to_dict()
        break
    
    if config:                
        return config
    else:
        print(f"No configuration found for app_id: {app_id}")
        return None


async def update_config(app_id: str, config: dict):
    # Initialize Firestore client
    db = firestore.Client(database=DATABASE)
    config_ref = db.collection('paperglass_app_config')

    # Ensure app_id is in the config
    config['app_id'] = app_id

    # Check if id is missing
    if 'id' not in config:
        # Generate new ID
        new_id = uuid.uuid4().hex
        config['id'] = new_id
        config['active'] = True

        # Execute transaction
        with db.transaction() as transaction:
            # Query for existing active config
            query = config_ref.where(filter=FieldFilter('app_id', '==', app_id)).where(filter=FieldFilter('active', '==', True))
            docs = query.stream()
            
            # Deactivate existing configs
            for doc in docs:
                transaction.update(doc.reference, {'active': False})
            
            # Create new document
            new_doc_ref = config_ref.document(new_id)
            transaction.set(new_doc_ref, config)
    else:
        # If id exists, just update the document
        doc_ref = config_ref.document(config['id'])
        doc_ref.set(config)
    
    return config



async def run():    
    app_id = "ltc"
    
    # Get current config    
    current_config = await get_config(app_id)

    print("\nCurrent config:") 
    print(json.dumps(current_config, indent=2, cls=DateTimeEncoder))
     

    config = json.loads(CONFIG, object_pairs_hook=OrderedDict)
    
    print("\nUpdating config:")
    updated_config = await update_config(app_id, config)
    print(json.dumps(updated_config, indent=2, cls=DateTimeEncoder))
    
    # Get updated config to verify
    print("\nVerified updated config:")
    final_config = await get_config(app_id)

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()
