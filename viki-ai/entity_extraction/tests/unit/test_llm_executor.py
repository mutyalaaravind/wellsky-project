import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import json

# Import and setup test environment first
from tests.test_env import setup_test_env
setup_test_env()

# Now import modules that depend on environment variables
from src.usecases.llm_executor import (
    _uppercase_types_for_vertex_ai,
    _uppercase_property_types,
    _remove_extension_fields,
    LlmExecutionService,
    execute_llm_request
)
from src.contracts.llm import LlmExecuteRequest, LlmExecuteResponse, ModelParameters

# Test cases for _uppercase_types_for_vertex_ai
def test_uppercase_types_basic():
    """Test basic type uppercasing."""
    input_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        }
    }
    expected = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"},
            "age": {"type": "INTEGER"}
        }
    }
    result = _uppercase_types_for_vertex_ai(input_schema)
    assert result == expected

def test_uppercase_types_nested():
    """Test nested object type uppercasing."""
    input_schema = {
        "type": "object",
        "properties": {
            "person": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            }
        }
    }
    expected = {
        "type": "OBJECT",
        "properties": {
            "person": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "age": {"type": "INTEGER"}
                }
            }
        }
    }
    result = _uppercase_types_for_vertex_ai(input_schema)
    assert result == expected

def test_uppercase_types_array():
    """Test array type uppercasing."""
    input_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }
    expected = {
        "type": "OBJECT",
        "properties": {
            "items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING"}
                    }
                }
            }
        }
    }
    result = _uppercase_types_for_vertex_ai(input_schema)
    assert result == expected

def test_uppercase_types_remove_meta_schema():
    """Test removal of JSON Schema meta fields."""
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "test",
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    expected = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"}
        }
    }
    result = _uppercase_types_for_vertex_ai(input_schema)
    assert result == expected

def test_remove_extension_fields_basic():
    """Test removal of x-* extension fields at root level."""
    input_schema = {
        "type": "object",
        "x-schema-id": "test-schema",
        "x-app-id": "test-app",
        "x-label": "Test Label",
        "properties": {
            "name": {"type": "string"}
        }
    }
    expected = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    result = _remove_extension_fields(input_schema)
    assert result == expected
    # Verify original extension fields are not in result
    assert "x-schema-id" not in result
    assert "x-app-id" not in result
    assert "x-label" not in result

def test_remove_extension_fields_nested():
    """Test removal of x-* extension fields in nested objects."""
    input_schema = {
        "type": "object",
        "x-schema-id": "test-schema",
        "properties": {
            "person": {
                "type": "object",
                "x-custom-field": "should be removed",
                "properties": {
                    "name": {
                        "type": "string",
                        "x-validation": "custom"
                    }
                }
            }
        }
    }
    result = _remove_extension_fields(input_schema)

    # Check root level
    assert "x-schema-id" not in result
    assert "type" in result

    # Check nested person object
    assert "x-custom-field" not in result["properties"]["person"]
    assert "type" in result["properties"]["person"]

    # Check deeply nested name field
    assert "x-validation" not in result["properties"]["person"]["properties"]["name"]
    assert "type" in result["properties"]["person"]["properties"]["name"]

def test_remove_extension_fields_in_arrays():
    """Test removal of x-* extension fields in array items."""
    input_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "x-array-metadata": "should be removed",
                "items": {
                    "type": "object",
                    "x-item-metadata": "also removed",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }
    result = _remove_extension_fields(input_schema)

    # Check that array-level x-* field is removed
    assert "x-array-metadata" not in result["properties"]["items"]

    # Check that item-level x-* field is removed
    assert "x-item-metadata" not in result["properties"]["items"]["items"]

    # Verify structure is preserved
    assert result["properties"]["items"]["type"] == "array"
    assert result["properties"]["items"]["items"]["type"] == "object"

