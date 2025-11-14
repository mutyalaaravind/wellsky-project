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
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    MedispanDrug,
    DocumentOperationInstanceLog
)

from paperglass.domain.values import (
    Configuration,
    RuleSet,
    Rule,
    RuleAction,
)

from paperglass.infrastructure.ports import (
    IPromptAdapter,
    IQueryPort,
    IRelevancyFilterPort,
    IUnitOfWorkManagerPort
)

from paperglass.usecases.configuration import get_config


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

cloud_client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)
#cloud_client = firestore.AsyncClient()  # Local emulator
coll = cloud_client.collection("paperglass_app_config")

ruleset_hhh = {
    "key": "file_ingress",
    "rules": [
        {
            "name": "basic_rule",
            "conditions": {
                "all": [                    
                    {
                        # JSONPath support
                        "path": "$.storage_metadata.SOURCE",
                        "operator": "equal",
                        "value": "Medication"
                    }
                ]
            },
            "extra": {
                "actions": [
                    {
                        "id": "extract",        
                        "params": {
                            "queue": "high"
                        },
                        "priority": 100
                    }
                ]
            }
        }
    ],
    "default_actions": [
        {
            "id": "extract",
            "params": {
                "queue": "default"
            },
            "priority": 1
        }
    ]
}


rulesets_hhh = {
    "file_ingress": ruleset_hhh
}

@inject
async def do_something(query: IQueryPort, uowm: IUnitOfWorkManagerPort ):
    app_id = "hhh"

    query = coll.where("app_id","==", app_id)    
    doc_list = await query.get()    
    docs = [doc.to_dict() for doc in doc_list]
    
    for doc in docs:
        if doc["active"] == False:
            continue
        config = doc["config"]
        if True or "rulesets" not in config:
            LOGGER.debug("No ruleset found for app_id: %s  Adding...", app_id)
            LOGGER.debug("Config: %s", json.dumps(doc, cls=DateTimeEncoder, indent=2))

            doc["config"]["rulesets"] = rulesets_hhh
            

            LOGGER.debug("Updating config for app_id: %s", app_id)
            await coll.document(doc["id"]).set(doc)

            LOGGER.debug("Configuration updated successfully")
        else:
            LOGGER.debug("(Ignoring) Ruleset found for app_id: %s", app_id)           


async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()