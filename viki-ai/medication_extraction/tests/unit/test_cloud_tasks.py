import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.adapters.cloud_tasks import CloudTaskAdapter

@pytest.fixture
def cloud_tasks_adapter():
    return CloudTaskAdapter("test-project")

@pytest.fixture
def mock_cloud_tasks_client():
    with patch('google.cloud.tasks_v2.CloudTasksClient') as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        mock_response = MagicMock()
        mock_response.name = "test-task"
        mock_response._pb = MagicMock()
        client_instance.create_task.return_value = mock_response
        yield mock_client

@pytest.fixture
def mock_message_to_dict():
    with patch('proto.message.MessageToDict') as mock:
        mock.return_value = {"name": "test-task"}
        yield mock

@pytest.mark.asyncio
async def test_create_task_with_token(cloud_tasks_adapter, mock_cloud_tasks_client, mock_message_to_dict):
    token = "test-token"
    location = "us-central1"
    service_account = "test@example.com"
    queue = "test-queue"
    url = "https://example.com"
    payload = {"key": "value"}

    result = await cloud_tasks_adapter.create_task(
        token=token,
        location=location,
        service_account_email=service_account,
        queue=queue,
        url=url,
        payload=payload
    )

    assert result == {"name": "test-task"}
    mock_cloud_tasks_client.return_value.create_task.assert_called_once()
    call_args = mock_cloud_tasks_client.return_value.create_task.call_args[1]
    assert "Bearer test-token" in str(call_args)

@pytest.mark.asyncio
async def test_create_task_without_token(cloud_tasks_adapter, mock_cloud_tasks_client, mock_message_to_dict):
    location = "us-central1"
    service_account = "test@example.com"
    queue = "test-queue"
    url = "https://example.com"
    payload = {"key": "value"}

    result = await cloud_tasks_adapter.create_task(
        token=None,
        location=location,
        service_account_email=service_account,
        queue=queue,
        url=url,
        payload=payload
    )

    assert result == {"name": "test-task"}
    mock_cloud_tasks_client.return_value.create_task.assert_called_once()
    call_args = mock_cloud_tasks_client.return_value.create_task.call_args[1]
    assert "Bearer" not in str(call_args)

@pytest.mark.asyncio
async def test_create_task_v2_basic(cloud_tasks_adapter, mock_cloud_tasks_client, mock_message_to_dict):
    location = "us-central1"
    service_account = "test@example.com"
    queue = "test-queue"
    url = "https://example.com"
    payload = {"key": "value"}

    result = await cloud_tasks_adapter.create_task_v2(
        location=location,
        service_account_email=service_account,
        queue=queue,
        url=url,
        payload=payload
    )

    assert result == {"name": "test-task"}
    mock_cloud_tasks_client.return_value.create_task.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_v2_with_headers(cloud_tasks_adapter, mock_cloud_tasks_client, mock_message_to_dict):
    location = "us-central1"
    service_account = "test@example.com"
    queue = "test-queue"
    url = "https://example.com"
    payload = {"key": "value"}
    headers = {"X-Custom-Header": "test-value"}

    result = await cloud_tasks_adapter.create_task_v2(
        location=location,
        service_account_email=service_account,
        queue=queue,
        url=url,
        payload=payload,
        http_headers=headers
    )

    assert result == {"name": "test-task"}
    mock_cloud_tasks_client.return_value.create_task.assert_called_once()
    call_args = mock_cloud_tasks_client.return_value.create_task.call_args[1]
    expected_headers = {
        "X-Custom-Header": "test-value"
    }
    assert call_args["task"]["http_request"]["headers"] == expected_headers

@pytest.mark.asyncio
async def test_create_task_v2_with_schedule_time(cloud_tasks_adapter, mock_cloud_tasks_client, mock_message_to_dict):
    location = "us-central1"
    service_account = "test@example.com"
    queue = "test-queue"
    url = "https://example.com"
    payload = {"key": "value"}
    schedule_time = datetime(2024, 1, 1, 12, 0)

    result = await cloud_tasks_adapter.create_task_v2(
        location=location,
        service_account_email=service_account,
        queue=queue,
        url=url,
        payload=payload,
        schedule_time=schedule_time
    )

    assert result == {"name": "test-task"}
    mock_cloud_tasks_client.return_value.create_task.assert_called_once()
    call_args = mock_cloud_tasks_client.return_value.create_task.call_args[1]
    assert "schedule_time" in call_args["task"]