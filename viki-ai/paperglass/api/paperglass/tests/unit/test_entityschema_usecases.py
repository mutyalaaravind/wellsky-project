"""
Unit tests for entity schema use case functions.
"""

import pytest
from paperglass.usecases.entityschema import (
    _apply_usecase_treatment,
    _uppercase_types_for_extraction,
    _uppercase_property_types,
    _remove_extension_fields,
)


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


def test_remove_extension_fields_with_list_of_objects():
    """Test that extension fields are removed from objects in lists."""
    input_schema = {
        "type": "object",
        "properties": {
            "items": [
                {"type": "string", "x-meta": "remove"},
                {"type": "number", "x-meta": "remove"}
            ]
        }
    }
    result = _remove_extension_fields(input_schema)

    # Check that all list items have x-* fields removed
    for item in result["properties"]["items"]:
        assert "x-meta" not in item
        assert "type" in item


def test_apply_usecase_treatment_extract():
    """Test that extract usecase removes extension fields, $id, and $schema."""
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "test-schema-id",
        "x-schema-id": "data-rights-3",
        "x-app-id": "test-app",
        "x-label": "Test Label",
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "x-required-scopes": {"extract": ["name"]}
            }
        }
    }

    result = _apply_usecase_treatment(input_schema, "extract")

    # Verify $id and $schema are removed
    assert "$id" not in result
    assert "$schema" not in result

    # Verify all x-* extension fields are removed
    assert "x-schema-id" not in result
    assert "x-app-id" not in result
    assert "x-label" not in result

    # Verify nested x-* fields are removed
    assert "x-required-scopes" not in result["properties"]["name"]

    # Verify types are uppercased
    assert result["type"] == "OBJECT"
    assert result["properties"]["name"]["type"] == "STRING"


def test_apply_usecase_treatment_publish():
    """Test that publish usecase doesn't modify the schema."""
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "x-schema-id": "data-rights-3",
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }

    result = _apply_usecase_treatment(input_schema, "publish")

    # For publish, everything should remain as-is
    assert result == input_schema
    assert "$schema" in result
    assert "x-schema-id" in result


def test_uppercase_types_for_extraction():
    """Test basic type uppercasing for extraction."""
    input_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"}
                }
            }
        }
    }

    result = _uppercase_types_for_extraction(input_schema)

    assert result["type"] == "OBJECT"
    assert result["properties"]["name"]["type"] == "STRING"
    assert result["properties"]["age"]["type"] == "INTEGER"
    assert result["properties"]["address"]["type"] == "OBJECT"
    assert result["properties"]["address"]["properties"]["street"]["type"] == "STRING"


def test_uppercase_property_types_with_arrays():
    """Test uppercase property types handles arrays correctly."""
    properties = {
        "tags": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "people": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        }
    }

    result = _uppercase_property_types(properties)

    assert result["tags"]["type"] == "ARRAY"
    assert result["tags"]["items"]["type"] == "STRING"
    assert result["people"]["type"] == "ARRAY"
    assert result["people"]["items"]["type"] == "OBJECT"
    assert result["people"]["items"]["properties"]["name"]["type"] == "STRING"


def test_extract_usecase_data_rights_schema():
    """Test the actual problematic schema from the error log."""
    # This is a simplified version of the schema that caused the error
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://example.com/schemas/data-rights-3.json",
        "x-schema-id": "data-rights-3",
        "x-app-id": "corp_other-22f297",
        "x-label": "Legal Document Extraction",
        "type": "object",
        "title": "Legal Document Extraction",
        "description": "A schema for extracting key information from a legal agreement",
        "required": ["Effective_Date", "Agreement_Type", "Signing_Entity"],
        "properties": {
            "Effective_Date": {
                "type": "string",
                "format": "date",
                "description": "The most recent date associated with a signature"
            },
            "Agreement_Type": {
                "type": "string",
                "enum": ["master-agreement", "business-associate-agreement", "order-form"],
                "description": "The type of the agreement document"
            },
            "Signing_Entity": {
                "type": "string",
                "description": "The name of the entity signing the document"
            },
            "Licenses": {
                "type": "object",
                "x-nested-metadata": "should be removed",
                "properties": {
                    "Data_Aggregation": {
                        "type": "string",
                        "enum": ["yes", "no", "indeterminate"]
                    }
                }
            }
        }
    }

    result = _apply_usecase_treatment(input_schema, "extract")

    # Verify all problematic fields are removed
    assert "$schema" not in result
    assert "$id" not in result
    assert "x-schema-id" not in result
    assert "x-app-id" not in result
    assert "x-label" not in result

    # Verify nested x-* fields are removed
    assert "x-nested-metadata" not in result["properties"]["Licenses"]

    # Verify types are uppercased
    assert result["type"] == "OBJECT"
    assert result["properties"]["Effective_Date"]["type"] == "STRING"
    assert result["properties"]["Agreement_Type"]["type"] == "STRING"
    assert result["properties"]["Licenses"]["type"] == "OBJECT"
    assert result["properties"]["Licenses"]["properties"]["Data_Aggregation"]["type"] == "STRING"

    # Verify other fields are preserved
    assert result["title"] == "Legal Document Extraction"
    assert result["description"] == "A schema for extracting key information from a legal agreement"
    assert result["required"] == ["Effective_Date", "Agreement_Type", "Signing_Entity"]
    assert result["properties"]["Effective_Date"]["format"] == "date"
    assert result["properties"]["Agreement_Type"]["enum"] == ["master-agreement", "business-associate-agreement", "order-form"]
