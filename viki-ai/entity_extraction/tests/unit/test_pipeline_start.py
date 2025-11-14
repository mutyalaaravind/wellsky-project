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

from usecases.pipeline_start import pipeline_start
from models.general import PipelineParameters, TaskParameters
from models.pipeline_config import PipelineConfig, TaskConfig, TaskType, ModuleConfig


class TestPipelineStart:
    """Test suite for pipeline_start function."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        self.valid_scope = "default"
        self.valid_pipeline_key = "test-pipeline"
        
        # Create sample pipeline parameters
        self.pipeline_params = PipelineParameters(
            app_id="test-app",
            tenant_id="test-tenant",
            patient_id="test-patient",
            document_id="test-document"
        )
        
        # Create sample task config
        self.task_config = TaskConfig(
            id="test-task",
            type=TaskType.MODULE,
            module=ModuleConfig(type="test_module")
        )
        
        # Create sample pipeline config
        self.pipeline_config = PipelineConfig(
            id="test-config-id",
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            scope="default",
            output_entity="test_entity",
            tasks=[self.task_config]
        )

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.TaskOrchestrator')
    @patch('usecases.pipeline_start.set_pipeline_context')
    @patch('usecases.pipeline_start.generate_timeprefixed_id')
    @patch('usecases.pipeline_start.now_utc')
    async def test_pipeline_start_success(self, mock_now_utc, mock_generate_id, mock_set_context, mock_orchestrator, mock_search_config):
        """Test successful pipeline start."""
        # Setup mocks
        mock_search_config.return_value = self.pipeline_config
        mock_generate_id.return_value = "20231201T120000-abc123"
        mock_now_utc.return_value = datetime(2023, 12, 1, 12, 0, 0)
        
        mock_orchestrator_instance = AsyncMock()
        mock_orchestrator_instance.invoke.return_value = MagicMock()
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Ensure run_id is None so it will use the generated one
        self.pipeline_params.run_id = None
        
        # Execute
        result = await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)
        
        # Verify
        assert result == self.pipeline_params
        assert result.pipeline_scope == self.valid_scope
        assert result.pipeline_key == self.valid_pipeline_key
        assert result.run_id == "20231201T120000-abc123"
        assert result.pipeline_start_date == datetime(2023, 12, 1, 12, 0, 0)
        
        mock_search_config.assert_called_once_with(self.valid_scope, self.valid_pipeline_key)
        mock_set_context.assert_called_once()
        mock_orchestrator_instance.invoke.assert_called_once()

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.TaskOrchestrator')
    @patch('usecases.pipeline_start.set_pipeline_context')
    @patch('usecases.pipeline_start.now_utc')
    async def test_pipeline_start_with_existing_run_id(self, mock_now_utc, mock_set_context, mock_orchestrator, mock_search_config):
        """Test pipeline start with existing run_id."""
        # Setup mocks
        mock_search_config.return_value = self.pipeline_config
        mock_now_utc.return_value = datetime(2023, 12, 1, 12, 0, 0)
        
        mock_orchestrator_instance = AsyncMock()
        mock_orchestrator_instance.invoke.return_value = MagicMock()
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Set existing run_id
        self.pipeline_params.run_id = "existing-run-id"
        
        # Execute
        result = await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)
        
        # Verify existing run_id is preserved
        assert result.run_id == "existing-run-id"

    async def test_pipeline_start_invalid_scope_none(self):
        """Test pipeline start with None scope."""
        with pytest.raises(ValueError, match="Scope 'None' and pipeline_key 'test-pipeline' must be provided"):
            await pipeline_start(None, self.valid_pipeline_key, self.pipeline_params)

    async def test_pipeline_start_invalid_scope_empty(self):
        """Test pipeline start with empty scope."""
        with pytest.raises(ValueError, match="Scope '' and pipeline_key 'test-pipeline' must be provided"):
            await pipeline_start("", self.valid_pipeline_key, self.pipeline_params)

    async def test_pipeline_start_invalid_scope_whitespace(self):
        """Test pipeline start with whitespace-only scope."""
        with pytest.raises(ValueError, match="Scope '   ' and pipeline_key 'test-pipeline' must be provided"):
            await pipeline_start("   ", self.valid_pipeline_key, self.pipeline_params)

    async def test_pipeline_start_invalid_pipeline_key_none(self):
        """Test pipeline start with None pipeline_key."""
        with pytest.raises(ValueError, match="Scope 'default' and pipeline_key 'None' must be provided"):
            await pipeline_start(self.valid_scope, None, self.pipeline_params)

    async def test_pipeline_start_invalid_pipeline_key_empty(self):
        """Test pipeline start with empty pipeline_key."""
        with pytest.raises(ValueError, match="Scope 'default' and pipeline_key '' must be provided"):
            await pipeline_start(self.valid_scope, "", self.pipeline_params)

    async def test_pipeline_start_invalid_pipeline_key_whitespace(self):
        """Test pipeline start with whitespace-only pipeline_key."""
        with pytest.raises(ValueError, match="Scope 'default' and pipeline_key '   ' must be provided"):
            await pipeline_start(self.valid_scope, "   ", self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    async def test_pipeline_start_config_not_found(self, mock_search_config):
        """Test pipeline start when configuration is not found."""
        # Setup mock to return None
        mock_search_config.return_value = None
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Pipeline configuration not found for scope 'default' and key 'test-pipeline'"):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    async def test_pipeline_start_no_tasks_none(self, mock_search_config):
        """Test pipeline start when tasks is None."""
        # Create a mock config that bypasses Pydantic validation
        mock_config = MagicMock()
        mock_config.id = "test-config-id"
        mock_config.name = "Test Pipeline"
        mock_config.version = "1.0"
        mock_config.output_entity = None
        mock_config.tasks = None
        mock_config.dict.return_value = {"id": "test-config-id", "name": "Test Pipeline"}
        
        mock_search_config.return_value = mock_config
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Pipeline configuration must define at least one task"):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    async def test_pipeline_start_no_tasks_empty(self, mock_search_config):
        """Test pipeline start when tasks is empty list."""
        # Create config with empty tasks
        config_no_tasks = PipelineConfig(
            id="test-config-id",
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            scope="default",
            tasks=[]
        )
        mock_search_config.return_value = config_no_tasks
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Pipeline configuration must define at least one task"):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    async def test_pipeline_start_search_config_exception(self, mock_search_config):
        """Test pipeline start when search_pipeline_config raises exception."""
        # Setup mock to raise exception
        mock_search_config.side_effect = Exception("Database connection error")
        
        # Execute and verify exception is propagated
        with pytest.raises(Exception, match="Database connection error"):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.TaskOrchestrator')
    @patch('usecases.pipeline_start.set_pipeline_context')
    @patch('usecases.pipeline_start.generate_timeprefixed_id')
    @patch('usecases.pipeline_start.now_utc')
    async def test_pipeline_start_orchestrator_exception(self, mock_now_utc, mock_generate_id, mock_set_context, mock_orchestrator, mock_search_config):
        """Test pipeline start when TaskOrchestrator raises exception."""
        # Setup mocks
        mock_search_config.return_value = self.pipeline_config
        mock_generate_id.return_value = "20231201T120000-abc123"
        mock_now_utc.return_value = datetime(2023, 12, 1, 12, 0, 0)
        
        mock_orchestrator_instance = AsyncMock()
        mock_orchestrator_instance.invoke.side_effect = Exception("Task execution failed")
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Execute and verify exception is propagated
        with pytest.raises(Exception, match="Task execution failed"):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.TaskOrchestrator')
    @patch('usecases.pipeline_start.set_pipeline_context')
    @patch('usecases.pipeline_start.generate_timeprefixed_id')
    @patch('usecases.pipeline_start.now_utc')
    @patch('usecases.pipeline_start.TaskParameters')
    async def test_pipeline_start_task_parameters_creation_exception(self, mock_task_params, mock_now_utc, mock_generate_id, mock_set_context, mock_orchestrator, mock_search_config):
        """Test pipeline start when TaskParameters creation raises exception."""
        # Setup mocks
        mock_search_config.return_value = self.pipeline_config
        mock_generate_id.return_value = "20231201T120000-abc123"
        mock_now_utc.return_value = datetime(2023, 12, 1, 12, 0, 0)
        
        # Mock TaskParameters.from_pipeline_parameters to raise exception
        mock_task_params.from_pipeline_parameters.side_effect = Exception("Task parameter creation failed")
        
        # Execute and verify exception is propagated
        with pytest.raises(Exception, match="Task parameter creation failed"):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)


    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.TaskOrchestrator')
    @patch('usecases.pipeline_start.set_pipeline_context')
    @patch('usecases.pipeline_start.generate_timeprefixed_id')
    @patch('usecases.pipeline_start.now_utc')
    @patch('usecases.pipeline_start.logger')
    async def test_pipeline_start_logging_coverage(self, mock_logger, mock_now_utc, mock_generate_id, mock_set_context, mock_orchestrator, mock_search_config):
        """Test pipeline start to ensure logging statements are covered."""
        # Setup mocks
        mock_search_config.return_value = self.pipeline_config
        mock_generate_id.return_value = "20231201T120000-abc123"
        mock_now_utc.return_value = datetime(2023, 12, 1, 12, 0, 0)
        
        mock_orchestrator_instance = AsyncMock()
        mock_orchestrator_instance.invoke.return_value = MagicMock()
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Execute
        result = await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)
        
        # Verify logging calls were made
        assert mock_logger.info.call_count >= 2  # Start and success messages
        assert mock_logger.debug.call_count >= 2  # Debug messages
        
        # Verify result
        assert result == self.pipeline_params

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.logger')
    async def test_pipeline_start_value_error_logging(self, mock_logger, mock_search_config):
        """Test pipeline start ValueError logging."""
        # Setup mock to return None (config not found)
        mock_search_config.return_value = None
        
        # Execute and verify exception
        with pytest.raises(ValueError):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)
        
        # Verify error logging
        mock_logger.error.assert_called()

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.logger')
    async def test_pipeline_start_general_exception_logging(self, mock_logger, mock_search_config):
        """Test pipeline start general exception logging."""
        # Setup mock to raise general exception
        mock_search_config.side_effect = RuntimeError("Unexpected error")
        
        # Execute and verify exception
        with pytest.raises(RuntimeError):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)
        
        # Verify error logging
        mock_logger.error.assert_called()

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.TaskOrchestrator')
    @patch('usecases.pipeline_start.set_pipeline_context')
    @patch('usecases.pipeline_start.generate_timeprefixed_id')
    @patch('usecases.pipeline_start.now_utc')
    async def test_pipeline_start_complex_config(self, mock_now_utc, mock_generate_id, mock_set_context, mock_orchestrator, mock_search_config):
        """Test pipeline start with complex configuration."""
        # Create complex config with multiple tasks
        complex_config = PipelineConfig(
            id="complex-config-id",
            key="complex-pipeline",
            version="2.1.0",
            name="Complex Test Pipeline",
            scope="medical",
            output_entity="complex_entity",
            tasks=[
                self.task_config,
                TaskConfig(
                    id="second-task",
                    type=TaskType.MODULE,
                    module=ModuleConfig(type="second_module")
                )
            ]
        )
        
        # Setup mocks
        mock_search_config.return_value = complex_config
        mock_generate_id.return_value = "20231201T120000-xyz789"
        mock_now_utc.return_value = datetime(2023, 12, 1, 12, 0, 0)
        
        mock_orchestrator_instance = AsyncMock()
        mock_orchestrator_instance.invoke.return_value = MagicMock()
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Ensure run_id is None so it will use the generated one
        self.pipeline_params.run_id = None
        
        # Execute
        result = await pipeline_start("medical", "complex-pipeline", self.pipeline_params)
        
        # Verify
        assert result.pipeline_scope == "medical"
        assert result.pipeline_key == "complex-pipeline"
        assert result.run_id == "20231201T120000-xyz789"
        
        # Verify orchestrator was called with first task
        mock_orchestrator.assert_called_once_with("test-task")

    async def test_pipeline_start_invalid_input_logging_coverage(self):
        """Test pipeline start invalid input to cover logging branches."""
        # Test with None scope to cover error logging
        with pytest.raises(ValueError):
            await pipeline_start(None, self.valid_pipeline_key, self.pipeline_params)
        
        # Test with None pipeline_key to cover error logging
        with pytest.raises(ValueError):
            await pipeline_start(self.valid_scope, None, self.pipeline_params)

    @patch('usecases.pipeline_start.search_pipeline_config')
    @patch('usecases.pipeline_start.logger')
    async def test_pipeline_start_no_tasks_logging_coverage(self, mock_logger, mock_search_config):
        """Test pipeline start with no tasks to cover JSON logging."""
        # Create config with empty tasks
        config_no_tasks = PipelineConfig(
            id="test-config-id",
            key="test-pipeline",
            version="1.0",
            name="Test Pipeline",
            scope="default",
            tasks=[]
        )
        mock_search_config.return_value = config_no_tasks
        
        # Execute and verify exception
        with pytest.raises(ValueError):
            await pipeline_start(self.valid_scope, self.valid_pipeline_key, self.pipeline_params)
        
        # Verify that JSON logging was attempted (covers the JSON dump lines)
        mock_logger.error.assert_called()
