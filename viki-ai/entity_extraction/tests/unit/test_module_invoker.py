"""
Unit tests for usecases.module_invoker module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.usecases.module_invoker import ModuleInvoker
from src.models.general import TaskParameters, TaskResults
from src.models.pipeline_config import TaskConfig, ModuleConfig, TaskType


class TestModuleInvoker:
    """Test cases for ModuleInvoker class."""

    @pytest.fixture
    def module_invoker(self):
        """Create a ModuleInvoker instance for testing."""
        return ModuleInvoker()

    @pytest.fixture
    def sample_task_params(self):
        """Create sample task parameters for testing."""
        # Create task config as dict to avoid validation issues
        task_config_dict = {
            "id": "test_task",
            "type": "module",
            "module": {"type": "test_module"}
        }
        return TaskParameters(
            task_config=task_config_dict,
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="doc123",
            pipeline_scope="test_scope",
            pipeline_key="test_pipeline"
        )

    @pytest.fixture
    def sample_task_results(self):
        """Create sample task results for testing."""
        return TaskResults(
            task_config_id="test_task",
            subject_uri="gs://bucket/test.pdf",
            success=True,
            output_uri="gs://bucket/output.json",
            metadata={"processed": True}
        )

    @pytest.mark.asyncio
    async def test_run_success(self, module_invoker, sample_task_params, sample_task_results):
        """Test successful module execution."""
        # Mock module class
        mock_module_class = Mock()
        mock_module_instance = AsyncMock()
        mock_module_instance.run.return_value = sample_task_results
        mock_module_class.return_value = mock_module_instance
        
        # Mock registry
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            mock_registry.get_module.return_value = mock_module_class
            
            # Execute the module
            result = await module_invoker.run(sample_task_params)
            
            # Verify the result
            assert result == sample_task_results
            mock_registry.get_module.assert_called_once_with("test_module")
            mock_module_class.assert_called_once()
            mock_module_instance.run.assert_called_once_with(sample_task_params)

    @pytest.mark.asyncio
    async def test_run_module_not_found(self, module_invoker, sample_task_params):
        """Test handling when module is not found in registry."""
        # Mock registry to return None (module not found)
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            mock_registry.get_module.return_value = None
            mock_registry.list_modules.return_value = ["module1", "module2", "module3"]
            
            # Execute and expect ValueError
            with pytest.raises(ValueError) as exc_info:
                await module_invoker.run(sample_task_params)
            
            # Verify the error message
            assert "Module 'test_module' not found in registry" in str(exc_info.value)
            assert "Available modules: ['module1', 'module2', 'module3']" in str(exc_info.value)
            mock_registry.get_module.assert_called_once_with("test_module")
            mock_registry.list_modules.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_module_execution_error(self, module_invoker, sample_task_params):
        """Test handling when module execution fails."""
        # Mock module class that raises an exception
        mock_module_class = Mock()
        mock_module_instance = AsyncMock()
        mock_module_instance.run.side_effect = RuntimeError("Module execution failed")
        mock_module_class.return_value = mock_module_instance
        
        # Mock registry
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            mock_registry.get_module.return_value = mock_module_class
            
            # Execute and expect RuntimeError to be re-raised
            with pytest.raises(RuntimeError) as exc_info:
                await module_invoker.run(sample_task_params)
            
            # Verify the error
            assert "Module execution failed" in str(exc_info.value)
            mock_module_instance.run.assert_called_once_with(sample_task_params)

    @pytest.mark.asyncio
    async def test_run_module_instantiation_error(self, module_invoker, sample_task_params):
        """Test handling when module instantiation fails."""
        # Mock module class that raises an exception during instantiation
        mock_module_class = Mock(side_effect=Exception("Module instantiation failed"))
        
        # Mock registry
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            mock_registry.get_module.return_value = mock_module_class
            
            # Execute and expect Exception to be re-raised
            with pytest.raises(Exception) as exc_info:
                await module_invoker.run(sample_task_params)
            
            # Verify the error
            assert "Module instantiation failed" in str(exc_info.value)
            mock_module_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_logging(self, module_invoker, sample_task_params, sample_task_results):
        """Test that proper logging occurs during module execution."""
        # Mock module class
        mock_module_class = Mock()
        mock_module_instance = AsyncMock()
        mock_module_instance.run.return_value = sample_task_results
        mock_module_instance.__class__.__name__ = "TestModuleClass"
        mock_module_class.return_value = mock_module_instance
        
        # Mock registry
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            with patch('src.usecases.module_invoker.LOGGER') as mock_logger:
                mock_registry.get_module.return_value = mock_module_class
                
                # Execute the module
                result = await module_invoker.run(sample_task_params)
                
                # Verify logging was called
                assert mock_logger.debug.call_count >= 3  # Initial log, execution log, completion log
                
                # Verify result
                assert result == sample_task_results

    @pytest.mark.asyncio
    async def test_run_with_different_module_types(self, module_invoker, sample_task_results):
        """Test running different module types."""
        module_types = ["sleep", "split_pages", "noop"]

        for module_type in module_types:
            # Create task params for each module type
            task_config_dict = {
                "id": f"test_task_{module_type}",
                "type": "module",
                "module": {"type": module_type}
            }
            task_params = TaskParameters(
                task_config=task_config_dict,
                app_id="test_app",
                tenant_id="test_tenant",
                patient_id="test_patient",
                document_id="doc123",
                pipeline_scope="test_scope",
                pipeline_key="test_pipeline"
            )
            
            # Mock module class
            mock_module_class = Mock()
            mock_module_instance = AsyncMock()
            mock_module_instance.run.return_value = sample_task_results
            mock_module_class.return_value = mock_module_instance
            
            # Mock registry
            with patch('src.usecases.module_invoker.registry') as mock_registry:
                mock_registry.get_module.return_value = mock_module_class
                
                # Execute the module
                result = await module_invoker.run(task_params)
                
                # Verify the result
                assert result == sample_task_results
                mock_registry.get_module.assert_called_with(module_type)

    @pytest.mark.asyncio
    async def test_run_with_complex_task_parameters(self, module_invoker):
        """Test running with complex task parameters."""
        # Create complex task parameters
        task_config_dict = {
            "id": "complex_task",
            "type": "module",
            "module": {
                "type": "complex_module",
                "context": {"param1": "value1", "param2": 123}
            }
        }
        task_params = TaskParameters(
            task_config=task_config_dict,
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="complex_doc_123",
            pipeline_scope="complex_scope",
            pipeline_key="complex_pipeline",
            entities={"key1": "value1", "key2": {"nested": "value"}}
        )
        
        # Create expected results
        expected_results = TaskResults(
            task_config_id="complex_task",
            subject_uri="gs://bucket/complex_document.pdf",
            success=True,
            output_uri="gs://bucket/complex_output.json",
            metadata={"processed": True, "complexity": "high"}
        )
        
        # Mock module class
        mock_module_class = Mock()
        mock_module_instance = AsyncMock()
        mock_module_instance.run.return_value = expected_results
        mock_module_class.return_value = mock_module_instance
        
        # Mock registry
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            mock_registry.get_module.return_value = mock_module_class
            
            # Execute the module
            result = await module_invoker.run(task_params)
            
            # Verify the result
            assert result == expected_results
            mock_registry.get_module.assert_called_once_with("complex_module")
            mock_module_instance.run.assert_called_once_with(task_params)

    @pytest.mark.asyncio
    async def test_run_error_logging(self, module_invoker, sample_task_params):
        """Test that errors are properly logged."""
        # Mock module class that raises an exception
        mock_module_class = Mock()
        mock_module_instance = AsyncMock()
        test_error = ValueError("Test validation error")
        mock_module_instance.run.side_effect = test_error
        mock_module_class.return_value = mock_module_instance
        
        # Mock registry
        with patch('src.usecases.module_invoker.registry') as mock_registry:
            with patch('src.usecases.module_invoker.LOGGER') as mock_logger:
                mock_registry.get_module.return_value = mock_module_class
                
                # Execute and expect error
                with pytest.raises(ValueError):
                    await module_invoker.run(sample_task_params)
                
                # Verify error logging was called
                mock_logger.error.assert_called_once()
                error_call_args = mock_logger.error.call_args
                assert "Error running module task test_module" in error_call_args[0][0]