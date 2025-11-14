import os
import pytest
from unittest.mock import Mock, patch
import aiohttp
from typing import Optional

# Set required environment variables before any imports
os.environ.update({
    'VERSION': 'test',
    'SERVICE': 'test',
    'STAGE': 'test',
    'DEBUG': 'true',
    'CLOUD_PROVIDER': 'test',
    'GCP_PROJECT_ID': 'test',
    'GCP_PUBSUB_PROJECT_ID': 'test',
    'GCS_BUCKET_NAME': 'test',
    'GCP_LOCATION': 'test',
    'GCP_LOCATION_2': 'test',
    'GCP_LOCATION_3': 'test',
    'GCP_MULTI_REGION_FIRESTORE_LOCATON': 'test',
    'GCP_FIRESTORE_DB': 'test',
    'SERVICE_ACCOUNT_EMAIL': 'test',
    'SELF_API_URL': 'test',
    'SELF_API_URL_2': 'test',
    'PAPERGLASS_API_URL': 'test',
    'PAPERGLASS_INTEGRATION_TOPIC': 'test',
    'DJT_API_URL': 'test',
    'MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME': 'test'
})

from src.adapters.schema_client import SchemaClient

class MockResponse:
    """Mock aiohttp response with async context manager support"""
    def __init__(self, status=200, json_data=None, text=""):
        self.status = status
        self._json = json_data
        self._text = text

    async def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockSession:
    """Mock aiohttp ClientSession with proper async context management"""
    def __init__(self):
        self.response = None
        self.calls = []

    def set_response(self, response):
        self.response = response

    def get(self, url, **kwargs):
        if isinstance(self.response, Exception):
            raise self.response
        self.calls.append(url)
        return self.response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def client():
    return SchemaClient()

@pytest.fixture
def mock_session():
    return MockSession()

def test_schema_client_init():
    """Test SchemaClient initialization"""
    client = SchemaClient()
    assert isinstance(client, SchemaClient)

@pytest.mark.asyncio
async def test_get_entity_schema_success(client, mock_session):
    """Test successful schema retrieval"""
    url = "http://example.com/schema"
    expected_schema = {"schema": "test"}
    mock_session.set_response(MockResponse(status=200, json_data=expected_schema))

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await client.get_entity_schema(url)
        assert result == expected_schema
        assert mock_session.calls == [f"{url}?usecase=extract"]

@pytest.mark.asyncio
async def test_get_entity_schema_with_existing_params(client, mock_session):
    """Test schema retrieval with existing URL parameters"""
    url = "http://example.com/schema?version=1"
    expected_schema = {"schema": "test"}
    mock_session.set_response(MockResponse(status=200, json_data=expected_schema))

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await client.get_entity_schema(url)
        assert result == expected_schema
        assert mock_session.calls == [f"{url}&usecase=extract"]

@pytest.mark.asyncio
async def test_get_entity_schema_error_response(client, mock_session):
    """Test schema retrieval with error response"""
    url = "http://example.com/schema"
    mock_session.set_response(MockResponse(status=404, text="Not found"))

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await client.get_entity_schema(url)
        assert result is None
        assert mock_session.calls == [f"{url}?usecase=extract"]

@pytest.mark.asyncio
async def test_get_entity_schema_connection_error(client, mock_session):
    """Test schema retrieval with connection error"""
    url = "http://example.com/schema"
    mock_session.set_response(aiohttp.ClientError("Connection failed"))

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await client.get_entity_schema(url)
        assert result is None
        assert mock_session.calls == []

@pytest.mark.asyncio
async def test_get_entity_schema_cache(client, mock_session):
    """Test schema retrieval caching"""
    url = "http://example.com/schema"
    expected_schema = {"schema": "test"}
    mock_session.set_response(MockResponse(status=200, json_data=expected_schema))

    with patch('aiohttp.ClientSession', return_value=mock_session):
        # First request
        result1 = await client.get_entity_schema(url)
        assert result1 == expected_schema
        assert len(mock_session.calls) == 1

        # Second request should use cache
        mock_session.set_response(MockResponse(status=404, text="Should not be called"))
        result2 = await client.get_entity_schema(url)
        assert result2 == expected_schema
        # Call count should remain 1 since we used cache
        assert len(mock_session.calls) == 1

@pytest.mark.asyncio
async def test_get_entity_schema_json_error(client, mock_session):
    """Test schema retrieval with JSON decode error"""
    url = "http://example.com/schema"
    mock_session.set_response(MockResponse(status=200, json_data=ValueError("Invalid JSON")))

    with patch('aiohttp.ClientSession', return_value=mock_session):
        result = await client.get_entity_schema(url)
        assert result is None
        assert mock_session.calls == [f"{url}?usecase=extract"]
