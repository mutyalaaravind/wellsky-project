"""
Model entities for representing simplified JSON Schema structures.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from uuid import uuid1
from pydantic import Field
from datetime import datetime

# Import AppAggregate from models
from .models import AppAggregate, Aggregate
from .time import now_utc
from paperglass.settings import SELF_API
from ..log import getLogger

LOGGER = getLogger(__name__)


class ValidationScope(Enum):
    """Validation scopes for different stages of data processing."""
    EXTRACT = "extract"
    PUBLISH = "publish"


class JsonSchemaType(Enum):
    """Supported JSON Schema types."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


@dataclass
class PropertyConstraints:
    """Constraints that can be applied to schema properties."""
    # String constraints
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None
    
    # Number constraints
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    exclusive_minimum: Optional[Union[int, float]] = None
    exclusive_maximum: Optional[Union[int, float]] = None
    multiple_of: Optional[Union[int, float]] = None
    
    # Array constraints
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    unique_items: Optional[bool] = None
    
    # Object constraints
    min_properties: Optional[int] = None
    max_properties: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert constraints to dictionary format for JSON Schema."""
        result = {}
        
        # String constraints
        if self.max_length is not None:
            result["maxLength"] = self.max_length
        if self.min_length is not None:
            result["minLength"] = self.min_length
        if self.pattern is not None:
            result["pattern"] = self.pattern
            
        # Number constraints
        if self.minimum is not None:
            result["minimum"] = self.minimum
        if self.maximum is not None:
            result["maximum"] = self.maximum
        if self.exclusive_minimum is not None:
            result["exclusiveMinimum"] = self.exclusive_minimum
        if self.exclusive_maximum is not None:
            result["exclusiveMaximum"] = self.exclusive_maximum
        if self.multiple_of is not None:
            result["multipleOf"] = self.multiple_of
            
        # Array constraints
        if self.min_items is not None:
            result["minItems"] = self.min_items
        if self.max_items is not None:
            result["maxItems"] = self.max_items
        if self.unique_items is not None:
            result["uniqueItems"] = self.unique_items
            
        # Object constraints
        if self.min_properties is not None:
            result["minProperties"] = self.min_properties
        if self.max_properties is not None:
            result["maxProperties"] = self.max_properties
            
        return result


@dataclass
class SchemaProperty:
    """Represents a single property in a JSON Schema."""
    name: str
    type: JsonSchemaType
    description: Optional[str] = None
    constraints: Optional[PropertyConstraints] = None
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    
    # For object types
    properties: Optional[Dict[str, 'SchemaProperty']] = None
    additional_properties: Optional[bool] = None
    
    # For array types
    items: Optional['SchemaProperty'] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert property to dictionary format for JSON Schema."""
        result = {
            "type": self.type.value
        }
        
        if self.description:
            result["description"] = self.description
            
        if self.default is not None:
            result["default"] = self.default
            
        if self.enum:
            result["enum"] = self.enum
            
        if self.constraints:
            result.update(self.constraints.to_dict())
            
        # Handle object properties
        if self.type == JsonSchemaType.OBJECT:
            if self.properties:
                result["properties"] = {
                    name: prop.to_dict() for name, prop in self.properties.items()
                }
            if self.additional_properties is not None:
                result["additionalProperties"] = self.additional_properties
                
        # Handle array items
        if self.type == JsonSchemaType.ARRAY and self.items:
            result["items"] = self.items.to_dict()
            
        return result


