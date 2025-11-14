import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from models import Document, ExtractedMedication, MedicationValue, MedispanStatus, Page
from services.page_service import PageService


@pytest.fixture
def mock_dependencies():
    with patch('adapters.llm.genai') as mock_genai, \
         patch('adapters.llm.StorageAdapter') as mock_storage_adapter, \
         patch('adapters.llm.CloudTaskAdapter') as mock_cloud_task_adapter, \
         patch('adapters.llm.GooglePubSubAdapter') as mock_pubsub_adapter:
        
        # Setup storage mock
        mock_storage = MagicMock()
        mock_storage.get_base_path = AsyncMock()
        mock_storage.write_text = AsyncMock()
        mock_storage_adapter.return_value = mock_storage

        # Setup cloud task mock
        mock_cloud_task = MagicMock()
        mock_cloud_task.create_task = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_cloud_task

        # Setup pubsub mock
        mock_pubsub = MagicMock()
        mock_pubsub.publish = AsyncMock()
        mock_pubsub_adapter.return_value = mock_pubsub

        yield {
            'genai': mock_genai,
            'storage': mock_storage,
            'cloud_task': mock_cloud_task,
            'pubsub': mock_pubsub
        }
        
@pytest.fixture
def document():
    return Document(
        app_id="test_app",
        tenant_id="test_tenant",
        patient_id="test_patient",
        document_id="test_doc",
        storage_uri="gs://test-bucket/test.pdf",
        created_at="2025-01-01T00:00:00Z",
        total_pages=1
    )

@pytest.fixture
def page():
    return Page(
        page_number=1,
        run_id="test_run",
        storage_uri="gs://test-bucket/test/1.pdf",
        total_pages=1
    )

@pytest.fixture
def llm_response():
    """
    This test data has 3 medications
    The first medication has all fields populated
    The second medication has only strength and dosage populated and is non string (viki-551)
    The third medication has no name
    """
    return """[
        {
            "name": "Aspirin",
            "strength": "81mg",
            "dosage": "1 tablet",
            "route": "oral",
            "frequency": "daily",
            "form": "tablet",
            "start_date": "01/01/2025",
            "end_date": "12/31/2025",
            "discontinued_date": null,
            "instructions": "Take one tablet by mouth daily",
            "explanation": "For heart health"
        },
        {
            "name": "Ibuprofen",
            "strength": 11,
            "dosage": 1,
            "route": "",
            "frequency": "",
            "form": "",
            "start_date": "",
            "end_date": "",
            "discontinued_date": null,
            "instructions": "",
            "explanation": ""
        },
        {
            "name": "",
            "strength": 10,
            "dosage": 1,
            "route": "",
            "frequency": "",
            "form": "",
            "start_date": "",
            "end_date": "",
            "discontinued_date": null,
            "instructions": "",
            "explanation": ""
        }
    ]"""

@pytest.mark.asyncio
async def test_medication_extraction_success(mock_dependencies,document, page, llm_response):
    # Arrange
    with patch('services.page_service.StandardPromptAdapter') as mock_adapter, \
         patch('services.page_service.StorageAdapter') as mock_storage, \
         patch('services.page_service.PageService.get_config') as mock_get_config:
        
        # Setup config mock
        mock_config = {
            "config": {
                "accounting": {
                    "business_unit": "test_bu",
                    "solution_id": "test_solution"
                }
            }
        }
        mock_get_config.return_value = mock_config

        # Setup mocks
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.multi_modal_predict_2 = AsyncMock(return_value=llm_response)
        mock_adapter.extract_json_from_response.return_value =json.loads(llm_response)
        mock_adapter.return_value = mock_adapter_instance

        mock_storage_instance = MagicMock()
        mock_storage_instance.get_base_path = AsyncMock(return_value="test/path")
        mock_storage_instance.write_text = AsyncMock()
        mock_storage.return_value = mock_storage_instance

        # Act
        service = PageService(document, page)
        result = await service.medication()

        # Assert
        assert len(result) == 2  # Only one valid medication should be processed
        med = result[0]
        assert isinstance(med, ExtractedMedication)
        assert med.medication.name == "Aspirin"
        assert med.medication.strength == "81mg"
        assert med.medication.dosage == "1 tablet"
        assert med.medication.route == "oral"
        assert med.medication.frequency == "daily"
        assert med.document_id == document.document_id
        assert med.page_number == page.page_number
        assert med.medispan_status == MedispanStatus.NONE

        # Verify storage write was called
        mock_storage_instance.write_text.assert_called_once()

@pytest.mark.asyncio
async def test_medication_extraction_empty_response(document, page):
    # Arrange
    with patch('services.page_service.StandardPromptAdapter') as mock_adapter, \
         patch('services.page_service.StorageAdapter') as mock_storage, \
         patch('services.page_service.PageService.get_config') as mock_get_config:
        
        # Setup config mock
        mock_config = {
            "config": {
                "accounting": {
                    "business_unit": "test_bu",
                    "solution_id": "test_solution"
                }
            }
        }
        mock_get_config.return_value = mock_config

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.multi_modal_predict_2 = AsyncMock(return_value="raw_llm_response")
        mock_adapter_instance.extract_json_from_response = MagicMock(return_value=None)
        mock_adapter.return_value = mock_adapter_instance

        mock_storage_instance = MagicMock()
        mock_storage_instance.get_base_path = AsyncMock(return_value="test/path")
        mock_storage_instance.write_text = AsyncMock()
        mock_storage.return_value = mock_storage_instance

        # Act
        service = PageService(document, page)
        result = await service.medication()

        # Assert
        assert len(result) == 0
        assert isinstance(result, list)
        
        # Verify empty list was stored
        mock_storage_instance.write_text.assert_called_once()

@pytest.mark.asyncio
async def test_medication_extraction_with_storage_uri(document, page):
    # Arrange
    with patch('services.page_service.StorageAdapter') as mock_storage:
        mock_storage_instance = MagicMock()
        mock_storage_instance.get_base_path = AsyncMock(return_value="test/path")
        mock_storage.return_value = mock_storage_instance

        # Act
        service = PageService(document, page)
        uri = await service.get_medication_storage_uri()

        # Assert
        assert "gs://" in uri
        assert f"{page.run_id}" in uri
        assert f"{page.page_number}.json" in uri