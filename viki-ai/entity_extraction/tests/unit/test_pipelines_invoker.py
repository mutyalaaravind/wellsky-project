import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from src.models.general import TaskParameters, TaskResults, PipelineParameters
from src.models.pipeline_config import TaskConfig, PipelineReference, TaskType
from src.usecases.pipelines_invoker import PipelinesInvoker
from src.models.djt_models import PipelineStatusUpdate, PipelineStatus
from src.util.exception import exceptionToMap


class TestPipelinesInvoker:
    """Test class for PipelinesInvoker"""

    @pytest.fixture
    def pipeline_ref(self):
        """Create a sample pipeline reference."""
        return PipelineReference(
            id="test-pipeline",
            scope="test-scope",
            host="https://api.example.com",
            queue="test-queue",
            context={"key": "value"}
        )

    @pytest.fixture
    def task_config(self, pipeline_ref):
        """Create a sample task config with pipeline references."""
        return TaskConfig(
            id="test-task-config",
            type=TaskType.PIPELINE,
            pipelines=[pipeline_ref]
        )

    @pytest.fixture
    def task_params(self, task_config):
        """Create sample task parameters."""
        return TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            page_number=1,
            page_count=5,
            pipeline_start_date="2024-01-01T00:00:00Z",
            run_id="test-run-123",
            subject={"id": "test-subject"},
            context={"existing": "context"},
            task_config=task_config.model_dump()
        )

    @pytest.fixture
    def invoker(self):
        """Create PipelinesInvoker instance."""
        return PipelinesInvoker()

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_success_single_pipeline(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker, task_params):
        """Test successful execution with single pipeline."""
        # Setup settings
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        # Setup CloudTaskAdapter mock
        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.return_value = {"task_id": "task-123"}
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        # Setup DJT client mock
        mock_djt_client = AsyncMock()
        mock_djt_client.pipeline_status_update.return_value = {"status": "updated"}
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        result = await invoker.run(task_params)

        # Verify results
        assert result.success is True
        assert result.results is None
        assert result.metadata["invoker_type"] == "pipelines"
        assert result.metadata["pipeline_count"] == 1
        assert "test-scope.test-pipeline" in result.metadata["pipelines_executed"]
        assert len(result.metadata["pipeline_results"]) == 1
        
        pipeline_result = result.metadata["pipeline_results"][0]
        assert pipeline_result["pipeline_id"] == "test-pipeline"
        assert pipeline_result["status"] == "queued"
        assert pipeline_result["cloud_task_response"]["task_id"] == "task-123"

        # Verify CloudTaskAdapter was called correctly
        mock_adapter_instance.create_task.assert_called_once()
        call_args = mock_adapter_instance.create_task.call_args
        assert call_args.kwargs["location"] == "us-central1"
        assert call_args.kwargs["queue"] == "test-queue"
        assert call_args.kwargs["url"] == "https://api.example.com/api/pipeline/test-scope/test-pipeline/start"
        assert call_args.kwargs["task_name"] == "pipeline-test-pipeline-test-run-123"
        assert call_args.kwargs["service_account_email"] == "test@example.com"

        # Verify payload contains merged context
        payload = call_args.kwargs["payload"]
        assert payload["context"]["existing"] == "context"
        assert payload["context"]["key"] == "value"

        # Verify DJT client was called
        mock_djt_client.pipeline_status_update.assert_called_once()
        djt_call_args = mock_djt_client.pipeline_status_update.call_args
        assert djt_call_args.kwargs["job_id"] == "test-run-123"
        assert djt_call_args.kwargs["pipeline_id"] == "test-scope:test-pipeline"

        # Verify adapter cleanup
        mock_adapter_instance.close.assert_called_once()

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_success_multiple_pipelines(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker, task_config):
        """Test successful execution with multiple pipelines."""
        # Setup multiple pipeline references
        pipeline_ref1 = PipelineReference(id="pipeline1", scope="scope1")
        pipeline_ref2 = PipelineReference(id="pipeline2", scope="scope2")
        task_config = TaskConfig(id="test-task-config", type=TaskType.PIPELINE, pipelines=[pipeline_ref1, pipeline_ref2])
        
        task_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            page_number=1,
            run_id="test-run-123",
            subject={"id": "test-subject"},
            task_config=task_config.model_dump()
        )

        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.side_effect = [
            {"task_id": "task-1"},
            {"task_id": "task-2"}
        ]
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        mock_djt_client = AsyncMock()
        mock_djt_client.pipeline_status_update.return_value = {"status": "updated"}
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        result = await invoker.run(task_params)

        # Verify results
        assert result.success is True
        assert result.metadata["pipeline_count"] == 2
        assert "scope1.pipeline1,scope2.pipeline2" in result.metadata["pipelines_executed"]
        assert len(result.metadata["pipeline_results"]) == 2

        # Verify both pipelines were processed
        assert mock_adapter_instance.create_task.call_count == 2
        assert mock_djt_client.pipeline_status_update.call_count == 2

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_with_context_merging(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker):
        """Test context merging between task params and pipeline ref."""
        pipeline_ref = PipelineReference(
            id="test-pipeline",
            scope="test-scope",
            context={"pipeline_key": "pipeline_value", "shared_key": "pipeline_override"}
        )
        
        task_config = TaskConfig(id="test-task-config", type=TaskType.PIPELINE, pipelines=[pipeline_ref])
        task_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            run_id="test-run-123",
            context={"task_key": "task_value", "shared_key": "task_value"},
            task_config=task_config.model_dump()
        )

        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.return_value = {"task_id": "task-123"}
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        mock_djt_client = AsyncMock()
        mock_djt_client.pipeline_status_update.return_value = {"status": "updated"}
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        await invoker.run(task_params)

        # Verify context merging in payload
        call_args = mock_adapter_instance.create_task.call_args
        payload = call_args.kwargs["payload"]
        context = payload["context"]
        
        assert context["task_key"] == "task_value"  # From task params
        assert context["pipeline_key"] == "pipeline_value"  # From pipeline ref
        assert context["shared_key"] == "pipeline_override"  # Pipeline ref overrides task params

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_with_no_context(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker):
        """Test execution when no context is provided."""
        pipeline_ref = PipelineReference(id="test-pipeline", scope="test-scope")
        task_config = TaskConfig(id="test-task-config", type=TaskType.PIPELINE, pipelines=[pipeline_ref])
        task_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            run_id="test-run-123",
            context={},  # Empty context instead of None
            task_config=task_config.model_dump()
        )

        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.return_value = {"task_id": "task-123"}
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        mock_djt_client = AsyncMock()
        mock_djt_client.pipeline_status_update.return_value = {"status": "updated"}
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        result = await invoker.run(task_params)

        # Verify successful execution even without context
        assert result.success is True

        # Verify payload has empty context
        call_args = mock_adapter_instance.create_task.call_args
        payload = call_args.kwargs["payload"]
        assert payload["context"] == {}

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_djt_client_error_continues_execution(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker, task_params):
        """Test that DJT client errors don't stop pipeline execution."""
        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.return_value = {"task_id": "task-123"}
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        # DJT client fails
        mock_djt_client = AsyncMock()
        mock_djt_client.pipeline_status_update.side_effect = Exception("DJT service unavailable")
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        result = await invoker.run(task_params)

        # Verify execution continues despite DJT error
        assert result.success is True
        assert result.metadata["pipeline_count"] == 1
        assert len(result.metadata["pipeline_results"]) == 1

        # Verify cloud task was still created
        mock_adapter_instance.create_task.assert_called_once()

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_cloud_task_error_fails_execution(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker, task_params):
        """Test that cloud task creation errors fail the execution."""
        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.side_effect = Exception("Cloud Tasks API error")
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        mock_djt_client = AsyncMock()
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        result = await invoker.run(task_params)

        # Verify execution fails
        assert result.success is False
        assert result.error_message is not None  # Just check an error occurred
        assert result.metadata["invoker_type"] == "pipelines"
        assert "error" in result.metadata

        # Verify adapter cleanup still happens
        mock_adapter_instance.close.assert_called_once()

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_uses_default_settings(self, mock_settings, mock_cloud_task_adapter, invoker):
        """Test that default settings are used when pipeline ref doesn't specify them."""
        pipeline_ref = PipelineReference(
            id="test-pipeline",
            scope="test-scope"
            # No host or queue specified
        )
        
        task_config = TaskConfig(id="test-task-config", type=TaskType.PIPELINE, pipelines=[pipeline_ref])
        task_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            run_id="test-run-123",
            task_config=task_config.model_dump()
        )

        # Setup settings
        mock_settings.SELF_API_URL = "https://default-api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-west1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-task-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "default@example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.return_value = {"task_id": "task-123"}
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        # Execute
        await invoker.run(task_params)

        # Verify default settings were used
        call_args = mock_adapter_instance.create_task.call_args
        assert call_args.kwargs["queue"] == "default-task-queue"
        assert "https://default-api.example.com/api/pipeline" in call_args.kwargs["url"]

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.get_djt_client')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_run_pipeline_status_update_metadata(self, mock_settings, mock_get_djt_client, mock_cloud_task_adapter, invoker, task_params):
        """Test pipeline status update contains correct metadata."""
        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"
        mock_settings.GCP_LOCATION_2 = "us-central1"
        mock_settings.DEFAULT_TASK_QUEUE = "default-queue"
        mock_settings.SERVICE_ACCOUNT_EMAIL = "test@example.com"

        mock_adapter_instance = AsyncMock()
        cloud_task_response = {"task_id": "task-123", "name": "projects/test/locations/us-central1/queues/test-queue/tasks/task-123"}
        mock_adapter_instance.create_task.return_value = cloud_task_response
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        mock_djt_client = AsyncMock()
        mock_djt_client.pipeline_status_update.return_value = {"status": "updated"}
        mock_get_djt_client.return_value = mock_djt_client

        # Execute
        await invoker.run(task_params)

        # Verify DJT status update call
        djt_call_args = mock_djt_client.pipeline_status_update.call_args
        pipeline_data = djt_call_args.kwargs["pipeline_data"]
        
        # The pipeline_data should be a PipelineStatusUpdate instance
        assert pipeline_data.id == "test-scope.test-pipeline"
        assert pipeline_data.id == "test-scope.test-pipeline"
        assert pipeline_data.status == PipelineStatus.IN_PROGRESS
        assert pipeline_data.page_number == 1
        assert pipeline_data.pages == 5
        assert pipeline_data.app_id == "test-app"
        assert pipeline_data.tenant_id == "test-tenant"
        assert pipeline_data.patient_id == "test-patient"
        assert pipeline_data.document_id == "test-doc"
        
        # Verify metadata
        assert pipeline_data.metadata["cloud_task_response"] == cloud_task_response
        assert pipeline_data.metadata["queue"] == "test-queue"
        assert pipeline_data.metadata["url"] == "https://api.example.com/api/pipeline/test-scope/test-pipeline/start"
        assert pipeline_data.metadata["pipeline_scope"] == "test-scope"

    @patch('src.usecases.pipelines_invoker.CloudTaskAdapter')
    @patch('src.usecases.pipelines_invoker.settings')
    async def test_adapter_close_called_on_exception(self, mock_settings, mock_cloud_task_adapter, invoker, task_params):
        """Test that adapter.close() is called even when exceptions occur."""
        # Setup mocks
        mock_settings.SELF_API_URL = "https://api.example.com"

        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.create_task.side_effect = Exception("Unexpected error")
        mock_cloud_task_adapter.return_value = mock_adapter_instance

        # Execute
        result = await invoker.run(task_params)

        # Verify execution failed but cleanup happened
        assert result.success is False
        mock_adapter_instance.close.assert_called_once()

    async def test_run_exception_handling(self, invoker):
        """Test exception handling when task_params has invalid pipeline config."""
        # Create task_params with empty pipelines list which will cause iteration issues
        task_config = TaskConfig(
            id="test-task-config",
            type=TaskType.PIPELINE,
            pipelines=None  # This will cause an error when trying to iterate
        )
        
        malformed_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-doc",
            run_id="test-run-123",
            task_config=task_config.model_dump()
        )

        # Execute
        result = await invoker.run(malformed_params)

        # Verify error handling
        assert result.success is False
        assert result.error_message is not None
        assert result.metadata["invoker_type"] == "pipelines"
        assert "error" in result.metadata