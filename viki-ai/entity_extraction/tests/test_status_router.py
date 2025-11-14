import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app

client = TestClient(app)

class TestStatusRouter:
    
    @patch('routers.status.get_djt_client')
    async def test_get_job_status_success(self, mock_get_djt_client):
        """Test successful job status retrieval."""
        # Mock the DJT client
        mock_djt_client = AsyncMock()
        mock_djt_client.get_job_pipelines.return_value = {
            "job_id": "test-run-id",
            "status": "running",
            "pipelines": [
                {"name": "pipeline1", "status": "completed"},
                {"name": "pipeline2", "status": "running"}
            ]
        }
        mock_get_djt_client.return_value = mock_djt_client
        
        # Make the request
        response = client.get("/api/status/test-run-id")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-run-id"
        assert data["status"] == "running"
        assert len(data["pipelines"]) == 2
        
        # Verify the DJT client was called correctly
        mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")
    
    @patch('routers.status.get_djt_client')
    async def test_get_job_status_not_found(self, mock_get_djt_client):
        """Test job status retrieval when job is not found."""
        # Mock the DJT client to raise an exception with status_code
        mock_djt_client = AsyncMock()
        error = Exception("Job not found")
        error.status_code = 404
        error.response_text = "Job not found"
        mock_djt_client.get_job_pipelines.side_effect = error
        mock_get_djt_client.return_value = mock_djt_client
        
        # Make the request
        response = client.get("/api/status/nonexistent-run-id")
        
        # Assertions
        assert response.status_code == 404
        assert "Error from distributed job tracking service" in response.json()["detail"]
        
        # Verify the DJT client was called correctly
        mock_djt_client.get_job_pipelines.assert_called_once_with("nonexistent-run-id")
    
    @patch('routers.status.get_djt_client')
    async def test_get_job_status_network_error(self, mock_get_djt_client):
        """Test job status retrieval when network error occurs."""
        # Mock the DJT client to raise a network error
        mock_djt_client = AsyncMock()
        mock_djt_client.get_job_pipelines.side_effect = Exception("Unable to connect to distributed job tracking service: Connection failed")
        mock_get_djt_client.return_value = mock_djt_client
        
        # Make the request
        response = client.get("/api/status/test-run-id")
        
        # Assertions
        assert response.status_code == 503
        assert "Unable to connect to distributed job tracking service" in response.json()["detail"]
        
        # Verify the DJT client was called correctly
        mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")
    
    @patch('routers.status.get_djt_client')
    async def test_get_job_status_generic_error(self, mock_get_djt_client):
        """Test job status retrieval when a generic error occurs."""
        # Mock the DJT client to raise a generic error
        mock_djt_client = AsyncMock()
        mock_djt_client.get_job_pipelines.side_effect = Exception("Some unexpected error")
        mock_get_djt_client.return_value = mock_djt_client
        
        # Make the request
        response = client.get("/api/status/test-run-id")
        
        # Assertions
        assert response.status_code == 500
        assert "Error retrieving job status" in response.json()["detail"]
        
        # Verify the DJT client was called correctly
        mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")
    
    @patch('routers.status.get_djt_client')
    async def test_djt_client_instantiation(self, mock_get_djt_client):
        """Test that the DJT client is properly instantiated."""
        # Mock the DJT client
        mock_djt_client = AsyncMock()
        mock_djt_client.get_job_pipelines.return_value = {"status": "success"}
        mock_get_djt_client.return_value = mock_djt_client
        
        # Make the request
        response = client.get("/api/status/test-run-id")
        
        # Verify the DJT client factory was called
        mock_get_djt_client.assert_called_once()
        assert response.status_code == 200
