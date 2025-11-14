
import json

import asyncio,sys, pytest,pytest_asyncio

from tests.integration.decorators import read_from_file

from services.medispan_service import MedispanMatchService,MedispanStatus
from models import ExtractedMedication

@pytest_asyncio.fixture
async def input_data():
    
    @read_from_file("tests/integration/data/viki-518.json")
    async def data(data:str):
        return data
    
    return data()
    
@pytest.mark.asyncio
async def test_medispan_match(input_data):
    app_id="hhh"
    tenant_id="dummy_tenant_id"
    patient_id="dummy_patient_id"
    document_id="dummy_document_id"              
    page_number=45
    run_id="dummy_run_id"
    extracted_medications=json.loads(await input_data)
    extracted_medications = [ExtractedMedication(**med) for med in extracted_medications]
    
    medispan_matched_medications = await MedispanMatchService().run(app_id, tenant_id, patient_id, document_id, page_number, run_id, extracted_medications)
    assert len(medispan_matched_medications) == len(extracted_medications)
    not_matched = [med for med in medispan_matched_medications if med.medispan_status == MedispanStatus.NONE]
    matched = [med for med in medispan_matched_medications if med.medispan_status == MedispanStatus.MATCHED]
    assert len(not_matched) + len(matched) == len(medispan_matched_medications)
    assert len(not_matched) + len(matched) == len(extracted_medications)
    assert len(not_matched) > 0
    assert len(matched) > 0

    