@dataclass
class EntitySchema:
    """Represents a complete JSON Schema for an entity."""
    schema_uri: str = "https://json-schema.org/draft/2020-12/schema"
    id: Optional[str] = None
    fqn: Optional[str] = None
    title: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    type: JsonSchemaType = JsonSchemaType.OBJECT
    properties: Dict[str, SchemaProperty] = field(default_factory=dict)
    required: Dict[ValidationScope, List[str]] = field(default_factory=dict)
    additional_properties: bool = False
    app_id: str = "GLOBAL"
    
    def add_property(self, property: SchemaProperty) -> None:
        """Add a property to the schema."""
        self.properties[property.name] = property
        
    def set_required(self, scope: ValidationScope, property_names: List[str]) -> None:
        """Set which properties are required for a specific validation scope."""
        self.required[scope] = property_names
        
    def make_property_required(self, scope: ValidationScope, property_name: str) -> None:
        """Mark a single property as required for a specific validation scope."""
        if scope not in self.required:
            self.required[scope] = []
        if property_name not in self.required[scope]:
            self.required[scope].append(property_name)
            
    def get_required_for_scope(self, scope: ValidationScope) -> List[str]:
        """Get required properties for a specific validation scope."""
        return self.required.get(scope, [])
        
    def to_dict(self, scope: Optional[ValidationScope] = None) -> Dict[str, Any]:
        """Convert schema to dictionary format for JSON Schema.
        
        Args:
            scope: If provided, exports schema with required fields for that scope.
                  If None, exports without required fields (for internal use).
        """
        result = {
            "$schema": self.schema_uri,
            "type": self.type.value,
            "properties": {
                name: prop.to_dict() for name, prop in self.properties.items()
            },
            "additionalProperties": self.additional_properties
        }
        
        if self.id:
            result["$id"] = self.id
            
        if self.title:
            result["title"] = self.title
            
        if self.description:
            result["description"] = self.description
            
        # Include required fields for the specified scope
        if scope is not None and scope in self.required:
            required_fields = self.required[scope]
            if required_fields:
                result["required"] = required_fields
                
        return result
        
    def to_dict_all_scopes(self) -> Dict[str, Any]:
        """Convert schema to dictionary format including all validation scopes.
        
        This is useful for internal storage and processing where all scope information
        needs to be preserved.
        """
        result = self.to_dict()  # Get base schema without scope-specific required fields
        
        # Add scoped required fields
        if self.required:
            result["x-required-scopes"] = {
                scope.value: fields for scope, fields in self.required.items()
            }
            
        # Add app_id
        result["x-app-id"] = self.app_id
        
        return result


