import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid
import httpx

# Import and setup test environment first

# Now import the modules that depend on environment variables
from src.adapters.cloud_tasks import CloudTaskAdapter


@pytest.fixture
def mock_settings():
    with patch('src.adapters.cloud_tasks.settings') as mock_settings:
        mock_settings.GCP_PROJECT_ID = "test-project"
        mock_settings.CLOUD_PROVIDER = "local"
        mock_settings.CLOUDTASK_EMULATOR_URL = "http://localhost:8123"
        mock_settings.GCP_LOCATION_2 = "test-location"
        mock_settings.DEFAULT_TASK_QUEUE = "test-queue"
        mock_settings.SELF_API_URL = "http://localhost:8000"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"
        yield mock_settings

@pytest.fixture
def mock_logger():
    with patch('src.adapters.cloud_tasks.LOGGER') as mock_logger:
        yield mock_logger

@pytest.fixture
def adapter(mock_settings):
    return CloudTaskAdapter()

@pytest.mark.asyncio
async def test_init_default(mock_settings):
    adapter = CloudTaskAdapter()
    assert adapter.project_id == mock_settings.GCP_PROJECT_ID
    assert adapter._emulator_client is None

@pytest.mark.asyncio
async def test_init_custom():
    adapter = CloudTaskAdapter(project_id="custom-project")
    assert adapter.project_id == "custom-project"
    assert adapter._emulator_client is None

@pytest.mark.asyncio
async def test_get_emulator_client(adapter, mock_settings):
    mock_emulator = AsyncMock()
    mock_emulator.close = AsyncMock()
    with patch('adapters.cloudtask_emulator_client.CloudTaskEmulatorClient', return_value=mock_emulator) as mock_client_class:
        client = await adapter._get_emulator_client()
        mock_client_class.assert_called_once_with(emulator_url=mock_settings.CLOUDTASK_EMULATOR_URL)
        assert client == mock_emulator
        
        # Test caching
        client2 = await adapter._get_emulator_client()
        assert client2 == client
        mock_client_class.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_emulator(adapter, mock_settings, mock_logger):
    mock_response = {"name": "test-task"}
    mock_emulator = AsyncMock()
    mock_emulator.create_task.return_value = mock_response
    mock_emulator.close = AsyncMock()
    
    with patch('adapters.cloudtask_emulator_client.CloudTaskEmulatorClient', return_value=mock_emulator):
        mock_emulator.close = AsyncMock()
        response = await adapter.create_task(
            location="test-location",
            queue="test-queue",
            url="http://test.com",
            payload={"key": "value"},
            task_name="test-task",
            headers={"Custom": "Header"},
            service_account_email="test@example.com"
        )
        
        assert response == mock_response
        mock_emulator.create_task.assert_called_once()
        call_args = mock_emulator.create_task.call_args[1]
        assert call_args["project"] == "test-project"
        assert call_args["location"] == "test-location"
        assert call_args["queue"] == "test-queue"
        assert call_args["url"] == "http://test.com"
        assert call_args["payload"] == {"key": "value"}
        assert call_args["task_name"] == "test-task"
        assert call_args["headers"] == {"Custom": "Header"}
        assert call_args["service_account_email"] == "test@example.com"

@pytest.mark.asyncio
async def test_create_task_cloud(adapter, mock_logger):
    mock_response = Mock()
    mock_response._pb = Mock()
    mock_response.name = "test-task"
    mock_dict_result = {"name": "test-task"}
    mock_http_method = Mock()
    mock_http_method.POST = 1
    
    with patch('src.adapters.cloud_tasks.settings.CLOUD_PROVIDER', "gcp"), \
         patch('google.cloud.tasks_v2.CloudTasksClient') as mock_tasks_client, \
         patch('google.cloud.tasks_v2.HttpMethod', mock_http_method), \
         patch('google.protobuf.timestamp_pb2.Timestamp') as mock_timestamp, \
         patch('proto.message.MessageToDict', return_value=mock_dict_result) as mock_to_dict, \
         patch('src.adapters.cloud_tasks.JsonUtil.dumps', return_value='{"key": "value"}') as mock_dumps:
        
        mock_client_instance = mock_tasks_client.return_value
        mock_client_instance.queue_path.return_value = "test-queue-path"
        mock_client_instance.create_task.return_value = mock_response
        
        response = await adapter.create_task(
            location="test-location",
            queue="test-queue",
            url="http://test.com",
            payload={"key": "value"},
            task_name="test-task",
            headers={"Custom": "Header"},
            service_account_email="test@example.com"
        )
        
        assert response == mock_dict_result
        mock_client_instance.queue_path.assert_called_once_with("test-project", "test-location", "test-queue")
        mock_client_instance.create_task.assert_called_once()
        task_args = mock_client_instance.create_task.call_args[1]
        assert task_args['parent'] == "test-queue-path"
        mock_to_dict.assert_any_call(mock_response._pb)

