import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest
from datetime import datetime
import json
from typing import List, Dict, Any

# Import and setup test environment first
from tests.test_env import setup_test_env
setup_test_env()

# Now import modules that depend on environment variables
from src.models.general import PipelineParameters, TaskParameters, TaskResults
from src.models.pipeline_config import TaskConfig, TaskType, PromptConfig

# Import the LLM adapter classes
from src.adapters.llm import (
    StandardPromptAdapter,
    LLMResponse,
    UsageMetadata,
    PromptStats,
    DEFAULT_SAFETY_SETTINGS,
    DEFAULT_RESPONSE_MIME_TYPE
)


class TestUsageMetadata(unittest.TestCase):
    """Test the UsageMetadata model."""
    
    def test_usage_metadata_creation(self):
        """Test basic UsageMetadata creation."""
        usage = UsageMetadata(
            prompt_token_count=100,
            candidates_token_count=50,
            total_token_count=150
        )
        assert usage.prompt_token_count == 100
        assert usage.candidates_token_count == 50
        assert usage.total_token_count == 150
        assert usage.cached_content_token_count is None
    
    def test_usage_metadata_optional_fields(self):
        """Test UsageMetadata with all optional fields."""
        usage = UsageMetadata()
        assert usage.prompt_token_count is None
        assert usage.candidates_token_count is None
        assert usage.total_token_count is None
        assert usage.cached_content_token_count is None


class TestLLMResponse(unittest.TestCase):
    """Test the LLMResponse model."""
    
    def test_llm_response_creation(self):
        """Test basic LLMResponse creation."""
        usage = UsageMetadata(prompt_token_count=100, total_token_count=150)
        response = LLMResponse(text="Generated text", usage_metadata=usage)
        assert response.text == "Generated text"
        assert response.usage_metadata == usage
    
    def test_llm_response_without_usage(self):
        """Test LLMResponse without usage metadata."""
        response = LLMResponse(text="Generated text")
        assert response.text == "Generated text"
        assert response.usage_metadata is None


class TestPromptStats(unittest.TestCase):
    """Test the PromptStats model."""
    
    def test_prompt_stats_creation(self):
        """Test basic PromptStats creation."""
        stats = PromptStats(
            model_name="gemini-1.5-flash",
            max_output_tokens=1000,
            temperature=0.7,
            top_p=0.9,
            prompt_length=500,
            prompt_tokens=100,
            response_length=200,
            response_tokens=50,
            elapsed_time=2.5
        )
        assert stats.model_name == "gemini-1.5-flash"
        assert stats.max_output_tokens == 1000
        assert stats.temperature == 0.7
        assert stats.top_p == 0.9
        assert stats.prompt_length == 500
        assert stats.prompt_tokens == 100
        assert stats.response_length == 200
        assert stats.response_tokens == 50
        assert stats.elapsed_time == 2.5
        assert stats.has_image is False
        assert stats.has_binary_data is False
    
    def test_prompt_stats_with_media(self):
        """Test PromptStats with media flags."""
        stats = PromptStats(
            model_name="gemini-1.5-flash",
            max_output_tokens=1000,
            temperature=0.7,
            top_p=0.9,
            prompt_length=500,
            prompt_tokens=100,
            response_length=200,
            response_tokens=50,
            elapsed_time=2.5,
            has_image=True,
            has_binary_data=True
        )
        assert stats.has_image is True
        assert stats.has_binary_data is True


