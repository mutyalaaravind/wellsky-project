"""
Comprehensive tests for PromptInvoker class.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json

from src.models.general import TaskParameters, TaskResults
from src.models.pipeline_config import PromptConfig, TaskConfig, EntitySchemaRef
from src.usecases.prompt_invoker import PromptInvoker
from src.adapters.llm import StandardPromptAdapter, LLMResponse, UsageMetadata


class TestPromptInvoker:
    """Comprehensive test class for PromptInvoker."""

    def test_prompt_invoker_initialization(self):
        """Test that PromptInvoker initializes correctly."""
        invoker = PromptInvoker()
        
        # Should not have an llm_adapter attribute
        assert not hasattr(invoker, 'llm_adapter')

    def test_format_prompt_template_success(self):
        """Test successful template formatting."""
        invoker = PromptInvoker()
        
        template = "Hello {name}, your ID is {user_id}"
        context = {"name": "John", "user_id": "12345"}
        
        result = invoker._format_prompt_template(template, context)
        assert result == "Hello John, your ID is 12345"

    def test_format_prompt_template_missing_variable(self):
        """Test template formatting with missing variables."""
        invoker = PromptInvoker()
        
        template = "Hello {name}, your ID is {missing_var}"
        context = {"name": "John"}
        
        with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
            result = invoker._format_prompt_template(template, context)
            assert result == template
            mock_logger.warning.assert_called()

    def test_format_prompt_template_exception(self):
        """Test template formatting with general exception."""
        invoker = PromptInvoker()
        
        # Use a mock template that will cause an error
        template = Mock()
        template.format.side_effect = ValueError("Test error")
        context = {"name": "John"}
        
        with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
            result = invoker._format_prompt_template(template, context)
            assert result == template
            mock_logger.error.assert_called()

    def test_extract_file_items_with_document_uri(self):
        """Test file items extraction when is_add_document_uri_to_context is True."""
        invoker = PromptInvoker()
        
        # Create task parameters
        task_params = Mock()
        task_params.subject_uri = 'gs://bucket/test-document.pdf'
        task_params.document_id = 'doc123'
        task_params.task_config = Mock()
        task_params.task_config.prompt = Mock()
        task_params.task_config.prompt.is_add_document_uri_to_context = True
        task_params.task_config.id = 'task123'
        
        with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
            file_items = invoker._extract_file_items_from_context(task_params)
            
            assert len(file_items) == 1
            assert ('gs://bucket/test-document.pdf', 'application/pdf') in file_items
            mock_logger.info.assert_called()

    def test_extract_file_items_without_document_uri(self):
        """Test file items extraction when is_add_document_uri_to_context is False."""
        invoker = PromptInvoker()
        
        task_params = Mock()
        task_params.subject_uri = 'gs://bucket/test-document.pdf'
        task_params.document_id = 'doc123'
        task_params.task_config = Mock()
        task_params.task_config.prompt = Mock()
        task_params.task_config.prompt.is_add_document_uri_to_context = False
        task_params.task_config.id = 'task123'
        
        with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
            file_items = invoker._extract_file_items_from_context(task_params)
            
            assert len(file_items) == 0
            mock_logger.debug.assert_called()

    def test_extract_file_items_empty_subject_uri(self):
        """Test file items extraction with empty subject_uri."""
        invoker = PromptInvoker()
        
        task_params = Mock()
        task_params.subject_uri = None
        task_params.document_id = 'doc123'
        task_params.task_config = Mock()
        task_params.task_config.prompt = Mock()
        task_params.task_config.prompt.is_add_document_uri_to_context = True
        task_params.task_config.id = 'task123'
        
        with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
            file_items = invoker._extract_file_items_from_context(task_params)
            
            assert len(file_items) == 0
            mock_logger.warning.assert_called()

    def test_process_response_json_format(self):
        """Test response processing with JSON format."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.response_format = 'json'
        
        json_response = '{"test": "value", "number": 42}'
        
        # Since the method imports and calls extract_json_from_response directly, we need to mock it differently
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter.extract_json_from_response') as mock_extract:
            mock_extract.return_value = {"test": "value", "number": 42}
            
            result = invoker._process_response(json_response, prompt_config)
            assert result == {"test": "value", "number": 42}
            mock_extract.assert_called_once_with(json_response)

    def test_process_response_non_json_format(self):
        """Test response processing without JSON format."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.response_format = 'text'
        
        response = "This is a plain text response"
        
        result = invoker._process_response(response, prompt_config)
        assert result == response

    def test_process_response_no_format_attribute(self):
        """Test response processing when prompt_config has no response_format."""
        invoker = PromptInvoker()
        
        prompt_config = Mock(spec=[])  # Mock with no attributes
        response = "This is a plain text response"
        
        result = invoker._process_response(response, prompt_config)
        assert result == response

    def test_process_response_exception_handling(self):
        """Test response processing with exception handling."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.response_format = 'json'
        
        json_response = 'invalid json'
        
        with patch.object(StandardPromptAdapter, 'extract_json_from_response') as mock_extract:
            mock_extract.side_effect = ValueError("Invalid JSON")
            
            with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
                result = invoker._process_response(json_response, prompt_config)
                assert result == json_response
                mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_run_success_basic(self):
        """Test successful run with basic configuration."""
        invoker = PromptInvoker()
        
        # Create task parameters
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Analyze this document: {subject_uri}'
        prompt_config.max_output_tokens = 4096
        prompt_config.temperature = 0.1
        prompt_config.top_p = 0.9
        prompt_config.system_instructions = ['You are a helpful assistant']
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = None
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        # Mock LLM response
        usage_metadata = Mock()
        usage_metadata.model_dump.return_value = {'input_tokens': 100, 'output_tokens': 50}
        
        llm_response = Mock()
        llm_response.text = '{"entities": ["test"]}'
        llm_response.usage_metadata = usage_metadata
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            with patch('src.usecases.prompt_invoker.Metric') as mock_metric:
                with patch('src.usecases.prompt_invoker.LOGGER'):
                    result = await invoker.run(task_params)
                    
                    assert result.success is True
                    assert result.results == {"entities": ["test"]}
                    assert result.execution_time_ms > 0
                    assert result.metadata['invoker_type'] == 'prompt'
                    assert result.metadata['model'] == 'gemini-pro'
                    
                    # Verify metrics were sent
                    assert mock_metric.send.call_count == 2  # start and complete

    @pytest.mark.asyncio
    async def test_run_with_context_and_file_items(self):
        """Test run with context that includes file items."""
        invoker = PromptInvoker()
        
        # Create task parameters with context
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Analyze this: {subject_uri}'
        prompt_config.max_output_tokens = 4096
        prompt_config.temperature = 0.0
        prompt_config.top_p = 0.95
        prompt_config.system_instructions = []
        prompt_config.is_add_document_uri_to_context = True
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = None
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = {'file_data': 'binary_data'}
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        llm_response = Mock()
        llm_response.text = '{"result": "success"}'
        llm_response.usage_metadata = None
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            with patch('src.usecases.prompt_invoker.Metric') as mock_metric:
                with patch('src.usecases.prompt_invoker.LOGGER'):
                    result = await invoker.run(task_params)
                    
                    assert result.success is True
                    assert result.results == {"result": "success"}
                    
                    # Verify adapter was called with correct parameters
                    mock_adapter.generate_content_async.assert_called_once()
                    call_args = mock_adapter.generate_content_async.call_args
                    assert call_args[1]['response_mime_type'] == 'application/json'
                    assert call_args[1]['stream'] is True

    @pytest.mark.asyncio
    async def test_run_with_entity_schema(self):
        """Test run with entity schema reference."""
        invoker = PromptInvoker()
        
        # Create entity schema ref
        entity_schema_ref = Mock()
        entity_schema_ref.schema_uri = 'gs://schemas/test.json'
        
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Extract entities'
        prompt_config.system_instructions = None
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = entity_schema_ref
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        llm_response = Mock()
        llm_response.text = '{"entities": []}'
        llm_response.usage_metadata = None
        
        mock_schema = {'type': 'object', 'properties': {}}
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            with patch('src.adapters.schema_client.SchemaClient') as mock_schema_client_class:
                mock_schema_client = AsyncMock()
                mock_schema_client.get_entity_schema.return_value = mock_schema
                mock_schema_client_class.return_value = mock_schema_client
                
                with patch('src.usecases.prompt_invoker.Metric') as mock_metric:
                    with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
                        result = await invoker.run(task_params)
                        
                        assert result.success is True
                        # Verify that the code path with entity_schema_ref was executed
                        assert result.results == {"entities": []}

    @pytest.mark.asyncio
    async def test_run_with_failed_schema_retrieval(self):
        """Test run when schema retrieval fails."""
        invoker = PromptInvoker()
        
        entity_schema_ref = Mock()
        entity_schema_ref.schema_uri = 'gs://schemas/test.json'
        
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Extract entities'
        prompt_config.system_instructions = None
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = entity_schema_ref
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        llm_response = Mock()
        llm_response.text = '{"entities": []}'
        llm_response.usage_metadata = None
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            with patch('src.adapters.schema_client.SchemaClient') as mock_schema_client_class:
                mock_schema_client = AsyncMock()
                mock_schema_client.get_entity_schema.return_value = None
                mock_schema_client_class.return_value = mock_schema_client
                
                with patch('src.usecases.prompt_invoker.Metric') as mock_metric:
                    with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
                        result = await invoker.run(task_params)
                        
                        assert result.success is True
                        mock_logger.warning.assert_any_call(f"Failed to retrieve entity schema from {entity_schema_ref.schema_uri}")

    @pytest.mark.asyncio
    async def test_run_without_prompt_text(self):
        """Test run when prompt config has no prompt text."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = None  # No prompt text
        prompt_config.system_instructions = None  # No system instructions
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = None
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        llm_response = Mock()
        llm_response.text = '{"result": "fallback"}'
        llm_response.usage_metadata = None
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            with patch('src.usecases.prompt_invoker.Metric'):
                with patch('src.usecases.prompt_invoker.LOGGER'):
                    result = await invoker.run(task_params)
                    
                    assert result.success is True
                    # Should use fallback prompt
                    call_args = mock_adapter.generate_content_async.call_args
                    items = call_args[1]['items']
                    assert "Please analyze the provided content and extract relevant entities." in items

    @pytest.mark.asyncio
    async def test_run_exception_handling(self):
        """Test run method exception handling."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Test prompt'
        prompt_config.system_instructions = None
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = None
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter_class.side_effect = Exception("Test error")
            
            with patch('src.usecases.prompt_invoker.Metric') as mock_metric:
                with patch('src.usecases.prompt_invoker.LOGGER') as mock_logger:
                    with patch('src.usecases.prompt_invoker.exceptionToMap') as mock_exception_map:
                        mock_exception_map.return_value = {'error': 'test'}
                        
                        result = await invoker.run(task_params)
                        
                        assert result.success is False
                        assert "Error running prompt task: Test error" in result.error_message
                        assert result.results == {}
                        assert result.execution_time_ms >= 0  # Could be 0 in fast test execution
                        assert result.metadata['invoker_type'] == 'prompt'
                        assert result.metadata['error'] == {'error': 'test'}
                        
                        # Verify error metric was sent
                        mock_metric.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_exception_with_llm_response_token_usage(self):
        """Test exception handling when LLM response exists with token usage."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Test prompt'
        prompt_config.system_instructions = None
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = None
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {'test': 'data'}
        
        # Mock LLM response with usage metadata
        usage_metadata = Mock()
        usage_metadata.model_dump.return_value = {'input_tokens': 100, 'output_tokens': 50}
        
        llm_response = Mock()
        llm_response.text = '{"entities": []}'
        llm_response.usage_metadata = usage_metadata
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            # Make JSON parsing fail to trigger exception after LLM response
            with patch('json.loads', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
                with patch('src.usecases.prompt_invoker.Metric') as mock_metric:
                    with patch('src.usecases.prompt_invoker.LOGGER'):
                        with patch('src.usecases.prompt_invoker.exceptionToMap') as mock_exception_map:
                            mock_exception_map.return_value = {'error': 'json_error'}
                            
                            result = await invoker.run(task_params)
                            
                            assert result.success is False
                            assert "Error running prompt task:" in result.error_message
                            
                            # Verify error metric was sent with token usage
                            mock_metric.send.assert_called()
                            error_call = mock_metric.send.call_args
                            assert 'token_usage' in error_call[0][1]  # Check metadata includes token usage

    @pytest.mark.asyncio
    async def test_run_with_system_instructions(self):
        """Test run with multiple system instructions."""
        invoker = PromptInvoker()
        
        prompt_config = Mock()
        prompt_config.model = 'gemini-pro'
        prompt_config.prompt = 'Analyze: {subject_uri}'
        prompt_config.system_instructions = [
            'You are an expert analyzer',
            'Focus on {task_config.id} task'
        ]
        prompt_config.is_add_document_uri_to_context = False
        
        task_config = Mock()
        task_config.id = 'task123'
        task_config.prompt = prompt_config
        task_config.entity_schema_ref = None
        
        task_params = Mock()
        task_params.task_config = task_config
        task_params.subject_uri = 'gs://bucket/doc.pdf'
        task_params.context = None
        task_params.pipeline_scope = 'test'
        task_params.pipeline_key = 'key123'
        task_params.run_id = 'run123'
        task_params.app_id = 'app123'
        task_params.tenant_id = 'tenant123'
        task_params.patient_id = 'patient123'
        task_params.document_id = 'doc123'
        task_params.page_number = 1
        task_params.model_dump.return_value = {
            'subject_uri': 'gs://bucket/doc.pdf',
            'task_config': {'id': 'task123'}
        }
        
        llm_response = Mock()
        llm_response.text = '{"analysis": "complete"}'
        llm_response.usage_metadata = None
        
        with patch('src.usecases.prompt_invoker.StandardPromptAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter.generate_content_async.return_value = llm_response
            mock_adapter_class.return_value = mock_adapter
            
            with patch('src.usecases.prompt_invoker.Metric'):
                with patch('src.usecases.prompt_invoker.LOGGER'):
                    result = await invoker.run(task_params)
                    
                    assert result.success is True
                    
                    # Verify system prompts were formatted and passed
                    call_args = mock_adapter.generate_content_async.call_args
                    system_prompts = call_args[1]['system_prompts']
                    assert len(system_prompts) == 2
                    assert 'You are an expert analyzer' in system_prompts
