import json
from base64 import b64encode
from datetime import datetime, timedelta
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from adapters.llm import StandardPromptAdapter, PromptStats
from vertexai.generative_models import GenerativeModel, Part

@pytest.fixture
def mock_dependencies():
    with patch('adapters.llm.vertexai.init') as mock_vertex_init, \
         patch('adapters.llm.aiplatform.init') as mock_aiplatform_init, \
         patch('adapters.llm.StorageAdapter') as mock_storage_adapter, \
         patch('adapters.llm.CloudTaskAdapter') as mock_cloud_task_adapter, \
         patch('adapters.llm.GooglePubSubAdapter') as mock_pubsub_adapter:
        
        # Setup storage mock
        mock_storage = MagicMock()
        mock_storage.get_base_path = AsyncMock()
        mock_storage.write_text = AsyncMock()
        mock_storage_adapter.return_value = mock_storage

        # Setup cloud task mock
        mock_cloud_task = MagicMock()
        mock_cloud_task.create_task = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_cloud_task

        # Setup pubsub mock
        mock_pubsub = MagicMock()
        mock_pubsub.publish = AsyncMock()
        mock_pubsub_adapter.return_value = mock_pubsub

        yield {
            'vertex_init': mock_vertex_init,
            'aiplatform_init': mock_aiplatform_init,
            'storage': mock_storage,
            'cloud_task': mock_cloud_task,
            'pubsub': mock_pubsub
        }

@pytest.fixture
def standard_prompt_adapter(mock_dependencies):
    adapter = StandardPromptAdapter(
        project_id="test-project",
        location="test-location",
        max_tokens=100,
        temperature=0.1,
        top_p=0.95
    )
    # No need to assert vertex_init or aiplatform_init as they're not used directly
    return adapter

@pytest.fixture
def sample_text_input():
    return ["Test prompt"]

@pytest.fixture
def sample_uri_input():
    return [("gs://test-bucket/test.pdf", "application/pdf")]

@pytest.fixture
def sample_binary_input():
    return [(b"test binary data", "application/pdf")]

@pytest.fixture
def mock_response():
    return "Test response"

# @pytest.mark.asyncio
# async def test_uri_input_prediction(standard_prompt_adapter, sample_uri_input, mock_response, mock_dependencies):
#     # Arrange
#     with patch('adapters.llm.GenerativeModel') as mock_model_class, \
#          patch('adapters.llm.Part') as mock_part:
#         mock_model = MagicMock()
#         mock_model_class.return_value = mock_model
        
#         # Mock Part.from_uri
#         mock_uri_part = MagicMock()
#         mock_part.from_uri.return_value = mock_uri_part
        
#         mock_stream = MagicMock()
#         mock_stream.text = mock_response
#         mock_model.generate_content_async.return_value.__aiter__.return_value = [mock_stream]
        
#         mock_token_count = MagicMock()
#         mock_token_count.total_tokens = 10
#         mock_token_count.total_billable_characters = 100
#         mock_model.count_tokens.return_value = mock_token_count

#         # Act
#         result = await standard_prompt_adapter.multi_modal_predict_2(
#             items=sample_uri_input,
#             model="test-model"
#         )

#         # Assert
#         assert result == mock_response
#         mock_part.from_uri.assert_called_once_with(
#             uri="gs://test-bucket/test.pdf",
#             mime_type="application/pdf"
#         )
#         mock_model.generate_content_async.assert_called_once_with(
#             [mock_uri_part],
#             generation_config={
#                 'max_output_tokens': 100,
#                 'temperature': 0.1,
#                 'top_p': 0.95
#             },
#             safety_settings=mock_model_class.call_args[1]['safety_settings'],
#             stream=True
#         )

# @pytest.mark.asyncio
# async def test_binary_input_prediction(standard_prompt_adapter, sample_binary_input, mock_response, mock_dependencies):
#     # Arrange
#     with patch('adapters.llm.GenerativeModel') as mock_model_class, \
#          patch('adapters.llm.Part') as mock_part:
#         mock_model = MagicMock()
#         mock_model_class.return_value = mock_model
        