class TestStandardPromptAdapter(unittest.TestCase):
    """Test the StandardPromptAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_settings_patcher = patch.multiple(
            'adapters.llm.settings',
            LLM_MODEL_DEFAULT='gemini-1.5-flash',
            LLM_MAX_OUTPUT_TOKENS_DEFAULT=1000,
            LLM_TEMPERATURE_DEFAULT=0.7,
            LLM_TOP_P_DEFAULT=0.9,
            LLM_API_VERSION='v1',
            GCP_PROJECT_ID='test-project',
            GCP_LOCATION_3='us-central1',
            STAGE='test',
            SERVICE='entity-extraction'
        )
        self.mock_settings = self.mock_settings_patcher.start()
    
    def tearDown(self):
        """Clean up patches."""
        self.mock_settings_patcher.stop()
    
    @patch('adapters.llm.genai.Client')
    def test_init_default_parameters(self, mock_client_class):
        """Test initialization with default parameters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        adapter = StandardPromptAdapter()
        
        assert adapter.model_name == 'gemini-1.5-flash-002'
        assert adapter.max_tokens == 8192
        assert adapter.temperature == 0.0
        assert adapter.top_p == 0.95
        assert adapter.response_mime_type == DEFAULT_RESPONSE_MIME_TYPE
        assert adapter.safety_settings_dict == DEFAULT_SAFETY_SETTINGS
        assert adapter.client == mock_client
        
        # Verify client was initialized correctly
        mock_client_class.assert_called_once()
        args, kwargs = mock_client_class.call_args
        assert kwargs['vertexai'] is True
        assert kwargs['project'] == 'test-project'
        assert kwargs['location'] == 'us-central1'
    
    @patch('adapters.llm.genai.Client')
    def test_init_custom_parameters(self, mock_client_class):
        """Test initialization with custom parameters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        custom_safety = {"HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH"}
        custom_labels = {"environment": "prod"}
        
        adapter = StandardPromptAdapter(
            model_name='gemini-1.5-pro',
            max_tokens=2000,
            temperature=0.5,
            top_p=0.8,
            safety_settings=custom_safety,
            response_mime_type='text/plain',
            default_labels=custom_labels
        )
        
        assert adapter.model_name == 'gemini-1.5-pro'
        assert adapter.max_tokens == 2000
        assert adapter.temperature == 0.5
        assert adapter.top_p == 0.8
        assert adapter.response_mime_type == 'text/plain'
        assert adapter.default_labels == custom_labels
        
        # Check that safety settings were merged with defaults
        expected_safety = DEFAULT_SAFETY_SETTINGS.copy()
        expected_safety.update(custom_safety)
        assert adapter.safety_settings_dict == expected_safety
    
    @patch('adapters.llm.genai.Client')
    def test_dict_to_safety_settings(self, mock_client_class):
        """Test conversion of safety settings dictionary to SafetySetting objects."""
        mock_client_class.return_value = Mock()
        
        adapter = StandardPromptAdapter()
        
        safety_dict = {
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_LOW_AND_ABOVE"
        }
        
        result = adapter._dict_to_safety_settings(safety_dict)
        
        assert len(result) == 2
        # Check that we get SafetySetting objects with correct categories and thresholds
        categories = [setting.category.name for setting in result]
        thresholds = [setting.threshold.name for setting in result]
        assert "HARM_CATEGORY_HATE_SPEECH" in categories
        assert "HARM_CATEGORY_DANGEROUS_CONTENT" in categories
        assert "BLOCK_NONE" in thresholds
        assert "BLOCK_LOW_AND_ABOVE" in thresholds
            
    
    def test_extract_json_from_response_plain_json(self):
        """Test extracting JSON from plain JSON response."""
        response_text = '{"key": "value", "number": 42}'
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        expected = {"key": "value", "number": 42}
        assert result == expected
    
    def test_extract_json_from_response_markdown_wrapped(self):
        """Test extracting JSON from markdown-wrapped response."""
        response_text = '''```json
{"key": "value", "number": 42}
```'''
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        expected = {"key": "value", "number": 42}
        assert result == expected
    
    def test_extract_json_from_response_no_json_block(self):
        """Test extracting JSON when no JSON block is present."""
        response_text = '{"key": "value"}'
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        expected = {"key": "value"}
        assert result == expected
    
    def test_extract_json_from_response_empty_result(self):
        """Test extracting JSON when result is empty."""
        response_text = '{}'
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        assert result == {}
    
    def test_extract_json_from_response_invalid_json(self):
        """Test extracting JSON from invalid JSON string."""
        response_text = '{"key": invalid json}'
        with pytest.raises(ValueError, match="Failed to parse JSON.*Expecting value"):
            StandardPromptAdapter.extract_json_from_response(response_text)

    def test_extract_json_from_response_nested_markdown(self):
        """Test extracting JSON from markdown with extra text."""
        response_text = '''```json
{"nested": "value"}
```
Some additional text'''
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        expected = {"nested": "value"}
        assert result == expected

    def test_extract_json_from_response_multiple_json_blocks(self):
        """Test extracting JSON when multiple blocks exist (should use first)."""
        response_text = '''```json
{"first": "block"}
```
Some text
```json
{"second": "block"}
```'''
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        expected = {"first": "block"}
        assert result == expected

    def test_extract_json_from_response_malformed_markdown(self):
        """Test extracting JSON from malformed markdown."""
        response_text = '''```json
{"key": "value"
```'''
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            StandardPromptAdapter.extract_json_from_response(response_text)

    def test_extract_json_from_response_empty_string(self):
        """Test extracting JSON from empty string."""
        result = StandardPromptAdapter.extract_json_from_response("")
        assert result is None

    def test_extract_json_from_response_whitespace_only(self):
        """Test extracting JSON from whitespace-only string."""
        result = StandardPromptAdapter.extract_json_from_response("   \n\t   ")
        assert result is None

    def test_dict_to_safety_settings_empty_dict(self):
        """Test converting empty safety settings dict."""
        adapter = StandardPromptAdapter("test-model")
        result = adapter._dict_to_safety_settings({})
        assert result == []

    def test_dict_to_safety_settings_invalid_category(self):
        """Test converting safety settings with invalid category."""
        adapter = StandardPromptAdapter("test-model")
        safety_dict = {"INVALID_CATEGORY": "BLOCK_NONE"}

        # Should create SafetySetting objects even with invalid values
        result = adapter._dict_to_safety_settings(safety_dict)
        assert len(result) == 1
        assert result[0].category.name == "INVALID_CATEGORY"
        assert result[0].threshold.name == "BLOCK_NONE"

    def test_dict_to_safety_settings_invalid_threshold(self):
        """Test converting safety settings with invalid threshold."""
        adapter = StandardPromptAdapter("test-model")
        safety_dict = {"HARM_CATEGORY_HATE_SPEECH": "INVALID_THRESHOLD"}

        # Should create SafetySetting objects even with invalid values
        result = adapter._dict_to_safety_settings(safety_dict)
        assert len(result) == 1
        assert result[0].category.name == "HARM_CATEGORY_HATE_SPEECH"
        assert result[0].threshold.name == "INVALID_THRESHOLD"

    def test_adapter_initialization_with_custom_params(self):
        """Test adapter initialization with all custom parameters."""
        adapter = StandardPromptAdapter(
            model_name="custom-model",
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
            response_mime_type="application/json"
        )

        assert adapter.model_name == "custom-model"
        assert adapter.max_tokens == 2048
        assert adapter.temperature == 0.7
        assert adapter.top_p == 0.9
        assert adapter.response_mime_type == "application/json"

    def test_adapter_parameter_storage(self):
        """Test that adapter properly stores initialization parameters."""
        adapter = StandardPromptAdapter(
            "test-model",
            max_tokens=1024,
            temperature=0.8,
            top_p=0.95
        )

        # Test that parameters are stored correctly
        assert adapter.model_name == "test-model"
        assert adapter.max_tokens == 1024
        assert adapter.temperature == 0.8
        assert adapter.top_p == 0.95

    @patch('adapters.llm.vertexai.init')
    @patch('adapters.llm.GenerativeModel')
    async def test_generate_content_with_safety_settings(self, mock_model_class, mock_init):
        """Test generate_content with custom safety settings."""
        # Mock the model and response
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_response.usage_metadata.prompt_token_count = 15
        mock_response.usage_metadata.candidates_token_count = 10
        mock_model.generate_content_async.return_value = mock_response
        mock_model_class.return_value = mock_model

        adapter = StandardPromptAdapter("test-model")

        # Test with safety settings
        safety_settings = {
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE"
        }

        result = await adapter.generate_content(
            prompt="Test prompt",
            app_id="test-app",
            safety_settings=safety_settings
        )

        assert result.text == "Generated response"
        assert result.prompt_tokens == 15
        assert result.completion_tokens == 10

    @patch('adapters.llm.vertexai.init')
    @patch('adapters.llm.GenerativeModel')
    async def test_generate_content_with_metadata_logging(self, mock_model_class, mock_init):
        """Test generate_content with metadata for logging."""
        # Mock the model and response
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Response with metadata"
        mock_response.usage_metadata.prompt_token_count = 20
        mock_response.usage_metadata.candidates_token_count = 15
        mock_model.generate_content_async.return_value = mock_response
        mock_model_class.return_value = mock_model

        adapter = StandardPromptAdapter("test-model")

        metadata = {
            "business_unit": "test-bu",
            "solution_id": "test-solution",
            "tenant_id": "test-tenant"
        }

        result = await adapter.generate_content(
            prompt="Test prompt",
            app_id="test-app",
            metadata=metadata
        )

        assert result.text == "Response with metadata"
        # Verify the model was called with expected parameters
        mock_model.generate_content_async.assert_called_once()

    @patch('adapters.llm.vertexai.init')
    @patch('adapters.llm.GenerativeModel')
    async def test_generate_content_exception_handling(self, mock_model_class, mock_init):
        """Test generate_content exception handling."""
        # Mock the model to raise an exception
        mock_model = AsyncMock()
        mock_model.generate_content_async.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        adapter = StandardPromptAdapter("test-model")

        with pytest.raises(Exception, match="API Error"):
            await adapter.generate_content(
                prompt="Test prompt",
                app_id="test-app"
            )
        result = StandardPromptAdapter.extract_json_from_response(response_text)
        assert result is None
    
    def test_extract_json_from_response_none_input(self):
        """Test extracting JSON from None input."""
        with pytest.raises(ValueError, match="Failed to parse JSON.*'NoneType' object has no attribute 'startswith'"):
            StandardPromptAdapter.extract_json_from_response(None)


class TestDefaultValues(unittest.TestCase):
    """Test default values and constants."""
    
    def test_default_safety_settings(self):
        """Test default safety settings structure."""
        expected_keys = {
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_DANGEROUS_CONTENT", 
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_HARASSMENT"
        }
        assert set(DEFAULT_SAFETY_SETTINGS.keys()) == expected_keys
        
        # All should be set to BLOCK_NONE
        for value in DEFAULT_SAFETY_SETTINGS.values():
            assert value == "BLOCK_NONE"
    
    def test_default_response_mime_type(self):
        """Test default response MIME type."""
        assert DEFAULT_RESPONSE_MIME_TYPE == "application/json"


if __name__ == '__main__':
    unittest.main()