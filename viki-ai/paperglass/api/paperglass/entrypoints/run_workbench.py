import asyncio
import sys, os
import json
import argparse
import importlib
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

LOGGER.setLevel(logging.INFO)
logging.getLogger('google.auth._default').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('grpc._cython.cygrpc').setLevel(logging.INFO)
logging.getLogger('google.auth.transport.requests').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

def get_args():
    parser = argparse.ArgumentParser(description='Workbench launcher')
    parser.add_argument('--workbench', type=str, help='Workbench to run')
    return parser.parse_args()

async def run(workbench):
    LOGGER.info("Running workbench: %s", workbench)

    module_name = f"paperglass.entrypoints.workbench.{workbench}"
    module = importlib.import_module(module_name)
    
    # Run the main function of the imported module
    if hasattr(module, 'run'):
        await module.run()
    else:
        LOGGER.error(f"Module {module_name} does not have a async run() function")

def main():
    args = get_args()
    asyncio.run(run(args.workbench))

if __name__ == "__main__":
    main()






