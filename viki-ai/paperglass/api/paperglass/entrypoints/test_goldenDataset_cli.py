# Do golden data document orchestration using the old configuration
import asyncio
import sys, os
from typing import List
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kink import inject
from paperglass.usecases.commands import CreateDocument, CreateGoldenDatasetTest
from paperglass.infrastructure.ports import IQueryPort
from paperglass.usecases.medications import get_resolved_reconcilled_medications_v3
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.adapters.google import GoogleStorageAdapter
from paperglass.domain.model_testing import TestDataDetails
from paperglass.settings import GCP_PROJECT_ID, CLOUD_PROVIDER
import subprocess
from paperglass.domain.models import DocumentOperationInstance, DocumentOperationInstanceLog

from mktoken import mktoken, mktoken2
from google.cloud import firestore
import csv
from paperglass.domain.time import now_utc
from paperglass.entrypoints import test_orchestrator_flash as tf

GCS_TEST_BUCKET = "viki-test"
app_id = "007"
tenant_id = "54321"
patient_id_pro = "dec60138be8c4bd98ed223793dc6d475"
patient_id_new = "7c03ff786c904cf5a128704d5a1081f7"
excel_name = "GoldenDataSet.xlxs"


@inject
async def load_golden_data_set(patient_id: str,command_handler: ICommandHandlingPort):
    try:

        test_storage = lambda _: GoogleStorageAdapter(GCP_PROJECT_ID, GCS_TEST_BUCKET, CLOUD_PROVIDER)
        adapter_test = test_storage(None)
        document_list = []
        for i in range(16, 21):
            gsutil_uri = f"gs://viki-test/golden_data_set/test data {i}.pdf"
            print(f"Reading file from GCS: {gsutil_uri}")
            file_content = await adapter_test.get_document_raw(gsutil_uri)
            doc_id = await command_handler.handle_command(
                CreateDocument(
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    file_name=f"test data{i}.pdf",
                    file=file_content,
                    token=mktoken2(app_id, tenant_id, patient_id),
                    metadata=None,
                )
            )
            document_list.append({'document_id': doc_id.id, 'file_name': f"test data{i}.pdf"})
        return document_list
    except subprocess.CalledProcessError as e:
        print(f"Error reading file from GCS: {e}")
        print(f"Output: {e.output}")
        print(f"Error Output: {e.stderr}")


def is_medication_in_document(medication, document_id):
    if medication.get("extracted_medication_reference"):
        for extracted_reference in medication.get("extracted_medication_reference"):
            if extracted_reference.get("document_id") == document_id:
                return True
    return False


@inject
async def get_medication_profile(document_id, patient_id, tenant_id, app_id, query: IQueryPort):
    document_ids = document_id
    ret = [
        x.dict()
        for x in await get_resolved_reconcilled_medications_v3(document_ids, patient_id, app_id, tenant_id, query)
    ]

    filtered_medications = []

    for medication in ret:
        if is_medication_in_document(medication, document_id):
            filtered_medications.append(medication)

    return json.loads(json.dumps(filtered_medications, indent=4, sort_keys=True, default=str))


@inject
async def update_golden_data_set(
    patient_id:str,document_id: str, test_document_path: str, query: IQueryPort, commands: ICommandHandlingPort
):  
    test_data = TestDataDetails.create(
        app_id=app_id,
        tenant_id=tenant_id,
        patient_id=patient_id,
        document_id=document_id,
        test_document=test_document_path
    )
    test_data_create_command: CreateGoldenDatasetTest = CreateGoldenDatasetTest(test_data=test_data)
    await commands.handle_command(test_data_create_command)


async def create_golden_data_set():
    document_list = await load_golden_data_set(patient_id_pro)
    for document in document_list:
        document_id = document.get('document_id')
        test_document_path = document.get('file_name')
        await update_golden_data_set(patient_id_pro,document_id, test_document_path)

        


if __name__ == '__main__':
    # asyncio.run(create_golden_data_set())
    # asyncio.run(create_golden_data_set())
    asyncio.run(load_golden_data_set(patient_id_new))
