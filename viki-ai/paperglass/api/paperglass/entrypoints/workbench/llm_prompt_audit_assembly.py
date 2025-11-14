import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject
from typing import List, Dict, Any

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

from paperglass.domain.string_utils import remove_suffix

async def list_documents_json(path: str) -> List[dict]:
    
        project_id = "viki-dev-app"
        bucket_name = "viki-ai-provisional-dev"
        sync_client = storage.Client(project=project_id)

        results = {}

        LOGGER.debug("list_documents_json: %s", path)
        bucket = sync_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=path)

        for blob in blobs:
            LOGGER.debug("Blob: %s", blob.name)

            if blob.name.endswith('.json'):

                item_key = remove_suffix(_get_filename(blob.name), ".json")
                
                content = _download_and_deserialize_json_blob(blob)

                results[item_key] = content
        
        return results

def _get_filename(blob_name: str) -> str:
    return blob_name.split('/')[-1] 

def _download_and_deserialize_json_blob(blob):
    content = blob.download_as_text()
    return json.loads(content)

async def do_something():
    path = "paperglass/documents/007/54321/29437dd24ffe465eb611a61b0b62f608/184f56f0d3af11ef9b0b42004e494300/logs/cb692f1b4a5a4b4c9dc30acf7f1ee8ba/prompt/"
    results = await list_documents_json(path)

    print(json.dumps(results, cls=DateTimeEncoder, indent=2))

    # Write to file
    output_path = "/tmp/mock-prompt-data.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, cls=DateTimeEncoder, indent=2)

async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()