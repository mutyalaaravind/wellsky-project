import pytest
import sys
import os
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock environment variables before importing main
test_env_vars = {
    'VERSION': '1.0.0',
    'SERVICE': 'entity-extraction',
    'STAGE': 'test',
    'DEBUG': 'false',
    'CLOUD_PROVIDER': 'gcp',
    'GCP_PROJECT_ID': 'test-project',
    'GCP_PUBSUB_PROJECT_ID': 'test-project',
    'GCS_BUCKET_NAME': 'test-bucket',
    'GCP_LOCATION': 'us-central1',
    'GCP_LOCATION_2': 'us-east1',
    'GCP_LOCATION_3': 'us-west1',
    'GCP_MULTI_REGION_FIRESTORE_LOCATON': 'nam5',
    'GCP_FIRESTORE_DB': 'test-db',
    'SERVICE_ACCOUNT_EMAIL': 'test@test-project.iam.gserviceaccount.com',
    'SELF_API_URL': 'http://localhost:8000',
    'SELF_API_URL_2': 'http://localhost:8001',
    'PAPERGLASS_API_URL': 'http://localhost:9000',
    'PAPERGLASS_INTEGRATION_TOPIC': 'test-topic'
}

with patch.dict(os.environ, test_env_vars):
    from main import app
from models.pipeline_config import PipelineConfig, TaskConfig, TaskType
from datetime import datetime

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Reset app dependencies before each test
    app.dependency_overrides = {}
    yield
    # Clean up after each test
    app.dependency_overrides = {}

@pytest.fixture
def mock_auth_info():
    """Default auth info for successful authentication"""
    return {
        "authenticated": True,
        "token_subject": "test-subject",
        "token_email": "test@example.com",
        "service_account": "test-service-account",
        "cloud_provider": "gcp"
    }

@pytest.fixture
def auth_headers():
    """Valid auth headers for testing"""
    return {"Authorization": "Bearer valid-test-token"}

def test_root_endpoint():
    """Test the root endpoint returns welcome message (public endpoint)."""
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Entity Extraction API"}

