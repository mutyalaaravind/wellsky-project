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

from paperglass.api.paperglass.domain.values import Configuration
from paperglass.settings import GCP_FIRESTORE_DB
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    MedispanDrug,
    DocumentOperationInstanceLog,
    ExtractedMedication,
)

from paperglass.usecases.commands import (
    MedispanMatching
)
from paperglass.usecases.step_medispan_matching import (
    StepMedispanMatchingResolver
)

from paperglass.infrastructure.ports import (
    IPromptAdapter,
    IQueryPort,
    IRelevancyFilterPort,
    IUnitOfWorkManagerPort
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

PROMPT_OLD = """
For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
1) The name of medication should be present in the \"content\" field of the MATCH LIST entries. Otherwise say no name match
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

PROMPT = """
For each GIVEN MEDICATIONS, can you find the best medication match from the MATCH LIST given below? Please follow these instructions:
1) The name of the GIVEN MEDICATION should be match the \"NameDescription\" field of the MATCH LIST entries. Otherwise no name match
2) Prefer the match if the MATCH LIST entry's \"NameDescription\" begins with the first word of the GIVEN MEDICATION name
3) Prefer the match if the name of the GIVEN MEDICATION exactly matches (case insensitive) the name of the MATCH LIST \"NameDescription\" entry.  
4) Lower the consideration for the match if the name of the GIVEN MEDICATION only matches the \"GenericName\" field and does not match the \"NameDescription\" field of the MATCH LIST entry.
5) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
6) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
7) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route

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


@inject
async def test_matching(uowm: IUnitOfWorkManagerPort):

    med_dict = {
            "created_at": "2024-11-19T01:16:52.437464+00:00",
            "app_id": "007",
            "route": None,
            "id": "f573d8a4a61311ef909542004e494300",
            "change_sets": [],
            "document_id": "7d6f6e9aa60e11ef860042004e494300",
            "medispan_id": "23638",
            "document_operation_instance_id": "7eeb9316a60e11ef8a4242004e494300",
            "explaination": None,
            "modified_at": "2024-11-19T01:16:52.437468+00:00",
            "active": True,
            "events": [],
            "patient_id": "29437dd24ffe465eb611a61b0b62f608",
            "medispan_medication": None,
            "medispan_status": "MATCHED",
            "page_number": 7,
            "reason": None,
            "medication": {
              "end_date": "09/26/2022",
              "route": "by mouth",
              "name_original": None,
              "medispan_id": None,
              "instructions": "for supplement",
              "form": "Tablet",
              "name": "Ascorbic Acid",
              "is_long_standing": False,
              "discontinued_date": None,
              "classification": None,
              "frequency": "two times a day",
              "dosage": "1 tablet",
              "strength": "250 MG",
              "start_date": "09/26/2022"
            },
            "page_id": "8cf6fc9ca60f11efba0142004e494300",
            "tenant_id": "54321",
            "created_by": None,
            "score": None,
            "document_reference": "7d6f6e9aa60e11ef860042004e494300",
            "modified_by": None,
            "execution_id": None,
            "deleted": False
          }
    
    medication = ExtractedMedication(**med_dict)

    command = MedispanMatching(
        app_id="007",
        tenant_id="54321",
        patient_id="29437dd24ffe465eb611a61b0b62f608",
        document_id="7d6f6e9aa60e11ef860042004e494300",
        document_operation_definition_id="",
        document_operation_instance_id="7eeb9316a60e11ef8a4242004e494300",
        extracted_medications=[medication],
        prompt=PROMPT,
        page_id="8cf6fc9ca60f11efba0142004e494300",
        page_number=7,
        model="gemini-1.5-flash-002",
        is_test=True
    )

    async with uowm.start() as uow:
        results = await StepMedispanMatchingResolver().run(command, uow, Configuration())
        LOGGER.debug("Results: %s", results)

async def run():    
    results = await test_matching()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()