import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from pydantic import BaseModel

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from util.json_utils import (
    convertToJson, safe_loads, JsonUtil, DateTimeEncoder
)


class SamplePydanticModel(BaseModel):
    """Sample Pydantic model for testing."""
    name: str
    value: int
    
    def dict(self, **kwargs):
        return {"name": self.name, "value": self.value}


class TestConvertToJson:
    """Test suite for convertToJson function."""

    def test_convertToJson_regular_json(self):
        """Test convertToJson with regular JSON string."""
        json_str = '{"key": "value", "number": 42}'
        result = convertToJson(json_str)
        expected = {"key": "value", "number": 42}
        assert result == expected

    def test_convertToJson_with_whitespace(self):
        """Test convertToJson with whitespace around JSON."""
        json_str = '  {"key": "value"}  '
        result = convertToJson(json_str)
        expected = {"key": "value"}
        assert result == expected

    def test_convertToJson_markdown_wrapped(self):
        """Test convertToJson with markdown JSON wrapper."""
        json_str = '```json\n{"key": "value", "array": [1, 2, 3]}\n```'
        result = convertToJson(json_str)
        expected = {"key": "value", "array": [1, 2, 3]}
        assert result == expected

    def test_convertToJson_markdown_wrapped_no_newlines(self):
        """Test convertToJson with markdown wrapper without newlines."""
        json_str = '```json{"key": "value"}```'
        result = convertToJson(json_str)
        expected = {"key": "value"}
        assert result == expected

    def test_convertToJson_complex_object(self):
        """Test convertToJson with complex JSON object."""
        json_str = '''```json
        {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "metadata": {
                "total": 2,
                "active": true
            }
        }
        ```'''
        result = convertToJson(json_str)
        expected = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "metadata": {
                "total": 2,
                "active": True
            }
        }
        assert result == expected

    def test_convertToJson_invalid_json(self):
        """Test convertToJson with invalid JSON raises exception."""
        json_str = '{"key": invalid}'
        with pytest.raises(json.JSONDecodeError):
            convertToJson(json_str)

    def test_convertToJson_markdown_invalid_json(self):
        """Test convertToJson with markdown wrapped invalid JSON."""
        json_str = '```json\n{"key": invalid}\n```'
        with pytest.raises(json.JSONDecodeError):
            convertToJson(json_str)


class TestSafeLoads:
    """Test suite for safe_loads function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock JSON_CLEANERS for testing
        self.mock_cleaners = [
            {"match": r'"([^"]*)":', "replace": r'"\1":'},  # Fix quotes
            {"match": r"'([^']*)':", "replace": r'"\1":'},  # Single to double quotes
            {"match": r",\s*}", "replace": "}"},           # Remove trailing commas
        ]

    def test_safe_loads_regular_json(self):
        """Test safe_loads with valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = safe_loads(json_str)
        expected = {"key": "value", "number": 42}
        assert result == expected

    def test_safe_loads_markdown_wrapped(self):
        """Test safe_loads with markdown JSON wrapper."""
        json_str = '```json\n{"key": "value"}\n```'
        result = safe_loads(json_str)
        expected = {"key": "value"}
        assert result == expected

    def test_safe_loads_markdown_wrapped_no_newlines(self):
        """Test safe_loads with markdown wrapper without newlines."""
        json_str = '```json{"test": true}```'
        result = safe_loads(json_str)
        expected = {"test": True}
        assert result == expected

    def test_safe_loads_invalid_json_returns_none(self):
        """Test safe_loads with invalid JSON that can't be fixed."""
        # Completely invalid JSON that cleaners can't fix
        json_str = "completely invalid json {{{{"
        
        # Should eventually return None after exhausting all cleaners
        result = safe_loads(json_str)
        assert result is None

    def test_safe_loads_with_index_parameter(self):
        """Test safe_loads with index parameter."""
        # Test with valid JSON and specific index
        json_str = '{"key": "value"}'
        result = safe_loads(json_str, index=0)
        expected = {"key": "value"}
        assert result == expected

    def test_safe_loads_with_high_index(self):
        """Test safe_loads with index beyond available cleaners."""
        # Request index beyond available cleaners should return None
        result = safe_loads('{"key": "value"}', index=999)
        assert result is None

    def test_safe_loads_empty_string(self):
        """Test safe_loads with empty string."""
        # Empty string actually returns None after trying all cleaners
        result = safe_loads("")
        assert result is None

    def test_safe_loads_none_input(self):
        """Test safe_loads with None input."""
        with pytest.raises(AttributeError):
            safe_loads(None)


