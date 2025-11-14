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

data = {
  "kind": "storage#object",
  "id": "wsh-monolith_attachment-prod/AMDocuments2/16918/20250117151329Physician Order 1220914594 _ Julian Restrepo.pdf/1737148409677498",
  "selfLink": "https://www.googleapis.com/storage/v1/b/wsh-monolith_attachment-prod/o/AMDocuments2%2F16918%2F20250117151329Physician%20Order%201220914594%20_%20Julian%20Restrepo.pdf",
  "name": "AMDocuments2/16918/20250117151329Physician Order 1220914594 _ Julian Restrepo.pdf",
  "bucket": "wsh-monolith_attachment-prod",
  "generation": "1737148409677498",
  "metageneration": "1",
  "contentType": "*/*",
  "timeCreated": "2025-01-17T21:13:29.700Z",
  "updated": "2025-01-17T21:13:29.700Z",
  "storageClass": "MULTI_REGIONAL",
  "timeStorageClassUpdated": "2025-01-17T21:13:29.700Z",
  "size": "316742",
  "metadata": {
    "extract_enabled": True,
  },
  "md5Hash": "LHSRSZKVKd0poiB/yp0eOg==",
  "mediaLink": "https://storage.googleapis.com/download/storage/v1/b/wsh-monolith_attachment-prod/o/AMDocuments2%2F16918%2F20250117151329Physician%20Order%201220914594%20_%20Julian%20Restrepo.pdf?generation=1737148409677498&alt=media",
  "crc32c": "csDzwg==",
  "etag": "CLqNho/W/YoDEAE="
}

async def do_something():
    from python_rule_engine import RuleEngine

    rule = {
        "name": "basic_rule",
        "conditions": {
            "all": [
                {
                    # JSONPath support
                    "path": "$.kind",
                    "operator": "equal",
                    "value": "storage#object"
                },
                {
                    "path": "$.bucket",
                    "operator": "equal",
                    "value": "wsh-monolith_attachment-prod"
                }
            ]
        },
        "extra": {
            "action": "extract"
        }
    }

    rule2 = {
        "name": "basic_rule2",
        "conditions": {
            "all": [
                {
                    # JSONPath support
                    "path": "$.metadata.extract_enabled",
                    "operator": "equal",
                    "value": True
                }
            ]
        },
        "extra": {
            "action": "extract_hard"
        }
    }

    rules = [rule, rule2]

    obj = {
        "person": {
            "name": "Lionel",
            "last_name": "Messi"
        }
    }

    engine = RuleEngine(rules)

    results = engine.evaluate(data)

    LOGGER.debug("Results: %s", results)

    for item in results:
        LOGGER.debug("Result: %s", json.dumps(item.extra, indent=2, cls=DateTimeEncoder))        

async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()