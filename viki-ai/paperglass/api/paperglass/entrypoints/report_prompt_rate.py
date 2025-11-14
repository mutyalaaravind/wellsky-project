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
from paperglass.domain.values import DocumentOperationStatus, MedispanStatus
from paperglass.domain.model_testing import TestCase, TestCaseType, TestResults

from paperglass.usecases.documents import get_document_status, get_document_logs
from paperglass.usecases.medications import get_medications_by_document, get_medication_profile_by_documents,get_resolved_reconcilled_medications

from paperglass.interface.ports import CommandError, ICommandHandlingPort
from paperglass.usecases.commands import (
    Orchestrate,
    SaveTestResults
)

from paperglass.infrastructure.ports import IQueryPort

from paperglass.tests.test_automation.testcase_repository import list_test_cases

from paperglass.settings import GCP_FIRESTORE_DB
from paperglass.domain.values import DocumentOperationStep

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)



client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)
log_coll = client.collection("paperglass_document_operation_instance_log")

async def list_log_entries(step_id: str):
    LOGGER.debug(f"list_log_entries called with {step_id}")
    query = log_coll.where('step_id', '==', step_id)
    LOGGER.debug("Query built")
    docs = await query.get()
    LOGGER.debug("Query executed")
    return [x.to_dict() for x in docs]

async def calc_generic_step(step_id: str):
    entries = await list_log_entries(step_id)

    no_data = []
    total_in = 0
    total_out = 0
    total_cnt = 0

    for entry in entries:
        context = entry["context"]
        if not "llm_prompt" in context:
            no_data.append(entry)
            continue
        if not "model_response" in context:
            no_data.append(entry)
            continue

        llm_prompt = ""
        for prompt in context["llm_prompt"]:
            llm_prompt += prompt

        llm_response = context["model_response"]
        total_in = total_in + len(llm_prompt)
        total_out = total_out + len(llm_response)

        total_cnt += 1

    avg_in = 0
    avg_out = 0
    if total_cnt > 0:
        avg_in = total_in / total_cnt
        avg_out = total_out / total_cnt
  

    ret = {
        "avg_in": avg_in,
        "avg_out": avg_out,        
        "total_out": total_out,
        "total_cnt": total_cnt,
        "error_count": len(no_data)
    }

    return ret

async def calc_normalized_step(step_id: str):
    entries = await list_log_entries(step_id)

    no_data = []
    total_in = 0
    total_out = 0
    total_cnt = 0

    for entry in entries:
        context = entry["context"]
        if not "llm_prompt" in context:
            no_data.append(entry)
            continue
        if not "llm_raw_response" in context:
            no_data.append(entry)
            continue

        llm_prompt = context["llm_prompt"]
        llm_response = context["llm_raw_response"]
        total_in = total_in + len(llm_prompt)
        total_out = total_out + len(llm_response)

        total_cnt += 1

    avg_in = 0
    avg_out = 0
    if total_cnt > 0:
        avg_in = total_in / total_cnt
        avg_out = total_out / total_cnt
  

    ret = {
        "avg_in": avg_in,
        "avg_out": avg_out,        
        "total_out": total_out,
        "total_cnt": total_cnt,
        "error_count": len(no_data)
    }

    return ret

async def calc_medispan_step(step_id: str):
    entries = await list_log_entries(step_id)

    no_data = []
    total_in = 0
    total_out = 0
    total_cnt = 0

    for entry in entries:
        context = entry["context"]
        if not "medications" in context:
            no_data.append(entry)
            continue
        if not "step_results" in context:
            no_data.append(entry)
            continue

        input = context["medications"]
        prompt = """
            For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:\n 1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match\n 2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength\n 3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form\n 4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route\n 5) Otherwise, return "{}" and specific what attributes were not found\n \n Only return the best match from the list. If no match is found, return "{}"\n \n Only return the best match from the list. If no match is found, return "{}"\n \n GIVEN MEDICATION:\n {SEARCH_TERM}\n \n MATCH LIST:\n
        """
        input_str = json.dumps(input)
        llm_prompt = prompt + input_str

        llm_response = json.dumps(context["step_results"])


        total_in = total_in + len(llm_prompt)
        total_out = total_out + len(llm_response)

        total_cnt += 1

    avg_in = 0
    avg_out = 0
    if total_cnt > 0:
        avg_in = total_in / total_cnt
        avg_out = total_out / total_cnt
  

    ret = {
        "avg_in": avg_in,
        "avg_out": avg_out,        
        "total_out": total_out,
        "total_cnt": total_cnt,
        "error_count": len(no_data)
    }

    return ret

async def run():
    LOGGER.debug("Starting run()...")
    out = {}

    this_step = DocumentOperationStep.TEXT_EXTRACTION.value
    out[this_step] = await calc_generic_step(this_step)

    this_step = DocumentOperationStep.CLASSIFICATION.value
    out[this_step] = await calc_generic_step(this_step)
    
    this_step = DocumentOperationStep.MEDICATIONS_EXTRACTION.value
    out[this_step] = await calc_generic_step(this_step)

    this_step = DocumentOperationStep.MEDISPAN_MATCHING.value
    out[this_step] = await calc_medispan_step(this_step)

    this_step = DocumentOperationStep.NORMALIZE_MEDICATIONS.value
    out[this_step] = await calc_normalized_step(this_step)

    this_step = DocumentOperationStep.ALLERGIES_EXTRACTION.value
    out[this_step] = await calc_generic_step(this_step)

    this_step = DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value
    out[this_step] = await calc_generic_step(this_step)




    LOGGER.debug("Final Results: %s", json.dumps(out, indent=2, cls=DateTimeEncoder))


def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()