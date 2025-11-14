import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from google.cloud.firestore_v1.vector import Vector
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


# Initialize the cloud Firestore client
cloud_client = firestore.AsyncClient(database="viki-dev")

# Set the environment variable to point to the Firestore emulator
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

# Initialize the local Firestore emulator client
local_client = firestore.AsyncClient()

idx = 0

async def copy_collection(collection_name):
    # Retrieve all documents from the cloud Firestore collection
    cloud_collection_ref = cloud_client.collection(collection_name)
    cloud_docs = cloud_collection_ref.stream()

    # Write documents to the local Firestore emulator collection
    local_collection_ref = local_client.collection(collection_name)
    async for doc in cloud_docs:

        LOGGER.debug("doc: %s", doc.to_dict())
        o = doc.to_dict()
        del o["med_embedding"]
        o["med_embedding"] = Vector([0.1, 0.2, 0.3, 0.4])
        
        await local_collection_ref.document(doc.id).set(o)
        LOGGER.debug(f"Copied document {doc.id} to local Firestore emulator [{str(idx)}]")
        idx += 1

        return
        

async def c_collection(collection_name):
    doc = {
        "id": "1",
        "name": "John Doe",
    }
    local_collection_ref = local_client.collection(collection_name)
    await local_collection_ref.document(doc.get("id")).set(doc)


async def run():    
    results = await copy_collection("medispan_meds")

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()