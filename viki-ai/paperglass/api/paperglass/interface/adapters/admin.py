import json
from logging import getLogger
import traceback
from typing import Dict, Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import ValidationError, BaseModel, Field
from kink import inject

from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.log import CustomLogger
from paperglass.domain.model_entities import EntitySchema, create_entity_schema_from_json
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort
from paperglass.usecases.commands import CreateEntitySchema, ProcessOnboardingWizard, CreateAppConfiguration, CreateTenantConfiguration, UpdateAppConfiguration, UpdateTenantConfiguration
from paperglass.domain.values import Configuration

LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)


class EntitySchemaRequest(BaseModel):
    """Request model for entity schema creation/update with meta attributes in envelope."""
    
    name: str = Field(..., description="Human-readable name for the entity schema")
    description: Optional[str] = Field(None, description="Description of the entity schema")
    app_id: str = Field(..., description="Application ID this schema belongs to")
    label: Optional[str] = Field(None, description="UI-friendly label for the schema")
    required_scopes: Optional[Dict[str, list]] = Field(None, description="Scope-specific required fields mapping")
    entity_schema: Dict[str, Any] = Field(..., description="Pure JSON schema without meta attributes", alias="schema")


class AdminAdapter:
    """Admin endpoints for administrative operations."""

    @inject
    async def get_entity_schema(self, request: Request, query: IQueryPort):
        """Get an entity schema by FQN endpoint."""
        extra = {}
        try:
            # Get the fqn query parameter
            fqn = request.query_params.get('fqn')
            
            if not fqn:
                return JSONResponse({
                    'success': False,
                    'error': 'Missing required query parameter: fqn'
                }, status_code=400)
            
            extra = {
                "fqn": fqn,
            }
            
            LOGGER2.info("Retrieving entity schema with FQN: %s", fqn, extra=extra)
            
            # Query the entity schema by FQN
            try:
                entity_schema = await query.get_entity_schema_by_fqn(fqn)
                
                if not entity_schema:
                    LOGGER2.warning("Entity schema not found with FQN: %s", fqn, extra=extra)
                    return JSONResponse({
                        'success': False,
                        'error': f'Entity schema not found with FQN: {fqn}'
                    }, status_code=404)
                
                # Convert the EntitySchemaAggregate to a response format
                response_data = {
                    'success': True,
                    'entity_schema': {
                        'id': entity_schema.id,
                        'schema_id': entity_schema.schema_id,
                        'fqn': entity_schema.fqn,
                        'title': entity_schema.title,
                        'label': entity_schema.label,
                        'app_id': entity_schema.app_id,
                        'active': entity_schema.active,
                        'schema_data': entity_schema.schema_data,
                        'created_at': entity_schema.created_at.isoformat() if hasattr(entity_schema, 'created_at') and entity_schema.created_at else None,
                        'modified_at': entity_schema.modified_at.isoformat() if hasattr(entity_schema, 'modified_at') and entity_schema.modified_at else None
                    }
                }
                
                LOGGER2.info("Successfully retrieved entity schema: %s", entity_schema.schema_id, extra=extra)
                return JSONResponse(response_data, status_code=200)
                
            except AttributeError as e:
                # If get_entity_schema_by_fqn doesn't exist in the query interface
                LOGGER2.error("Query method not implemented: get_entity_schema_by_fqn", extra=extra)
                return JSONResponse({
                    'success': False,
                    'error': 'Entity schema retrieval not implemented',
                    'details': 'get_entity_schema_by_fqn method not available'
                }, status_code=501)  # 501 Not Implemented
                
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error retrieving entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def create_entity_schema(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        """Create a new entity schema endpoint with meta attributes in request envelope."""
        extra = {}
        try:
            payload = await request.json()
            extra = {
                "payload": payload,
            }
            
            # Validate using the new request model
            try:
                entity_request = EntitySchemaRequest(**payload)
            except ValidationError as e:
                LOGGER2.error("Invalid EntitySchemaRequest payload: %s", e.errors(), extra=extra)
                return JSONResponse({
                    'success': False, 
                    'error': 'Invalid request format',
                    'details': e.errors()
                }, status_code=400)
            
            # Build the JSON schema with meta attributes for processing
            json_schema = entity_request.entity_schema.copy()
            
            # Add meta attributes back to the schema for processing by existing domain logic
            if entity_request.app_id:
                json_schema["x-app-id"] = entity_request.app_id
            if entity_request.label:
                json_schema["x-label"] = entity_request.label
            if entity_request.required_scopes:
                json_schema["x-required-scopes"] = entity_request.required_scopes
                
            # Set title and description from envelope if not present in schema
            if entity_request.name and "title" not in json_schema:
                json_schema["title"] = entity_request.name
            if entity_request.description and "description" not in json_schema:
                json_schema["description"] = entity_request.description
            
            # Validate that the combined schema represents a valid EntitySchema
            try:
                entity_schema = create_entity_schema_from_json(json_schema)
            except Exception as e:
                LOGGER2.error("Invalid EntitySchema after processing: %s", str(e), extra=extra)
                return JSONResponse({
                    'success': False, 
                    'error': 'Invalid EntitySchema format after processing',
                    'details': str(e)
                }, status_code=400)
            
            # Check if schema ID is provided
            if not entity_schema.id:
                return JSONResponse({
                    'success': False, 
                    'error': 'EntitySchema must have an $id field'
                }, status_code=400)
            
            # Check if a schema with this ID already exists in Firestore
            try:
                # For now, we'll check by querying all entity schemas and filtering by schema_id
                # This is a temporary implementation until get_entity_schema_by_id is properly implemented
                existing_schemas = await query.list_entity_schemas()
                existing_schema = None
                
                if existing_schemas:
                    for schema in existing_schemas:
                        if hasattr(schema, 'schema_id') and schema.schema_id == entity_schema.id:
                            existing_schema = schema
                            break
                
                if existing_schema:
                    LOGGER2.warning("Schema with ID already exists: %s", entity_schema.id, extra=extra)
                    return JSONResponse({
                        'success': False, 
                        'error': f'A schema with ID "{entity_schema.id}" already exists',
                        'existing_schema_id': existing_schema.schema_id,
                        'existing_schema_title': existing_schema.title if hasattr(existing_schema, 'title') else None
                    }, status_code=409)  # 409 Conflict
                    
            except AttributeError:
                # If list_entity_schemas doesn't exist, skip the check for now
                LOGGER2.warning("Entity schema existence check skipped - query method not implemented", extra=extra)
            except Exception as e:
                LOGGER2.error("Error checking for existing schema: %s", str(e), extra=extra)
                return JSONResponse({
                    'success': False, 
                    'error': 'Error checking for existing schema',
                    'details': str(e)
                }, status_code=500)
            
            # Create entity_schema_dict that contains just the pure schema without meta attributes
            # The CreateEntitySchema command will handle the persistence
            entity_schema_dict = {
                'app_id': entity_request.app_id,
                'schema_id': entity_schema.id,
                'title': entity_request.name,
                'label': entity_request.label,
                'description': entity_request.description,
                'version': json_schema.get('version', '1.0'),
                'schema': entity_request.entity_schema  # Pure JSON schema without meta attributes
            }
            
            # Create the command to persist the schema
            command = CreateEntitySchema(entity_schema_dict=entity_schema_dict)
            
            # Execute the command
            result = await commands.handle_command(command)
            
            LOGGER2.info("Successfully created entity schema with ID: %s", entity_schema.id, extra=extra)
            
            return JSONResponse({
                'success': True,
                'schema_id': entity_schema.id,
                'message': 'Entity schema created successfully'
            }, status_code=201)
            
        except ValidationError as e:
            extra.update({'errors': exceptionToMap(e)})
            LOGGER2.error("Validation error creating entity schema: %s", e.errors(), extra=extra)
            return JSONResponse({
                'success': False, 
                'errors': e.errors()
            }, status_code=400)
        except Exception as e:
            extra.update({'errors': exceptionToMap(e)})
            LOGGER2.error("Error creating entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False, 
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def create_or_update_app_config(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        """Create or update app configuration."""
        extra = {}
        try:
            payload = await request.json()
            extra = {
                "payload": payload,
            }
            
            # Validate required fields
            if 'app_id' not in payload:
                return JSONResponse({
                    'success': False, 
                    'error': 'Missing required field: app_id'
                }, status_code=400)
            
            app_id = payload['app_id']
            tenant_id = payload.get('tenant_id')
            config_data = payload.get('config', {})
            name = payload.get('name')  # Extract root-level name
            description = payload.get('description')  # Extract root-level description
            active = payload.get('active', True)
            archive_current = payload.get('archive_current', True)
            version_comment = payload.get('version_comment')
            
            # Check if entity schema should be created (for onboarding generation)
            entity_schema_data = payload.get('entity_schema')
            entity_name = payload.get('entity_name')
            entity_description = payload.get('entity_description')
            schema_created_id = None
            
            extra.update({
                "app_id": app_id,
                "tenant_id": tenant_id,
                "name": name,
                "description": description,
                "active": active,
                "archive_current": archive_current,
                "has_config_data": bool(config_data)
            })
            
            LOGGER2.info("Creating/updating app configuration", extra=extra)
            
            # Create Configuration object from config data
            config = Configuration(**config_data) if config_data else Configuration()
            
            # Check if configuration already exists to determine create vs update
            if tenant_id:
                existing_config = await query.get_app_tenant_config(app_id, tenant_id)
                config_type = "tenant"
            else:
                existing_config = await query.get_app_config(app_id)
                config_type = "app"
            
            # Determine which command to use based on existence and tenant_id
            if existing_config:
                # Configuration exists, use update command
                if tenant_id:
                    command = UpdateTenantConfiguration(
                        app_id=app_id,
                        tenant_id=tenant_id,
                        name=name,
                        description=description,
                        config=config,
                        archive_current=archive_current,
                        version_comment=version_comment
                    )
                else:
                    command = UpdateAppConfiguration(
                        app_id=app_id,
                        name=name,
                        description=description,
                        config=config,
                        archive_current=archive_current,
                        version_comment=version_comment
                    )
                operation = "updated"
            else:
                # Configuration doesn't exist, use create command
                if tenant_id:
                    command = CreateTenantConfiguration(
                        app_id=app_id,
                        tenant_id=tenant_id,
                        name=name,
                        description=description,
                        config=config
                    )
                else:
                    command = CreateAppConfiguration(
                        app_id=app_id,
                        name=name,
                        description=description,
                        config=config
                    )
                operation = "created"
            
            # Execute the command
            result = await commands.handle_command(command)
            
            LOGGER2.info("Successfully %s %s configuration for app_id: %s", operation, config_type, app_id, extra=extra)
            
            # Create entity schema if provided (for onboarding generation)
            if entity_schema_data and entity_name:
                schema_created_id = await self._create_entity_schema_for_onboarding(
                    app_id, entity_name, entity_description, entity_schema_data, commands, extra
                )
            
            # Build response message
            message = f'{config_type.capitalize()} configuration {operation} successfully'
            if schema_created_id:
                message += f' and entity schema created'
            
            return JSONResponse({
                'success': True,
                'message': message,
                'data': {
                    'id': result.id if hasattr(result, 'id') else None,
                    'app_id': app_id,
                    'name': result.name if hasattr(result, 'name') else name,
                    'description': result.description if hasattr(result, 'description') else description,
                    'tenant_id': tenant_id,
                    'active': active,
                    'config_type': config_type,
                    'operation': operation,
                    'entity_schema_id': schema_created_id,
                    'config': result.config.dict() if hasattr(result, 'config') and result.config else None
                }
            })
            
        except ValidationError as e:
            extra.update({'errors': exceptionToMap(e)})
            LOGGER2.error("Validation error in create_or_update_app_config: %s", e.errors(), extra=extra)
            return JSONResponse({
                'success': False, 
                'error': 'Validation error',
                'details': e.errors()
            }, status_code=400)
            
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error in create_or_update_app_config: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False, 
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def process_onboarding_wizard(self, request: Request, commands: ICommandHandlingPort):
        """Process onboarding wizard with PDF document and configuration."""
        extra = {}
        try:
            # Get form data
            form = await request.form()
            
            # Extract JSON payload from 'data' field
            data_field = form.get('data')
            if not data_field:
                return JSONResponse({
                    'success': False,
                    'error': 'Missing required field: data (JSON payload)'
                }, status_code=400)
            
            # Parse JSON data
            try:
                data = json.loads(data_field)
            except json.JSONDecodeError as e:
                return JSONResponse({
                    'success': False,
                    'error': 'Invalid JSON in data field',
                    'details': str(e)
                }, status_code=400)
            
            # Extract fields from JSON data
            business_unit = data.get('business_unit')
            solution_id = data.get('solution_id')
            app_id = data.get('app_id')
            entity_name = data.get('entity_name')
            entity_data_description = data.get('entity_data_description')
            extraction_prompt = data.get('extraction_prompt')
            peak_docs_per_minute = data.get('peak_docs_per_minute')
            processing_time_sla_max = data.get('processing_time_sla_max')
            
            # Get PDF file
            pdf_file = form.get('file')
            
            extra = {
                "business_unit": business_unit,
                "solution_id": solution_id,
                "app_id": app_id,
                "entity_name": entity_name,
                "peak_docs_per_minute": peak_docs_per_minute,
                "processing_time_sla_max": processing_time_sla_max,
                "has_pdf_file": pdf_file is not None,
                "pdf_filename": pdf_file.filename if pdf_file else None,
            }
            
            LOGGER2.info("Processing onboarding wizard request", extra=extra)
            
            # Validate required fields
            if not all([business_unit, solution_id, app_id, entity_name, entity_data_description, 
                       extraction_prompt, peak_docs_per_minute is not None, processing_time_sla_max is not None, pdf_file]):
                missing_fields = []
                if not business_unit: missing_fields.append('business_unit')
                if not solution_id: missing_fields.append('solution_id')
                if not app_id: missing_fields.append('app_id')
                if not entity_name: missing_fields.append('entity_name')
                if not entity_data_description: missing_fields.append('entity_data_description')
                if not extraction_prompt: missing_fields.append('extraction_prompt')
                if peak_docs_per_minute is None: missing_fields.append('peak_docs_per_minute')
                if processing_time_sla_max is None: missing_fields.append('processing_time_sla_max')
                if not pdf_file: missing_fields.append('file')
                
                return JSONResponse({
                    'success': False,
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }, status_code=400)
            
            # Validate numeric fields
            try:
                peak_docs_per_minute = float(peak_docs_per_minute)
                processing_time_sla_max = int(processing_time_sla_max)
            except (ValueError, TypeError) as e:
                return JSONResponse({
                    'success': False,
                    'error': 'Invalid numeric values for peak_docs_per_minute or processing_time_sla_max',
                    'details': str(e)
                }, status_code=400)
            
            # Validate PDF file
            if not pdf_file.filename.lower().endswith('.pdf'):
                return JSONResponse({
                    'success': False,
                    'error': 'File must be a PDF document'
                }, status_code=400)
            
            # Read PDF file content
            pdf_content = await pdf_file.read()
            
            # Create the command
            command = ProcessOnboardingWizard(
                business_unit=business_unit,
                solution_id=solution_id,
                app_id=app_id,
                entity_name=entity_name,
                entity_data_description=entity_data_description,
                extraction_prompt=extraction_prompt,
                peak_docs_per_minute=peak_docs_per_minute,
                processing_time_sla_max=processing_time_sla_max,
                pdf_file=pdf_content
            )
            
            # Execute the command
            result = await commands.handle_command(command)
            
            LOGGER2.info("Successfully processed onboarding wizard", extra=extra)
            
            return JSONResponse({
                'success': True,
                'message': 'Onboarding wizard processed successfully',
                'document_id': result.get('document_id') if result else None,
                'pipeline_execution_id': result.get('pipeline_execution_id') if result else None
            }, status_code=200)
            
        except ValidationError as e:
            extra.update({'errors': exceptionToMap(e)})
            LOGGER2.error("Validation error processing onboarding wizard: %s", e.errors(), extra=extra)
            return JSONResponse({
                'success': False, 
                'errors': e.errors()
            }, status_code=400)
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error processing onboarding wizard: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False, 
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)
    
    async def _create_entity_schema_for_onboarding(
        self, 
        app_id: str, 
        entity_name: str, 
        entity_description: str, 
        entity_schema_data: Dict[str, Any], 
        commands: ICommandHandlingPort,
        extra: Dict[str, Any]
    ) -> str:
        """
        Create an entity schema for onboarding generation by calling the PaperGlass API internally.
        
        Args:
            app_id: Application ID
            entity_name: Name of the entity
            entity_description: Description of the entity
            entity_schema_data: The generated JSON schema from LLM
            commands: Command handling port for executing commands
            extra: Extra logging context
            
        Returns:
            The schema ID if created successfully, empty string if failed
        """
        try:
            # Extract schema ID from the JSON schema's $id field
            schema_id = None
            schema_uri = entity_schema_data.get('$id')
            if schema_uri:
                # Extract schema_id from URI (e.g., "entity_name" from "https://viki.ai/schemas/app/entity_name.json")
                schema_id = schema_uri.split('/')[-1].replace('.json', '')
            
            if not schema_id:
                # Fallback: generate schema_id from entity_name
                schema_id = entity_name.lower().replace(' ', '_').replace('-', '_')
            
            # Create entity schema using new envelope structure 
            entity_schema_dict = {
                'app_id': app_id,
                'schema_id': schema_id,
                'title': entity_schema_data.get('title', f"{entity_name} Schema"),
                'label': entity_name,
                'description': entity_description or entity_schema_data.get('description', ''),
                'version': '1.0',
                'schema': entity_schema_data  # Pure JSON schema without meta attributes
            }
            
            # Create the CreateEntitySchema command
            schema_command = CreateEntitySchema(entity_schema_dict=entity_schema_dict)
            
            # Execute the command to create the entity schema
            await commands.handle_command(schema_command)
            
            LOGGER2.info("Successfully created entity schema %s for app_id: %s during onboarding", 
                        schema_id, app_id, extra=extra)
            
            return schema_id
            
        except Exception as e:
            LOGGER2.error("Failed to create entity schema for onboarding: %s", str(e), extra=extra)
            # Don't fail the entire config operation if schema creation fails
            return ""