def test_uppercase_types_with_extension_fields():
    """Test that _uppercase_types_for_vertex_ai removes both meta-schema and extension fields."""
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "test",
        "x-schema-id": "data-rights-3",
        "x-app-id": "test-app",
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "x-required-scopes": {"extract": True}
            }
        }
    }
    expected = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"}
        }
    }
    result = _uppercase_types_for_vertex_ai(input_schema)

    # Verify all unwanted fields are removed
    assert "$schema" not in result
    assert "$id" not in result
    assert "x-schema-id" not in result
    assert "x-app-id" not in result

    # Verify nested x-* fields are removed
    assert "x-required-scopes" not in result["properties"]["name"]

    # Verify types are uppercased
    assert result["type"] == "OBJECT"
    assert result["properties"]["name"]["type"] == "STRING"

def test_uppercase_property_types():
    """Test _uppercase_property_types function directly."""
    properties = {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "numbers": {
                    "type": "array",
                    "items": {"type": "integer"}
                }
            }
        }
    }
    
    result = _uppercase_property_types(properties)
    
    assert result["name"]["type"] == "STRING"
    assert result["age"]["type"] == "INTEGER"
    assert result["address"]["type"] == "OBJECT"
    assert result["address"]["properties"]["street"]["type"] == "STRING"
    assert result["address"]["properties"]["numbers"]["type"] == "ARRAY"
    assert result["address"]["properties"]["numbers"]["items"]["type"] == "INTEGER"

@pytest.fixture
def llm_service():
    """Fixture for LLM execution service."""
    return LlmExecutionService()