@dataclass
class Entity:
    """Represents an entity instance that conforms to a schema."""
    schema: EntitySchema
    data: Dict[str, Any] = field(default_factory=dict)
    
    def set_value(self, property_name: str, value: Any) -> None:
        """Set a value for a property."""
        if property_name in self.schema.properties:
            self.data[property_name] = value
        else:
            raise ValueError(f"Property '{property_name}' not defined in schema")
            
    def get_value(self, property_name: str) -> Any:
        """Get a value for a property."""
        return self.data.get(property_name)
        
    def validate(self, scope: Optional[ValidationScope] = None) -> List[str]:
        """Validate the entity data against its schema. Returns list of validation errors.
        
        Args:
            scope: Validation scope to use for required field checking.
                  If None, no required field validation is performed.
        """
        errors = []
        
        # Check required properties for the specified scope
        if scope is not None:
            required_props = self.schema.get_required_for_scope(scope)
            for required_prop in required_props:
                if required_prop not in self.data or self.data[required_prop] is None:
                    errors.append(f"Required property '{required_prop}' is missing for {scope.value} scope")
                
        # Basic type validation for existing properties
        for prop_name, value in self.data.items():
            if prop_name in self.schema.properties:
                prop_schema = self.schema.properties[prop_name]
                if not self._validate_type(value, prop_schema.type):
                    errors.append(f"Property '{prop_name}' has invalid type")
                    
                # Validate constraints
                if prop_schema.constraints:
                    constraint_errors = self._validate_constraints(prop_name, value, prop_schema.constraints)
                    errors.extend(constraint_errors)
                    
        return errors
        
    def _validate_type(self, value: Any, expected_type: JsonSchemaType) -> bool:
        """Validate that a value matches the expected JSON Schema type."""
        if value is None:
            return True  # Allow null values for now
            
        type_mapping = {
            JsonSchemaType.STRING: str,
            JsonSchemaType.NUMBER: (int, float),
            JsonSchemaType.INTEGER: int,
            JsonSchemaType.BOOLEAN: bool,
            JsonSchemaType.OBJECT: dict,
            JsonSchemaType.ARRAY: list,
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
            
        return True
        
    def _validate_constraints(self, prop_name: str, value: Any, constraints: PropertyConstraints) -> List[str]:
        """Validate constraints for a property value."""
        errors = []
        
        # String constraints
        if isinstance(value, str):
            if constraints.max_length is not None and len(value) > constraints.max_length:
                errors.append(f"Property '{prop_name}' exceeds maximum length of {constraints.max_length}")
            if constraints.min_length is not None and len(value) < constraints.min_length:
                errors.append(f"Property '{prop_name}' is below minimum length of {constraints.min_length}")
                
        # Number constraints
        if isinstance(value, (int, float)):
            if constraints.minimum is not None and value < constraints.minimum:
                errors.append(f"Property '{prop_name}' is below minimum value of {constraints.minimum}")
            if constraints.maximum is not None and value > constraints.maximum:
                errors.append(f"Property '{prop_name}' exceeds maximum value of {constraints.maximum}")
                
        return errors
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary format."""
        return self.data.copy()


# Factory functions for common schema patterns

def create_entity_schema_from_json(json_schema: Dict[str, Any], default_scope: ValidationScope = ValidationScope.PUBLISH) -> EntitySchema:
    """Create an EntitySchema from a JSON Schema dictionary.
    
    Args:
        json_schema: Standard JSON Schema dictionary
        default_scope: Default validation scope to assign required fields to
    """

    def get_simple_id(schema_uri: str):
        """Extract a simple ID from the schema URI."""
        if schema_uri:
            id = schema_uri.split("/")[-1].split(".")[0]
            return id
        return schema_uri



    schema = EntitySchema(
        schema_uri=json_schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        id=get_simple_id(json_schema.get("$id")),
        fqn=json_schema.get("$id"),
        title=json_schema.get("title"),
        label=json_schema.get("x-label", _synthesize_label_from_schema_id(json_schema.get("$id", ""))),
        description=json_schema.get("description"),
        type=JsonSchemaType(json_schema.get("type", "object")),
        additional_properties=json_schema.get("additionalProperties", False),
        app_id=json_schema.get("x-app-id", "GLOBAL")
    )
    
    # Convert properties
    properties = json_schema.get("properties", {})
    for prop_name, prop_def in properties.items():
        schema_property = _create_property_from_json(prop_name, prop_def)
        schema.add_property(schema_property)
    
    # Handle required fields
    if "required" in json_schema:
        schema.set_required(default_scope, json_schema["required"])
    
    # Handle scoped required fields if present
    if "x-required-scopes" in json_schema:
        for scope_name, required_fields in json_schema["x-required-scopes"].items():
            scope = ValidationScope(scope_name)
            schema.set_required(scope, required_fields)
    
    return schema


def create_entity_schema_from_json_with_scopes(json_schema: Dict[str, Any]) -> EntitySchema:
    """Create an EntitySchema from an extended JSON Schema dictionary that includes scope information.
    
    This function expects the JSON schema to have x-required-scopes and x-app-id extensions.
    """
    return create_entity_schema_from_json(json_schema)


def _create_property_from_json(name: str, prop_def: Dict[str, Any]) -> SchemaProperty:
    """Create a SchemaProperty from a JSON Schema property definition."""
    prop_type = JsonSchemaType(prop_def["type"])
    
    # Create constraints
    constraints = None
    constraint_fields = {
        "maxLength": "max_length",
        "minLength": "min_length", 
        "pattern": "pattern",
        "minimum": "minimum",
        "maximum": "maximum",
        "exclusiveMinimum": "exclusive_minimum",
        "exclusiveMaximum": "exclusive_maximum",
        "multipleOf": "multiple_of",
        "minItems": "min_items",
        "maxItems": "max_items",
        "uniqueItems": "unique_items",
        "minProperties": "min_properties",
        "maxProperties": "max_properties"
    }
    
    constraint_kwargs = {}
    for json_key, python_key in constraint_fields.items():
        if json_key in prop_def:
            constraint_kwargs[python_key] = prop_def[json_key]
    
    if constraint_kwargs:
        constraints = PropertyConstraints(**constraint_kwargs)
    
    # Handle nested properties for objects
    nested_properties = None
    additional_properties = None
    if prop_type == JsonSchemaType.OBJECT:
        if "properties" in prop_def:
            nested_properties = {}
            for nested_name, nested_def in prop_def["properties"].items():
                nested_properties[nested_name] = _create_property_from_json(nested_name, nested_def)
        additional_properties = prop_def.get("additionalProperties")
    
    # Handle array items
    items = None
    if prop_type == JsonSchemaType.ARRAY and "items" in prop_def:
        items = _create_property_from_json("items", prop_def["items"])
    
    return SchemaProperty(
        name=name,
        type=prop_type,
        description=prop_def.get("description"),
        constraints=constraints,
        default=prop_def.get("default"),
        enum=prop_def.get("enum"),
        properties=nested_properties,
        additional_properties=additional_properties,
        items=items
    )


def create_string_property(name: str, description: str = None, max_length: int = None, 
                          min_length: int = None, pattern: str = None, required: bool = False) -> SchemaProperty:
    """Create a string property with common constraints."""
    constraints = None
    if max_length or min_length or pattern:
        constraints = PropertyConstraints(
            max_length=max_length,
            min_length=min_length,
            pattern=pattern
        )
    
    return SchemaProperty(
        name=name,
        type=JsonSchemaType.STRING,
        description=description,
        constraints=constraints
    )


def create_number_property(name: str, description: str = None, minimum: Union[int, float] = None,
                          maximum: Union[int, float] = None) -> SchemaProperty:
    """Create a number property with range constraints."""
    constraints = None
    if minimum is not None or maximum is not None:
        constraints = PropertyConstraints(minimum=minimum, maximum=maximum)
    
    return SchemaProperty(
        name=name,
        type=JsonSchemaType.NUMBER,
        description=description,
        constraints=constraints
    )


def create_object_property(name: str, description: str = None, 
                          additional_properties: bool = True) -> SchemaProperty:
    """Create an object property."""
    return SchemaProperty(
        name=name,
        type=JsonSchemaType.OBJECT,
        description=description,
        additional_properties=additional_properties
    )


def create_processing_object_schema() -> EntitySchema:
    """Create the example processing object schema from the task description."""
    schema = EntitySchema(
        id="https://example.com/schemas/processing-object.json",
        title="Processing Object Schema",
        description="[Placeholder for schema description]",
        additional_properties=False
    )
    
    # Add properties
    schema.add_property(create_string_property(
        "id", 
        "Unique identifier for the object"
    ))
    
    schema.add_property(create_string_property(
        "name",
        "Name of the processing object",
        max_length=25
    ))
    
    schema.add_property(create_string_property(
        "run_id",
        "Identifier for the processing run"
    ))
    
    schema.add_property(create_number_property(
        "processing_progress",
        "Progress of processing as a decimal between 0 and 1",
        minimum=0,
        maximum=1
    ))
    
    schema.add_property(create_object_property(
        "context",
        "Additional context information as key-value pairs",
        additional_properties=True
    ))
    
    # Set required fields for different scopes
    schema.set_required(ValidationScope.PUBLISH, ["name"])
    
    return schema


def _synthesize_label_from_schema_id(schema_id: str) -> str:
    """
    Synthesize a human-readable label from a schema ID.
    
    Takes the last token of the schema_id, drops the ".json", replaces 
    underscores and hyphens with spaces, and uppercases each word.
    
    Args:
        schema_id: The schema ID (e.g., "insurance_data.json" or "patient-info")
        
    Returns:
        A synthesized label (e.g., "Insurance Data" or "Patient Info")
    """
    if not schema_id:
        return ""
    
    # Get the last token (filename part)
    last_token = schema_id.split("/")[-1]
    
    # Remove .json extension if present
    if last_token.endswith(".json"):
        last_token = last_token[:-5]
    
    # Replace underscores and hyphens with spaces
    label = last_token.replace("_", " ").replace("-", " ")
    
    # Uppercase each word
    label = " ".join(word.capitalize() for word in label.split())
    
    return label


def _format_entity_schema_id_and_fqn(schema_data: Dict[str, Any], app_id: str) -> tuple[Dict[str, Any], Optional[str], Optional[str]]:
    """
    Format the entity schema $id and fqn according to the paperglass convention.
    
    Args:
        schema_data: The original schema data dictionary
        app_id: The application ID
        
    Returns:
        Tuple of (updated_schema_data, schema_id, fqn)
    """
    # Extract simple ID from existing $id or use provided schema_id
    original_id = schema_data.get("$id")
    if original_id:
        simple_id = original_id.split("/")[-1].split(".")[0] if original_id else None
    else:
        simple_id = None
        
    if simple_id:
        # Format: {SELF_API}/api/schemas/{APP_ID}/{simple_id}.json
        formatted_fqn = f"{SELF_API}/api/schemas/{app_id}/{simple_id}.json"
        
        # Update the schema_data with the new $id and ensure consistency
        updated_schema_data = schema_data.copy()  # Don't modify the original
        updated_schema_data["$id"] = formatted_fqn
        updated_schema_data["x-app-id"] = app_id
        
        return updated_schema_data, simple_id, formatted_fqn
    else:
        return schema_data, None, None


# Domain aggregate for persistence
class EntitySchemaAggregate(AppAggregate):
    """
    Domain aggregate for EntitySchema that can be persisted.
    This wraps the dataclass EntitySchema with the proper aggregate structure.
    """
    schema_data: Dict[str, Any]
    schema_id: Optional[str] = None
    fqn: Optional[str] = None
    title: Optional[str] = None
    label: Optional[str] = None
    app_id: str = "GLOBAL"
    active: bool = True

    def __init__(self, schema_data: Dict[str, Any], schema_id: str = None, fqn: str = None, title: str = None, label: str = None, app_id: str = "GLOBAL", **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = uuid1().hex
        
        # Format the schema data, schema_id, and fqn according to paperglass conventions
        formatted_schema_data, formatted_schema_id, formatted_fqn = _format_entity_schema_id_and_fqn(schema_data, app_id)
        
        # Use formatted values if they were generated, otherwise use provided values
        final_schema_data = formatted_schema_data
        final_schema_id = formatted_schema_id if formatted_schema_id else schema_id
        final_fqn = formatted_fqn if formatted_fqn else fqn
        
        # Extract label from x-label or synthesize from schema_id
        if label is None:
            label = schema_data.get("x-label")
            if label is None and final_schema_id:
                label = _synthesize_label_from_schema_id(final_schema_id)
        
        super().__init__(            
            schema_data=final_schema_data,
            schema_id=final_schema_id,
            fqn=final_fqn,
            title=title,
            label=label,
            app_id=app_id,
            **kwargs
        )

    @classmethod
    def create_from_dict(cls, schema_dict: Dict[str, Any]) -> 'EntitySchemaAggregate':
        """Create an EntitySchemaAggregate from a JSON schema dictionary."""
        # Handle two cases:
        # 1. schema_dict contains nested 'schema' field (from admin API)
        # 2. schema_dict is the JSON schema itself
        
        if 'schema' in schema_dict:
            # Case 1: Admin API format with nested schema
            json_schema = schema_dict['schema']
            app_id = schema_dict.get('app_id', 'GLOBAL')
            
            # Add app_id to the JSON schema for validation
            if 'x-app-id' not in json_schema:
                json_schema['x-app-id'] = app_id
                
            schema_dataclass = create_entity_schema_from_json(json_schema)
        else:
            # Case 2: Direct JSON schema
            json_schema = schema_dict
            schema_dataclass = create_entity_schema_from_json(json_schema)
            app_id = schema_dataclass.app_id
        
        # The __init__ method will handle the formatting, so we just pass the original data
        # and let the constructor apply the formatting logic
        return cls(
            schema_data=json_schema,
            schema_id=schema_dataclass.id,
            fqn=schema_dataclass.fqn,
            title=schema_dataclass.title,
            app_id=app_id
        )
    
    def to_dataclass(self) -> EntitySchema:
        """Convert back to the dataclass representation."""
        return create_entity_schema_from_json(self.schema_data)
    
    def get_schema_dict(self) -> Dict[str, Any]:
        """Get the raw schema dictionary."""
        return self.schema_data
    
    def update_schema(self, schema_dict: Dict[str, Any]) -> None:
        """Update the schema data."""
        # Validate the new schema
        schema_dataclass = create_entity_schema_from_json(schema_dict)
        
        # Apply formatting to the schema data
        formatted_schema_data, formatted_schema_id, formatted_fqn = _format_entity_schema_id_and_fqn(schema_dict, schema_dataclass.app_id)
        
        # Use formatted values if they were generated, otherwise use dataclass values
        self.schema_data = formatted_schema_data
        self.schema_id = formatted_schema_id if formatted_schema_id else schema_dataclass.id
        self.fqn = formatted_fqn if formatted_fqn else schema_dataclass.fqn
        self.title = schema_dataclass.title
        self.app_id = schema_dataclass.app_id
    
    def deactivate(self) -> None:
        """Mark the schema as inactive."""
        self.active = False

    def toExtra(self):
        """Return extra information for logging."""
        return {
            "entity_schema_id": self.schema_id,
            "entity_schema_fqn": self.fqn,
            "entity_schema_title": self.title,
            "app_id": self.app_id,
        }


class EntityAggregate(Aggregate):
    """
    Domain aggregate for Entity instances that can be persisted to Firestore.
    This aggregate contains entity data and determines its own collection based on schema information.
    """
    entity_data: Dict[str, Any]
    schema_ref: str
    entity_type: str
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    document_operation_instance_id: Optional[str] = None
    confidence_score: Optional[float] = None
    active: bool = True

    @classmethod
    def calculate_entity_type(cls, entity: Dict[str, Any], schema_ref: str, metadata: Dict[str, Any]) -> str:
        """
        Calculate the entity type from multiple sources in order of preference:
        1. From the entity data itself
        2. From the schema_ref (extract from URL)
        3. From entity wrapper metadata
        4. Default to 'unknown' as last resort
        
        Args:
            entity: The individual entity dictionary
            schema_ref: The schema reference URL
            metadata: Metadata from the entity wrapper
            
        Returns:
            The determined entity type as a string
        """
        # 1. Try to get from entity data itself
        entity_type = entity.get('type')
        
        if not entity_type and schema_ref and schema_ref != 'default':
            # 2. Try to extract entity type from schema_ref URL
            # Expected format: http://host:port/api/schemas/{app_id}/{entity_type}.json
            try:
                url_parts = schema_ref.split('/')
                if len(url_parts) >= 2:
                    filename = url_parts[-1]
                    entity_type = filename.split('.')[0]  # Remove .json extension
            except Exception as e:
                LOGGER.warning(f"Failed to extract entity type from schema_ref '{schema_ref}': {e}")
        
        if not entity_type:
            # 3. Try to get from metadata
            entity_type = metadata.get('entity_type')
        
        if not entity_type:
            # 4. Last resort default
            entity_type = 'unknown'
            LOGGER.warning(f"Could not determine entity type for entity {entity}, defaulting to 'unknown'")
        
        return entity_type

    @classmethod
    def create_from_entity_wrapper(cls, entity_wrapper: Dict[str, Any]) -> List['EntityAggregate']:
        """
        Create EntityAggregate instances from an EntityWrapper.
        
        Args:
            entity_wrapper: The EntityWrapper dictionary containing entities and metadata
            
        Returns:
            List of EntityAggregate instances
        """
        entities = entity_wrapper.get('entities', [])
        
        # Handle case where entities is not a list (check is_entity_list flag)
        is_entity_list = entity_wrapper.get('is_entity_list', True)
        if not is_entity_list and entities:
            # If entities is not a list, wrap it in a list
            entities = [entities]
        
        if not entities:
            return []
        
        # Extract metadata from the wrapper
        metadata = entity_wrapper.get('metadata', {})
        source_document_id = metadata.get('document_id')
        source_page_number = metadata.get('page_number')
        
        
        # Extract app/tenant/patient info - these might be in metadata or at the top level
        app_id = entity_wrapper.get('app_id')
        tenant_id = entity_wrapper.get('tenant_id')
        patient_id = entity_wrapper.get('patient_id')
        document_id = entity_wrapper.get('document_id')
        page_number = entity_wrapper.get('page_number')
        run_id = entity_wrapper.get('run_id')
        schema_ref = entity_wrapper.get('schema_ref', 'default')
        
        entity_aggregates = []
        
        for entity in entities:
            # Handle case where entity might be a string instead of a dict
            if isinstance(entity, str):
                # If entity is a string, try to parse it as JSON
                try:
                    entity = json.loads(entity)
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, skip this entity or create a minimal structure
                    LOGGER.warning(f"Skipping invalid entity data: {entity}")
                    continue
            
            # Ensure entity is a dictionary
            if not isinstance(entity, dict):
                LOGGER.warning(f"Skipping non-dictionary entity: {type(entity)} - {entity}")
                continue
            
            # Determine entity type using the calculate_entity_type method
            entity_type = cls.calculate_entity_type(entity, schema_ref, metadata)
            
            # Extract confidence if available
            confidence_score = entity.get('confidence')
            
            # Create the aggregate
            aggregate = cls(
                id=uuid1().hex,
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id,
                document_id=document_id,
                page_number=page_number,
                document_operation_instance_id=run_id,
                entity_data=entity,
                schema_ref=schema_ref,
                entity_type=entity_type,                                
                confidence_score=confidence_score
            )
            
            entity_aggregates.append(aggregate)
        
        return entity_aggregates
    
    def get_collection_name(self) -> str:
        """
        Determine the Firestore collection name for this entity.
        This allows the UOW to dynamically determine where to store the entity.
        
        Expected format: paperglass_entities_{schema_name}
        Where schema_name is extracted from the schema_ref URL.
        
        Example:
        - schema_ref: http://viki-ai-paperglass-api-1:15000/api/schemas/007/insurance_data.json
        - collection: paperglass_entities_insurance_data
        """
        if not self.schema_ref:
            return f"paperglass_entities_{self.entity_type}"
        
        # Extract schema name from URL
        # Expected format: http://host:port/api/schemas/{app_id}/{schema_name}.json
        try:
            # Split by '/' and get the last part, then remove .json extension
            url_parts = self.schema_ref.split('/')
            if len(url_parts) >= 2:
                # Get the last part (filename) and remove extension
                filename = url_parts[-1]
                schema_name = filename.split('.')[0]  # Remove .json extension
                return f"paperglass_entities_{schema_name}"
        except Exception as e:
            LOGGER.warning(f"Failed to parse schema_ref '{self.schema_ref}': {e}")
        
        # Fallback to entity_type if parsing fails
        return f"paperglass_entities_{self.entity_type}"
    
    def deactivate(self) -> None:
        """Mark the entity as inactive."""
        self.active = False
    
    def toExtra(self):
        """Return extra information for logging."""
        supero = super().toExtra()
        o = {
            "entity_type": self.entity_type,
            "schema_ref": self.schema_ref,
            "schema_collection_name": self.get_collection_name(),
            "document_id": self.source_document_id,
            "page_number": self.source_page_number,
            "extraction_run_id": self.extraction_run_id,
            "confidence_score": self.confidence_score,
        }
        supero.update(o)
        return supero
