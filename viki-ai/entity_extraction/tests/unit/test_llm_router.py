"""
Unit tests for src.routers.llm module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# Import test environment setup
from tests.test_env import setup_test_env
setup_test_env()

# Import the module under test
from src.routers.llm import router, execute_llm
from src.contracts.llm import LlmExecuteRequest, LlmExecuteResponse
from src.usecases.llm_executor import execute_llm_request


class TestLLMRouter:
    """Test cases for the LLM router."""

    def test_router_configuration(self):
        """Test that the router is properly configured."""
        assert router.prefix == "/v1/llm"
        assert "llm" in router.tags
        
        # Check that the execute endpoint is registered
        routes = [route.path for route in router.routes]
        assert "/v1/llm/execute" in routes

    @pytest.mark.asyncio
    async def test_execute_llm_success(self):
        """Test successful LLM execution."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json", "User-Agent": "TestClient"}
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "token_subject": "test@example.com",
            "service_account": "test-service@project.iam.gserviceaccount.com"
        }
        
        # Mock LLM request
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/test-file.pdf",
            prompt="Extract key information",
            system_instructions="You are a helpful assistant",
            json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            metadata={"task_id": "test-123"}
        )
        
        # Mock successful response
        mock_response = LlmExecuteResponse(
            success=True,
            content={"name": "John Doe"},
            raw_response="Generated content",
            execution_metadata={"model": "gemini-1.5-flash", "tokens": 150}
        )
        
        # Mock the execute_llm_request function
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            mock_execute.return_value = mock_response
            
            # Execute the endpoint
            result = await execute_llm(llm_request, mock_http_request)
            
            # Verify the result
            assert result == mock_response
            assert result.success is True
            assert result.content == {"name": "John Doe"}
            assert result.raw_response == "Generated content"
            
            # Verify the usecase was called with correct parameters
            mock_execute.assert_called_once_with(llm_request)

    @pytest.mark.asyncio
    async def test_execute_llm_failed_execution(self):
        """Test LLM execution that fails but returns a response."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {"authenticated": True, "service_account": "test@example.com"}
        
        # Mock LLM request
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/test-file.pdf",
            prompt="Extract information"
        )
        
        # Mock failed response
        mock_response = LlmExecuteResponse(
            success=False,
            error_message="Model failed to process the document",
            content=None,
            raw_response=None
        )
        
        # Mock the execute_llm_request function
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            mock_execute.return_value = mock_response
            
            # Execute the endpoint
            result = await execute_llm(llm_request, mock_http_request)
            
            # Verify the result
            assert result == mock_response
            assert result.success is False
            assert result.error_message == "Model failed to process the document"

    @pytest.mark.asyncio
    async def test_execute_llm_validation_error(self):
        """Test handling of validation errors."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {"authenticated": True}
        
        # Mock LLM request with valid GS URI
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/test-file.pdf",
            prompt="Extract information"
        )
        
        # Mock the execute_llm_request function to raise ValueError
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            mock_execute.side_effect = ValueError("Invalid GS URI format")
            
            # Execute the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await execute_llm(llm_request, mock_http_request)
            
            # Verify the exception details
            assert exc_info.value.status_code == 422
            assert "Invalid request: Invalid GS URI format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_execute_llm_unexpected_error(self):
        """Test handling of unexpected errors."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {"authenticated": True}
        
        # Mock LLM request
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/test-file.pdf",
            prompt="Extract information"
        )
        
        # Mock the execute_llm_request function to raise unexpected error
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            mock_execute.side_effect = RuntimeError("Database connection failed")
            
            # Execute the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await execute_llm(llm_request, mock_http_request)
            
            # Verify the exception details
            assert exc_info.value.status_code == 500
            assert "Internal server error: Database connection failed" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_execute_llm_logging_context(self):
        """Test that proper logging context is created."""
        # Mock request with comprehensive headers
        mock_http_request = Mock()
        mock_http_request.headers = {
            "Content-Type": "application/json",
            "User-Agent": "TestClient/1.0",
            "X-Request-ID": "req-123"
        }
        
        # Mock auth info
        mock_auth_info = {
            "authenticated": True,
            "token_subject": "test@example.com",
            "service_account": "test-service@project.iam.gserviceaccount.com"
        }
        
        # Mock LLM request with all optional fields
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/test-file.pdf",
            prompt="Extract detailed information from this document",
            system_instructions="You are an expert document analyzer",
            json_schema={"type": "object", "properties": {"summary": {"type": "string"}}},
            metadata={"task_id": "test-456", "priority": "high"}
        )
        
        # Mock successful response
        mock_response = LlmExecuteResponse(
            success=True,
            content={"summary": "Document summary"},
            raw_response="Raw model output here",
            execution_metadata={"tokens_used": 250, "model": "gemini-1.5-flash"}
        )
        
        # Mock the execute_llm_request function
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            with patch('src.routers.llm.LOGGER') as mock_logger:
                mock_execute.return_value = mock_response
                
                # Execute the endpoint
                result = await execute_llm(llm_request, mock_http_request)
                
                # Verify the result
                assert result == mock_response
                
                # Verify logging was called
                assert mock_logger.info.call_count >= 2  # Initial request log + success log
                
                # Check the logging context includes expected fields
                call_args_list = mock_logger.info.call_args_list
                
                # First call should be the request log
                first_call_args = call_args_list[0]
                assert "Received LLM execution request" in first_call_args[0][0]
                assert "extra" in first_call_args[1]
                
                extra_context = first_call_args[1]["extra"]
                assert extra_context["gs_uri"] == "gs://test-bucket/test-file.pdf"
                assert extra_context["prompt_length"] == len(llm_request.prompt)
                assert extra_context["has_system_instructions"] is True
                assert extra_context["has_json_schema"] is True
                assert extra_context["metadata"] == {"task_id": "test-456", "priority": "high"}
                
                # Last call should be the success log
                last_call_args = call_args_list[-1]
                assert "LLM execution completed successfully" in last_call_args[0][0]
                
                success_extra = last_call_args[1]["extra"]
                assert success_extra["success"] is True
                assert success_extra["has_content"] is True
                assert success_extra["raw_response_length"] == len(mock_response.raw_response)

    @pytest.mark.asyncio
    async def test_execute_llm_minimal_request(self):
        """Test execution with minimal request parameters."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {"authenticated": True}
        
        # Mock minimal LLM request (only required fields)
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/file.txt",
            prompt="Summarize this document"
        )
        
        # Mock successful response
        mock_response = LlmExecuteResponse(
            success=True,
            content={"summary": "Document summary"},
            raw_response="Summary response",
            execution_metadata={}
        )
        
        # Mock the execute_llm_request function
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            with patch('src.routers.llm.LOGGER') as mock_logger:
                mock_execute.return_value = mock_response
                
                # Execute the endpoint
                result = await execute_llm(llm_request, mock_http_request)
                
                # Verify the result
                assert result == mock_response
                
                # Verify logging context handles None values properly
                call_args = mock_logger.info.call_args_list[0]
                extra_context = call_args[1]["extra"]
                assert extra_context["has_system_instructions"] is False
                assert extra_context["has_json_schema"] is False
                assert extra_context["metadata"] == {}

    @pytest.mark.asyncio
    async def test_execute_llm_error_logging(self):
        """Test error logging for different exception types."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {"authenticated": True}
        
        # Mock LLM request
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/test.pdf",
            prompt="Test prompt"
        )
        
        # Test ValueError logging
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            with patch('src.routers.llm.LOGGER') as mock_logger:
                mock_execute.side_effect = ValueError("Invalid input parameter")
                
                with pytest.raises(HTTPException):
                    await execute_llm(llm_request, mock_http_request)
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                error_call_args = mock_logger.error.call_args
                assert "Validation error in LLM execution request" in error_call_args[0][0]
        
        # Test general Exception logging
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            with patch('src.routers.llm.LOGGER') as mock_logger:
                mock_execute.side_effect = ConnectionError("Network timeout")
                
                with pytest.raises(HTTPException):
                    await execute_llm(llm_request, mock_http_request)
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                error_call_args = mock_logger.error.call_args
                assert "Unexpected error in LLM execution" in error_call_args[0][0]

    @pytest.mark.asyncio
    async def test_execute_llm_response_with_no_content(self):
        """Test handling of response with no content."""
        # Mock request
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}
        
        # Mock auth info
        mock_auth_info = {"authenticated": True}
        
        # Mock LLM request
        llm_request = LlmExecuteRequest(
            gs_uri="gs://test-bucket/empty.pdf",
            prompt="Extract information"
        )
        
        # Mock response with no content
        mock_response = LlmExecuteResponse(
            success=True,
            content=None,
            raw_response=None,
            execution_metadata={"status": "no_content_extracted"}
        )
        
        # Mock the execute_llm_request function
        with patch('src.routers.llm.execute_llm_request') as mock_execute:
            with patch('src.routers.llm.LOGGER') as mock_logger:
                mock_execute.return_value = mock_response
                
                # Execute the endpoint
                result = await execute_llm(llm_request, mock_http_request)
                
                # Verify the result
                assert result == mock_response
                assert result.content is None
                assert result.raw_response is None
                
                # Verify logging handles None values
                success_call = mock_logger.info.call_args_list[-1]
                success_extra = success_call[1]["extra"]
                assert success_extra["has_content"] is False
                assert success_extra["raw_response_length"] == 0


if __name__ == '__main__':
    pytest.main([__file__])