class TestJsonUtil:
    """Test suite for JsonUtil class."""

    def test_dumps_basic_object(self):
        """Test JsonUtil.dumps with basic object."""
        obj = {"key": "value", "number": 42}
        result = JsonUtil.dumps(obj)
        expected = '{"key": "value", "number": 42}'
        assert result == expected

    def test_dumps_with_datetime(self):
        """Test JsonUtil.dumps with datetime object."""
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        obj = {"timestamp": dt, "message": "test"}
        result = JsonUtil.dumps(obj)
        
        # Should use DateTimeEncoder
        parsed = json.loads(result)
        assert parsed["timestamp"] == "2024-12-24T10:30:00+00:00"
        assert parsed["message"] == "test"

    def test_loads_basic_string(self):
        """Test JsonUtil.loads with basic JSON string."""
        json_str = '{"key": "value", "number": 42}'
        result = JsonUtil.loads(json_str)
        expected = {"key": "value", "number": 42}
        assert result == expected

    def test_loads_invalid_json(self):
        """Test JsonUtil.loads with invalid JSON."""
        json_str = '{"key": invalid}'
        with pytest.raises(json.JSONDecodeError):
            JsonUtil.loads(json_str)

    def test_clean_basic_object(self):
        """Test JsonUtil.clean with basic serializable object."""
        obj = {"key": "value", "number": 42, "bool": True}
        result = JsonUtil.clean(obj)
        expected = {"key": "value", "number": 42, "bool": True}
        assert result == expected

    def test_clean_none_object(self):
        """Test JsonUtil.clean with None object."""
        result = JsonUtil.clean(None)
        assert result is None

    def test_clean_empty_object(self):
        """Test JsonUtil.clean with empty object."""
        result = JsonUtil.clean({})
        assert result == {}

    def test_clean_with_datetime(self):
        """Test JsonUtil.clean with datetime objects."""
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        obj = {"timestamp": dt, "message": "test"}
        result = JsonUtil.clean(obj)
        
        # Should convert datetime to ISO string
        assert result["timestamp"] == "2024-12-24T10:30:00+00:00"
        assert result["message"] == "test"

    def test_clean_with_pydantic_model(self):
        """Test JsonUtil.clean with Pydantic model."""
        model = SamplePydanticModel(name="test", value=42)
        obj = {"model": model, "other": "data"}
        result = JsonUtil.clean(obj)
        
        # Pydantic models are filtered out as non-serializable
        expected = {"other": "data"}
        assert result == expected

    def test_clean_with_non_serializable_objects(self):
        """Test JsonUtil.clean removes non-serializable objects."""
        class NonSerializable:
            pass
        
        obj = {
            "good": "value",
            "bad": NonSerializable(),
            "nested": {
                "good": 42,
                "bad": NonSerializable()
            }
        }
        result = JsonUtil.clean(obj)
        
        # Non-serializable objects are filtered out completely
        expected = {"good": "value"}
        assert result == expected

    def test_clean_with_list_containing_non_serializable(self):
        """Test JsonUtil.clean with list containing non-serializable items."""
        class NonSerializable:
            pass
        
        obj = {
            "items": [
                "good",
                42,
                NonSerializable(),
                {"nested": "value"},
                NonSerializable()
            ]
        }
        result = JsonUtil.clean(obj)
        
        # Lists with non-serializable items are filtered out completely
        expected = {}
        assert result == expected

    def test_clean_nested_pydantic_models(self):
        """Test JsonUtil.clean with nested Pydantic models."""
        model1 = SamplePydanticModel(name="first", value=1)
        model2 = SamplePydanticModel(name="second", value=2)
        
        obj = {
            "models": [model1, model2],
            "single": model1
        }
        result = JsonUtil.clean(obj)
        
        # Pydantic models are filtered out completely
        expected = {}
        assert result == expected

    def test_clean_with_serializable_pydantic_model(self):
        """Test JsonUtil.clean with a Pydantic model that is serializable."""
        # Create a model that will pass the is_serializable check
        model = SamplePydanticModel(name="test", value=42)
        
        # Mock is_serializable to return True for our model to test the dict() call path
        with patch.object(JsonUtil, 'is_serializable') as mock_is_serializable:
            # Return True for the model itself and its dict content
            def mock_serializable(value):
                if isinstance(value, SamplePydanticModel):
                    return True
                if isinstance(value, dict):
                    return True
                if isinstance(value, str):
                    return True
                if isinstance(value, int):
                    return True
                return False
            
            mock_is_serializable.side_effect = mock_serializable
            
            obj = {"model": model}
            result = JsonUtil.clean(obj)
            
            # Should include the model's dict representation
            expected = {"model": {"name": "test", "value": 42}}
            assert result == expected

    def test_is_serializable_basic_types(self):
        """Test JsonUtil.is_serializable with basic types."""
        assert JsonUtil.is_serializable("string") is True
        assert JsonUtil.is_serializable(42) is True
        assert JsonUtil.is_serializable(3.14) is True
        assert JsonUtil.is_serializable(True) is True
        assert JsonUtil.is_serializable(None) is True
        assert JsonUtil.is_serializable([1, 2, 3]) is True
        assert JsonUtil.is_serializable({"key": "value"}) is True

    def test_is_serializable_datetime(self):
        """Test JsonUtil.is_serializable with datetime."""
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        assert JsonUtil.is_serializable(dt) is True

    def test_is_serializable_non_serializable(self):
        """Test JsonUtil.is_serializable with non-serializable objects."""
        class NonSerializable:
            pass
        
        assert JsonUtil.is_serializable(NonSerializable()) is False
        assert JsonUtil.is_serializable(lambda x: x) is False

    def test_is_serializable_complex_structures(self):
        """Test JsonUtil.is_serializable with complex structures."""
        # Serializable complex structure
        good_obj = {
            "list": [1, "two", {"three": 3}],
            "nested": {"deep": {"value": True}}
        }
        assert JsonUtil.is_serializable(good_obj) is True
        
        # Non-serializable complex structure
        class NonSerializable:
            pass
        
        bad_obj = {
            "good": "value",
            "bad": NonSerializable()
        }
        assert JsonUtil.is_serializable(bad_obj) is False


