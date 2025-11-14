import sys, os
import asyncio
import uuid
from typing import List
import base64
from functools import wraps
import jwt,json
from datetime import datetime, timezone, timedelta

from kink import inject

from google.auth import compute_engine
from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.time import now_utc

from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.values import DocumentOperationType, DocumentOperationStatus, MedispanStatus
from paperglass.domain.model_testing import TestCase, TestCaseType, TestResults

from paperglass.usecases.documents import get_document_status, get_document_logs
from paperglass.usecases.medications import get_medications_by_document, get_medication_profile_by_documents,get_resolved_reconcilled_medications

from paperglass.interface.ports import CommandError, ICommandHandlingPort
from paperglass.usecases.commands import (
    QueueOrchestration,
)

from paperglass.infrastructure.ports import IQueryPort

from paperglass.tests.test_automation.testcase_repository import list_test_cases

from paperglass.settings import GCP_LOCATION_2
from paperglass.domain.values import DocumentOperationStep

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from paperglass.infrastructure.ports import IMessagingPort

@inject()
async def run(commands: ICommandHandlingPort):
    LOGGER.debug("Starting run()...")
    document_id = "02fd6b207a9511efa42042004e494300"

    queue_orch_command = QueueOrchestration(document_operation_type=DocumentOperationType.MEDICATION_GRADER.value, document_id=document_id)
    ret = await commands.handle_command(queue_orch_command)
    LOGGER.debug("Queued orchestration for grader to perform grading on document %s: %s", queue_orch_command.document_id, ret)

    #ret = await svc.enable(GCP_LOCATION_2, "command-scheduledwindow-1-trigger-dev", False)

    LOGGER.debug("Finished run()... Output is %s", ret)
    

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()