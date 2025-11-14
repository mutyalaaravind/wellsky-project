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
from paperglass.domain.model_testing import E2ETestCaseSummaryResults

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.commands import AssessTestCaseSummaryResults
from paperglass.usecases.e2e_v4_tests import TestHarness

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

@inject
async def list_documents(query: IQueryPort):
    documents = await query.list_documents_in_test_run("65f349a4c6d54f7097b41cb04b02c07a")
    LOGGER.info(f"documents: {json.dumps([x.dict() for x in documents], indent=2, cls=DateTimeEncoder)}")

@inject
async def do_something(commands: ICommandHandlingPort):

    command = AssessTestCaseSummaryResults(run_id="5f7352707e824ee38eef284356301fbf")
    results:E2ETestCaseSummaryResults = await commands.handle_command(command)
    results.test_cases = None
    LOGGER.info(f"results: {json.dumps(results.dict(), indent=2, cls=DateTimeEncoder)}")

@inject
async def get_tldr(commands: ICommandHandlingPort):
    test_harness = TestHarness()
    mode="sample"
    age_window=2880
    f1_threshold=0.85
    results = await test_harness.get_testcase_latest_tldr(mode=mode, age_window=age_window, f1_threshold=f1_threshold)

    LOGGER.info(f"results: {results['summary']}")

async def run():    
    #results = await do_something()
    await list_documents()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()