import json
from datetime import datetime
import pytest
import httpx
import os
import sys
from unittest.mock import Mock, patch

# Import and setup test environment first
from tests.test_env import setup_test_env
setup_test_env()

# Create complete settings mock
settings_mock = Mock()
settings_mock.DEBUG = False
settings_mock.CLOUD_PROVIDER = 'gcp'
settings_mock.STAGE = 'test'
settings_mock.VERSION = '0.1.0'
settings_mock.LOGGING_CHATTY_LOGGERS = []

# Now import application modules after environment is set up
from src.adapters.cloudtask_emulator_client import CloudTaskEmulatorClient

@pytest.fixture
def client():
    return CloudTaskEmulatorClient("http://localhost:8123")

@pytest.fixture
def mock_response():
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"status": "success"}
    return response

@pytest.mark.asyncio
async def test_init():
    # Test with trailing slash
    client = CloudTaskEmulatorClient("http://localhost:8123/")
    assert client.emulator_url == "http://localhost:8123"
    
    # Test without trailing slash
    client = CloudTaskEmulatorClient("http://localhost:8123")
    assert client.emulator_url == "http://localhost:8123"
    
    await client.close()

@pytest.mark.asyncio
async def test_create_task_success(client, mock_response, monkeypatch):
    async def mock_post(*args, **kwargs):
        assert args[0] == "http://localhost:8123/v2/projects/test-project/locations/us-central1/queues/test-queue/tasks"
        payload = json.loads(kwargs["json"]["task"]["payload"]["body"])
        assert payload == {"key": "value"}
        return mock_response
    
    monkeypatch.setattr(client.client, "post", mock_post)
    
    result = await client.create_task(
        project="test-project",
        location="us-central1",
        queue="test-queue",
        task_name="test-task",
        url="http://example.com",
        payload={"key": "value"},
        headers={"custom": "header"},
        schedule_time=datetime(2023, 1, 1),
        service_account_email="test@example.com"
    )
    
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_create_task_with_schedule_time(client, mock_response, monkeypatch):
    schedule_time = datetime(2023, 1, 1, 12, 0)
    
    async def mock_post(*args, **kwargs):
        task_data = kwargs["json"]["task"]
        assert task_data["schedule_time"] == schedule_time.isoformat()
        return mock_response
    
    monkeypatch.setattr(client.client, "post", mock_post)
    
    result = await client.create_task(
        project="test-project",
        location="us-central1",
        queue="test-queue",
        task_name="test-task",
        url="http://example.com",
        payload={"key": "value"},
        schedule_time=schedule_time
    )
    
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_create_task_connection_error(client, monkeypatch):
    async def mock_post(*args, **kwargs):
        raise httpx.ConnectError("Connection failed")
    
    monkeypatch.setattr(client.client, "post", mock_post)
    
    with pytest.raises(Exception) as exc_info:
        await client.create_task(
            project="test-project",
            location="us-central1",
            queue="test-queue",
            task_name="test-task",
            url="http://example.com",
            payload={"key": "value"}
        )
    
    assert "Cloud Task Emulator is not running" in str(exc_info.value)

@pytest.mark.asyncio
async def test_list_tasks_success(client, mock_response, monkeypatch):
    async def mock_get(*args, **kwargs):
        assert args[0] == "http://localhost:8123/v2/projects/test-project/locations/us-central1/queues/test-queue/tasks"
        return mock_response
    
    monkeypatch.setattr(client.client, "get", mock_get)
    
    result = await client.list_tasks(
        project="test-project",
        location="us-central1",
        queue="test-queue"
    )
    
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_list_tasks_connection_error(client, monkeypatch):
    async def mock_get(*args, **kwargs):
        raise httpx.ConnectError("Connection failed")
    
    monkeypatch.setattr(client.client, "get", mock_get)
    
    with pytest.raises(Exception) as exc_info:
        await client.list_tasks(
            project="test-project",
            location="us-central1",
            queue="test-queue"
        )
    
    assert "Cloud Task Emulator is not running" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_status_success(client, mock_response, monkeypatch):
    async def mock_get(*args, **kwargs):
        assert args[0] == "http://localhost:8123/status"
        return mock_response
    
    monkeypatch.setattr(client.client, "get", mock_get)
    
    result = await client.get_status()
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_get_status_connection_error(client, monkeypatch):
    async def mock_get(*args, **kwargs):
        raise httpx.ConnectError("Connection failed")
    
    monkeypatch.setattr(client.client, "get", mock_get)
    
    with pytest.raises(Exception) as exc_info:
        await client.get_status()
    
    assert "Cloud Task Emulator is not running" in str(exc_info.value)

@pytest.mark.asyncio
async def test_clear_tasks_success(client, mock_response, monkeypatch):
    async def mock_delete(*args, **kwargs):
        assert args[0] == "http://localhost:8123/tasks"
        return mock_response
    
    monkeypatch.setattr(client.client, "delete", mock_delete)
    
    result = await client.clear_tasks()
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_clear_tasks_connection_error(client, monkeypatch):
    async def mock_delete(*args, **kwargs):
        raise httpx.ConnectError("Connection failed")
    
    monkeypatch.setattr(client.client, "delete", mock_delete)
    
    with pytest.raises(Exception) as exc_info:
        await client.clear_tasks()
    
    assert "Cloud Task Emulator is not running" in str(exc_info.value)

@pytest.mark.asyncio
async def test_error_responses(client, monkeypatch):
    error_response = Mock(spec=httpx.Response)
    error_response.status_code = 500
    error_response.text = "Internal Server Error"
    
    async def mock_request(*args, **kwargs):
        return error_response
    
    # Test error response for each method
    monkeypatch.setattr(client.client, "post", mock_request)
    monkeypatch.setattr(client.client, "get", mock_request)
    monkeypatch.setattr(client.client, "delete", mock_request)
    
    # create_task
    with pytest.raises(Exception) as exc_info:
        await client.create_task(
            project="test-project",
            location="us-central1",
            queue="test-queue",
            task_name="test-task",
            url="http://example.com",
            payload={"key": "value"}
        )
    assert "Failed to create task: 500" in str(exc_info.value)
    
    # list_tasks
    with pytest.raises(Exception) as exc_info:
        await client.list_tasks(
            project="test-project",
            location="us-central1",
            queue="test-queue"
        )
    assert "Failed to list tasks: 500" in str(exc_info.value)
    
    # get_status
    with pytest.raises(Exception) as exc_info:
        await client.get_status()
    assert "Failed to get status: 500" in str(exc_info.value)
    
    # clear_tasks
    with pytest.raises(Exception) as exc_info:
        await client.clear_tasks()
    assert "Failed to clear tasks: 500" in str(exc_info.value)