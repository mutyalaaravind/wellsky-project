"""
Unit tests for routers.admin module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.routers.admin import (
    router,
    CreateCloudTaskQueueRequest, 
    CreateCloudTaskQueueResponse,
    create_cloudtask_queue,
    get_cloudtask_queue,
    list_cloudtask_queues,
    delete_cloudtask_queue
)


class TestCreateCloudTaskQueueRequest:
    """Test cases for CreateCloudTaskQueueRequest model."""

    def test_create_with_required_fields_only(self):
        """Test creating request with only required fields."""
        request = CreateCloudTaskQueueRequest(queue_name="test-queue")
        assert request.queue_name == "test-queue"
        assert request.location is None
        assert request.max_concurrent_dispatches is None

    def test_create_with_all_fields(self):
        """Test creating request with all fields."""
        request = CreateCloudTaskQueueRequest(
            queue_name="test-queue",
            location="us-central1",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0,
            max_retry_duration_seconds=3600,
            min_backoff_seconds=1,
            max_backoff_seconds=60,
            max_attempts=3
        )
        assert request.queue_name == "test-queue"
        assert request.location == "us-central1"
        assert request.max_concurrent_dispatches == 10
        assert request.max_dispatches_per_second == 5.0
        assert request.max_retry_duration_seconds == 3600
        assert request.min_backoff_seconds == 1
        assert request.max_backoff_seconds == 60
        assert request.max_attempts == 3


class TestCreateCloudTaskQueueResponse:
    """Test cases for CreateCloudTaskQueueResponse model."""

    def test_create_response_model(self):
        """Test creating response model."""
        queue_info = {"name": "test-queue", "state": "RUNNING"}
        response = CreateCloudTaskQueueResponse(
            success=True,
            queue_name="test-queue",
            queue_info=queue_info,
            message="Queue created successfully"
        )
        assert response.success is True
        assert response.queue_name == "test-queue"
        assert response.queue_info == queue_info
        assert response.message == "Queue created successfully"


class TestCreateCloudTaskQueue:
    """Test cases for create_cloudtask_queue endpoint."""

    @pytest.mark.asyncio
    async def test_create_queue_success(self):
        """Test successful queue creation."""
        # Mock request
        request = CreateCloudTaskQueueRequest(queue_name="test-queue")
        mock_http_request = Mock()
        mock_http_request.headers = {"Content-Type": "application/json"}

        # Mock queue info response
        mock_queue_info = {
            "name": "projects/test-project/locations/us-central1/queues/test-queue",
            "state": "RUNNING"
        }

        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.return_value = mock_queue_info
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint
            result = await create_cloudtask_queue(request, mock_http_request)

            # Verify the result
            assert isinstance(result, CreateCloudTaskQueueResponse)
            assert result.success is True
            assert result.queue_name == "test-queue"
            assert result.queue_info == mock_queue_info
            assert "Successfully created" in result.message

            # Verify adapter was called correctly
            mock_adapter.create_queue.assert_called_once_with(
                queue_name="test-queue",
                location=None,
                max_concurrent_dispatches=None,
                max_dispatches_per_second=None,
                max_retry_duration_seconds=None,
                min_backoff_seconds=None,
                max_backoff_seconds=None,
                max_attempts=None
            )
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_queue_with_all_parameters(self):
        """Test queue creation with all parameters."""
        # Mock request with all parameters
        request = CreateCloudTaskQueueRequest(
            queue_name="test-queue",
            location="us-central1",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0,
            max_retry_duration_seconds=3600,
            min_backoff_seconds=1,
            max_backoff_seconds=60,
            max_attempts=3
        )
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.return_value = {"name": "test-queue", "state": "RUNNING"}
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint
            result = await create_cloudtask_queue(request, mock_http_request)

            # Verify adapter was called with all parameters
            mock_adapter.create_queue.assert_called_once_with(
                queue_name="test-queue",
                location="us-central1",
                max_concurrent_dispatches=10,
                max_dispatches_per_second=5.0,
                max_retry_duration_seconds=3600,
                min_backoff_seconds=1,
                max_backoff_seconds=60,
                max_attempts=3
            )

    @pytest.mark.asyncio
    async def test_create_queue_already_exists_error(self):
        """Test handling when queue already exists."""
        request = CreateCloudTaskQueueRequest(queue_name="existing-queue")
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise already exists error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.side_effect = Exception("Queue already exists")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await create_cloudtask_queue(request, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 409
            assert "already exists" in exc_info.value.detail
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_queue_permission_error(self):
        """Test handling permission errors."""
        request = CreateCloudTaskQueueRequest(queue_name="test-queue")
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise permission error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.side_effect = Exception("Permission denied")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await create_cloudtask_queue(request, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 403
            assert "Permission denied" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_queue_not_found_error(self):
        """Test handling not found errors."""
        request = CreateCloudTaskQueueRequest(queue_name="test-queue")
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise not found error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.side_effect = Exception("Project not found")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await create_cloudtask_queue(request, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_queue_invalid_request_error(self):
        """Test handling invalid request errors."""
        request = CreateCloudTaskQueueRequest(queue_name="test-queue")
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise invalid error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.side_effect = Exception("Invalid queue name")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await create_cloudtask_queue(request, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 400
            assert "Invalid request" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_queue_generic_error(self):
        """Test handling generic errors."""
        request = CreateCloudTaskQueueRequest(queue_name="test-queue")
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise generic error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.create_queue.side_effect = Exception("Some unexpected error")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await create_cloudtask_queue(request, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 500
            assert "Error creating Cloud Task queue" in exc_info.value.detail


class TestGetCloudTaskQueue:
    """Test cases for get_cloudtask_queue endpoint."""

    @pytest.mark.asyncio
    async def test_get_queue_success(self):
        """Test successful queue retrieval."""
        mock_http_request = Mock()
        mock_http_request.headers = {"Authorization": "Bearer token"}

        # Mock queue info response
        mock_queue_info = {
            "name": "projects/test-project/locations/us-central1/queues/test-queue",
            "state": "RUNNING"
        }

        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.get_queue.return_value = mock_queue_info
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint
            result = await get_cloudtask_queue("test-queue", "us-central1", mock_http_request)

            # Verify the result
            assert result["success"] is True
            assert result["queue_name"] == "test-queue"
            assert result["queue_info"] == mock_queue_info

            # Verify adapter was called correctly
            mock_adapter.get_queue.assert_called_once_with(
                queue_name="test-queue",
                location="us-central1"
            )
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_queue_not_found(self):
        """Test handling when queue is not found."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to return None
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.get_queue.return_value = None
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_cloudtask_queue("nonexistent-queue", None, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_queue_without_request(self):
        """Test queue retrieval without HTTP request object."""
        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.get_queue.return_value = {"name": "test-queue", "state": "RUNNING"}
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint without HTTP request
            result = await get_cloudtask_queue("test-queue", None, None)

            # Verify the result
            assert result["success"] is True
            assert result["queue_name"] == "test-queue"

    @pytest.mark.asyncio
    async def test_get_queue_generic_error(self):
        """Test handling generic errors."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.get_queue.side_effect = Exception("Network error")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_cloudtask_queue("test-queue", None, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 500
            assert "Error retrieving Cloud Task queue" in exc_info.value.detail


class TestListCloudTaskQueues:
    """Test cases for list_cloudtask_queues endpoint."""

    @pytest.mark.asyncio
    async def test_list_queues_success(self):
        """Test successful queue listing."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock queues response
        mock_queues = [
            {"name": "queue1", "state": "RUNNING"},
            {"name": "queue2", "state": "PAUSED"}
        ]

        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.list_queues.return_value = mock_queues
            mock_adapter.location = "us-central1"
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint
            result = await list_cloudtask_queues("us-central1", 50, mock_http_request)

            # Verify the result
            assert result["success"] is True
            assert result["location"] == "us-central1"
            assert result["queue_count"] == 2
            assert result["queues"] == mock_queues

            # Verify adapter was called correctly
            mock_adapter.list_queues.assert_called_once_with(
                location="us-central1",
                page_size=50
            )
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_queues_default_location(self):
        """Test queue listing with default location."""
        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.list_queues.return_value = []
            mock_adapter.location = "us-central1"
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint without location
            result = await list_cloudtask_queues(None, 100, None)

            # Verify the result uses adapter's default location
            assert result["location"] == "us-central1"
            assert result["queue_count"] == 0

    @pytest.mark.asyncio
    async def test_list_queues_error(self):
        """Test handling errors during queue listing."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.list_queues.side_effect = Exception("API error")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await list_cloudtask_queues("us-central1", 100, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 500
            assert "Error listing Cloud Task queues" in exc_info.value.detail


class TestDeleteCloudTaskQueue:
    """Test cases for delete_cloudtask_queue endpoint."""

    @pytest.mark.asyncio
    async def test_delete_queue_success(self):
        """Test successful queue deletion."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.delete_queue.return_value = True
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint
            result = await delete_cloudtask_queue("test-queue", "us-central1", mock_http_request)

            # Verify the result
            assert result["success"] is True
            assert result["queue_name"] == "test-queue"
            assert "Successfully deleted" in result["message"]

            # Verify adapter was called correctly
            mock_adapter.delete_queue.assert_called_once_with(
                queue_name="test-queue",
                location="us-central1"
            )
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_queue_not_found(self):
        """Test handling when queue to delete is not found."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to return False
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.delete_queue.return_value = False
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await delete_cloudtask_queue("nonexistent-queue", None, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail
            mock_adapter.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_queue_generic_error(self):
        """Test handling generic errors during deletion."""
        mock_http_request = Mock()
        mock_http_request.headers = {}

        # Mock CloudTaskAdapter to raise error
        with patch('src.routers.admin.CloudTaskAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.delete_queue.side_effect = Exception("Delete failed")
            mock_adapter_class.return_value = mock_adapter

            # Call the endpoint and expect HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await delete_cloudtask_queue("test-queue", None, mock_http_request)

            # Verify the exception
            assert exc_info.value.status_code == 500
            assert "Error deleting Cloud Task queue" in exc_info.value.detail


class TestAdminRouter:
    """Test cases for admin router configuration."""

    def test_router_configuration(self):
        """Test that router is properly configured."""
        assert router.prefix == "/admin"
        assert "admin" in router.tags

    def test_router_integration(self):
        """Test router integration with FastAPI."""
        app = FastAPI()
        app.include_router(router)
        
        # Verify routes are registered
        route_paths = [route.path for route in app.routes]
        assert "/admin/cloudtask" in route_paths
        assert "/admin/cloudtask/{queue_name}" in route_paths