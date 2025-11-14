import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import tasks_v2
from google.protobuf import json_format

# Import and setup test environment first
from tests.test_env import setup_test_env
setup_test_env()

# Now import modules that depend on environment variables
from src.adapters.cloudtask import CloudTaskAdapter, create_cloud_task_queue, ensure_cloud_task_queue_exists

# Mock response for common queue operations
def create_mock_queue(name="test-queue", state="RUNNING"):
    """Create a mock queue response with corresponding dict representation."""
    full_name = f"projects/test-project/locations/test-location/queues/{name}"
    
    # Create a mock state object
    mock_state = MagicMock()
    mock_state.name = state

    # Create a protobuf message mock that matches the actual structure
    mock_pb = MagicMock()
    mock_pb.name = full_name
    mock_pb.state = mock_state

    # Configure the mock queue
    mock_queue = MagicMock()
    mock_queue.name = full_name
    mock_queue.state = mock_state

    # Return the mock queue object
    return mock_queue

def create_mock_queue_dict(name="test-queue", state="RUNNING"):
    """Create the expected dictionary format for queue responses."""
    full_name = f"projects/test-project/locations/test-location/queues/{name}"
    return {
        "name": full_name,
        "state": state
    }

@pytest.fixture
def mock_tasks_client():
    """Fixture to provide a mock Cloud Tasks client."""
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        
        # Set up default successful responses
        mock_queue = create_mock_queue()
        mock_paused_queue = create_mock_queue(state="PAUSED")
        
        client_instance.create_queue = Mock(return_value=mock_queue)
        client_instance.get_queue = Mock(return_value=mock_queue)
        client_instance.list_queues = Mock(return_value=[mock_queue])
        client_instance.update_queue = Mock(return_value=mock_queue)
        client_instance.delete_queue = Mock(return_value=None)
        client_instance.pause_queue = Mock(return_value=mock_paused_queue)
        client_instance.resume_queue = Mock(return_value=mock_queue)
        yield client_instance