@pytest.mark.asyncio
async def test_create_task_for_next_step(adapter, mock_settings):
    mock_task_params = Mock()
    mock_task_params.pipeline_scope = "test-scope"
    mock_task_params.pipeline_key = "test-key"
    mock_task_params.run_id = "test-run"
    mock_task_params.dict.return_value = {"param": "value"}
    
    with patch.object(adapter, 'create_task') as mock_create_task:
        mock_create_task.return_value = {"name": "test-task"}
        
        response = await adapter.create_task_for_next_step(
            task_id="test-task",
            task_parameters=mock_task_params
        )
        
        expected_url = f"{mock_settings.SELF_API_URL}/api/pipeline/test-scope/test-key/test-task/run"
        mock_create_task.assert_called_once()
        call_args = mock_create_task.call_args[1]
        assert call_args["location"] == mock_settings.GCP_LOCATION_2
        assert call_args["queue"] == mock_settings.DEFAULT_TASK_QUEUE
        assert call_args["url"] == expected_url
        assert call_args["payload"] == {"param": "value"}

@pytest.mark.asyncio
async def test_close(adapter):
    mock_emulator = AsyncMock()
    adapter._emulator_client = mock_emulator
    
    await adapter.close()
    mock_emulator.close.assert_called_once()
    assert adapter._emulator_client is None

@pytest.mark.asyncio
async def test_create_task_emulator_error(adapter, mock_logger):
    error_msg = "object MagicMock can't be used in 'await' expression"
    mock_emulator = AsyncMock()
    mock_emulator.create_task.side_effect = Exception(error_msg)
    
    with patch('adapters.cloudtask_emulator_client.CloudTaskEmulatorClient', return_value=mock_emulator), \
         pytest.raises(Exception, match=error_msg):
        await adapter.create_task(
            location="test-location",
            queue="test-queue",
            url="http://test.com",
            payload={"key": "value"}
        )
        
    mock_logger.error.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_cloud_error(adapter, mock_logger):
    with patch('src.adapters.cloud_tasks.settings.CLOUD_PROVIDER', "gcp"), \
         patch('google.cloud.tasks_v2.CloudTasksClient') as mock_tasks_client, \
         pytest.raises(Exception, match="Test error"):
        
        mock_client_instance = mock_tasks_client.return_value
        mock_client_instance.create_task.side_effect = Exception("Test error")
        
        await adapter.create_task(
            location="test-location",
            queue="test-queue",
            url="http://test.com",
            payload={"key": "value"}
        )
        
    mock_logger.error.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_cloud_with_schedule_time(adapter, mock_logger):
    schedule_time = datetime.now()
    mock_response = Mock()
    mock_response._pb = Mock()
    mock_response.name = "test-task"
    mock_dict_result = {"name": "test-task"}
    mock_timestamp = Mock()
    mock_http_method = Mock()
    mock_http_method.POST = 1
    
    with patch('src.adapters.cloud_tasks.settings.CLOUD_PROVIDER', "gcp"), \
         patch('google.cloud.tasks_v2.CloudTasksClient') as mock_tasks_client, \
         patch('google.cloud.tasks_v2.HttpMethod', mock_http_method), \
         patch('google.protobuf.timestamp_pb2.Timestamp', return_value=mock_timestamp) as mock_timestamp_class, \
         patch('proto.message.MessageToDict', return_value=mock_dict_result) as mock_to_dict, \
         patch('src.adapters.cloud_tasks.JsonUtil.dumps', return_value='{"key": "value"}') as mock_dumps:
        
        mock_client_instance = mock_tasks_client.return_value
        mock_client_instance.queue_path.return_value = "test-queue-path"
        mock_client_instance.create_task.return_value = mock_response
        
        response = await adapter.create_task(
            location="test-location",
            queue="test-queue",
            url="http://test.com",
            payload={"key": "value"},
            schedule_time=schedule_time
        )
        
        assert response == mock_dict_result
        mock_client_instance.queue_path.assert_called_once_with("test-project", "test-location", "test-queue")
        mock_timestamp.FromDatetime.assert_called_once_with(schedule_time)
        task_args = mock_client_instance.create_task.call_args[1]
        assert task_args['parent'] == "test-queue-path"
        assert 'schedule_time' in task_args['task']
        mock_to_dict.assert_any_call(mock_response._pb)