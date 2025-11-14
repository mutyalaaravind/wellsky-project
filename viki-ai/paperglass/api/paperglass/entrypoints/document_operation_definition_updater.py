import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import (
    GCP_FIRESTORE_DB
)
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    MedispanDrug,
    DocumentOperationInstanceLog
)
from paperglass.domain.values import (
    OrchestrationPriority
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

# Initialize the cloud Firestore client
cloud_client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)

# PROMPT_OLD = """
# For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
# 1) The name of medication should be present in the \"content\" field of the MATCH LIST entries. Otherwise say no name match
# 2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
# 3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
# 4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
# 5) Otherwise, return \"{}\" and specific what attributes were not found

# Only return the best match from the list. If no match is found, return \"{}\"

# Only return the best match from the list. If no match is found, return \"{}\"

# GIVEN MEDICATION:
# {SEARCH_TERM}

# MATCH LIST:
# """

PROMPT_NEW = """
For each GIVEN MEDICATIONS, find the best medication match from the MATCH LIST given below. Follow these instructions strictly:
1) The name of the GIVEN MEDICATION must exactly match (case insensitive) the \"NameDescription\" field of the MATCH LIST entries. Do not return a match if the names don't match exactly.
2) Do not match based on partial name matches or just the first word - the entire medication name must match.
3) If multiple entries match the name, then:
   a) If the GIVEN MEDICATION has strength specified, only match if there is an exact match of the Strength
   b) If the GIVEN MEDICATION has form specified, only match if there is an exact match of the Dosage_Form
   c) If the GIVEN MEDICATION has route specified, only match if there is an exact match of the Route
4) If no exact name match is found, do not return any match for that medication.
5) Never match medications with different names, even if other properties match.

The list of GIVEN MEDICATIONS is a dictionary with the key being the index and the value being the name of the medication.

For each medication, only return the best match from the list. 

Return the response in the following json format:

[
    {"**MEDICATION_ID": "**MATCHLIST id"}
]

GIVEN MEDICATIONS:
{SEARCH_TERM}

MATCH LIST:
{DATA}
"""

PROMPT = PROMPT_NEW

async def update_document_operation_definition(id, step_id, model, prompt):

    log_coll = cloud_client.collection("paperglass_document_operation_definition")

    LOGGER.debug(f"Fetching document with id: %s", id)
    query = log_coll.where("id","==", id)
    doc_list = await query.get()
    docs = [doc.to_dict() for doc in doc_list]

    if docs:
        doc = docs[0]
        step_config = doc["step_config"]
        if step_id not in step_config:
            prompt_config = {
                "description": f"{step_id} step",
                "model": model,
                "prompt": prompt
            }
        else:
            prompt_config = step_config[step_id]
            prompt_config["model"] = model
            prompt_config["prompt"] = prompt
        
        step_config[step_id] = prompt_config

        LOGGER.debug(f"Updating step config {step_id}: %s", json.dumps(doc, indent=2) )

        await log_coll.document(doc["id"]).set(doc)

        LOGGER.debug(f"Configuration updated successfully")

    else:
        LOGGER.debug(f"No documents found with id: %s", id)
        return


async def run():
    id = "4d3f0b2aa2c811ef9e0b3e3297f4bd07"
    # id = "c90a701ea38111ef9fbe3e3297f4bd07" #DEV
    #id = "68ef54e8a5ec11ef80d63e3297f4bd07" # QA
    #id = "c90a701ea38111ef9fbe3e3297f4bd07" # STAGE
    # id = "" # PRORD


    step_id = "MEDISPAN_MATCHING"
    model = "gemini-1.5-flash-002"
    prompt = PROMPT
    await update_document_operation_definition(id, step_id, model, prompt)
    

def main():
    
    asyncio.run(run())

if __name__ == "__main__":   
    main()