@pytest.fixture
def cloud_task_adapter(mock_tasks_client):
    """Fixture to provide a CloudTaskAdapter instance with mocked client."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    adapter._client = mock_tasks_client
    return adapter

def test_init_with_custom_values():
    """Test CloudTaskAdapter initialization with custom values."""
    adapter = CloudTaskAdapter(project_id="custom-project", location="custom-location")
    assert adapter.project_id == "custom-project"
    assert adapter.location == "custom-location"
    assert adapter._client is None

def test_init_with_default_values():
    """Test CloudTaskAdapter initialization with default values."""
    with patch('src.adapters.cloudtask.settings') as mock_settings:
        mock_settings.GCP_PROJECT_ID = "default-project"
        mock_settings.GCP_LOCATION_2 = "default-location"
        
        adapter = CloudTaskAdapter()
        assert adapter.project_id == "default-project"
        assert adapter.location == "default-location"
        assert adapter._client is None

def test_get_client(mock_tasks_client):
    """Test client initialization."""
    adapter = CloudTaskAdapter()
    client = adapter._get_client()
    assert client is not None
    assert isinstance(client, Mock)  # In our test case, it's a Mock
    
    # Test caching behavior
    assert adapter._get_client() is client  # Should return the same instance

@pytest.mark.asyncio
async def test_ensure_cloud_task_queue_exists_existing_queue(mock_tasks_client):
    """Test ensure_cloud_task_queue_exists when queue already exists."""
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    
    mock_response = create_mock_queue("test-queue")
    
    # Mock get_queue to return existing queue
    mock_tasks_client.get_queue.return_value = mock_response
    
    # Mock create_queue to ensure it's not called
    mock_tasks_client.create_queue.side_effect = Exception("Should not be called")
    
    # Mock MessageToDict for this test case - patch it where it's imported
    with patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        result = await ensure_cloud_task_queue_exists(
            queue_name="test-queue",
            location="test-location",
            project_id="test-project"
        )
        
        # Verify get_queue was called with correct name
        mock_tasks_client.get_queue.assert_called_once_with(name=expected_name)
        
        # Verify create_queue was not called
        mock_tasks_client.create_queue.assert_not_called()
        
        # Verify the result matches expected format
        assert result == dict_result

@pytest.mark.asyncio
async def test_ensure_cloud_task_queue_exists_new_queue(mock_tasks_client):
    """Test ensure_cloud_task_queue_exists when queue needs to be created."""
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    
    mock_response = create_mock_queue("test-queue")
    mock_tasks_client.get_queue.side_effect = Exception("Queue not found")
    mock_tasks_client.create_queue.return_value = mock_response
    
    with patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        result = await ensure_cloud_task_queue_exists(
            queue_name="test-queue",
            location="test-location",
            project_id="test-project",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0
        )
        
        # Verify get_queue was called first
        mock_tasks_client.get_queue.assert_called_once_with(name=expected_name)
        
        # Verify create_queue was called with correct parameters
        mock_tasks_client.create_queue.assert_called_once()
        call_args = mock_tasks_client.create_queue.call_args[1]
        assert call_args['parent'] == "projects/test-project/locations/test-location"
        queue_config = call_args['queue']
        assert queue_config['name'] == expected_name
        assert queue_config['rate_limits']['max_concurrent_dispatches'] == 10
        assert queue_config['rate_limits']['max_dispatches_per_second'] == 5.0
        
        # Verify result matches expected format
        assert result == dict_result

@pytest.mark.asyncio
async def test_ensure_cloud_task_queue_exists_error(mock_tasks_client):
    """Test ensure_cloud_task_queue_exists error handling."""
    # Setup
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    adapter._client = mock_tasks_client
    
    # Simulate an error during get_queue
    error_msg = "Internal server error"
    mock_tasks_client.get_queue.side_effect = Exception(error_msg)
    
    # Verify error is propagated
    with pytest.raises(Exception) as exc_info:
        await ensure_cloud_task_queue_exists(
            queue_name="test-queue",
            location="test-location",
            project_id="test-project"
        )
    
    assert error_msg in str(exc_info.value)
    mock_tasks_client.create_queue.assert_not_called()

@pytest.mark.asyncio
async def test_create_cloud_task_queue_success():
    """Test standalone create_cloud_task_queue function with successful creation."""
    mock_response = create_mock_queue("test-queue")
    
    with patch('src.adapters.cloudtask.CloudTaskAdapter', autospec=True) as mock_adapter_class:
        mock_adapter = mock_adapter_class.return_value
        mock_adapter.create_queue.return_value = {
            "name": "projects/test-project/locations/test-location/queues/test-queue",
            "state": "RUNNING"
        }
        
        result = await create_cloud_task_queue(
            queue_name="test-queue",
            location="test-location",
            project_id="test-project",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0,
            max_retry_duration_seconds=300,
            min_backoff_seconds=10,
            max_backoff_seconds=60,
            max_attempts=5
        )
        
        # Verify adapter creation and configuration
        mock_adapter_class.assert_called_once_with(
            project_id="test-project",
            location="test-location"
        )
        
        # Verify queue creation parameters
        mock_adapter.create_queue.assert_called_once_with(
            queue_name="test-queue",
            location="test-location",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0,
            max_retry_duration_seconds=300,
            min_backoff_seconds=10,
            max_backoff_seconds=60,
            max_attempts=5
        )
        
        # Verify cleanup
        mock_adapter.close.assert_called_once()
        
        # Verify result matches expected format
        assert result == {
            "name": "projects/test-project/locations/test-location/queues/test-queue",
            "state": "RUNNING"
        }

@pytest.mark.asyncio
async def test_create_cloud_task_queue_error():
    """Test standalone create_cloud_task_queue function error handling."""
    error_message = "Test error"
    
    with patch('src.adapters.cloudtask.CloudTaskAdapter', autospec=True) as mock_adapter_class:
        mock_adapter = mock_adapter_class.return_value
        mock_adapter.create_queue.side_effect = Exception(error_message)
        
        # Verify error is propagated correctly
        with pytest.raises(Exception, match=error_message):
            await create_cloud_task_queue(
                queue_name="test-queue",
                location="test-location",
                project_id="test-project"
            )
        
        # Verify adapter was properly cleaned up despite error
        mock_adapter.close.assert_called_once()
        
        # Verify create attempt was made
        mock_adapter.create_queue.assert_called_once_with(
            queue_name="test-queue",
            location="test-location",
            max_concurrent_dispatches=None,
            max_dispatches_per_second=None,
            max_retry_duration_seconds=None,
            min_backoff_seconds=None,
            max_backoff_seconds=None,
            max_attempts=None
        )

def test_close_with_active_client():
    """Test closing adapter with an active client."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    mock_client = Mock()
    mock_client.transport = Mock()
    adapter._client = mock_client
    
    adapter.close()
    
    # Verify transport was closed
    mock_client.transport.close.assert_called_once()
    # Verify client was cleared
    assert adapter._client is None

