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

from paperglass.settings import GCP_FIRESTORE_DB
from paperglass.domain.util_json import DateTimeEncoder, convertToJson
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    Medication,
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

JSONSTR = "```json\n[\n  {\n    \"name\": \"INSULIN REG HUMAN NOVOLIN R\",\n    \"strength\": \"100 UNIT/ML\",\n    \"dosage\": null,\n    \"route\": \"SUBCUTANEOUSLY\",\n    \"form\": null,\n    \"discontinued_date\": null,\n    \"frequency\": \"AC\\T\\HS\",\n    \"start_date\": null,\n    \"end_date\": null,\n    \"instructions\": null,\n    \"explanation\": null,\n    \"document_reference\": null,\n    \"page_number\": 8\n  },\n  {\n    \"name\": \"ATORVASTATIN CALCIUM\",\n    \"strength\": \"40MG\",\n    \"dosage\": \"1 TAB\",\n    \"route\": \"MOUTH\",\n    \"form\": \"TAB\",\n    \"discontinued_date\": null,\n    \"frequency\": \"ONE TIME EACH DAY\",\n    \"start_date\": null,\n    \"end_date\": null,\n    \"instructions\": null,\n    \"explanation\": null,\n    \"document_reference\": null,\n    \"page_number\": 8\n  },\n  {\n    \"name\": \"APIXABAN\",\n    \"strength\": \"5MG\",\n    \"dosage\": \"1 TAB\",\n    \"route\": \"MOUTH\",\n    \"form\": \"TAB\",\n    \"discontinued_date\": null,\n    \"frequency\": \"EVERY 12 HOURS\",\n    \"start_date\": null,\n    \"end_date\": null,\n    \"instructions\": null,\n    \"explanation\": null,\n    \"document_reference\": null,\n    \"page_number\": 8\n  },\n  {\n    \"name\": \"BUMETANIDE\",\n    \"strength\": \"1MG\",\n    \"dosage\": \"1 TAB\",\n    \"route\": \"MOUTH\",\n    \"form\": \"TAB\",\n    \"discontinued_date\": null,\n    \"frequency\": \"ONE TIME EACH DAY\",\n    \"start_date\": null,\n    \"end_date\": null,\n    \"instructions\": null,\n    \"explanation\": null,\n    \"document_reference\": null,\n    \"page_number\": 8\n  },\n  {\n    \"name\": \"CARVEDILOL\",\n    \"strength\": \"6.25MG\",\n    \"dosage\": \"1 TAB\",\n    \"route\": \"MOUTH\",\n    \"form\": \"TAB\",\n    \"discontinued_date\": null,\n    \"frequency\": \"EVERY 12 HOURS\",\n    \"start_date\": null,\n    \"end_date\": null,\n    \"instructions\": null,\n    \"explanation\": null,\n    \"document_reference\": null,\n    \"page_number\": 8\n  }\n]\n```"

async def do_something():
    LOGGER.debug("Testing something")
    result = JSONSTR
    result = result.replace('**', '').replace('##', '').replace('```', '').replace('json', '')    
    
    #rslt = json.loads(result)
    #LOGGER.debug("Medication input: %s", rslt)

    #for r in rslt:        
    #    LOGGER.debug("Medication frequency: %s", r["frequency"])
    
    output = Medication.toJSON(result)
    LOGGER.debug("Medication output: %s", output)
    for o in output:
        LOGGER.debug("Medication frequency: %s", o["frequency"])

async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()