#         # Mock Part.from_data
#         mock_data_part = MagicMock()
#         mock_part.from_data.return_value = mock_data_part
        
#         mock_stream = MagicMock()
#         mock_stream.text = mock_response
#         mock_model.generate_content_async.return_value.__aiter__.return_value = [mock_stream]
        
#         mock_token_count = MagicMock()
#         mock_token_count.total_tokens = 10
#         mock_token_count.total_billable_characters = 100
#         mock_model.count_tokens.return_value = mock_token_count

#         # Act
#         result = await standard_prompt_adapter.multi_modal_predict_2(
#             items=sample_binary_input,
#             model="test-model"
#         )

#         # Assert
#         assert result == mock_response
#         mock_part.from_data.assert_called_once_with(
#             data=b"test binary data",
#             mime_type="application/pdf"
#         )

# @pytest.mark.asyncio
# async def test_error_handling(standard_prompt_adapter, sample_text_input, mock_dependencies):
#     # Arrange
#     with patch('adapters.llm.GenerativeModel') as mock_model_class:
#         mock_model = MagicMock()
#         mock_model_class.return_value = mock_model
        
#         test_error = Exception("Test error")
#         mock_model.generate_content_async.side_effect = test_error
        
#         mock_token_count = MagicMock()
#         mock_token_count.total_tokens = 10
#         mock_token_count.total_billable_characters = 100
#         mock_model.count_tokens.return_value = mock_token_count

#         # Act & Assert
#         with pytest.raises(Exception) as exc_info:
#             await standard_prompt_adapter.multi_modal_predict_2(
#                 items=sample_text_input,
#                 model="test-model"
#             )
#         assert str(exc_info.value) == "Test error"
        
#         # Verify audit_prompt was called with error
#         mock_dependencies['storage'].write_text.assert_not_called()  # Since it's commented out in the code

# @pytest.mark.asyncio
# async def test_load_test_emulator(standard_prompt_adapter, sample_text_input, mock_dependencies):
#     # Arrange
#     with patch('adapters.llm.STAGE', 'dev'), \
#          patch('adapters.llm.LOADTEST_LLM_EMULATOR_ENABLED', True), \
#          patch('adapters.llm.DummyPromptAdapter') as mock_dummy_adapter, \
#          patch('adapters.llm.Part') as mock_part:
        
#         mock_dummy = MagicMock()
#         mock_dummy.multi_modal_predict_2 = AsyncMock(return_value="Dummy response")
#         mock_dummy_adapter.return_value = mock_dummy

#         # Act
#         result = await standard_prompt_adapter.multi_modal_predict_2(
#             items=sample_text_input,
#             model="test-model"
#         )

#         # Assert
#         assert result == "Dummy response"
#         mock_dummy.multi_modal_predict_2.assert_called_once_with(
#             sample_text_input,
#             "test-model",
#             [],  # system_prompts
#             None,  # response_mime_type
#             None,  # metadata
#         )

# @pytest.mark.asyncio
# async def test_prompt_stats_calculation(standard_prompt_adapter, sample_text_input, mock_response, mock_dependencies):
#     # Arrange
#     with patch('adapters.llm.GenerativeModel') as mock_model_class, \
#          patch('adapters.llm.BurndownCalculator') as mock_burndown, \
#          patch('adapters.llm.Part') as mock_part:
        
#         mock_model = MagicMock()
#         mock_model_class.return_value = mock_model
        
#         mock_stream = MagicMock()
#         mock_stream.text = mock_response
#         mock_model.generate_content_async.return_value.__aiter__.return_value = [mock_stream]
        
#         mock_token_count = MagicMock()
#         mock_token_count.total_tokens = 10
#         mock_token_count.total_billable_characters = 100
#         mock_model.count_tokens.return_value = mock_token_count

#         mock_burndown.calculate_burndown.return_value = 1000

#         # Act
#         await standard_prompt_adapter.multi_modal_predict_2(
#             items=sample_text_input,
#             model="test-model",
#             metadata={"test": "metadata"}
#         )

#         # Assert
#         mock_burndown.calculate_burndown.assert_called_once_with(
#             "test-model",
#             sample_text_input,
#             mock_response
#         )