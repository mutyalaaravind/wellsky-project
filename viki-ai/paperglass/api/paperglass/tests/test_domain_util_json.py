import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest 
import json
from paperglass.domain.util_json import convertToJson, safe_loads



def test_convertToJson_unwrapped():
    json_str = '{"key": "value"}'
    expected = {"key": "value"}
    result = convertToJson(json_str)
    assert result == expected

def test_convertToJson_wrapped():
    json_str = "```json\n{\"key\": \"value\"}\n```"
    expected = {"key": "value"}
    result = convertToJson(json_str)
    assert result == expected

def test_safe_loads_unwrapped():
    json_str = '{"key": "value"}'
    expected = {"key": "value"}
    result = safe_loads(json_str)
    assert result == expected

def test_safe_loads_wrapped():
    json_str = "```json\n{\"key\": \"value\"}\n```"
    expected = {"key": "value"}
    result = safe_loads(json_str)
    assert result == expected

def test_safe_loads_with_cleaner():
    json_str = '{"key": "va\\lue"}'
    expected = {"key": "va\\lue"}
    # Assuming JSON_CLEANERS is defined in util_json.py
    # and contains a cleaner that matches and replaces something in json_str
    result = safe_loads(json_str, index=0)
    assert result == expected

def test_safe_loads_invalid_json():
    json_str = '{"key": "value"'

    result = safe_loads(json_str)
    assert result is None

def test_safe_loads_invalid_index():
    json_str = '{"key": "value"}'
    result = safe_loads(json_str, index=999)  # Assuming 999 is out of range for JSON_CLEANERS
    assert result is None

if __name__ == "__main__":
    pytest.main()