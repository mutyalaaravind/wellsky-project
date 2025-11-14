import json
import pytest
from datetime import datetime
from pydantic import BaseModel

from viki_shared.utils.json_utils import JsonUtil, DateTimeEncoder, convertToJson, safe_loads


class SampleModel(BaseModel):
    name: str
    value: int
    timestamp: datetime


def test_datetime_encoder():
    """Test DateTimeEncoder converts datetime to ISO format."""
    now = datetime.now()
    encoder = DateTimeEncoder()
    result = encoder.default(now)
    assert result == now.isoformat()


def test_json_util_dumps():
    """Test JsonUtil.dumps with datetime objects."""
    now = datetime.now()
    data = {"timestamp": now, "name": "test"}
    
    result = JsonUtil.dumps(data)
    parsed = json.loads(result)
    
    assert parsed["name"] == "test"
    assert parsed["timestamp"] == now.isoformat()


def test_json_util_loads():
    """Test JsonUtil.loads."""
    data = '{"name": "test", "value": 42}'
    result = JsonUtil.loads(data)
    
    assert result["name"] == "test"
    assert result["value"] == 42


def test_json_util_clean():
    """Test JsonUtil.clean with complex objects."""
    now = datetime.now()
    model = SampleModel(name="test", value=42, timestamp=now)
    data = {"model": model, "timestamp": now}
    
    result = JsonUtil.clean(data)
    
    assert result["model"]["name"] == "test"
    assert result["model"]["value"] == 42
    assert isinstance(result["timestamp"], str)


def test_json_util_is_serializable():
    """Test JsonUtil.is_serializable."""
    assert JsonUtil.is_serializable("string")
    assert JsonUtil.is_serializable(42)
    assert JsonUtil.is_serializable({"key": "value"})
    assert JsonUtil.is_serializable(datetime.now())
    
    # Non-serializable objects
    assert not JsonUtil.is_serializable(lambda x: x)


def test_convert_to_json():
    """Test convertToJson with code block formatting."""
    # Regular JSON
    regular_json = '{"key": "value"}'
    result = convertToJson(regular_json)
    assert result == {"key": "value"}
    
    # JSON in code blocks
    code_block_json = '```json\n{"key": "value"}\n```'
    result = convertToJson(code_block_json)
    assert result == {"key": "value"}


def test_safe_loads():
    """Test safe_loads with various input formats."""
    # Regular JSON
    result = safe_loads('{"key": "value"}')
    assert result == {"key": "value"}
    
    # JSON in code blocks
    result = safe_loads('```json\n{"key": "value"}\n```')
    assert result == {"key": "value"}
    
    # Invalid JSON should return None or handle gracefully
    cleaners = [{"match": r"'", "replace": '"'}]
    result = safe_loads("{'key': 'value'}", cleaners=cleaners)
    assert result == {"key": "value"}