import pytest
from unittest.mock import MagicMock, patch, create_autospec
import google.cloud.documentai
from google.cloud.documentai import ProcessRequest, GcsDocument, ProcessOptions
from src.adapters.doc_ai import DocumentAIAdapter

@pytest.fixture
def mock_process_request():
    with patch('google.cloud.documentai.ProcessRequest') as mock:
        process_request = MagicMock()
        mock.return_value = process_request
        yield process_request

@pytest.fixture
def mock_gcs_document():
    with patch('google.cloud.documentai.GcsDocument') as mock:
        gcs_doc = MagicMock()
        mock.return_value = gcs_doc
        yield gcs_doc

@pytest.fixture
def mock_process_options():
    with patch('google.cloud.documentai.ProcessOptions') as mock:
        process_options = MagicMock()
        mock.return_value = process_options
        yield process_options

@pytest.fixture
def mock_client_options():
    with patch('google.api_core.client_options.ClientOptions') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_class, mock_instance

@pytest.fixture
def mock_doc_ai_client(mock_process_request, mock_gcs_document, mock_process_options, mock_client_options):
    test_data = {
        "text": "sample text",
        "pages": [
            {
                "pageNumber": 1,
                "tokens": [
                    {
                        "layout": {
                            "boundingPoly": {
                                "vertices": [
                                    {"x": 0, "y": 0},
                                    {"x": 10, "y": 0},
                                    {"x": 10, "y": 10},
                                    {"x": 0, "y": 10}
                                ]
                            }
                        }
                    }
                ]
            }
        ]
    }
    
    test_response = MagicMock()
    test_response.document = MagicMock()
    test_response.document._pb = MagicMock()

    async def async_process_document(*args, **kwargs):
        return test_response

    with patch('google.cloud.documentai.DocumentProcessorServiceAsyncClient') as mock_client:
        with patch('google.auth.default', return_value=(MagicMock(), "project")):
            client_instance = MagicMock()
            client_instance.process_document = async_process_document
            mock_client.return_value = client_instance

            # Mock processor_version_path method
            client_instance.processor_version_path.return_value = "test-processor-path"
            client_instance.processor_path.return_value = "test-processor-path"
            
            # Store test data for access in tests
            mock_client.test_data = test_data
            mock_client.test_response = test_response
            yield mock_client

@pytest.mark.asyncio
async def test_doc_ai_adapter_init():
    with patch('src.adapters.doc_ai.ClientOptions') as mock_client_options:
        with patch('google.cloud.documentai.DocumentProcessorServiceAsyncClient') as mock_doc_ai_client:
            mock_instance = MagicMock()
            mock_client_options.return_value = mock_instance

            adapter = DocumentAIAdapter(
                project_id="test-project",
                location="test-location",
                document_processor_id="test-processor",
                document_processor_version="test-version"
            )
            
            assert adapter.project_id == "test-project"
            assert adapter.location == "test-location"
            mock_client_options.assert_called_once_with(api_endpoint="test-location-documentai.googleapis.com")
            mock_doc_ai_client.assert_called_once_with(client_options=mock_instance)

@pytest.mark.asyncio
async def test_process_document(mock_doc_ai_client):
    with patch('src.adapters.doc_ai.MessageToDict', return_value={
        "text": "sample text",
        "pages": [
            {
                "pageNumber": 1,
                "tokens": [
                    {
                        "layout": {
                            "boundingPoly": {
                                "vertices": [
                                    {"x": 0, "y": 0},
                                    {"x": 10, "y": 0},
                                    {"x": 10, "y": 10},
                                    {"x": 0, "y": 10}
                                ]
                            }
                        }
                    }
                ]
            }
        ]
    }):
        adapter = DocumentAIAdapter(
            project_id="test-project",
            location="test-location",
            document_processor_id="test-processor",
            document_processor_version="test-version"
        )
        
        result = await adapter.process_document(
            storage_uri="gs://test-bucket/test.pdf",
            mime_type="application/pdf"
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["text"] == "sample text"
        assert result[0]["page"]["pageNumber"] == 1

def test_identify_rotation_with_tokens():
    with (patch('src.adapters.doc_ai.ClientOptions') as mock_client_options,
          patch('google.cloud.documentai.DocumentProcessorServiceAsyncClient') as mock_doc_ai_client,
          patch('google.auth.default', return_value=(MagicMock(), "default-project"))):
        
        adapter = DocumentAIAdapter()
        page = {
            "tokens": [
                {
                    "layout": {
                        "boundingPoly": {
                            "vertices": [
                                {"x": 0, "y": 0},
                                {"x": 10, "y": 0},
                                {"x": 10, "y": 10},
                                {"x": 0, "y": 10}
                            ]
                        }
                    }
                }
            ]
        }
        rotation = adapter.identify_rotation(page)
        assert rotation == 0.0

def test_identify_rotation_without_tokens():
    with (patch('src.adapters.doc_ai.ClientOptions') as mock_client_options,
          patch('google.cloud.documentai.DocumentProcessorServiceAsyncClient') as mock_doc_ai_client,
          patch('google.auth.default', return_value=(MagicMock(), "default-project"))):
        
        adapter = DocumentAIAdapter()
        page = {}
        rotation = adapter.identify_rotation(page)
        assert rotation == 0.0

def test_identify_rotation_with_invalid_tokens():
    with (patch('src.adapters.doc_ai.ClientOptions') as mock_client_options,
          patch('google.cloud.documentai.DocumentProcessorServiceAsyncClient') as mock_doc_ai_client,
          patch('google.auth.default', return_value=(MagicMock(), "default-project"))):
        
        adapter = DocumentAIAdapter()
        page = {
            "tokens": [
                {
                    "layout": {
                        "boundingPoly": {
                            "vertices": [
                                {"x": 0},  # Missing y coordinate
                                {"x": 10, "y": 0},
                                {"x": 10, "y": 10},
                                {"x": 0, "y": 10}
                            ]
                        }
                    }
                }
            ]
        }
        rotation = adapter.identify_rotation(page)
        assert rotation == 0.0

@pytest.mark.asyncio
async def test_process_document_with_empty_response(mock_doc_ai_client):
    with patch('src.adapters.doc_ai.MessageToDict') as mock:
        mock.return_value = {
            "text": "",
            "pages": []
        }
        
        adapter = DocumentAIAdapter()
        result = await adapter.process_document(
            storage_uri="gs://test-bucket/test.pdf"
        )
        
        assert isinstance(result, list)
        assert len(result) == 0