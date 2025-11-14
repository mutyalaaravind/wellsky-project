"""
Test the new create/update pipeline configuration endpoint.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

# Patch tracing functions before importing the main application
with patch('util.tracing.initialize_tracing', MagicMock()), \
     patch('util.tracing.instrument_libraries', MagicMock()):
    from main import app
    from middleware.security import require_service_account_auth

# Auth test fixtures and mocks
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
def mock_invalid_token():
    """Mock an invalid token scenario"""
    from util.oidc_validator import OIDCValidationError
    return OIDCValidationError("Invalid token format")

@pytest.fixture
def mock_expired_token():
    """Mock an expired token scenario"""
    from util.oidc_validator import OIDCValidationError
    return OIDCValidationError("Token has expired")

@pytest.fixture
def mock_auth_bypass():
    """Auth info when bypassing auth in local development"""
    return {
        "authenticated": False,
        "bypass_reason": "local_development",
        "cloud_provider": "local"
    }

class MockAuthDependency:
    def __init__(self, auth_info=None, should_raise=False, error=None):
        self.auth_info = auth_info
        self.should_raise = should_raise
        self.error = error
    
    async def __call__(self, request: Request):
        if self.should_raise:
            raise self.error
        return self.auth_info

# Initialize mock auth dependency with default values
mock_auth_dependency = MockAuthDependency(auth_info={
    "authenticated": True,
    "token_subject": "test-subject",
    "token_email": "test@example.com",
    "service_account": "test-service-account",
    "cloud_provider": "gcp"
})

client = TestClient(app)

@pytest.fixture
def sample_config_data():
    """Sample pipeline configuration data for testing."""
    return {
        "id": "test-config-001",
        "key": "test-pipeline",
        "scope": "test-scope",
        "name": "Test Pipeline Configuration",
        "description": "A test configuration for unit testing",
        "version": "1.0.0",
        "active": True,
        "tasks": [
            {
                "id": "task-1",
                "name": "Test Task",
                "type": "prompt",
                "prompt": {
                    "model": "gemini-1.5-flash-002",
                    "prompt": "Extract entities from the following text: {text}",
                    "system_instructions": ["You are a helpful assistant."],
                    "response_format": "json",
                    "max_output_tokens": 4096,
                    "temperature": 0.5,
                    "top_p": 0.8
                }
            }
        ]
    }

class TestCreateConfigEndpoint:
    """Test the POST /config/{scope}/{pipeline_key} endpoint with auth scenarios."""
    
    def setup_method(self, mock_auth_info=None):
        """Reset app dependencies before each test"""
        app.dependency_overrides = {}
        # Set up default auth if not provided
        if mock_auth_info is None:
            mock_auth_info = {
                "authenticated": True,
                "token_subject": "test-subject",
                "token_email": "test@example.com",
                "service_account": "test-service-account",
                "cloud_provider": "gcp"
            }
        app.dependency_overrides[require_service_account_auth] = MockAuthDependency(auth_info=mock_auth_info)

    def teardown_method(self):
        """Clean up after each test"""
        app.dependency_overrides = {}

    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_create_new_config_success(self, mock_usecase, sample_config_data):
        """Test creating a new pipeline configuration."""
        # Mock the usecase result
        from usecases.pipeline_config import PipelineConfigResult
        from models.pipeline_config import PipelineConfig
        
        mock_config = PipelineConfig(**sample_config_data)
        mock_result = PipelineConfigResult(
            config=mock_config,
            document_id="doc-123",
            operation="created",
            archived_config_id=None
        )
        mock_usecase.return_value = mock_result
        
        # Make the request
        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Pipeline configuration created successfully"
        assert data["scope"] == "test-scope"
        assert data["pipeline_key"] == "test-pipeline"
        assert data["document_id"] == "doc-123"
        assert data["operation"] == "created"
        assert "archived_config_id" not in data  # No archiving for new configs
        
        # Verify usecase was called correctly
        mock_usecase.assert_called_once_with("test-scope", "test-pipeline", sample_config_data)

    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_update_existing_config_success(self, mock_usecase, sample_config_data):
        """Test updating an existing pipeline configuration."""
        # Mock the usecase result for update
        from usecases.pipeline_config import PipelineConfigResult
        from models.pipeline_config import PipelineConfig
        
        mock_config = PipelineConfig(**sample_config_data)
        mock_result = PipelineConfigResult(
            config=mock_config,
            document_id="doc-789",
            operation="updated",
            archived_config_id="archive-456"
        )
        mock_usecase.return_value = mock_result
        
        # Make the request
        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Pipeline configuration updated successfully"
        assert data["scope"] == "test-scope"
        assert data["pipeline_key"] == "test-pipeline"
        assert data["document_id"] == "doc-789"
        assert data["operation"] == "updated"
        assert data["archived_config_id"] == "archive-456"  # Archive ID included for updates
        
        # Verify usecase was called correctly
        mock_usecase.assert_called_once_with("test-scope", "test-pipeline", sample_config_data)

    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_create_config_validation_error(self, mock_usecase, sample_config_data):
        """Test handling of validation errors."""
        # Mock usecase failure
        mock_usecase.side_effect = ValueError("Invalid configuration: missing required field")
        
        # Make the request
        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data
        )
        
        # Verify error response
        assert response.status_code == 422
        data = response.json()
        assert "Invalid pipeline configuration" in data["detail"]
        assert "missing required field" in data["detail"]

    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_create_config_save_error(self, mock_usecase, sample_config_data):
        """Test handling of save errors."""
        # Mock usecase failure
        mock_usecase.side_effect = Exception("Database connection failed")
        
        # Make the request
        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data
        )
        
        # Verify error response
        assert response.status_code == 500
        data = response.json()
        assert "Error saving pipeline configuration" in data["detail"]
        assert "Database connection failed" in data["detail"]

    def test_create_config_invalid_json(self, mock_auth_info):
        """Test handling of invalid JSON data."""
        # Setup auth
        app.dependency_overrides[require_service_account_auth] = MockAuthDependency(auth_info=mock_auth_info)
        
        # Make request with invalid JSON structure
        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json={"invalid": "structure"}
        )
        
        # Should get validation error
        assert response.status_code == 422

    @patch('settings.CLOUD_PROVIDER', 'local')
    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_auth_bypass_local_development(self, mock_usecase, mock_auth_bypass, sample_config_data):
        """Test authentication bypass in local development."""
        # Mock the usecase to avoid real Firestore calls
        from usecases.pipeline_config import PipelineConfigResult
        from models.pipeline_config import PipelineConfig
        
        mock_config = PipelineConfig(**sample_config_data)
        mock_result = PipelineConfigResult(
            config=mock_config,
            document_id="doc-123",
            operation="created",
            archived_config_id=None
        )
        mock_usecase.return_value = mock_result
        
        app.dependency_overrides[require_service_account_auth] = MockAuthDependency(auth_info=mock_auth_bypass)
        
        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data
        )
        
        assert response.status_code == 200
        
    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_endpoint_accepts_requests_without_auth_validation(self, mock_usecase, sample_config_data):
        """Test that the endpoint processes requests without authentication validation."""
        from usecases.pipeline_config import PipelineConfigResult
        from models.pipeline_config import PipelineConfig

        # Mock successful config creation
        mock_config = PipelineConfig(**sample_config_data)
        mock_result = PipelineConfigResult(
            config=mock_config,
            document_id="doc-123",
            operation="created",
            archived_config_id=None
        )
        mock_usecase.return_value = mock_result

        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data,
            headers={"Authorization": "Bearer any-token"}  # Token is ignored since no auth
        )

        assert response.status_code == 200
        assert "created successfully" in response.json()["message"]
        
    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_endpoint_processes_requests_with_no_headers(self, mock_usecase, sample_config_data):
        """Test that the endpoint processes requests even without authorization headers."""
        from usecases.pipeline_config import PipelineConfigResult
        from models.pipeline_config import PipelineConfig

        # Mock successful config creation
        mock_config = PipelineConfig(**sample_config_data)
        mock_result = PipelineConfigResult(
            config=mock_config,
            document_id="doc-456",
            operation="created",
            archived_config_id=None
        )
        mock_usecase.return_value = mock_result

        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data
            # No headers provided
        )

        assert response.status_code == 200
        assert "created successfully" in response.json()["message"]

    @patch('routers.config_pipeline.create_or_update_pipeline_config')
    def test_endpoint_accepts_empty_headers(self, mock_usecase, sample_config_data):
        """Test that the endpoint accepts requests with empty headers."""
        from usecases.pipeline_config import PipelineConfigResult
        from models.pipeline_config import PipelineConfig

        # Mock successful config creation
        mock_config = PipelineConfig(**sample_config_data)
        mock_result = PipelineConfigResult(
            config=mock_config,
            document_id="doc-789",
            operation="created",
            archived_config_id=None
        )
        mock_usecase.return_value = mock_result

        # Reset any existing overrides
        app.dependency_overrides = {}

        response = client.post(
            "/api/config/pipelines/test-scope/test-pipeline",
            json=sample_config_data,
            headers={}  # Explicitly send no headers
        )

        assert response.status_code == 200
        assert "created successfully" in response.json()["message"]
