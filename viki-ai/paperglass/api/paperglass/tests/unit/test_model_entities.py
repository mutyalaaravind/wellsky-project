"""
Unit tests for model_entities module.
Tests EntitySchema functionality including JSON conversion and validation.
"""

import pytest
import json
from paperglass.domain.model_entities import (
    EntitySchema,
    Entity,
    JsonSchemaType,
    PropertyConstraints,
    SchemaProperty,
    ValidationScope,
    create_entity_schema_from_json,
    create_processing_object_schema
)


class TestEntitySchema:
    """Test cases for EntitySchema functionality."""
    
    @pytest.fixture
    def test_json_schema(self):
        """Test JSON Schema as provided in the task."""
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://example.com/schemas/processing-object.json",
            "title": "Processing Object Schema",
            "description": "[Placeholder for schema description]",
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique identifier for the object"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the processing object",
                    "maxLength": 25
                },
                "run_id": {
                    "type": "string",
                    "description": "Identifier for the processing run"
                },
                "processing_progress": {
                    "type": "number",
                    "description": "Progress of processing as a decimal between 0 and 1",
                    "minimum": 0,
                    "maximum": 1
                },
                "context": {
                    "type": "object",
                    "description": "Additional context information as key-value pairs",
                    "additionalProperties": True
                }
            },
            "required": ["name"],
            "additionalProperties": False
        }
    
    @pytest.fixture
    def valid_test_data(self):
        """Valid test data that conforms to the schema."""
        return {
            "id": "proc-123",
            "name": "Test Processing",
            "run_id": "run-456",
            "processing_progress": 0.75,
            "context": {
                "environment": "test",
                "version": "1.0.0",
                "user_id": "user-789"
            }
        }
    
    @pytest.fixture
    def invalid_test_data_missing_required(self):
        """Invalid test data missing required field."""
        return {
            "id": "proc-123",
            "run_id": "run-456",
            "processing_progress": 0.75
            # Missing required 'name' field
        }
    
    @pytest.fixture
    def invalid_test_data_constraint_violation(self):
        """Invalid test data violating constraints."""
        return {
            "name": "This name is way too long for the maximum length constraint",  # Exceeds maxLength: 25
            "processing_progress": 1.5  # Exceeds maximum: 1
        }
    
    @pytest.fixture
    def invalid_test_data_type_mismatch(self):
        """Invalid test data with type mismatches."""
        return {
            "name": "Valid Name",
            "processing_progress": "not a number",  # Should be number
            "context": "not an object"  # Should be object
        }

    def test_convert_json_schema_to_entity_schema(self, test_json_schema):
        """Test converting JSON Schema dictionary to EntitySchema object."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        
        # Test schema metadata
        assert entity_schema.schema_uri == "https://json-schema.org/draft/2020-12/schema"
        assert entity_schema.id == "https://example.com/schemas/processing-object.json"
        assert entity_schema.title == "Processing Object Schema"
        assert entity_schema.description == "[Placeholder for schema description]"
        assert entity_schema.type == JsonSchemaType.OBJECT
        assert entity_schema.get_required_for_scope(ValidationScope.PUBLISH) == ["name"]
        assert entity_schema.additional_properties == False
        
        # Test properties
        assert len(entity_schema.properties) == 5
        
        # Test id property
        id_prop = entity_schema.properties["id"]
        assert id_prop.name == "id"
        assert id_prop.type == JsonSchemaType.STRING
        assert id_prop.description == "Unique identifier for the object"
        assert id_prop.constraints is None
        
        # Test name property with constraints
        name_prop = entity_schema.properties["name"]
        assert name_prop.name == "name"
        assert name_prop.type == JsonSchemaType.STRING
        assert name_prop.description == "Name of the processing object"
        assert name_prop.constraints is not None
        assert name_prop.constraints.max_length == 25
        
        # Test processing_progress property with number constraints
        progress_prop = entity_schema.properties["processing_progress"]
        assert progress_prop.name == "processing_progress"
        assert progress_prop.type == JsonSchemaType.NUMBER
        assert progress_prop.description == "Progress of processing as a decimal between 0 and 1"
        assert progress_prop.constraints is not None
        assert progress_prop.constraints.minimum == 0
        assert progress_prop.constraints.maximum == 1
        
        # Test context property (object type)
        context_prop = entity_schema.properties["context"]
        assert context_prop.name == "context"
        assert context_prop.type == JsonSchemaType.OBJECT
        assert context_prop.description == "Additional context information as key-value pairs"
        assert context_prop.additional_properties == True

    def test_export_entity_schema_as_json_schema(self, test_json_schema):
        """Test exporting EntitySchema back to JSON Schema format."""
        # Convert JSON to EntitySchema and back
        entity_schema = create_entity_schema_from_json(test_json_schema)
        exported_json = entity_schema.to_dict()
        
        # Test that exported JSON matches original structure
        assert exported_json["$schema"] == test_json_schema["$schema"]
        assert exported_json["$id"] == test_json_schema["$id"]
        assert exported_json["title"] == test_json_schema["title"]
        assert exported_json["description"] == test_json_schema["description"]
        assert exported_json["type"] == test_json_schema["type"]
        # Test that exported JSON with PUBLISH scope matches original required fields
        exported_json_with_scope = entity_schema.to_dict(ValidationScope.PUBLISH)
        assert exported_json_with_scope["required"] == test_json_schema["required"]
        assert exported_json["additionalProperties"] == test_json_schema["additionalProperties"]
        
        # Test properties structure
        assert "properties" in exported_json
        exported_props = exported_json["properties"]
        original_props = test_json_schema["properties"]
        
        # Test each property
        for prop_name in original_props:
            assert prop_name in exported_props
            exported_prop = exported_props[prop_name]
            original_prop = original_props[prop_name]
            
            assert exported_prop["type"] == original_prop["type"]
            assert exported_prop["description"] == original_prop["description"]
            
            # Test constraints
            for constraint in ["maxLength", "minimum", "maximum", "additionalProperties"]:
                if constraint in original_prop:
                    assert exported_prop[constraint] == original_prop[constraint]

    def test_validate_valid_json_object(self, test_json_schema, valid_test_data):
        """Test validating a valid JSON object against EntitySchema."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        entity = Entity(schema=entity_schema, data=valid_test_data)
        
        validation_errors = entity.validate()
        assert len(validation_errors) == 0, f"Expected no validation errors, got: {validation_errors}"

    def test_validate_missing_required_field(self, test_json_schema, invalid_test_data_missing_required):
        """Test validation fails when required field is missing."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        entity = Entity(schema=entity_schema, data=invalid_test_data_missing_required)
        
        # Test validation with PUBLISH scope (where name is required)
        validation_errors = entity.validate(ValidationScope.PUBLISH)
        assert len(validation_errors) > 0
        assert any("Required property 'name' is missing for publish scope" in error for error in validation_errors)
        
        # Test validation without scope (no required field validation)
        validation_errors_no_scope = entity.validate()
        assert len(validation_errors_no_scope) == 0  # No required field validation without scope

    def test_validate_constraint_violations(self, test_json_schema, invalid_test_data_constraint_violation):
        """Test validation fails when constraints are violated."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        entity = Entity(schema=entity_schema, data=invalid_test_data_constraint_violation)
        
        validation_errors = entity.validate()
        assert len(validation_errors) > 0
        
        # Check for maxLength violation
        assert any("exceeds maximum length" in error for error in validation_errors)
        
        # Check for maximum value violation
        assert any("exceeds maximum value" in error for error in validation_errors)

    def test_validate_type_mismatches(self, test_json_schema, invalid_test_data_type_mismatch):
        """Test validation fails when data types don't match schema."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        entity = Entity(schema=entity_schema, data=invalid_test_data_type_mismatch)
        
        validation_errors = entity.validate()
        assert len(validation_errors) > 0
        
        # Check for type validation errors
        assert any("has invalid type" in error for error in validation_errors)

    def test_entity_data_manipulation(self, test_json_schema):
        """Test Entity data manipulation methods."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        entity = Entity(schema=entity_schema)
        
        # Test setting values
        entity.set_value("name", "Test Entity")
        entity.set_value("processing_progress", 0.5)
        
        # Test getting values
        assert entity.get_value("name") == "Test Entity"
        assert entity.get_value("processing_progress") == 0.5
        assert entity.get_value("nonexistent") is None
        
        # Test setting invalid property
        with pytest.raises(ValueError, match="Property 'invalid_prop' not defined in schema"):
            entity.set_value("invalid_prop", "value")
        
        # Test to_dict
        data_dict = entity.to_dict()
        assert data_dict["name"] == "Test Entity"
        assert data_dict["processing_progress"] == 0.5

    def test_factory_function_creates_correct_schema(self):
        """Test that the factory function creates the correct schema."""
        schema = create_processing_object_schema()
        
        # Test schema metadata
        assert schema.id == "https://example.com/schemas/processing-object.json"
        assert schema.title == "Processing Object Schema"
        assert schema.description == "[Placeholder for schema description]"
        assert schema.additional_properties == False
        assert schema.get_required_for_scope(ValidationScope.PUBLISH) == ["name"]
        
        # Test properties exist
        expected_properties = ["id", "name", "run_id", "processing_progress", "context"]
        for prop_name in expected_properties:
            assert prop_name in schema.properties
        
        # Test specific property constraints
        name_prop = schema.properties["name"]
        assert name_prop.constraints.max_length == 25
        
        progress_prop = schema.properties["processing_progress"]
        assert progress_prop.constraints.minimum == 0
        assert progress_prop.constraints.maximum == 1

    def test_round_trip_conversion(self, test_json_schema):
        """Test that JSON -> EntitySchema -> JSON conversion preserves data."""
        # Convert JSON to EntitySchema
        entity_schema = create_entity_schema_from_json(test_json_schema)
        
        # Convert back to JSON
        exported_json = entity_schema.to_dict()
        
        # Convert again to EntitySchema
        entity_schema_2 = create_entity_schema_from_json(exported_json)
        
        # Convert back to JSON again
        exported_json_2 = entity_schema_2.to_dict()
        
        # Both JSON representations should be identical
        assert exported_json == exported_json_2

    def test_complex_validation_scenarios(self, test_json_schema):
        """Test complex validation scenarios."""
        entity_schema = create_entity_schema_from_json(test_json_schema)
        
        # Test edge case: exactly at constraint boundaries
        boundary_data = {
            "name": "A" * 25,  # Exactly at maxLength
            "processing_progress": 0,  # Exactly at minimum
        }
        entity = Entity(schema=entity_schema, data=boundary_data)
        validation_errors = entity.validate()
        assert len(validation_errors) == 0
        
        # Test edge case: just over constraint boundaries
        over_boundary_data = {
            "name": "A" * 26,  # One over maxLength
            "processing_progress": 1.1,  # Over maximum
        }
        entity = Entity(schema=entity_schema, data=over_boundary_data)
        validation_errors = entity.validate()
        assert len(validation_errors) == 2  # Both constraints violated

    def test_property_constraints_to_dict(self):
        """Test PropertyConstraints to_dict method."""
        constraints = PropertyConstraints(
            max_length=25,
            minimum=0,
            maximum=1,
            pattern=r"^[A-Za-z]+$"
        )
        
        constraint_dict = constraints.to_dict()
        expected = {
            "maxLength": 25,
            "minimum": 0,
            "maximum": 1,
            "pattern": r"^[A-Za-z]+$"
        }
        
        assert constraint_dict == expected

    def test_schema_property_to_dict(self):
        """Test SchemaProperty to_dict method."""
        constraints = PropertyConstraints(max_length=25)
        prop = SchemaProperty(
            name="test_prop",
            type=JsonSchemaType.STRING,
            description="Test property",
            constraints=constraints,
            default="default_value"
        )
        
        prop_dict = prop.to_dict()
        expected = {
            "type": "string",
            "description": "Test property",
            "default": "default_value",
            "maxLength": 25
        }
        
        assert prop_dict == expected

    def test_nested_object_properties(self):
        """Test handling of nested object properties."""
        nested_schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"}
                    },
                    "additionalProperties": False
                }
            }
        }
        
        entity_schema = create_entity_schema_from_json(nested_schema)
        user_prop = entity_schema.properties["user"]
        
        assert user_prop.type == JsonSchemaType.OBJECT
        assert user_prop.additional_properties == False
        assert "name" in user_prop.properties
        assert "age" in user_prop.properties
        assert user_prop.properties["name"].type == JsonSchemaType.STRING
        assert user_prop.properties["age"].type == JsonSchemaType.NUMBER

    def test_array_properties(self):
        """Test handling of array properties."""
        array_schema = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10
                }
            }
        }
        
        entity_schema = create_entity_schema_from_json(array_schema)
        tags_prop = entity_schema.properties["tags"]
        
        assert tags_prop.type == JsonSchemaType.ARRAY
        assert tags_prop.items.type == JsonSchemaType.STRING
        assert tags_prop.constraints.min_items == 1
        assert tags_prop.constraints.max_items == 10

    def test_scoped_validation_functionality(self):
        """Test the new scoped validation functionality."""
        # Create a schema with different required fields for different scopes
        schema = EntitySchema(
            title="Test Scoped Schema",
            app_id="TEST_APP"
        )
        
        # Add properties
        schema.add_property(SchemaProperty(name="id", type=JsonSchemaType.STRING))
        schema.add_property(SchemaProperty(name="name", type=JsonSchemaType.STRING))
        schema.add_property(SchemaProperty(name="status", type=JsonSchemaType.STRING))
        
        # Set different required fields for different scopes
        schema.set_required(ValidationScope.EXTRACT, ["id"])
        schema.set_required(ValidationScope.PUBLISH, ["id", "name", "status"])
        
        # Test data with only id
        partial_data = {"id": "123"}
        entity = Entity(schema=schema, data=partial_data)
        
        # Should pass EXTRACT validation
        extract_errors = entity.validate(ValidationScope.EXTRACT)
        assert len(extract_errors) == 0
        
        # Should fail PUBLISH validation
        publish_errors = entity.validate(ValidationScope.PUBLISH)
        assert len(publish_errors) == 2  # Missing name and status
        assert any("Required property 'name' is missing for publish scope" in error for error in publish_errors)
        assert any("Required property 'status' is missing for publish scope" in error for error in publish_errors)

    def test_app_id_functionality(self):
        """Test app_id functionality."""
        schema = EntitySchema(app_id="CUSTOM_APP")
        assert schema.app_id == "CUSTOM_APP"
        
        # Test default app_id
        default_schema = EntitySchema()
        assert default_schema.app_id == "GLOBAL"
        
        # Test app_id in to_dict_all_scopes
        all_scopes_dict = schema.to_dict_all_scopes()
        assert all_scopes_dict["x-app-id"] == "CUSTOM_APP"

    def test_scoped_json_export(self):
        """Test exporting JSON Schema for specific scopes."""
        schema = EntitySchema(title="Scoped Export Test")
        schema.add_property(SchemaProperty(name="field1", type=JsonSchemaType.STRING))
        schema.add_property(SchemaProperty(name="field2", type=JsonSchemaType.STRING))
        schema.add_property(SchemaProperty(name="field3", type=JsonSchemaType.STRING))
        
        # Set different required fields for different scopes
        schema.set_required(ValidationScope.EXTRACT, ["field1"])
        schema.set_required(ValidationScope.PUBLISH, ["field1", "field2", "field3"])
        
        # Export for EXTRACT scope
        extract_json = schema.to_dict(ValidationScope.EXTRACT)
        assert extract_json["required"] == ["field1"]
        
        # Export for PUBLISH scope
        publish_json = schema.to_dict(ValidationScope.PUBLISH)
        assert publish_json["required"] == ["field1", "field2", "field3"]
        
        # Export without scope (no required fields)
        no_scope_json = schema.to_dict()
        assert "required" not in no_scope_json

    def test_extended_json_schema_with_scopes(self):
        """Test creating EntitySchema from extended JSON Schema with scope information."""
        extended_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Extended Schema",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"}
            },
            "x-required-scopes": {
                "extract": ["id"],
                "publish": ["id", "name"]
            },
            "x-app-id": "EXTENDED_APP",
            "additionalProperties": False
        }
        
        entity_schema = create_entity_schema_from_json(extended_schema)
        
        # Test that scoped required fields were parsed correctly
        assert entity_schema.get_required_for_scope(ValidationScope.EXTRACT) == ["id"]
        assert entity_schema.get_required_for_scope(ValidationScope.PUBLISH) == ["id", "name"]
        assert entity_schema.app_id == "EXTENDED_APP"
        
        # Test round-trip with all scopes
        all_scopes_dict = entity_schema.to_dict_all_scopes()
        assert all_scopes_dict["x-required-scopes"]["extract"] == ["id"]
        assert all_scopes_dict["x-required-scopes"]["publish"] == ["id", "name"]
        assert all_scopes_dict["x-app-id"] == "EXTENDED_APP"

    def test_make_property_required_for_scope(self):
        """Test making individual properties required for specific scopes."""
        schema = EntitySchema()
        schema.add_property(SchemaProperty(name="prop1", type=JsonSchemaType.STRING))
        schema.add_property(SchemaProperty(name="prop2", type=JsonSchemaType.STRING))
        
        # Initially no required fields
        assert schema.get_required_for_scope(ValidationScope.EXTRACT) == []
        assert schema.get_required_for_scope(ValidationScope.PUBLISH) == []
        
        # Make prop1 required for EXTRACT
        schema.make_property_required(ValidationScope.EXTRACT, "prop1")
        assert schema.get_required_for_scope(ValidationScope.EXTRACT) == ["prop1"]
        assert schema.get_required_for_scope(ValidationScope.PUBLISH) == []
        
        # Make prop1 and prop2 required for PUBLISH
        schema.make_property_required(ValidationScope.PUBLISH, "prop1")
        schema.make_property_required(ValidationScope.PUBLISH, "prop2")
        assert schema.get_required_for_scope(ValidationScope.EXTRACT) == ["prop1"]
        assert schema.get_required_for_scope(ValidationScope.PUBLISH) == ["prop1", "prop2"]
        
        # Adding the same property again should not duplicate
        schema.make_property_required(ValidationScope.EXTRACT, "prop1")
        assert schema.get_required_for_scope(ValidationScope.EXTRACT) == ["prop1"]

    def test_validation_scope_enum(self):
        """Test ValidationScope enum functionality."""
        assert ValidationScope.EXTRACT.value == "extract"
        assert ValidationScope.PUBLISH.value == "publish"
        
        # Test creating from string
        extract_scope = ValidationScope("extract")
        publish_scope = ValidationScope("publish")
        assert extract_scope == ValidationScope.EXTRACT
        assert publish_scope == ValidationScope.PUBLISH
