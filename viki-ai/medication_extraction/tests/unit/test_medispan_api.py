import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import patch, MagicMock
from adapters.medispan_api import MedispanAPIAdapter, get_id_token
import settings

@pytest.fixture
def medispan_api():
    return MedispanAPIAdapter()

@pytest.fixture
def mock_response():
    return [
        {
            "id": "123",
            "nameDescription": "Test Med",
            "genericName": "Test Generic",
            "route": "ORAL",
            "strength": "10",
            "strengthUnit": "MG",
            "dosageForm": "TABLET"
        }
    ]

@pytest.fixture
def mock_requests():
    with patch('adapters.medispan_api.requests') as mock:
        response = MagicMock()
        response.json.return_value = [
            {
                "id": "123",
                "nameDescription": "Test Med",
                "genericName": "Test Generic",
                "route": "ORAL",
                "strength": "10",
                "strengthUnit": "MG",
                "dosageForm": "TABLET"
            }
        ]
        mock.get.return_value = response
        yield mock

@pytest.fixture
def mock_get_id_token():
    with patch('adapters.medispan_api.get_id_token') as mock:
        mock.return_value = "test-token"
        yield mock

def test_init(medispan_api):
    """Test adapter initialization"""
    assert medispan_api.base_url == settings.MEDISPAN_API_BASE_URL

@pytest.mark.asyncio
async def test_search_medications_success(medispan_api, mock_requests, mock_get_id_token):
    """Test successful medication search"""
    results = await medispan_api.search_medications("test med")
    
    assert len(results) == 1
    med = results[0]
    assert med.id == "123"
    assert med.NameDescription == "Test Med"
    assert med.GenericName == "Test Generic"
    assert med.Route == "ORAL"
    assert med.Strength == "10"
    assert med.StrengthUnitOfMeasure == "MG"
    assert med.Dosage_Form == "TABLET"

    mock_requests.get.assert_called_once()
    mock_get_id_token.assert_called_once()

@pytest.mark.asyncio
async def test_search_medications_error(medispan_api, mock_requests, mock_get_id_token):
    """Test error handling in medication search"""
    mock_requests.get.side_effect = Exception("API Error")
    
    with pytest.raises(Exception) as exc:
        await medispan_api.search_medications("test med")
    
    assert "Error occurred while searching medications" in str(exc.value)

@patch('adapters.medispan_api.google.auth.default')
@patch('adapters.medispan_api.impersonated_credentials.Credentials')
@patch('adapters.medispan_api.impersonated_credentials.IDTokenCredentials')
def test_get_id_token(mock_id_creds, mock_creds, mock_default):
    """Test ID token generation"""
    mock_default.return_value = (MagicMock(), None)
    mock_creds.return_value = MagicMock()
    mock_token = MagicMock()
    mock_token.token = "test-token"
    mock_id_creds.return_value = mock_token
    
    result = get_id_token(
        impersonated_service_account="test@example.com",
        target_audience="https://test.com"
    )
    
    assert result == "test-token"
    mock_default.assert_called_once()
    mock_creds.assert_called_once()
    mock_id_creds.assert_called_once()
    mock_token.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_search_medications_with_params(medispan_api, mock_requests, mock_get_id_token):
    """Test medication search with custom parameters"""
    await medispan_api.search_medications("test med", similarity_threshold=0.8, top_k=5)
    
    mock_requests.get.assert_called_once()
    call_args = mock_requests.get.call_args[1]
    assert call_args['params']['similarity_threshold'] == 0.8
    assert call_args['params']['top_k'] == 5