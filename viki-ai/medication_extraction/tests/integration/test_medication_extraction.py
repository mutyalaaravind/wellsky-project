
import json

from models import OrchestrationPriority
from utils.date import now_utc
from models import Document, Page
from services.page_service import PageService
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
async def test_medication_extraction(input_data):
    document=Document(
        app_id="app_id",
        tenant_id="tenant_id",
        patient_id="patient_id",
        document_id="document_id",
        storage_uri="",
        priority= OrchestrationPriority("high"), #OrchestrationPriority.HIGH if request.priority == "high" else OrchestrationPriority.DEFAULT,
        created_at=now_utc()
    )
    page=Page(
        storage_uri="",
        page_number="",
        total_pages="",
        run_id=""
    )
    
    page_service = PageService(document=document, page=page)
    medications = await page_service.medication()

    