def test_determine_mime_type(llm_service):
    """Test MIME type determination for various file types."""
    test_cases = [
        ("gs://bucket/doc.pdf", "application/pdf"),
        ("gs://bucket/image.jpg", "image/jpeg"),
        ("gs://bucket/image.jpeg", "image/jpeg"),
        ("gs://bucket/image.png", "image/png"),
        ("gs://bucket/doc.txt", "text/plain"),
        ("gs://bucket/doc.doc", "application/msword"),
        ("gs://bucket/doc.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("gs://bucket/unknown.xyz", "application/pdf"),  # Default case
    ]
    
    for uri, expected_mime in test_cases:
        assert llm_service._determine_mime_type(uri) == expected_mime

@pytest.mark.asyncio
async def test_llm_execute_success():
    """Test successful LLM execution."""
    # Create mock LLM response
    mock_response_text = '{"result": "success"}'
    mock_llm_response = Mock()
    mock_llm_response.text = mock_response_text
    mock_llm_response.usage_metadata = Mock(
        model_dump=Mock(return_value={"tokens": 100})
    )

    # Create mock adapter with async response
    mock_adapter = AsyncMock()
    async def async_return(*args, **kwargs):
        return mock_llm_response
    mock_adapter.generate_content_async.side_effect = async_return
    mock_adapter.extract_json_from_response = Mock(return_value={"result": "success"})
    
    with patch('src.usecases.llm_executor.StandardPromptAdapter', return_value=mock_adapter):
        service = LlmExecutionService()
        
        request = LlmExecuteRequest(
            gs_uri="gs://bucket/test.pdf",
            prompt="test prompt",
            system_instructions="system instructions",
            json_schema={"type": "object", "properties": {"result": {"type": "string"}}},
            metadata={"test": "metadata"}
        )
        
        response = await service.execute_llm_request(request)
        
        # Check basic response fields
        assert response.success is True
        assert response.content == {"result": "success"}
        assert response.raw_response == mock_response_text
        
        # Verify metadata
        assert response.execution_metadata["json_parsing_success"] is True
        assert "json_parsing_error" not in response.execution_metadata
        assert response.execution_metadata["response_length"] == len(mock_response_text)
        assert "execution_time_ms" in response.execution_metadata
        assert "tokens" in response.execution_metadata["usage_metadata"]
        assert response.execution_metadata["usage_metadata"]["tokens"] == 100

@pytest.mark.asyncio
async def test_llm_execute_with_model_parameters():
    """Test LLM execution with custom model parameters."""
    from src.contracts.llm import ModelParameters
    
    # Create mock LLM response
    mock_response = Mock()
    mock_response.text = '{"result": "success"}'
    mock_response.usage_metadata = Mock(
        model_dump=Mock(return_value={"tokens": 100})
    )
    
    # Create mock adapter with async response
    mock_adapter = AsyncMock()
    async def async_return(*args, **kwargs):
        return mock_response
    mock_adapter.generate_content_async.side_effect = async_return
    mock_adapter.extract_json_from_response = Mock(return_value={"result": "success"})
    
    with patch('src.usecases.llm_executor.StandardPromptAdapter', return_value=mock_adapter) as mock_adapter_class:
        service = LlmExecutionService()
        
        request = LlmExecuteRequest(
            gs_uri="gs://bucket/test.pdf",
            prompt="test prompt",
            model_parameters=ModelParameters(
                model_name="test-model",
                max_output_tokens=100,
                temperature=0.7,
                top_p=0.8
            )
        )
        
        await service.execute_llm_request(request)
        
        # Verify adapter was created with correct parameters
        mock_adapter_class.assert_called_once_with(
            model_name="test-model",
            max_tokens=100,
            temperature=0.7,
            top_p=0.8
        )

@pytest.mark.asyncio
async def test_llm_execute_json_parse_error():
    """Test LLM execution with JSON parsing error."""
    # Create mock response object
    mock_llm_response = Mock()
    mock_llm_response.text = 'invalid json'
    mock_llm_response.usage_metadata = Mock(
        model_dump=Mock(return_value={"tokens": 100})
    )

    # Create mock adapter with async response
    mock_adapter = AsyncMock()
    async def async_return(*args, **kwargs):
        return mock_llm_response
    mock_adapter.generate_content_async.side_effect = async_return
    mock_adapter.extract_json_from_response = Mock(
        side_effect=json.JSONDecodeError('Invalid JSON', 'invalid json', 0)
    )
    
    with patch('src.usecases.llm_executor.StandardPromptAdapter', return_value=mock_adapter):
        service = LlmExecutionService()
        
        request = LlmExecuteRequest(
            gs_uri="gs://bucket/test.pdf",
            prompt="test prompt"
        )
        
        response = await service.execute_llm_request(request)
        
        # Check basic response fields
        assert response.success is True  # Still successful since we got a response
        assert response.raw_response == 'invalid json'
        assert response.content is None  # No parsed content due to JSON error
        
        # Verify metadata
        assert response.execution_metadata["json_parsing_success"] is False
        assert "json_parsing_error" in response.execution_metadata
        assert isinstance(response.execution_metadata["json_parsing_error"], str)
        assert "Invalid JSON" in response.execution_metadata["json_parsing_error"]
        assert response.execution_metadata["response_length"] == len('invalid json')

@pytest.mark.asyncio
async def test_llm_execute_error():
    """Test LLM execution with error."""
    # Create mock adapter with error
    mock_adapter = AsyncMock()
    mock_adapter.generate_content_async.side_effect = Exception("LLM error")
    
    with patch('src.usecases.llm_executor.StandardPromptAdapter', return_value=mock_adapter):
        service = LlmExecutionService()
        
        request = LlmExecuteRequest(
            gs_uri="gs://bucket/test.pdf",
            prompt="test prompt"
        )
        
        response = await service.execute_llm_request(request)
        
        assert response.success == False
        assert "LLM error" in response.error_message
        assert "execution_time_ms" in response.execution_metadata
        assert "error" in response.execution_metadata
        assert "LLM error" in response.execution_metadata["error"]["message"]

@pytest.mark.asyncio
async def test_standalone_execute_function():
    """Test the standalone execute_llm_request function."""
    mock_response = LlmExecuteResponse(
        success=True,
        content={"result": "success"},
        raw_response='{"result": "success"}',
        execution_metadata={"test": "metadata"}
    )
    
    with patch('src.usecases.llm_executor.LlmExecutionService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.execute_llm_request.return_value = mock_response
        mock_service_class.return_value = mock_service
        
        request = LlmExecuteRequest(
            gs_uri="gs://bucket/test.pdf",
            prompt="test prompt"
        )
        
        response = await execute_llm_request(request)
        
        assert response == mock_response
        mock_service_class.assert_called_once()
        mock_service.execute_llm_request.assert_called_once_with(request)