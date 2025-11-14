import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from usecases.task_orchestrator import TaskOrchestrator
from models.general import TaskParameters, TaskResults, PipelineParameters
from models.pipeline_config import TaskConfig, TaskType, ModuleConfig, PromptConfig, PipelineReference, PipelineConfig


class TestTaskOrchestrator:
    """Test suite for TaskOrchestrator class."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        self.task_name = "test-task"
        self.orchestrator = TaskOrchestrator(self.task_name)
        
        # Create sample task parameters
        self.task_config = TaskConfig(
            id="test-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="test_module")
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
            context={"test": "data"}
        )

    def test_init(self):
        """Test TaskOrchestrator initialization."""
        orchestrator = TaskOrchestrator("my-task")
        assert orchestrator.task_name == "my-task"

    def test_build_gcs_path(self):
        """Test GCS path building."""
        filename = "test.json"
        expected_path = "test-app/test-tenant/test-patient/test-document/test-run-123/1/test-scope/test-pipeline/test-task/test.json"
        
        result = self.orchestrator._build_gcs_path(self.task_params, filename)
        assert result == expected_path

    def test_build_gcs_path_no_page_number(self):
        """Test GCS path building when page_number is None."""
        self.task_params.page_number = None
        filename = "test.json"
        expected_path = "test-app/test-tenant/test-patient/test-document/test-run-123/document/test-scope/test-pipeline/test-task/test.json"
        
        result = self.orchestrator._build_gcs_path(self.task_params, filename)
        assert result == expected_path

    @patch('usecases.task_orchestrator.StorageAdapter')
    @patch('usecases.task_orchestrator.JsonUtil')
    @patch('usecases.task_orchestrator.settings')
    async def test_persist_task_params_to_gcs_success(self, mock_settings, mock_json_util, mock_storage_adapter):
        """Test successful persistence of task parameters to GCS."""
        # Setup mocks
        mock_settings.STAGE = "test"
        mock_json_util.dumps.return_value = '{"test": "data"}'
        mock_storage = AsyncMock()
        mock_storage_adapter.return_value = mock_storage
        
        # Execute
        await self.orchestrator._persist_task_params_to_gcs(self.task_params)
        
        # Verify
        mock_storage_adapter.assert_called_once_with(bucket_name="entityextraction-context-test")
        mock_storage.save_document.assert_called_once()
        call_args = mock_storage.save_document.call_args
        assert call_args[1]['content_type'] == "application/json"
        assert call_args[1]['metadata']['task_name'] == self.task_name

    @patch('usecases.task_orchestrator.StorageAdapter')
    @patch('usecases.task_orchestrator.LOGGER')
    async def test_persist_task_params_to_gcs_failure(self, mock_logger, mock_storage_adapter):
        """Test handling of GCS persistence failure."""
        # Setup mocks to raise exception
        mock_storage = AsyncMock()
        mock_storage.save_document.side_effect = Exception("GCS Error")
        mock_storage_adapter.return_value = mock_storage
        
        # Execute (should not raise exception)
        await self.orchestrator._persist_task_params_to_gcs(self.task_params)
        
        # Verify error was logged
        mock_logger.error.assert_called()

    @patch('usecases.task_orchestrator.StorageAdapter')
    @patch('usecases.task_orchestrator.JsonUtil')
    @patch('usecases.task_orchestrator.settings')
    async def test_persist_task_results_to_gcs_success(self, mock_settings, mock_json_util, mock_storage_adapter):
        """Test successful persistence of task results to GCS."""
        # Setup mocks
        mock_settings.STAGE = "test"
        mock_json_util.dumps.return_value = '{"success": true}'
        mock_storage = AsyncMock()
        mock_storage_adapter.return_value = mock_storage
        
        # Create test results
        results = TaskResults(success=True, results={"test": "output"})
        
        # Execute
        await self.orchestrator._persist_task_results_to_gcs(self.task_params, results)
        
        # Verify
        mock_storage_adapter.assert_called_once_with(bucket_name="entityextraction-context-test")
        assert mock_storage.save_document.call_count == 2
        
        # Verify first call (output.json)
        output_call = mock_storage.save_document.call_args_list[0]
        assert output_call[1]['document_path'].endswith('output.json')
        assert output_call[1]['content_type'] == "application/json"
        assert output_call[1]['metadata']['success'] == "True"
        
        # Verify second call (results.json)
        results_call = mock_storage.save_document.call_args_list[1]
        assert results_call[1]['document_path'].endswith('results.json')
        assert results_call[1]['content_type'] == "application/json"
        assert results_call[1]['metadata']['success'] == "True"

    @patch('usecases.task_orchestrator.settings')
    async def test_invoke_local_development(self, mock_settings):
        """Test invoke method in local development mode."""
        # Setup mocks
        mock_settings.CLOUD_PROVIDER = "local"
        mock_settings.CLOUDTASK_EMULATOR_ENABLED = False
        
        with patch.object(self.orchestrator, 'run') as mock_run:
            mock_run.return_value = TaskResults(success=True)
            
            # Execute
            result = await self.orchestrator.invoke(self.task_params)
            
            # Verify
            mock_run.assert_called_once_with(self.task_params)
            assert result.success is True

    @patch('usecases.task_orchestrator.CloudTaskAdapter')
    @patch('usecases.task_orchestrator.settings')
    async def test_invoke_cloud_environment(self, mock_settings, mock_cloud_task_adapter):
        """Test invoke method in cloud environment."""
        # Setup mocks
        mock_settings.CLOUD_PROVIDER = "gcp"
        mock_settings.CLOUDTASK_EMULATOR_ENABLED = True
        
        mock_adapter = AsyncMock()
        mock_adapter.create_task_for_next_step.return_value = {"task_id": "123"}
        mock_cloud_task_adapter.return_value = mock_adapter
        
        # Execute
        result = await self.orchestrator.invoke(self.task_params)
        
        # Verify
        mock_adapter.create_task_for_next_step.assert_called_once_with(
            task_id=self.task_name,
            task_parameters=self.task_params,
            queue='entity-extraction-intra-default-default-queue'
        )
        mock_adapter.close.assert_called_once()
        assert result == self.task_params

    @patch('usecases.task_orchestrator.CloudTaskAdapter')
    @patch('usecases.task_orchestrator.settings')
    async def test_invoke_cloud_environment_failure(self, mock_settings, mock_cloud_task_adapter):
        """Test invoke method failure in cloud environment."""
        # Setup mocks
        mock_settings.CLOUD_PROVIDER = "gcp"
        mock_settings.CLOUDTASK_EMULATOR_ENABLED = True
        
        mock_adapter = AsyncMock()
        mock_adapter.create_task_for_next_step.side_effect = Exception("Cloud Task Error")
        mock_cloud_task_adapter.return_value = mock_adapter
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Cloud Task Error"):
            await self.orchestrator.invoke(self.task_params)
        
        # Verify cleanup was called
        mock_adapter.close.assert_called_once()

    @patch('usecases.task_orchestrator.ModuleInvoker')
    @patch('usecases.task_orchestrator.set_pipeline_context')
    @patch('usecases.task_orchestrator.settings')
    async def test_run_module_task(self, mock_settings, mock_set_context, mock_module_invoker):
        """Test running a MODULE type task."""
        # Setup mocks
        mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = False
        mock_invoker = AsyncMock()
        mock_invoker.run.return_value = TaskResults(success=True, results={"output": "data"})
        mock_module_invoker.return_value = mock_invoker
        
        with patch.object(self.orchestrator, '_determine_next_tasks') as mock_next_tasks:
            mock_next_tasks.return_value = []
            
            # Execute
            result = await self.orchestrator.run(self.task_params)
            
            # Verify
            mock_set_context.assert_called_once()
            mock_invoker.run.assert_called_once_with(self.task_params)
            assert result.success is True

    @patch('usecases.task_orchestrator.PromptInvoker')
    @patch('usecases.task_orchestrator.set_pipeline_context')
    @patch('usecases.task_orchestrator.settings')
    async def test_run_prompt_task(self, mock_settings, mock_set_context, mock_prompt_invoker):
        """Test running a PROMPT type task."""
        # Setup task config for PROMPT type
        self.task_params.task_config.type = TaskType.PROMPT
        self.task_params.task_config.prompt = PromptConfig(
            model="test-model",
            prompt="test prompt"
        )
        
        # Setup mocks
        mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = False
        mock_invoker = AsyncMock()
        mock_invoker.run.return_value = TaskResults(success=True, results={"output": "data"})
        mock_prompt_invoker.return_value = mock_invoker
        
        with patch.object(self.orchestrator, '_determine_next_tasks') as mock_next_tasks:
            mock_next_tasks.return_value = []
            
            # Execute
            result = await self.orchestrator.run(self.task_params)
            
            # Verify
            mock_invoker.run.assert_called_once_with(self.task_params)
            assert result.success is True

    @patch('usecases.task_orchestrator.PipelinesInvoker')
    @patch('usecases.task_orchestrator.set_pipeline_context')
    @patch('usecases.task_orchestrator.settings')
    async def test_run_pipeline_task(self, mock_settings, mock_set_context, mock_pipelines_invoker):
        """Test running a PIPELINE type task."""
        # Setup task config for PIPELINE type
        self.task_params.task_config.type = TaskType.PIPELINE
        self.task_params.task_config.pipelines = [
            PipelineReference(id="test-pipeline")
        ]
        
        # Setup mocks
        mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = False
        mock_invoker = AsyncMock()
        mock_invoker.run.return_value = TaskResults(success=True, results={"output": "data"})
        mock_pipelines_invoker.return_value = mock_invoker
        
        with patch.object(self.orchestrator, '_determine_next_tasks') as mock_next_tasks:
            mock_next_tasks.return_value = []
            
            # Execute
            result = await self.orchestrator.run(self.task_params)
            
            # Verify
            mock_invoker.run.assert_called_once_with(self.task_params)
            assert result.success is True

    @pytest.mark.filterwarnings("ignore::UserWarning")
    @patch('usecases.task_orchestrator.set_pipeline_context')
    @patch('usecases.task_orchestrator.settings')
    @patch('usecases.task_orchestrator.LOGGER')
    async def test_run_unknown_task_type(self, mock_logger, mock_settings, mock_set_context):
        """Test running a task with unknown type."""
        # Create a task config with an invalid enum value by directly setting the type
        # We'll mock the task_config.type property to return an invalid value
        mock_task_config = MagicMock()
        mock_task_config.type = "INVALID_TYPE"
        mock_task_config.id = "test-task"
        
        # Update task_params to use the mocked config
        self.task_params.task_config = mock_task_config
        
        # Setup mocks
        mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = False
        
        with patch.object(self.orchestrator, '_handle_task_failure') as mock_handle_failure:
            mock_handle_failure.return_value = TaskResults(success=False, error_message="Unknown task type")
            
            # Execute - should not raise exception but handle it via _handle_task_failure
            result = await self.orchestrator.run(self.task_params)
            
            # Verify that _handle_task_failure was called
            mock_handle_failure.assert_called_once()
            assert result.success is False

    @patch('usecases.task_orchestrator.CloudTaskAdapter')
    @patch('usecases.task_orchestrator.ModuleInvoker')
    @patch('usecases.task_orchestrator.set_pipeline_context')
    @patch('usecases.task_orchestrator.settings')
    async def test_run_with_next_tasks(self, mock_settings, mock_set_context, mock_module_invoker, mock_cloud_task_adapter):
        """Test running a task that has next tasks to execute."""
        # Setup mocks
        mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = False
        mock_invoker = AsyncMock()
        mock_invoker.run.return_value = TaskResults(success=True, results={"output": "data"})
        mock_module_invoker.return_value = mock_invoker
        
        # Mock next tasks
        next_task_config = TaskConfig(
            id="next-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="next_module")
        )
        next_task_params = TaskParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document",
            task_config=next_task_config
        )
        
        mock_adapter = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_adapter
        
        with patch.object(self.orchestrator, '_determine_next_tasks') as mock_next_tasks:
            mock_next_tasks.return_value = [next_task_params]
            
            # Execute
            result = await self.orchestrator.run(self.task_params)
            
            # Verify
            assert result.success is True
            assert "next_tasks" in result.metadata
            assert len(result.metadata["next_tasks"]) == 1
            mock_adapter.create_task_for_next_step.assert_called_once()
            mock_adapter.close.assert_called_once()

    @patch('usecases.task_orchestrator.search_pipeline_config')
    async def test_determine_next_tasks_no_pipeline_config(self, mock_search_config):
        """Test _determine_next_tasks when pipeline config is not found."""
        mock_search_config.return_value = None
        
        results = TaskResults(success=True)
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        assert next_tasks == []

    @patch('usecases.task_orchestrator.search_pipeline_config')
    async def test_determine_next_tasks_task_not_found(self, mock_search_config):
        """Test _determine_next_tasks when current task is not found in pipeline."""
        # Create mock pipeline config
        pipeline_config = PipelineConfig(
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            tasks=[
                TaskConfig(id="other-task", type=TaskType.MODULE, module=ModuleConfig(type="other"))
            ]
        )
        mock_search_config.return_value = pipeline_config
        
        results = TaskResults(success=True)
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        assert next_tasks == []

    @patch('usecases.task_orchestrator.search_pipeline_config')
    async def test_determine_next_tasks_pipeline_complete(self, mock_search_config):
        """Test _determine_next_tasks when pipeline is complete (no more tasks)."""
        # Create mock pipeline config with only current task
        pipeline_config = PipelineConfig(
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            tasks=[self.task_config]
        )
        mock_search_config.return_value = pipeline_config
        
        results = TaskResults(success=True)
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        assert next_tasks == []

    @patch('usecases.task_orchestrator.search_pipeline_config')
    async def test_determine_next_tasks_single_next_task(self, mock_search_config):
        """Test _determine_next_tasks with a single next task."""
        # Create next task
        next_task = TaskConfig(
            id="next-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="next_module")
        )
        
        # Create mock pipeline config
        pipeline_config = PipelineConfig(
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            tasks=[self.task_config, next_task]
        )
        mock_search_config.return_value = pipeline_config
        
        results = TaskResults(success=True)
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        assert len(next_tasks) == 1
        assert next_tasks[0].task_config.id == "next-task"

    def test_find_task_index(self):
        """Test _find_task_index method."""
        tasks = [
            TaskConfig(id="task1", type=TaskType.MODULE, module=ModuleConfig(type="mod1")),
            TaskConfig(id="task2", type=TaskType.MODULE, module=ModuleConfig(type="mod2")),
            TaskConfig(id="task3", type=TaskType.MODULE, module=ModuleConfig(type="mod3"))
        ]
        
        # Test finding existing tasks
        assert self.orchestrator._find_task_index(tasks, "task1") == 0
        assert self.orchestrator._find_task_index(tasks, "task2") == 1
        assert self.orchestrator._find_task_index(tasks, "task3") == 2
        
        # Test finding non-existing task
        assert self.orchestrator._find_task_index(tasks, "nonexistent") == -1

    def test_extract_pages_from_results_success(self):
        """Test _extract_pages_from_results with successful results."""
        pages_data = [
            {"page_number": 1, "content": "page1"},
            {"page_number": 2, "content": "page2"}
        ]
        results = TaskResults(
            success=True,
            results={"pages": pages_data}
        )
        
        pages = self.orchestrator._extract_pages_from_results(results)
        assert len(pages) == 2
        assert pages[0]["page_number"] == 1
        assert pages[1]["page_number"] == 2

    def test_extract_pages_from_results_failed_task(self):
        """Test _extract_pages_from_results with failed task."""
        results = TaskResults(success=False)
        
        pages = self.orchestrator._extract_pages_from_results(results)
        assert pages == []

    def test_extract_pages_from_results_no_results(self):
        """Test _extract_pages_from_results with no results."""
        results = TaskResults(success=True, results={})
        
        pages = self.orchestrator._extract_pages_from_results(results)
        assert pages == []

    def test_extract_pages_from_results_no_pages(self):
        """Test _extract_pages_from_results with no pages field."""
        results = TaskResults(success=True, results={"other": "data"})
        
        pages = self.orchestrator._extract_pages_from_results(results)
        assert pages == []

    def test_extract_pages_from_results_invalid_pages(self):
        """Test _extract_pages_from_results with invalid pages field."""
        results = TaskResults(success=True, results={"pages": "not_a_list"})
        
        pages = self.orchestrator._extract_pages_from_results(results)
        assert pages == []

    def test_create_task_parameters_for_pages(self):
        """Test _create_task_parameters_for_pages method."""
        pipeline_params = PipelineParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document"
        )
        
        task_config = TaskConfig(
            id="page-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="page_module")
        )
        
        pages = [
            {"page_number": 1, "storage_uri": "gs://bucket/page1.pdf", "total_pages": 3},
            {"page_number": 2, "storage_uri": "gs://bucket/page2.pdf", "total_pages": 3}
        ]
        
        task_params_list = self.orchestrator._create_task_parameters_for_pages(
            pipeline_params, task_config, pages
        )
        
        assert len(task_params_list) == 2
        
        # Check first page task
        assert task_params_list[0].page_number == 1
        assert task_params_list[0].task_config.id == "page-task"
        assert task_params_list[0].context["page_info"]["page_number"] == 1
        assert task_params_list[0].context["page_storage_uri"] == "gs://bucket/page1.pdf"
        
        # Check second page task
        assert task_params_list[1].page_number == 2
        assert task_params_list[1].context["page_info"]["page_number"] == 2

    def test_create_task_parameters_for_pages_missing_page_number(self):
        """Test _create_task_parameters_for_pages with missing page_number."""
        pipeline_params = PipelineParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document"
        )
        
        task_config = TaskConfig(
            id="page-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="page_module")
        )
        
        pages = [
            {"storage_uri": "gs://bucket/page1.pdf"},  # Missing page_number
            {"page_number": 2, "storage_uri": "gs://bucket/page2.pdf"}
        ]
        
        task_params_list = self.orchestrator._create_task_parameters_for_pages(
            pipeline_params, task_config, pages
        )
        
        # Should only create task for valid page
        assert len(task_params_list) == 1
        assert task_params_list[0].page_number == 2

    @patch('usecases.task_orchestrator.settings')
    async def test_run_with_gcs_persistence_enabled(self, mock_settings):
        """Test run method with GCS persistence enabled."""
        mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = True
        
        with patch.object(self.orchestrator, '_persist_task_params_to_gcs') as mock_persist_params, \
             patch.object(self.orchestrator, '_persist_task_results_to_gcs') as mock_persist_results, \
             patch.object(self.orchestrator, '_determine_next_tasks') as mock_next_tasks, \
             patch('usecases.task_orchestrator.ModuleInvoker') as mock_module_invoker, \
             patch('usecases.task_orchestrator.set_pipeline_context'):
            
            mock_persist_params.return_value = None
            mock_persist_results.return_value = None
            mock_next_tasks.return_value = []
            
            mock_invoker = AsyncMock()
            mock_invoker.run.return_value = TaskResults(success=True)
            mock_module_invoker.return_value = mock_invoker
            
            # Execute
            await self.orchestrator.run(self.task_params)
            
            # Verify persistence methods were called
            mock_persist_params.assert_called_once_with(self.task_params)
            mock_persist_results.assert_called_once()

    @patch('usecases.task_orchestrator.LOGGER')
    async def test_run_exception_handling(self, mock_logger):
        """Test run method exception handling."""
        with patch('usecases.task_orchestrator.ModuleInvoker') as mock_module_invoker, \
             patch('usecases.task_orchestrator.set_pipeline_context'), \
             patch('usecases.task_orchestrator.settings') as mock_settings:
            
            mock_settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = False
            mock_invoker = AsyncMock()
            mock_invoker.run.side_effect = Exception("Task execution failed")
            mock_module_invoker.return_value = mock_invoker
            
            with patch.object(self.orchestrator, '_handle_task_failure') as mock_handle_failure:
                mock_handle_failure.return_value = TaskResults(success=False, error_message="Task execution failed")
                
                # Execute - should not raise exception but handle it via _handle_task_failure
                result = await self.orchestrator.run(self.task_params)
                
                # Verify that _handle_task_failure was called
                mock_handle_failure.assert_called_once()
                assert result.success is False
                assert "Task execution failed" in result.error_message

    @patch('usecases.task_orchestrator.StorageAdapter')
    @patch('usecases.task_orchestrator.LOGGER')
    async def test_persist_task_results_to_gcs_failure(self, mock_logger, mock_storage_adapter):
        """Test handling of GCS persistence failure for task results."""
        # Setup mocks to raise exception
        mock_storage = AsyncMock()
        mock_storage.save_document.side_effect = Exception("GCS Error")
        mock_storage_adapter.return_value = mock_storage
        
        # Create test results
        results = TaskResults(success=True, results={"test": "output"})
        
        # Execute (should not raise exception)
        await self.orchestrator._persist_task_results_to_gcs(self.task_params, results)
        
        # Verify error was logged
        mock_logger.error.assert_called()

    @patch('usecases.task_orchestrator.search_pipeline_config')
    async def test_determine_next_tasks_with_post_processing_no_pages(self, mock_search_config):
        """Test _determine_next_tasks with post-processing but no pages found."""
        from models.pipeline_config import PostProcessing
        
        # Create next task
        next_task = TaskConfig(
            id="next-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="next_module")
        )
        
        # Create current task with post-processing
        current_task = TaskConfig(
            id="test-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="test_module"),
            post_processing=PostProcessing(for_each="page")
        )
        
        # Create mock pipeline config
        pipeline_config = PipelineConfig(
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            tasks=[current_task, next_task]
        )
        mock_search_config.return_value = pipeline_config
        
        # Create results with no pages
        results = TaskResults(success=True, results={"other": "data"})
        
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        # Should fall back to single task
        assert len(next_tasks) == 1
        assert next_tasks[0].task_config.id == "next-task"

    @patch('usecases.task_orchestrator.search_pipeline_config')
    @patch('usecases.task_orchestrator.LOGGER')
    async def test_determine_next_tasks_exception_handling(self, mock_logger, mock_search_config):
        """Test _determine_next_tasks exception handling."""
        # Setup mock to raise exception
        mock_search_config.side_effect = Exception("Database error")
        
        results = TaskResults(success=True)
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        # Should return empty list and log error
        assert next_tasks == []
        mock_logger.error.assert_called()


    @patch('usecases.task_orchestrator.LOGGER')
    def test_create_task_parameters_for_pages_exception_handling(self, mock_logger):
        """Test _create_task_parameters_for_pages exception handling."""
        pipeline_params = PipelineParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document"
        )
        
        task_config = TaskConfig(
            id="page-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="page_module")
        )
        
        # Create pages that will cause an exception
        pages = [
            {"page_number": 1, "storage_uri": "gs://bucket/page1.pdf"},
            None  # This will cause an exception when processing
        ]
        
        with patch.object(TaskParameters, 'from_pipeline_parameters') as mock_from_pipeline:
            mock_from_pipeline.side_effect = [
                TaskParameters(
                    app_id="test-app",
                    tenant_id="test-tenant", 
                    patient_id="test-patient",
                    document_id="test-document",
                    task_config=task_config
                ),
                Exception("Error creating task parameters")
            ]
            
            task_params_list = self.orchestrator._create_task_parameters_for_pages(
                pipeline_params, task_config, pages
            )
            
            # Should only create task for valid page and log error for invalid one
            assert len(task_params_list) == 1
            mock_logger.error.assert_called()

    @patch('usecases.task_orchestrator.search_pipeline_config')
    async def test_determine_next_tasks_with_post_processing_and_pages(self, mock_search_config):
        """Test _determine_next_tasks with post-processing and pages found."""
        from models.pipeline_config import PostProcessing
        
        # Create next task
        next_task = TaskConfig(
            id="next-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="next_module")
        )
        
        # Create current task with post-processing
        current_task = TaskConfig(
            id="test-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="test_module"),
            post_processing=PostProcessing(for_each="page")
        )
        
        # Create mock pipeline config
        pipeline_config = PipelineConfig(
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            tasks=[current_task, next_task]
        )
        mock_search_config.return_value = pipeline_config
        
        # Create results with pages
        results = TaskResults(success=True, results={
            "pages": [
                {"page_number": 1, "storage_uri": "gs://bucket/page1.pdf"},
                {"page_number": 2, "storage_uri": "gs://bucket/page2.pdf"}
            ]
        })
        
        next_tasks = await self.orchestrator._determine_next_tasks(self.task_params, results)
        
        # Should create task for each page
        assert len(next_tasks) == 2
        assert next_tasks[0].page_number == 1
        assert next_tasks[1].page_number == 2

    def test_add_task_results_to_context_with_entity_schema(self):
        """Test _add_task_results_to_context with entity schema reference."""
        from models.pipeline_config import EntitySchemaRef
        
        # Setup task config with entity schema reference
        self.task_params.task_config.entity_schema_ref = EntitySchemaRef(
            schema_uri="https://example.com/schema",
            var_name="test_entities"
        )
        
        # Create test results
        results = TaskResults(success=True, results={"entities": [{"id": 1, "name": "test"}]})

        # Mock EntityWrapper in the task_orchestrator module
        with patch('usecases.task_orchestrator.EntityWrapper') as mock_entity_wrapper:
            mock_wrapper_instance = MagicMock()
            mock_wrapper_instance.model_dump.return_value = {"wrapped": "data"}
            mock_entity_wrapper.return_value = mock_wrapper_instance

            # Execute
            self.orchestrator._add_task_results_to_context(self.task_params, results)

            # Verify EntityWrapper was created and used
            mock_entity_wrapper.assert_called_once_with(
                schema_ref="https://example.com/schema",
                app_id=self.task_params.app_id,
                tenant_id=self.task_params.tenant_id,
                patient_id=self.task_params.patient_id,
                document_id=self.task_params.document_id,
                page_number=self.task_params.page_number,
                run_id=self.task_params.run_id,
                entities={"entities": [{"id": 1, "name": "test"}]}
            )
            mock_wrapper_instance.add_entities.assert_called_once_with({"entities": [{"id": 1, "name": "test"}]})
            
            # Verify context was updated
            assert self.task_params.context is not None
            assert self.task_params.entities is not None

    def test_add_task_results_to_context_no_context_initialized(self):
        """Test _add_task_results_to_context when context is None."""
        # Set context and entities to None
        self.task_params.context = None
        self.task_params.entities = None
        
        # Create test results
        results = TaskResults(success=True, results={"test": "data"})
        
        # Execute
        self.orchestrator._add_task_results_to_context(self.task_params, results)
        
        # Verify context and entities were initialized
        assert self.task_params.context is not None
        assert self.task_params.entities is not None

    def test_add_task_results_to_context_no_entities_initialized(self):
        """Test _add_task_results_to_context when entities is None."""
        # Set entities to None but keep context
        self.task_params.entities = None
        
        # Create test results
        results = TaskResults(success=True, results={"test": "data"})
        
        # Execute
        self.orchestrator._add_task_results_to_context(self.task_params, results)
        
        # Verify entities was initialized
        assert self.task_params.entities is not None

    @patch('usecases.task_orchestrator.LOGGER')
    def test_add_task_results_to_context_exception_handling(self, mock_logger):
        """Test _add_task_results_to_context exception handling."""
        # Create test results
        results = TaskResults(success=True, results={"test": "data"})

        # Mock the results.model_dump method to raise an exception
        with patch.object(TaskResults, 'model_dump', side_effect=Exception("Model dump failed")):
            # Execute (should not raise exception)
            self.orchestrator._add_task_results_to_context(self.task_params, results)

            # Verify error was logged
            mock_logger.error.assert_called_once()

    @patch('usecases.task_orchestrator.settings')
    async def test_invoke_direct_queue_override(self, mock_settings):
        """Test invoke method with DIRECT queue override."""
        # Setup task config with DIRECT queue
        from usecases.task_orchestrator import QUEUE_DIRECT
        from models.pipeline_config import TaskInvocation
        
        invoke_config = TaskInvocation(queue_name=QUEUE_DIRECT)
        self.task_params.task_config.invoke = invoke_config
        
        # Setup settings for cloud environment
        mock_settings.CLOUD_PROVIDER = "gcp"
        mock_settings.CLOUDTASK_EMULATOR_ENABLED = True
        
        with patch.object(self.orchestrator, 'run') as mock_run:
            mock_run.return_value = TaskResults(success=True)
            
            # Execute
            result = await self.orchestrator.invoke(self.task_params)
            
            # Verify direct execution was used
            mock_run.assert_called_once_with(self.task_params)
            assert result.success is True

    @patch('usecases.task_orchestrator.CloudTaskAdapter')
    @patch('usecases.task_orchestrator.settings')
    async def test_invoke_default_queue_mapping(self, mock_settings, mock_cloud_task_adapter):
        """Test invoke method with DEFAULT queue mapping."""
        from usecases.task_orchestrator import QUEUE_DEFAULT
        from models.pipeline_config import TaskInvocation
        
        # Setup task config with DEFAULT queue
        invoke_config = TaskInvocation(queue_name=QUEUE_DEFAULT)
        self.task_params.task_config.invoke = invoke_config
        
        # Setup settings for cloud environment
        mock_settings.CLOUD_PROVIDER = "gcp"
        mock_settings.CLOUDTASK_EMULATOR_ENABLED = True
        mock_settings.INTRA_TASK_INVOCATION_DEFAULT_QUEUE = "mapped-default-queue"
        
        mock_adapter = AsyncMock()
        mock_adapter.create_task_for_next_step.return_value = {"task_id": "123"}
        mock_cloud_task_adapter.return_value = mock_adapter
        
        # Execute
        result = await self.orchestrator.invoke(self.task_params)
        
        # Verify the queue was mapped correctly
        mock_adapter.create_task_for_next_step.assert_called_once_with(
            task_id=self.task_name,
            task_parameters=self.task_params,
            queue="mapped-default-queue"
        )