def test_close_without_client():
    """Test closing adapter when no client exists."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    adapter._client = None
    
    # Should not raise any errors
    adapter.close()
    assert adapter._client is None

@pytest.mark.asyncio
async def test_create_queue_if_not_exists_new():
    """Test create_queue_if_not_exists when queue doesn't exist."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = create_mock_queue_dict("test-queue")
    new_queue = create_mock_queue("test-queue")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        # First get_queue fails (not found), then create_queue succeeds
        client_instance.get_queue.side_effect = Exception("Queue not found")
        client_instance.create_queue.return_value = new_queue
        
        response = await adapter.create_queue_if_not_exists(
            "test-queue",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0,
            max_retry_duration_seconds=30,
            min_backoff_seconds=10,
            max_backoff_seconds=60,
            max_attempts=5
        )
        
        # Verify get_queue was called first
        client_instance.get_queue.assert_called_once_with(name=expected_name)
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify create_queue was called with correct parameters
        expected_parent = "projects/test-project/locations/test-location"
        client_instance.create_queue.assert_called_once()
        call_args = client_instance.create_queue.call_args[1]
        assert call_args['parent'] == expected_parent
        queue_config = call_args['queue']
        assert queue_config['name'] == expected_name
        assert queue_config['rate_limits']['max_concurrent_dispatches'] == 10
        assert queue_config['rate_limits']['max_dispatches_per_second'] == 5.0
        assert 'retry_config' in queue_config

@pytest.mark.asyncio
async def test_create_queue_if_not_exists_existing():
    """Test create_queue_if_not_exists when queue already exists."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    queue_name = "test-queue"
    expected_name = f"projects/test-project/locations/test-location/queues/{queue_name}"
    dict_result = create_mock_queue_dict("test-queue")
    existing_queue = create_mock_queue("test-queue")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.get_queue.return_value = existing_queue
        
        response = await adapter.create_queue_if_not_exists(
            queue_name,
            max_concurrent_dispatches=10
        )
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify only get_queue was called, not create_queue
        client_instance.get_queue.assert_called_once_with(name=expected_name)
        client_instance.create_queue.assert_not_called()

@pytest.mark.asyncio
async def test_queue_exists_true():
    """Test queue_exists when queue is found."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    mock_response = create_mock_queue("test-queue")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.get_queue.return_value = mock_response
        
        exists = await adapter.queue_exists("test-queue")
        
        assert exists is True
        expected_name = "projects/test-project/locations/test-location/queues/test-queue"
        client_instance.get_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_queue_exists_false():
    """Test queue_exists when queue is not found."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    not_found_error = Exception("Queue not found")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.get_queue.side_effect = not_found_error
        
        exists = await adapter.queue_exists("nonexistent-queue")
        
        assert exists is False
        expected_name = "projects/test-project/locations/test-location/queues/nonexistent-queue"
        client_instance.get_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_pause_queue_success():
    """Test successful queue pause operation."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "PAUSED"
    }
    
    mock_response = create_mock_queue("test-queue", state="PAUSED")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.pause_queue.return_value = mock_response
        
        response = await adapter.pause_queue("test-queue")
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify correct queue path was used
        client_instance.pause_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_pause_queue_error():
    """Test error handling during queue pause operation."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Failed to pause queue"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.pause_queue.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.pause_queue("test-queue")
        
        assert error_message in str(exc_info.value)
        assert "Error pausing Cloud Task queue" in str(exc_info.value)

@pytest.mark.asyncio
async def test_resume_queue_success():
    """Test successful queue resume operation."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    
    mock_response = create_mock_queue("test-queue", state="RUNNING")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.resume_queue.return_value = mock_response
        
        response = await adapter.resume_queue("test-queue")
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify correct queue path was used
        client_instance.resume_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_resume_queue_error():
    """Test error handling during queue resume operation."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Failed to resume queue"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.resume_queue.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.resume_queue("test-queue")
        
        assert error_message in str(exc_info.value)
        assert "Error resuming Cloud Task queue" in str(exc_info.value)

@pytest.mark.asyncio
async def test_delete_queue_success():
    """Test successful queue deletion."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.delete_queue.return_value = None  # Delete returns None
        
        result = await adapter.delete_queue("test-queue")
        
        # Verify successful deletion
        assert result is True
        
        # Verify correct queue path was used
        expected_name = "projects/test-project/locations/test-location/queues/test-queue"
        client_instance.delete_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_delete_queue_not_found():
    """Test deletion of non-existent queue."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    not_found_error = Exception("Queue not found")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.delete_queue.side_effect = not_found_error
        
        result = await adapter.delete_queue("nonexistent-queue")
        
        # Should return False when queue is not found
        assert result is False
        
        # Verify the correct queue path was used
        expected_name = "projects/test-project/locations/test-location/queues/nonexistent-queue"
        client_instance.delete_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_delete_queue_error():
    """Test error handling during queue deletion."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Internal server error"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.delete_queue.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.delete_queue("test-queue")
        
        assert error_message in str(exc_info.value)
        assert "Error deleting Cloud Task queue" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_queue_basic():
    """Test basic queue update operation."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    mock_queue = create_mock_queue("test-queue")

    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.get_queue.return_value = mock_queue
        client_instance.update_queue.return_value = mock_queue

        response = await adapter.update_queue("test-queue")

        # Verify response matches expected format
        assert response == dict_result
        
        # Verify correct queue path was used
        client_instance.get_queue.assert_called_once_with(name=expected_name)
        client_instance.update_queue.assert_called_once()

@pytest.mark.asyncio
async def test_update_queue_with_rate_limits():
    """Test queue update with rate limiting configuration."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING",
        "rate_limits": {
            "max_concurrent_dispatches": 10,
            "max_dispatches_per_second": 5.0
        }
    }
    mock_queue = create_mock_queue("test-queue")
    mock_queue.rate_limits = Mock()
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.get_queue.return_value = mock_queue
        client_instance.update_queue.return_value = mock_queue
        
        response = await adapter.update_queue(
            "test-queue",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0
        )
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify rate limits were set
        update_call = client_instance.update_queue.call_args[1]
        updated_queue = update_call['queue']
        assert updated_queue.rate_limits.max_concurrent_dispatches == 10
        assert updated_queue.rate_limits.max_dispatches_per_second == 5.0

