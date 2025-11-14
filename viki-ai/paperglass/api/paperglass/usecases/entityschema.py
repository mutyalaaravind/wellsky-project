"""
Entity Schema use cases for business logic operations.
"""

from typing import Optional, Dict, Any
from logging import getLogger

from ..log import CustomLogger
from ..domain.models_common import GenericMessage
from ..infrastructure.ports import IQueryPort

LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)


async def get_entity_schema_for_usecase(
    app_id: str,
    schema_id: str, 
    usecase: Optional[str], 
    query: IQueryPort
) -> Dict[str, Any]:
    """
    Retrieve an entity schema by app_id and schema_id and format it for a specific use case.
    
    Args:
        app_id: The app ID of the entity schema to retrieve
        schema_id: The schema code of the entity schema to retrieve
        usecase: Optional use case parameter (e.g., "extract", "publish")
        query: Query port for database operations
        
    Returns:
        Dict containing the formatted JSON schema or error information
        
    Raises:
        Exception: If schema not found or other errors occur
    """
    extra = {
        "app_id": app_id,
        "schema_id": schema_id,
        "usecase": usecase,
    }
    
    # Retrieve the entity schema from Firestore
    entity_schema_aggregate = await query.get_entity_schema_by_app_id_and_schema_id(app_id, schema_id)
    
    if not entity_schema_aggregate:
        LOGGER2.warning("Entity schema not found for app_id: %s, schema_id: %s", app_id, schema_id, extra=extra)
        raise ValueError(f"Entity schema with app_id '{app_id}' and schema_id '{schema_id}' not found")

    # Get the raw schema data from the aggregate
    schema_dict = entity_schema_aggregate.get_schema_dict().copy()
    
    import json
    LOGGER2.debug("Retrieved raw schema: %s", json.dumps(schema_dict, indent=2), extra=extra)

    # If usecase is provided, update the required fields based on x-required-scopes
    if usecase and "x-required-scopes" in schema_dict:
        required_scopes = schema_dict["x-required-scopes"]
        if usecase in required_scopes:
            # Set the required field to the value from x-required-scopes[usecase]
            LOGGER2.debug("Setting required fields for usecase '%s': %s", usecase, required_scopes[usecase], extra=extra)
            schema_dict["required"] = required_scopes[usecase]
        else:
            # If usecase not found in x-required-scopes, remove required field
            LOGGER2.debug("Usecase '%s' not found in x-required-scopes, removing required field", usecase, extra=extra)
            schema_dict.pop("required", None)
    elif not usecase:
        # If no usecase provided, remove required field to return all properties without requirements
        LOGGER2.debug("No usecase provided, removing required field from schema", extra=extra)
        schema_dict.pop("required", None)
    
    # Remove the x-required-scopes, x-app-id, and x-label extensions from the final output
    # as they are internal metadata not part of standard JSON Schema
    schema_dict.pop("x-required-scopes", None)
    schema_dict.pop("x-app-id", None)
    schema_dict.pop("x-label", None)
    
    if usecase:
        schema_dict = _apply_usecase_treatment(schema_dict, usecase)

    LOGGER2.info("Successfully retrieved entity schema for app_id: %s, schema_id: %s", app_id, schema_id, extra=extra)
    
    return schema_dict


def _apply_usecase_treatment(schema_dict: Dict[str, Any], usecase: str) -> Dict[str, Any]:
    """
    Apply use case specific transformations to the schema dictionary.

    Args:
        schema_dict: The JSON schema dictionary to transform
        usecase: The use case to apply ("extraction", "publish", etc.)

    Returns:
        Dict containing the transformed JSON schema
    """
    if usecase == "publish":
        # No changes for publish use case
        LOGGER2.debug("No transformations applied for publish use case %s", usecase, extra={"usecase": usecase})
        return schema_dict
    elif usecase == "extract":
        # Apply extraction-specific transformations
        LOGGER2.debug("Applying transformations for extraction use case %s", usecase, extra={"usecase": usecase})
        schema_dict = _uppercase_types_for_extraction(schema_dict)
        # Remove $id and $schema for extraction use case
        schema_dict.pop("$id", None)
        schema_dict.pop("$schema", None)
        # Remove all x-* extension fields to avoid Pydantic validation errors in GenAI SDK
        schema_dict = _remove_extension_fields(schema_dict)
        return schema_dict
    else:
        # For unknown use cases, return unchanged
        LOGGER2.warning("Unknown use case '%s', returning schema unchanged", usecase, extra={"usecase": usecase})
        return schema_dict


def _uppercase_types_for_extraction(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uppercase type values for extraction use case.
    
    Args:
        schema_dict: The JSON schema dictionary to transform
        
    Returns:
        Dict containing the transformed JSON schema with uppercased types
    """
    # Create a copy to avoid modifying the original
    result = schema_dict.copy()

    LOGGER2.debug("Uppercasing types for extraction use case", extra={"schema": result})
    
    # Uppercase the main schema type
    if "type" in result and isinstance(result["type"], str):
        result["type"] = result["type"].upper()
    
    # Uppercase types in properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = _uppercase_property_types(result["properties"])
    
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

            # Uppercase the type if it exists and is a string
            if "type" in prop_copy and isinstance(prop_copy["type"], str):
                prop_copy["type"] = prop_copy["type"].upper()

            # Recursively handle nested properties (for object types)
            if "properties" in prop_copy and isinstance(prop_copy["properties"], dict):
                prop_copy["properties"] = _uppercase_property_types(prop_copy["properties"])

            # Handle array items (for array types)
            if "items" in prop_copy and isinstance(prop_copy["items"], dict):
                items_copy = prop_copy["items"].copy()
                if "type" in items_copy and isinstance(items_copy["type"], str):
                    items_copy["type"] = items_copy["type"].upper()

                # Recursively handle nested properties in array items
                if "properties" in items_copy and isinstance(items_copy["properties"], dict):
                    items_copy["properties"] = _uppercase_property_types(items_copy["properties"])

                prop_copy["items"] = items_copy

            result[prop_name] = prop_copy
        else:
            result[prop_name] = prop_def

    return result


def _remove_extension_fields(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively remove all JSON Schema extension fields (keys starting with 'x-').

    These custom extension fields (like x-schema-id, x-app-id, x-label) are used
    internally but cause validation errors when passed to external APIs like
    Google's GenAI SDK which uses Pydantic with extra='forbid'.

    Args:
        schema_dict: The JSON schema dictionary to clean

    Returns:
        Dict with all x-* extension fields removed
    """
    if not isinstance(schema_dict, dict):
        return schema_dict

    result = {}

    for key, value in schema_dict.items():
        # Skip any keys starting with 'x-'
        if key.startswith('x-'):
            LOGGER2.debug("Removing extension field: %s", key, extra={"field": key})
            continue

        # Recursively process nested dictionaries
        if isinstance(value, dict):
            result[key] = _remove_extension_fields(value)
        # Recursively process lists that might contain dictionaries
        elif isinstance(value, list):
            result[key] = [
                _remove_extension_fields(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result