class TestDateTimeEncoder:
    """Test suite for DateTimeEncoder class."""

    def test_datetime_encoding(self):
        """Test DateTimeEncoder with datetime objects."""
        encoder = DateTimeEncoder()
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        
        result = encoder.default(dt)
        expected = "2024-12-24T10:30:00+00:00"
        assert result == expected

    def test_datetime_encoding_no_timezone(self):
        """Test DateTimeEncoder with datetime without timezone."""
        encoder = DateTimeEncoder()
        dt = datetime(2024, 12, 24, 10, 30, 0)
        
        result = encoder.default(dt)
        expected = "2024-12-24T10:30:00"
        assert result == expected

    def test_datetime_encoding_with_microseconds(self):
        """Test DateTimeEncoder with datetime including microseconds."""
        encoder = DateTimeEncoder()
        dt = datetime(2024, 12, 24, 10, 30, 0, 123456, tzinfo=timezone.utc)
        
        result = encoder.default(dt)
        expected = "2024-12-24T10:30:00.123456+00:00"
        assert result == expected

    def test_non_datetime_encoding(self):
        """Test DateTimeEncoder with non-datetime objects."""
        encoder = DateTimeEncoder()
        
        # Should raise TypeError for non-datetime objects
        with pytest.raises(TypeError):
            encoder.default("not a datetime")
        
        with pytest.raises(TypeError):
            encoder.default(42)
        
        with pytest.raises(TypeError):
            encoder.default({"key": "value"})

    def test_json_dumps_integration(self):
        """Test DateTimeEncoder integration with json.dumps."""
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        obj = {
            "timestamp": dt,
            "message": "test",
            "number": 42
        }
        
        result = json.dumps(obj, cls=DateTimeEncoder)
        parsed = json.loads(result)
        
        assert parsed["timestamp"] == "2024-12-24T10:30:00+00:00"
        assert parsed["message"] == "test"
        assert parsed["number"] == 42

    def test_multiple_datetime_objects(self):
        """Test DateTimeEncoder with multiple datetime objects."""
        dt1 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        
        obj = {
            "start": dt1,
            "end": dt2,
            "events": [
                {"time": dt1, "event": "start"},
                {"time": dt2, "event": "end"}
            ]
        }
        
        result = json.dumps(obj, cls=DateTimeEncoder)
        parsed = json.loads(result)
        
        assert parsed["start"] == "2024-01-01T00:00:00+00:00"
        assert parsed["end"] == "2024-12-31T23:59:59+00:00"
        assert parsed["events"][0]["time"] == "2024-01-01T00:00:00+00:00"
        assert parsed["events"][1]["time"] == "2024-12-31T23:59:59+00:00"


