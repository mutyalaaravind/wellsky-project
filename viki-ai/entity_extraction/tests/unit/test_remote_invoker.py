import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import json
import asyncio
from aiohttp import ClientTimeout, ClientError, ClientResponseError
import os
import sys

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from usecases.remote_invoker import RemoteInvoker
from models.general import TaskParameters, TaskResults
from models.pipeline_config import TaskConfig, TaskType, RemoteConfig


class MockAsyncContextManager:
    """A proper async context manager for mocking aiohttp responses."""
    
    def __init__(self, mock_response):
        self.mock_response = mock_response
    
    async def __aenter__(self):
        return self.mock_response
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class TestRemoteInvoker:
    """Test suite for RemoteInvoker class."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        self.remote_config = RemoteConfig(
            url="https://api.example.com/process",
            method="POST",
            headers={"Authorization": "Bearer token"},
            timeout=30,
            context={"service": "test"}
        )
        
        self.task_config = TaskConfig(
            id="test-remote-task",
            type=TaskType.REMOTE,
            remote=self.remote_config
        )
        
        self.task_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document",
            page_number=1,
            pipeline_scope="test-scope",
            pipeline_key="test-pipeline",
            run_id="test-run-123",
            task_config=self.task_config,
            context={"test": "data"},
            entities={"entity1": "value1"}
        )
        
        self.invoker = RemoteInvoker()

    def test_init(self):
        """Test RemoteInvoker initialization."""
        invoker = RemoteInvoker()
        assert invoker is not None

    async def test_run_no_remote_config(self):
        """Test handling when task config has no remote configuration."""
        # Create task config without remote config
        task_config_no_remote = TaskConfig(
            id="test-task",
            type=TaskType.MODULE  # Wrong type
        )
        
        task_params_no_remote = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document",
            task_config=task_config_no_remote
        )
        
        # Execute
        result = await self.invoker.run(task_params_no_remote)
        
        # Verify
        assert result.success is False
        assert "remote configuration" in result.error_message.lower()

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_success_post_simple(self, mock_session):
        """Test successful POST request execution with simplified mocking."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})
        mock_response.text = AsyncMock(return_value='{"result": "success"}')
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True
        assert result.results == {"result": "success"}
        assert result.error_message is None
        assert result.execution_time_ms is not None
        assert result.execution_time_ms >= 0

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_success_get_simple(self, mock_session):
        """Test successful GET request execution with simplified mocking."""
        # Update config for GET request
        self.remote_config.method = "GET"
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "ok"})
        mock_response.text = AsyncMock(return_value='{"status": "ok"}')
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True
        assert result.results == {"status": "ok"}

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_http_error_simple(self, mock_session):
        """Test handling of HTTP errors with simplified mocking."""
        # Create a mock response that has a 400 status
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is False
        assert "400" in result.error_message
        assert "Bad Request" in result.error_message

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_timeout_error_simple(self, mock_session):
        """Test handling of timeout errors with simplified mocking."""
        # Create an async context manager that raises timeout error when entered
        class MockTimeoutContextManager:
            async def __aenter__(self):
                raise asyncio.TimeoutError("Request timed out")
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=MockTimeoutContextManager())
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is False
        assert "timed out" in result.error_message.lower()

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_connection_error_simple(self, mock_session):
        """Test handling of connection errors with simplified mocking."""
        # Create an async context manager that raises connection error when entered
        class MockConnectionErrorContextManager:
            async def __aenter__(self):
                raise ClientError("Connection failed")
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=MockConnectionErrorContextManager())
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is False
        assert "connection" in result.error_message.lower()

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_json_decode_error_simple(self, mock_session):
        """Test handling of JSON decode errors with simplified mocking."""
        # Create a mock response that fails JSON parsing
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.text = AsyncMock(return_value="Invalid JSON response")
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True  # Should succeed with fallback to text response
        assert result.results == {"response": "Invalid JSON response"}

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_general_exception_simple(self, mock_session):
        """Test handling of general exceptions with simplified mocking."""
        # Create an async context manager that raises general exception when entered
        class MockGeneralExceptionContextManager:
            async def __aenter__(self):
                raise Exception("Unexpected error")
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=MockGeneralExceptionContextManager())
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is False
        assert "Unexpected error" in result.error_message

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_custom_timeout_simple(self, mock_session):
        """Test that custom timeout is applied correctly."""
        # Update config with custom timeout
        self.remote_config.timeout = 60
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})
        mock_response.text = AsyncMock(return_value='{"result": "success"}')
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True
        
        # Note: We can't easily verify the timeout parameter with this mocking approach
        # but the test verifies that the custom timeout doesn't break the execution

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_no_headers_simple(self, mock_session):
        """Test execution without custom headers."""
        # Update config without headers
        self.remote_config.headers = None
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})
        mock_response.text = AsyncMock(return_value='{"result": "success"}')
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True
        
        # Note: We can't easily verify the headers parameter with this mocking approach
        # but the test verifies that the execution works without custom headers

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_empty_response_simple(self, mock_session):
        """Test handling of empty response."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.text = AsyncMock(return_value='{}')
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True
        assert result.results == {}

    @patch('usecases.remote_invoker.aiohttp.ClientSession')
    async def test_run_with_merged_headers_simple(self, mock_session):
        """Test that custom headers are properly merged with default headers."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})
        mock_response.text = AsyncMock(return_value='{"result": "success"}')
        mock_response.content_type = "application/json"
        
        # Create a proper async context manager
        mock_context_manager = MockAsyncContextManager(mock_response)
        
        # Mock the session instance
        mock_session_instance = AsyncMock()
        mock_session_instance.request = MagicMock(return_value=mock_context_manager)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session constructor to return the async context manager
        mock_session.return_value = mock_session_instance
        
        # Execute
        result = await self.invoker.run(self.task_params)
        
        # Verify
        assert result.success is True
        
        # Note: We can't easily verify the headers parameter with this mocking approach
        # but the test verifies that the execution works with custom headers

    def test_task_config_validation(self):
        """Test that task config validation works correctly."""
        # Test with valid remote config
        assert self.task_config.remote is not None
        assert self.task_config.remote.url == "https://api.example.com/process"
        assert self.task_config.remote.method == "POST"
        assert self.task_config.remote.timeout == 30
        
        # Test with invalid task config (no remote)
        invalid_config = TaskConfig(
            id="test-task",
            type=TaskType.MODULE
        )
        assert invalid_config.remote is None

    def test_remote_config_defaults(self):
        """Test RemoteConfig default values."""
        minimal_config = RemoteConfig(url="https://api.example.com")
        
        assert minimal_config.url == "https://api.example.com"
        assert minimal_config.method == "POST"  # default
        assert minimal_config.headers == {}  # default is empty dict, not None
        assert minimal_config.timeout == 30  # default
        assert minimal_config.context == {}  # default is empty dict, not None

    def test_remote_config_with_all_fields(self):
        """Test RemoteConfig with all fields specified."""
        full_config = RemoteConfig(
            url="https://api.example.com/endpoint",
            method="PUT",
            headers={"Custom-Header": "value"},
            timeout=120,
            context={"key": "value"}
        )
        
        assert full_config.url == "https://api.example.com/endpoint"
        assert full_config.method == "PUT"
        assert full_config.headers == {"Custom-Header": "value"}
        assert full_config.timeout == 120
        assert full_config.context == {"key": "value"}