@pytest.mark.asyncio
async def test_update_queue_with_retry_config():
    """Test queue update with retry configuration."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING",
        "retry_config": {
            "max_attempts": 5,
            "max_retry_duration": "30s",
            "min_backoff": "10s",
            "max_backoff": "60s"
        }
    }
    mock_queue = create_mock_queue("test-queue")
    mock_queue.retry_config = Mock()
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.get_queue.return_value = mock_queue
        client_instance.update_queue.return_value = mock_queue
        
        response = await adapter.update_queue(
            "test-queue",
            max_attempts=5,
            max_retry_duration_seconds=30,
            min_backoff_seconds=10,
            max_backoff_seconds=60
        )
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify retry config was set
        update_call = client_instance.update_queue.call_args[1]
        updated_queue = update_call['queue']
        assert updated_queue.retry_config.max_attempts == 5
        assert 'max_retry_duration' in str(updated_queue.retry_config.__dict__)
        assert 'min_backoff' in str(updated_queue.retry_config.__dict__)
        assert 'max_backoff' in str(updated_queue.retry_config.__dict__)

@pytest.mark.asyncio
async def test_update_queue_error():
    """Test error handling during queue update."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Failed to update queue"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.get_queue.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.update_queue("test-queue")
        
        assert error_message in str(exc_info.value)
        assert "Error updating Cloud Task queue" in str(exc_info.value)

@pytest.mark.asyncio
async def test_list_queues_success():
    """Test successful listing of queues."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name1 = "projects/test-project/locations/test-location/queues/queue-1"
    expected_name2 = "projects/test-project/locations/test-location/queues/queue-2"
    mock_queues = [
        create_mock_queue("queue-1"),
        create_mock_queue("queue-2")
    ]
    expected_responses = [
        {"name": expected_name1, "state": "RUNNING"},
        {"name": expected_name2, "state": "RUNNING"}
    ]

    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict') as mock_to_dict:
        client_instance = mock_client.return_value
        client_instance.list_queues.return_value = mock_queues
        
        # Configure MessageToDict to return appropriate results for each queue
        mock_to_dict.side_effect = [
            {"name": expected_name1, "state": "RUNNING"},
            {"name": expected_name2, "state": "RUNNING"}
        ]

        response = await adapter.list_queues(page_size=10)

        # Verify response matches mock
        assert len(response) == 2
        assert response == expected_responses
        assert response[1] == {"name": expected_name2, "state": "RUNNING"}
        
        # Verify correct request parameters
        expected_parent = "projects/test-project/locations/test-location"
        client_instance.list_queues.assert_called_once()
        request = client_instance.list_queues.call_args[1]['request']
        assert request.parent == expected_parent
        assert request.page_size == 10

@pytest.mark.asyncio
async def test_list_queues_empty():
    """Test listing queues when no queues exist."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.list_queues.return_value = []
        
        response = await adapter.list_queues()
        
        assert response == []
        client_instance.list_queues.assert_called_once()