def test_health_endpoint():
    """Test the health check endpoint (public endpoint)."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_cors_headers():
    """Test that CORS headers are properly configured."""
    response = client.get("/api/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-credentials" in response.headers

@patch('usecases.pipeline_start.search_pipeline_config')
def test_start_pipeline_with_auth(mock_search_config, mock_auth_info, auth_headers):
    """Test the start pipeline endpoint."""
    # Create a mock pipeline configuration
    mock_config = PipelineConfig(
        key="test-pipeline",
        version="1.0",
        name="Test Pipeline",
        scope="test-scope",
        tasks=[
            TaskConfig(
                id="TEST_TASK",
                type=TaskType.MODULE
            )
        ]
    )
    
    # Mock the search_pipeline_config function to return our mock config
    mock_search_config.return_value = mock_config
    
    response = client.post("/api/pipeline/test-scope/test-pipeline/start", json={"test": "data"})
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "test-pipeline"
    assert data["name"] == "Test Pipeline"
    assert data["scope"] == "test-scope"
    assert len(data["tasks"]) == 1
    
    # Verify the mock was called with correct parameters
    mock_search_config.assert_called_once_with("test-scope", "test-pipeline")

@patch('middleware.security.require_service_account_auth')
def test_run_pipeline_task_with_auth(mock_auth, mock_auth_info, auth_headers):
    """Test the run pipeline task endpoint with valid auth."""
    mock_auth.return_value = mock_auth_info
    response = client.post(
        "/api/pipeline/test-scope/test-pipeline/extract-entities/run",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Pipeline task 'extract-entities' running for scope: test-scope, pipeline: test-pipeline"
    assert data["scope"] == "test-scope"
    assert data["pipeline_key"] == "test-pipeline"
    assert data["task"] == "extract-entities"
    assert data["status"] == "running"

@patch('main.list_active_pipeline_configs')
def test_list_all_pipeline_configs_unauthorized(mock_list_configs):
    """Test list configs endpoint without auth fails."""
    response = client.get("/api/config")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

@patch('main.list_active_pipeline_configs')
def test_list_all_pipeline_configs_with_auth(mock_list_configs, mock_auth_info, auth_headers):
    """Test the list all pipeline configs endpoint."""
    # Create mock pipeline configurations
    mock_config1 = PipelineConfig(
        key="test-pipeline-1",
        version="1.0",
        name="Test Pipeline 1",
        scope="default",
        tasks=[
            TaskConfig(
                id="TEST_TASK_1",
                type=TaskType.MODULE
            )
        ]
    )
    
    mock_config2 = PipelineConfig(
        key="test-pipeline-2",
        version="1.0",
        name="Test Pipeline 2",
        scope="medical",
        tasks=[
            TaskConfig(
                id="TEST_TASK_2",
                type=TaskType.PROMPT
            )
        ]
    )
    
    # Mock the list_active_pipeline_configs function to return our mock configs
    mock_list_configs.return_value = [mock_config1, mock_config2]
    
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "configurations" in data
    assert "count" in data
    assert data["count"] == 2
    assert len(data["configurations"]) == 2
    
    # Check first config
    config1 = data["configurations"][0]
    assert config1["key"] == "test-pipeline-1"
    assert config1["name"] == "Test Pipeline 1"
    assert config1["scope"] == "default"
    
    # Check second config
    config2 = data["configurations"][1]
    assert config2["key"] == "test-pipeline-2"
    assert config2["name"] == "Test Pipeline 2"
    assert config2["scope"] == "medical"
    
    # Verify the mock was called
    mock_list_configs.assert_called_once()

@patch('main.search_pipeline_config')
def test_get_pipeline_config_not_found_with_auth(mock_search_config, mock_auth_info, auth_headers):
    """Test the get pipeline config endpoint when config is not found."""
    # Mock the search_pipeline_config function to return None (not found)
    mock_search_config.return_value = None
    
    response = client.get("/api/config/test-scope/nonexistent-pipeline")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
    
    # Verify the mock was called with correct parameters
    mock_search_config.assert_called_once_with("test-scope", "nonexistent-pipeline")

def test_request_without_token():
    """Test that protected endpoints require authentication."""
    protected_endpoints = [
        ("/api/config", "GET"),
        ("/api/pipeline/test-scope/test-pipeline/start", "POST"),
        ("/api/pipeline/test-scope/test-pipeline/extract-entities/run", "POST"),
        ("/api/config/pipelines/test-scope/test-pipeline", "POST"),
    ]
    
    for endpoint, method in protected_endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
            
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

@patch('middleware.security.require_service_account_auth')
def test_invalid_token(mock_auth):
    """Test handling of invalid authentication token."""
    from util.oidc_validator import OIDCValidationError
    mock_auth.side_effect = OIDCValidationError("Invalid token format")
    
    response = client.post(
        "/api/pipeline/test-scope/test-pipeline/start",
        json={"test": "data"},
        headers={"Authorization": "Bearer invalid-token"}
    )
    
    assert response.status_code == 401
    assert "Invalid token format" in response.json()["detail"]

@patch('middleware.security.require_service_account_auth')
def test_expired_token(mock_auth):
    """Test handling of expired authentication token."""
    from util.oidc_validator import OIDCValidationError
    mock_auth.side_effect = OIDCValidationError("Token has expired")
    
    response = client.post(
        "/api/pipeline/test-scope/test-pipeline/start",
        json={"test": "data"},
        headers={"Authorization": "Bearer expired-token"}
    )
    
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

@patch('settings.CLOUD_PROVIDER', 'local')
@patch('middleware.security.require_service_account_auth')
def test_local_development_bypass(mock_auth):
    """Test that authentication is bypassed in local development."""
    # Mock auth to return local development bypass info
    mock_auth.return_value = {
        "authenticated": False,
        "bypass_reason": "local_development",
        "cloud_provider": "local"
    }
    
    # Test both GET and POST protected endpoints
    endpoints = [
        (client.get, "/api/config"),
        (client.post, "/api/pipeline/test-scope/test-pipeline/start", {"test": "data"})
    ]
    
    for client_method, *args in endpoints:
        response = client_method(*args)
        assert response.status_code != 401  # Should not be unauthorized
        if response.status_code != 200:  # May fail for other reasons, but not auth
            assert "Authentication required" not in response.json().get("detail", "")

@patch('middleware.security.require_service_account_auth')
def test_malformed_token(mock_auth):
    """Test handling of malformed authentication token."""
    response = client.post(
        "/api/pipeline/test-scope/test-pipeline/start",
        json={"test": "data"},
        headers={"Authorization": "malformed-token-no-bearer"}
    )
    
    assert response.status_code == 401
    assert "Invalid token format" in response.json()["detail"]
