import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

from datetime import timedelta

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

client = storage.Client()
bucket_name = "viki-ai-provisional-dev"


async def do_something():
    LOGGER.debug("Testing something")

    path = "paperglass/documents/ltc/002329:FC34/2852/f7900a6042ce11f0afce42004e494300/document.pdf"

    blob = client.bucket(bucket_name).blob(path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=48),  # TODO: how much TTL?
        method="GET",
    )

    return url

async def run():    
    results = await do_something()

    print("Signed URL:", results)

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()