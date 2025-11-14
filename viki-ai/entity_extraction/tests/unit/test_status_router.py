"""
Unit tests for routers.status module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException

from src.routers.status import get_job_status


class TestStatusRouter:
    """Test cases for status router endpoints."""

    @pytest.mark.asyncio
    async def test_get_job_status_success(self):
        """Test successful job status retrieval."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"User-Agent": "TestClient/1.0"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Mock DJT response
        mock_djt_response = {
            "status": "COMPLETED",
            "pipelines": [
                {"id": "pipeline1", "status": "SUCCESS"},
                {"id": "pipeline2", "status": "SUCCESS"}
            ]
        }
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.return_value = mock_djt_response
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint
            result = await get_job_status("test-run-id", mock_request)
            
            # Verify the result
            assert result == mock_djt_response
            mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")

    @pytest.mark.asyncio
    async def test_get_job_status_djt_api_error(self):
        """Test handling of DJT API errors with status codes."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"User-Agent": "TestClient/1.0"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Create a mock exception with status_code
        mock_error = Exception("Not found")
        mock_error.status_code = 404
        mock_error.response_text = "Job not found in DJT service"
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.side_effect = mock_error
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_job_status("test-run-id", mock_request)
            
            # Verify the exception
            assert exc_info.value.status_code == 404
            assert "Error from distributed job tracking service: Job not found in DJT service" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_job_status_djt_api_error_without_response_text(self):
        """Test handling of DJT API errors without response_text."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"User-Agent": "TestClient/1.0"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Create a mock exception with status_code but no response_text
        mock_error = Exception("Service unavailable")
        mock_error.status_code = 503
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.side_effect = mock_error
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_job_status("test-run-id", mock_request)
            
            # Verify the exception
            assert exc_info.value.status_code == 503
            assert "Error from distributed job tracking service: Service unavailable" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_job_status_network_error(self):
        """Test handling of network/connection errors."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"User-Agent": "TestClient/1.0"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Create a network error
        network_error = Exception("Unable to connect to DJT service")
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.side_effect = network_error
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_job_status("test-run-id", mock_request)
            
            # Verify the exception
            assert exc_info.value.status_code == 503
            assert "Unable to connect to DJT service" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_job_status_unexpected_error(self):
        """Test handling of unexpected errors."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"User-Agent": "TestClient/1.0"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Create an unexpected error
        unexpected_error = ValueError("Unexpected validation error")
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.side_effect = unexpected_error
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_job_status("test-run-id", mock_request)
            
            # Verify the exception
            assert exc_info.value.status_code == 500
            assert "Error retrieving job status: Unexpected validation error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_job_status_logging(self):
        """Test that proper logging occurs during job status retrieval."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"X-Request-ID": "test-123"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Mock DJT response
        mock_djt_response = {"status": "IN_PROGRESS", "pipelines": []}
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            with patch('src.routers.status.LOGGER') as mock_logger:
                mock_djt_client = AsyncMock()
                mock_djt_client.get_job_pipelines.return_value = mock_djt_response
                mock_get_djt_client.return_value = mock_djt_client
                
                # Call the endpoint
                result = await get_job_status("test-run-id", mock_request)
                
                # Verify logging was called
                assert mock_logger.info.called
                assert mock_logger.debug.called
                
                # Verify result
                assert result == mock_djt_response

    @pytest.mark.asyncio
    async def test_get_job_status_with_empty_headers(self):
        """Test job status retrieval with empty headers."""
        # Mock request with empty headers
        mock_request = Mock()
        mock_request.headers = {}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": False,
            "bypass_reason": "local_development"
        }
        
        # Mock DJT response
        mock_djt_response = {"status": "FAILED", "error": "Pipeline failed"}
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.return_value = mock_djt_response
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint
            result = await get_job_status("test-run-id", mock_request)
            
            # Verify the result
            assert result == mock_djt_response
            mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")

    @pytest.mark.asyncio
    async def test_get_job_status_special_characters_in_run_id(self):
        """Test job status retrieval with special characters in run_id."""
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "service_account": "test@example.com"
        }
        
        # Use run_id with special characters
        special_run_id = "test-run_id.123@domain"
        
        # Mock DJT response
        mock_djt_response = {"status": "QUEUED", "pipelines": []}
        
        # Mock DJT client
        with patch('src.routers.status.get_djt_client') as mock_get_djt_client:
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.return_value = mock_djt_response
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint
            result = await get_job_status(special_run_id, mock_request)
            
            # Verify the result
            assert result == mock_djt_response
            mock_djt_client.get_job_pipelines.assert_called_once_with(special_run_id)