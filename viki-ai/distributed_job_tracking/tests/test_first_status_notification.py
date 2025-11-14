import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.usecases.pipeline_service import PipelineService
from src.models.pipeline import PipelineStatusUpdate, PipelineStatus


@pytest.fixture
async def pipeline_service():
    """Create a PipelineService instance for testing"""
    service = PipelineService()
    # Mock the Redis client
    service.redis_client = AsyncMock()
    yield service
    await service.close()


@pytest.fixture
def sample_pipeline_data():
    """Sample pipeline data for testing"""
    return PipelineStatusUpdate(
        status=PipelineStatus.IN_PROGRESS,
        page_number=1,
        metadata={"test": "data"},
        app_id="test_app",
        tenant_id="test_tenant",
        patient_id="test_patient",
        document_id="test_document",
        pages=5
    )


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        "app_id": "test_app",
        "tenant_id": "test_tenant",
        "patient_id": "test_patient",
        "document_id": "test_document",
        "run_id": "test_run_123",
        "name": "Test Job",
        "pages": 5,
        "metadata": {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


class TestFirstStatusNotification:
    """Test cases for first status notification feature"""

    async def test_is_first_status_for_run_when_no_pipelines_exist(self, pipeline_service):
        """Test that _is_first_status_for_run returns True when no pipelines exist"""
        # Mock Redis to return 0 pipelines
        pipeline_service.redis_client.scard.return_value = 0
        
        result = await pipeline_service._is_first_status_for_run("test_run_123")
        
        assert result is True
        pipeline_service.redis_client.scard.assert_called_once_with("djt::test_run_123:pipeline_list")

    async def test_is_first_status_for_run_when_pipelines_exist(self, pipeline_service):
        """Test that _is_first_status_for_run returns False when pipelines exist"""
        # Mock Redis to return 2 pipelines
        pipeline_service.redis_client.scard.return_value = 2
        
        result = await pipeline_service._is_first_status_for_run("test_run_123")
        
        assert result is False
        pipeline_service.redis_client.scard.assert_called_once_with("djt::test_run_123:pipeline_list")

    async def test_is_first_status_for_run_handles_exception(self, pipeline_service):
        """Test that _is_first_status_for_run handles exceptions gracefully"""
        # Mock Redis to raise an exception
        pipeline_service.redis_client.scard.side_effect = Exception("Redis error")
        
        result = await pipeline_service._is_first_status_for_run("test_run_123")
        
        # Should default to False to avoid duplicate notifications
        assert result is False

    @patch('src.usecases.pipeline_service.CloudTaskAdapter')
    async def test_publish_first_status_success(self, mock_cloud_task_adapter, pipeline_service, sample_pipeline_data, sample_job_data):
        """Test successful first status publication"""
        # Mock Redis to return job data
        pipeline_service.redis_client.hget.return_value = json.dumps(sample_job_data)
        
        # Mock CloudTaskAdapter
        mock_adapter_instance = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_adapter_instance
        mock_adapter_instance.create_task.return_value = {"task_id": "test_task_123"}
        
        # Call the method
        await pipeline_service._publish_first_status("test_run_123", sample_pipeline_data)
        
        # Verify Redis call
        pipeline_service.redis_client.hget.assert_called_once_with("djt::test_run_123", "job")
        
        # Verify CloudTask creation
        mock_adapter_instance.create_task.assert_called_once()
        call_args = mock_adapter_instance.create_task.call_args
        
        # Check the payload
        payload = call_args.kwargs['payload']
        assert payload['run_id'] == "test_run_123"
        assert payload['status'] == "IN_PROGRESS"
        assert payload['app_id'] == "test_app"
        assert payload['tenant_id'] == "test_tenant"
        assert payload['patient_id'] == "test_patient"
        assert payload['document_id'] == "test_document"
        assert payload['elapsed_time'] == 0
        assert payload['pipelines'] == []
        
        # Verify adapter was closed
        mock_adapter_instance.close.assert_called_once()

    async def test_publish_first_status_no_job_data(self, pipeline_service, sample_pipeline_data):
        """Test first status publication when job data is not found"""
        # Mock Redis to return None (no job data)
        pipeline_service.redis_client.hget.return_value = None
        
        # Call the method - should not raise exception
        await pipeline_service._publish_first_status("test_run_123", sample_pipeline_data)
        
        # Verify Redis call
        pipeline_service.redis_client.hget.assert_called_once_with("djt::test_run_123", "job")

    @patch('src.usecases.pipeline_service.CloudTaskAdapter')
    async def test_publish_first_status_handles_exception(self, mock_cloud_task_adapter, pipeline_service, sample_pipeline_data, sample_job_data):
        """Test that first status publication handles exceptions gracefully"""
        # Mock Redis to return job data
        pipeline_service.redis_client.hget.return_value = json.dumps(sample_job_data)
        
        # Mock CloudTaskAdapter to raise exception
        mock_adapter_instance = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_adapter_instance
        mock_adapter_instance.create_task.side_effect = Exception("CloudTask error")
        
        # Call the method - should not raise exception
        await pipeline_service._publish_first_status("test_run_123", sample_pipeline_data)
        
        # Verify adapter was still closed
        mock_adapter_instance.close.assert_called_once()

    @patch('src.usecases.pipeline_service.CloudTaskAdapter')
    async def test_update_pipeline_status_calls_first_status_notification(self, mock_cloud_task_adapter, pipeline_service, sample_pipeline_data, sample_job_data):
        """Test that update_pipeline_status calls first status notification when appropriate"""
        # Mock Redis responses
        pipeline_service.redis_client.hexists.return_value = True  # Job exists
        pipeline_service.redis_client.scard.return_value = 0  # No pipelines exist (first status)
        pipeline_service.redis_client.hget.side_effect = [
            json.dumps(sample_job_data),  # For job data in _publish_first_status
            None  # For pipeline check (pipeline doesn't exist)
        ]
        
        # Mock Redis pipeline operations
        mock_redis_pipeline = AsyncMock()
        pipeline_service.redis_client.pipeline.return_value = mock_redis_pipeline
        mock_redis_pipeline.execute.return_value = [1, True, 1, True]  # Success responses
        
        # Mock CloudTaskAdapter
        mock_adapter_instance = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_adapter_instance
        mock_adapter_instance.create_task.return_value = {"task_id": "test_task_123"}
        
        # Mock other methods to avoid side effects
        pipeline_service._check_and_publish_run_completion = AsyncMock()
        
        # Call update_pipeline_status
        result = await pipeline_service.update_pipeline_status("test_run_123", "test_pipeline", sample_pipeline_data)
        
        # Verify first status notification was called
        mock_adapter_instance.create_task.assert_called_once()
        call_args = mock_adapter_instance.create_task.call_args
        
        # Verify the URL contains the first status endpoint
        url = call_args.kwargs['url']
        assert "/api/v5/status_update/entity_extraction" in url
        
        # Verify task name indicates first status
        task_name = call_args.kwargs['task_name']
        assert task_name.startswith("first-status-update-")

    async def test_update_pipeline_status_skips_first_status_when_not_first(self, pipeline_service, sample_pipeline_data, sample_job_data):
        """Test that update_pipeline_status skips first status notification when not the first status"""
        # Mock Redis responses
        pipeline_service.redis_client.hexists.return_value = True  # Job exists
        pipeline_service.redis_client.scard.return_value = 2  # Pipelines already exist (not first status)
        pipeline_service.redis_client.hget.return_value = None  # Pipeline doesn't exist
        
        # Mock Redis pipeline operations
        mock_redis_pipeline = AsyncMock()
        pipeline_service.redis_client.pipeline.return_value = mock_redis_pipeline
        mock_redis_pipeline.execute.return_value = [1, True, 1, True]  # Success responses
        
        # Mock other methods to avoid side effects
        pipeline_service._check_and_publish_run_completion = AsyncMock()
        
        # Spy on _publish_first_status to ensure it's not called
        with patch.object(pipeline_service, '_publish_first_status', new_callable=AsyncMock) as mock_publish_first:
            # Call update_pipeline_status
            result = await pipeline_service.update_pipeline_status("test_run_123", "test_pipeline", sample_pipeline_data)
            
            # Verify first status notification was NOT called
            mock_publish_first.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