@pytest.mark.asyncio
async def test_list_queues_error():
    """Test error handling during queue listing."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Failed to list queues"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.list_queues.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.list_queues()
        
        assert error_message in str(exc_info.value)
        assert "Error listing queues" in str(exc_info.value)
        assert "test-location" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_queue_success():
    """Test successful queue retrieval."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_name = "projects/test-project/locations/test-location/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    mock_response = create_mock_queue("test-queue")

    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.get_queue.return_value = mock_response

        response = await adapter.get_queue("test-queue")

        # Verify correct queue path was used
        expected_name = "projects/test-project/locations/test-location/queues/test-queue"

        # Verify response matches expected format
        assert response == dict_result
        client_instance.get_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_get_queue_not_found():
    """Test queue retrieval when queue doesn't exist."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    not_found_error = Exception("Queue not found")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.get_queue.side_effect = not_found_error
        
        response = await adapter.get_queue("nonexistent-queue")
        
        # Should return None when queue is not found
        assert response is None
        
        # Verify the correct queue path was used
        expected_name = "projects/test-project/locations/test-location/queues/nonexistent-queue"
        client_instance.get_queue.assert_called_once_with(name=expected_name)

@pytest.mark.asyncio
async def test_get_queue_error():
    """Test error handling during queue retrieval."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Internal server error"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.get_queue.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.get_queue("test-queue")
        
        assert error_message in str(exc_info.value)
        assert "Error getting queue" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_queue_basic():
    """Test basic queue creation without optional parameters."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_parent = "projects/test-project/locations/test-location"
    expected_name = f"{expected_parent}/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    mock_response = create_mock_queue("test-queue")

    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.create_queue.return_value = mock_response

        response = await adapter.create_queue("test-queue")

        # Verify the correct parameters were used
        expected_parent = "projects/test-project/locations/test-location"
        expected_name = f"{expected_parent}/queues/test-queue"

        # Verify response matches expected format
        assert response == dict_result
        expected_queue = {
            "name": f"{expected_parent}/queues/test-queue"
        }
        client_instance.create_queue.assert_called_once_with(
            parent=expected_parent,
            queue=expected_queue
        )

@pytest.mark.asyncio
async def test_create_queue_with_rate_limits():
    """Test queue creation with rate limiting configuration."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_parent = "projects/test-project/locations/test-location"
    expected_name = f"{expected_parent}/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    mock_response = create_mock_queue("test-queue")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.create_queue.return_value = mock_response
        
        response = await adapter.create_queue(
            "test-queue",
            max_concurrent_dispatches=10,
            max_dispatches_per_second=5.0
        )
        
        # Verify response matches expected format
        assert response == dict_result
        expected_queue = {
            "name": f"{expected_parent}/queues/test-queue",
            "rate_limits": {
                "max_concurrent_dispatches": 10,
                "max_dispatches_per_second": 5.0
            }
        }
        client_instance.create_queue.assert_called_once_with(
            parent=expected_parent,
            queue=expected_queue
        )

@pytest.mark.asyncio
async def test_create_queue_with_retry_config():
    """Test queue creation with retry configuration."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    expected_parent = "projects/test-project/locations/test-location"
    expected_name = f"{expected_parent}/queues/test-queue"
    dict_result = {
        "name": expected_name,
        "state": "RUNNING"
    }
    mock_response = create_mock_queue("test-queue")
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client, \
         patch('src.adapters.cloudtask.MessageToDict', return_value=dict_result):
        client_instance = mock_client.return_value
        client_instance.create_queue.return_value = mock_response
        
        response = await adapter.create_queue(
            "test-queue",
            max_attempts=5,
            max_retry_duration_seconds=30,
            min_backoff_seconds=10,
            max_backoff_seconds=60
        )
        
        # Verify response matches expected format
        assert response == dict_result
        
        # Verify the retry config was set correctly
        client_instance.create_queue.assert_called_once()
        call_args = client_instance.create_queue.call_args[1]
        queue_config = call_args['queue']
        
        assert 'retry_config' in queue_config
        retry_config = queue_config['retry_config']
        assert retry_config['max_attempts'] == 5
        assert 'max_retry_duration' in retry_config
        assert 'min_backoff' in retry_config
        assert 'max_backoff' in retry_config

@pytest.mark.asyncio
async def test_create_queue_error_handling():
    """Test error handling during queue creation."""
    adapter = CloudTaskAdapter(project_id="test-project", location="test-location")
    error_message = "Queue creation failed"
    
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.create_queue.side_effect = Exception(error_message)
        
        with pytest.raises(Exception) as exc_info:
            await adapter.create_queue("test-queue")
        
        assert error_message in str(exc_info.value)
        assert "Error creating Cloud Task queue" in str(exc_info.value)
        
        assert error_message in str(exc_info.value)