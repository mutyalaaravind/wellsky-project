"""
Schema utilities for medication extraction.

This module provides utility functions for working with JSON schemas,
particularly for converting schemas to Vertex AI Gemini API format.
"""

from typing import Dict, Any
from utils.custom_logger import getLogger

LOGGER = getLogger(__name__)


def uppercase_types_for_vertex_ai(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON Schema types to uppercase format required by Vertex AI.
    Also removes JSON Schema meta-schema fields that Vertex AI doesn't accept.
    
    Args:
        schema_dict: The JSON schema dictionary to transform
        
    Returns:
        Dict containing the transformed JSON schema with uppercased types
    """
    # Create a copy to avoid modifying the original
    result = schema_dict.copy()

    LOGGER.debug("Converting schema types to Vertex AI format", extra={"schema": result})
    
    # Remove JSON Schema meta-schema fields that Vertex AI doesn't accept
    meta_schema_fields = ["$schema", "$id", "$ref", "$defs", "$vocabulary"]
    for field in meta_schema_fields:
        if field in result:
            del result[field]
    
    # Uppercase the main schema type
    if "type" in result:
        if isinstance(result["type"], str):
            result["type"] = result["type"].upper()
        elif isinstance(result["type"], list):
            # Handle union types like ["STRING", "NULL"]
            result["type"] = [t.upper() if isinstance(t, str) else t for t in result["type"]]
    
    # Uppercase types in properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = _uppercase_property_types(result["properties"])
    
    # Handle array items
    if "items" in result and isinstance(result["items"], dict):
        result["items"] = uppercase_types_for_vertex_ai(result["items"])
    
    return result


def _uppercase_property_types(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively uppercase type values in properties.
    
    Args:
        properties: Dictionary of property definitions
        
    Returns:
        Dict with uppercased type values
    """
    result = {}
    
    for prop_name, prop_def in properties.items():
        if isinstance(prop_def, dict):
            prop_copy = prop_def.copy()
            
            # Uppercase the type if it exists
            if "type" in prop_copy:
                if isinstance(prop_copy["type"], str):
                    prop_copy["type"] = prop_copy["type"].upper()
                elif isinstance(prop_copy["type"], list):
                    # Handle union types like ["STRING", "NULL"]
                    prop_copy["type"] = [t.upper() if isinstance(t, str) else t for t in prop_copy["type"]]
            
            # Recursively handle nested properties (for object types)
            if "properties" in prop_copy and isinstance(prop_copy["properties"], dict):
                prop_copy["properties"] = _uppercase_property_types(prop_copy["properties"])
            
            # Handle array items (for array types)
            if "items" in prop_copy and isinstance(prop_copy["items"], dict):
                prop_copy["items"] = uppercase_types_for_vertex_ai(prop_copy["items"])
            
            result[prop_name] = prop_copy
        else:
            result[prop_name] = prop_def
    
    return result


def get_schema_by_name(schema_name: str) -> Dict[str, Any]:
    """
    Get a schema by name from the SCHEMAS dictionary and convert it to Vertex AI format.
    
    Args:
        schema_name: The name of the schema to retrieve
        
    Returns:
        The schema in Vertex AI format
        
    Raises:
        KeyError: If the schema name is not found
    """
    from medication_schemas import SCHEMAS
    
    if schema_name not in SCHEMAS:
        available_schemas = ", ".join(SCHEMAS.keys())
        raise KeyError(f"Schema '{schema_name}' not found. Available schemas: {available_schemas}")
    
    schema = SCHEMAS[schema_name]
    
    # Schema is already in UPPERCASE format in entityschemas.py
    # But we still run it through the converter to ensure consistency
    # and handle any edge cases
    return uppercase_types_for_vertex_ai(schema)