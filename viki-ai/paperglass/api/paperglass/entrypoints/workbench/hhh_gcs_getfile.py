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

async def do_something():
    #gcs_uri = "gs://wsh-monolith_attachment-prod/AMDocuments2/11716/20250219111135original_fax-1951eee8a83b8064.pdf"
    gcs_uri = "gs://wsh-monolith_attachment-prod/AMDocuments2/17403/20250219111019Mackiewicz_W_DDE.pdf"

    # Extract bucket name and file name from the URI
    bucket_name = gcs_uri.split('/')[2]
    file_name = '/'.join(gcs_uri.split('/')[3:])

    # Initialize the GCS client
    client = storage.Client()

    # Get the bucket and blob
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Retrieve the file's metadata
    blob.reload()
    metadata = blob.metadata

    file_size = blob.size

    # Print the metadata (or process it as needed)
    print("File size: ", file_size)
    print("Metadata: ", json.dumps(metadata, indent=2))

async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()