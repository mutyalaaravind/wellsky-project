"""
Unit tests for entityschemas.py module.
"""

import pytest
from src.entityschemas import SCHEMAS


def test_schemas_structure():
    """Test that SCHEMAS is properly structured."""
    assert isinstance(SCHEMAS, dict)
    assert len(SCHEMAS) > 0


def test_insurance_data_schema_exists():
    """Test that insurance_data schema exists and has correct structure."""
    assert "insurance_data" in SCHEMAS
    schema = SCHEMAS["insurance_data"]
    
    # Check required fields
    assert "description" in schema
    assert "type" in schema
    assert "additionalProperties" in schema
    assert "title" in schema
    assert "properties" in schema
    assert "required" in schema
    
    # Check values
    assert schema["description"] == "A insurance data schema"
    assert schema["type"] == "OBJECT"
    assert schema["additionalProperties"] is False
    assert schema["title"] == "Insurance Data Schema"
    assert isinstance(schema["properties"], dict)
    assert isinstance(schema["required"], list)


def test_insurance_data_properties():
    """Test the properties of insurance_data schema."""
    properties = SCHEMAS["insurance_data"]["properties"]
    
    # Check all expected properties exist
    expected_properties = [
        "memberId", "metadata", "memberName", "providerName", 
        "planName", "groupNumber", "employerName"
    ]
    
    for prop in expected_properties:
        assert prop in properties
        assert "description" in properties[prop]
        assert "type" in properties[prop]
    
    # Check specific property types
    assert properties["memberId"]["type"] == "STRING"
    assert properties["metadata"]["type"] == "OBJECT"
    assert properties["metadata"]["additionalProperties"] is True
    assert properties["memberName"]["type"] == "STRING"
    assert properties["providerName"]["type"] == "STRING"
    assert properties["planName"]["type"] == "STRING"
    assert properties["groupNumber"]["type"] == "STRING"
    assert properties["employerName"]["type"] == "STRING"
    
    # Check employerName has maxLength
    assert "maxLength" in properties["employerName"]
    assert properties["employerName"]["maxLength"] == 100


def test_required_fields():
    """Test that required fields list is empty as expected."""
    required = SCHEMAS["insurance_data"]["required"]
    assert required == []


def test_schema_immutability():
    """Test that we can access schema data multiple times consistently."""
    schema1 = SCHEMAS["insurance_data"]
    schema2 = SCHEMAS["insurance_data"]
    
    assert schema1 is schema2
    assert schema1["type"] == schema2["type"]
    assert len(schema1["properties"]) == len(schema2["properties"])