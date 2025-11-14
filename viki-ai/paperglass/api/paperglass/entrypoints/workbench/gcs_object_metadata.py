import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject # type: ignore

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage # type: ignore
import google.auth # type: ignore
from google.auth.transport import requests # type: ignore

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

async def do_something():
    #object_uri = "gs://wsh-monolith_attachment-dev/AMDocuments2/9381/20250125151452lined up BMP.bmp"
    object_uri = "gs://wsh-monolith_attachment-dev/AMDocuments2/9381/20250125141328lined up TIFF.tiff"

    # Initialize the GCS client
    client = storage.Client()

    # Extract the bucket name and object name from the object_uri
    uri_parts = object_uri.replace("gs://", "").split("/", 1)
    bucket_name = uri_parts[0]
    path = uri_parts[1]    

    #bucket_name, path = self.extract_bucket_and_path(storage_uri)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)

    #blob.reload()
    await asyncio.get_event_loop().run_in_executor(None, blob.reload)
    metadata = await asyncio.get_event_loop().run_in_executor(None, lambda: getattr(blob, 'metadata'))

    LOGGER.debug("Metadata: %s", json.dumps(metadata, indent=2, cls=DateTimeEncoder))


async def run():
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()