class TestIntegration:
    """Integration tests for json_utils module."""

    def test_convertToJson_with_datetime_content(self):
        """Test convertToJson with JSON containing datetime strings."""
        json_str = '''```json
        {
            "timestamp": "2024-12-24T10:30:00+00:00",
            "data": {"value": 42}
        }
        ```'''
        result = convertToJson(json_str)
        
        expected = {
            "timestamp": "2024-12-24T10:30:00+00:00",
            "data": {"value": 42}
        }
        assert result == expected

    def test_safe_loads_with_convertToJson_compatibility(self):
        """Test that safe_loads and convertToJson handle similar inputs."""
        json_str = '```json\n{"key": "value"}\n```'
        
        result1 = convertToJson(json_str)
        result2 = safe_loads(json_str)
        
        assert result1 == result2 == {"key": "value"}

    def test_JsonUtil_round_trip(self):
        """Test JsonUtil dumps and loads round trip."""
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        original = {
            "timestamp": dt,
            "data": {"nested": "value"},
            "list": [1, 2, 3]
        }
        
        # Dumps with datetime encoding
        json_str = JsonUtil.dumps(original)
        
        # Loads back (datetime becomes string)
        result = JsonUtil.loads(json_str)
        
        expected = {
            "timestamp": "2024-12-24T10:30:00+00:00",
            "data": {"nested": "value"},
            "list": [1, 2, 3]
        }
        assert result == expected

    def test_full_workflow_with_pydantic(self):
        """Test complete workflow with Pydantic models."""
        model = SamplePydanticModel(name="test", value=42)
        dt = datetime(2024, 12, 24, 10, 30, 0, tzinfo=timezone.utc)
        
        # Original object with mixed types
        original = {
            "model": model,
            "timestamp": dt,
            "data": "value"
        }
        
        # Clean and serialize
        cleaned = JsonUtil.clean(original)
        json_str = JsonUtil.dumps(cleaned)
        
        # Parse back
        result = JsonUtil.loads(json_str)
        
        # Pydantic model gets filtered out during cleaning
        expected = {
            "timestamp": "2024-12-24T10:30:00+00:00",
            "data": "value"
        }
        assert result == expected

class TestAdditionalJsonUtilCoverage:
    """Additional tests to improve JSON util coverage."""

    def test_safe_loads_with_whitespace(self):
        """Test safe_loads with whitespace around JSON."""
        result = safe_loads('  \n  {"key": "value"}  \n  ')
        expected = {"key": "value"}
        assert result == expected

    def test_safe_loads_with_numbers(self):
        """Test safe_loads with numeric values."""
        result = safe_loads('{"int": 42, "float": 3.14, "bool": true}')
        expected = {"int": 42, "float": 3.14, "bool": True}
        assert result == expected

    def test_safe_loads_with_arrays(self):
        """Test safe_loads with array values."""
        result = safe_loads('{"array": [1, 2, 3], "nested": [{"a": 1}]}')
        expected = {"array": [1, 2, 3], "nested": [{"a": 1}]}
        assert result == expected

    def test_json_util_dumps_none(self):
        """Test JsonUtil.dumps with None value."""
        result = JsonUtil.dumps(None)
        assert result == "null"

    def test_json_util_dumps_empty_dict(self):
        """Test JsonUtil.dumps with empty dictionary."""
        result = JsonUtil.dumps({})
        assert result == "{}"

    def test_json_util_dumps_empty_list(self):
        """Test JsonUtil.dumps with empty list."""
        result = JsonUtil.dumps([])
        assert result == "[]"

    def test_json_util_loads_null(self):
        """Test JsonUtil.loads with null string."""
        result = JsonUtil.loads("null")
        assert result is None

    def test_json_util_loads_boolean(self):
        """Test JsonUtil.loads with boolean values."""
        assert JsonUtil.loads("true") is True
        assert JsonUtil.loads("false") is False

    def test_json_util_loads_numbers(self):
        """Test JsonUtil.loads with numeric values."""
        assert JsonUtil.loads("42") == 42
        assert JsonUtil.loads("3.14") == 3.14
        assert JsonUtil.loads("-100") == -100

    def test_json_util_clean_with_bytes(self):
        """Test JsonUtil.clean with bytes objects."""
        data = {"bytes": b"hello", "text": "world"}
        result = JsonUtil.clean(data)
        # Bytes should be filtered out
        assert "bytes" not in result
        assert result["text"] == "world"

    def test_json_util_clean_with_complex_nesting(self):
        """Test JsonUtil.clean with deeply nested structures."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep",
                        "none_value": None
                    }
                }
            }
        }
        result = JsonUtil.clean(data)
        # Should preserve nested structure and clean None values
        assert result["level1"]["level2"]["level3"]["value"] == "deep"

    def test_json_util_clean_with_callable(self):
        """Test JsonUtil.clean with callable objects."""
        def test_function():
            return "test"

        data = {"function": test_function, "value": "keep"}
        result = JsonUtil.clean(data)
        # Function should be filtered out
        assert "function" not in result
        assert result["value"] == "keep"
