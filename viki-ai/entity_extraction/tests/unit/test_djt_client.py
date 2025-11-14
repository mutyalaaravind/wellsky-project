import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.test_env import setup_test_env
setup_test_env()

import pytest
from unittest.mock import patch, AsyncMock
import httpx

from adapters.djt_client import DistributedJobTracking, get_djt_client
from models.djt_models import PipelineStatusUpdate, PipelineStatus

class TestDistributedJobTracking:
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'gcp')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    @patch('adapters.djt_client.get_oidc_headers')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_get_job_pipelines_success_with_auth(self, mock_client, mock_auth_headers):
        """Test successful job pipelines retrieval with authentication."""
        # Mock the authentication headers
        mock_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_auth_headers.return_value = mock_headers
        
        # Mock the httpx response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "job_id": "test-run-id",
            "status": "running",
            "pipelines": [
                {"name": "pipeline1", "status": "completed"},
                {"name": "pipeline2", "status": "running"}
            ]
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        result = await djt_client.get_job_pipelines("test-run-id")
        
        # Assertions
        assert result["job_id"] == "test-run-id"
        assert result["status"] == "running"
        assert len(result["pipelines"]) == 2
        
        # Verify the correct URL and headers were used
        expected_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_client_instance.get.assert_called_once_with(
            "http://test-djt-api/api/v1/jobs/test-run-id/pipelines",
            headers=expected_headers
        )
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'local')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://localhost:8001')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_get_job_pipelines_success_no_auth(self, mock_client):
        """Test successful job pipelines retrieval without authentication (local)."""
        # Mock the httpx response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "job_id": "test-run-id",
            "status": "completed"
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        result = await djt_client.get_job_pipelines("test-run-id")
        
        # Assertions
        assert result["job_id"] == "test-run-id"
        assert result["status"] == "completed"
        
        # Verify no Authorization header is included for local environment
        expected_headers = {
            "Content-Type": "application/json"
        }
        mock_client_instance.get.assert_called_once_with(
            "http://localhost:8001/api/v1/jobs/test-run-id/pipelines",
            headers=expected_headers
        )
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'gcp')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    @patch('adapters.djt_client.get_oidc_headers')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_get_job_pipelines_not_found(self, mock_client, mock_auth_headers):
        """Test job pipelines retrieval when job is not found."""
        # Mock the authentication headers
        mock_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_auth_headers.return_value = mock_headers
        
        # Mock the httpx response for 404
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = "Job not found"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        
        with pytest.raises(Exception) as exc_info:
            await djt_client.get_job_pipelines("nonexistent-run-id")
        
        # Verify the exception has the correct status code
        assert hasattr(exc_info.value, 'status_code')
        assert exc_info.value.status_code == 404
        assert "DJT API returned status 404" in str(exc_info.value)
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'gcp')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    @patch('adapters.djt_client.get_oidc_headers')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_get_job_pipelines_network_error(self, mock_client, mock_auth_headers):
        """Test job pipelines retrieval when network error occurs."""
        # Mock the authentication headers
        mock_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_auth_headers.return_value = mock_headers
        
        # Mock network error
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = httpx.RequestError("Connection failed")
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        
        with pytest.raises(Exception) as exc_info:
            await djt_client.get_job_pipelines("test-run-id")
        
        # Verify the exception message
        assert "Unable to connect to distributed job tracking service" in str(exc_info.value)
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'gcp')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    @patch('adapters.djt_client.get_oidc_headers')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_health_check_success(self, mock_client, mock_auth_headers):
        """Test successful health check."""
        # Mock the authentication headers
        mock_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_auth_headers.return_value = mock_headers
        
        # Mock the httpx response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"status": "healthy"})
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        result = await djt_client.health_check()
        
        # Assertions
        assert result["status"] == "healthy"
        
        # Verify the correct URL was called
        mock_client_instance.get.assert_called_once_with(
            "http://test-djt-api/health",
            headers={
                "Authorization": "Bearer mock-auth-token",
                "Content-Type": "application/json"
            }
        )
    
    def test_get_djt_client_factory(self):
        """Test the factory function for creating DJT client instances."""
        # Test with default settings
        client1 = get_djt_client()
        assert isinstance(client1, DistributedJobTracking)
        
        # Test with custom base URL
        client2 = get_djt_client(base_url="http://custom-djt-api")
        assert isinstance(client2, DistributedJobTracking)
        assert client2.base_url == "http://custom-djt-api"
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'gcp')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    @patch('adapters.djt_client.get_oidc_headers')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_pipeline_status_update_success(self, mock_client, mock_auth_headers):
        """Test successful pipeline status update."""
        # Mock the authentication headers
        mock_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_auth_headers.return_value = mock_headers
        
        # Mock the httpx response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "pipeline": {
                "id": "test-pipeline-id",
                "status": "COMPLETED",
                "page_number": 1,
                "metadata": {"test": "data"},
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-doc",
                "pages": 5
            },
            "message": "Pipeline status updated successfully"
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        pipeline_data = PipelineStatusUpdate(
            id="test-pipeline-id",
            status=PipelineStatus.COMPLETED,
            page_number=1,
            metadata={"test": "data"},
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            pages=5
        )
        
        result = await djt_client.pipeline_status_update("test-job-id", "test-pipeline-id", pipeline_data)
        
        # Assertions
        assert result["pipeline"]["id"] == "test-pipeline-id"
        assert result["pipeline"]["status"] == "COMPLETED"
        assert result["message"] == "Pipeline status updated successfully"
        
        # Verify the correct URL and headers were used
        expected_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_client_instance.post.assert_called_once_with(
            "http://test-djt-api/api/v1/jobs/test-job-id/pipelines/test-pipeline-id/status",
            headers=expected_headers,
            json=pipeline_data.model_dump()
        )
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'local')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://localhost:8001')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_pipeline_status_update_no_auth(self, mock_client):
        """Test pipeline status update without authentication (local)."""
        # Mock the httpx response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "pipeline": {
                "id": "test-pipeline-id",
                "status": "IN_PROGRESS"
            },
            "message": "Pipeline status updated successfully"
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        pipeline_data = PipelineStatusUpdate(
            status=PipelineStatus.IN_PROGRESS,
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            pages=1
        )
        
        result = await djt_client.pipeline_status_update("test-job-id", "test-pipeline-id", pipeline_data)
        
        # Assertions
        assert result["pipeline"]["status"] == "IN_PROGRESS"
        
        # Verify no Authorization header is included for local environment
        expected_headers = {
            "Content-Type": "application/json"
        }
        mock_client_instance.post.assert_called_once_with(
            "http://localhost:8001/api/v1/jobs/test-job-id/pipelines/test-pipeline-id/status",
            headers=expected_headers,
            json=pipeline_data.model_dump()
        )
    
    @patch('adapters.djt_client.settings.CLOUD_PROVIDER', 'gcp')
    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    @patch('adapters.djt_client.get_oidc_headers')
    @patch('adapters.djt_client.httpx.AsyncClient')
    async def test_pipeline_status_update_error(self, mock_client, mock_auth_headers):
        """Test pipeline status update when an error occurs."""
        # Mock the authentication headers
        mock_headers = {
            "Authorization": "Bearer mock-auth-token",
            "Content-Type": "application/json"
        }
        mock_auth_headers.return_value = mock_headers
        
        # Mock the httpx response for error
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid pipeline data"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create DJT client and call method
        djt_client = DistributedJobTracking()
        pipeline_data = PipelineStatusUpdate(
            status=PipelineStatus.FAILED,
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            pages=1
        )
        
        with pytest.raises(Exception) as exc_info:
            await djt_client.pipeline_status_update("test-job-id", "test-pipeline-id", pipeline_data)
        
        # Verify the exception has the correct status code
        assert hasattr(exc_info.value, 'status_code')
        assert exc_info.value.status_code == 400
        assert "DJT API returned status 400" in str(exc_info.value)

    @patch('adapters.djt_client.settings.DJT_API_URL', 'http://test-djt-api')
    def test_djt_client_initialization(self):
        """Test DJT client initialization."""
        # Test with default settings
        client = DistributedJobTracking()
        assert client.base_url == "http://test-djt-api"
        
        # Test with custom base URL
        client_custom = DistributedJobTracking(base_url="http://custom-url")
        assert client_custom.base_url == "http://custom-url"
