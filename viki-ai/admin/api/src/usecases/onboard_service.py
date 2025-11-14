from typing import Optional
from kink import inject
from viki_shared.utils.logger import getLogger

from contracts.paperglass import PaperglassPort, AppConfigUpdateRequest, EntitySchemaCreateRequest
from contracts.entity_extraction_contracts import EntityExtractionPort
from usecases.onboard_commands import SaveOnboardConfigCommand, CheckAppConfigExistsQuery
from models.onboard_models import OnboardSaveResponse

logger = getLogger(__name__)


@inject
class OnboardService:
    """Service for handling onboard commands and queries following hexagonal architecture"""

    def __init__(self, paperglass_port: PaperglassPort, entity_extraction_port: EntityExtractionPort):
        self.paperglass_port = paperglass_port
        self.entity_extraction_port = entity_extraction_port

    async def handle_save_onboard_config(self, command: SaveOnboardConfigCommand) -> OnboardSaveResponse:
        """
        Handle save onboard config command.
        
        This creates a new app configuration using the Paperglass API's default generation.
        
        Args:
            command: The save onboard config command
            
        Returns:
            OnboardSaveResponse: Response indicating success and config creation status
            
        Raises:
            Exception: If there's an error creating the configuration
        """
        logger.info(f"Handling save onboard config command for app_id: {command.app_id}")
        logger.info(f"Command parameters - business_unit: {command.business_unit}, solution_code: {command.solution_code}")
        
        try:
            # Check if config already exists
            existing_config = await self.paperglass_port.get_app_config(command.app_id, generate_if_missing=False)
            config_created = existing_config is None
            
            if existing_config:
                logger.warning(f"App config already exists for app_id: {command.app_id}. Skipping creation.")
                return OnboardSaveResponse(
                    success=True,
                    message=f"App configuration already exists for {command.app_id}",
                    app_id=command.app_id,
                    config_created=False,
                    entity_schema_id=None,
                    pipeline_key=None
                )
            
            # Create the new app configuration using Paperglass default generation
            new_config = await self.paperglass_port.get_app_config(command.app_id, generate_if_missing=True)
            
            if not new_config:
                raise Exception("Failed to generate default app configuration")
            
            # Always update the basic config information from onboarding wizard
            pipeline_key = None
            entity_schema_id = None
            
            # Get the current config and add onboarding-specific fields
            if not new_config.config:
                logger.error(f"new_config.config is None for app_id: {command.app_id}")
                raise Exception("Generated app configuration has no config data")
            
            updated_config = new_config.config.copy()
            
            if not updated_config:
                logger.error(f"updated_config is None after copy for app_id: {command.app_id}")
                raise Exception("Failed to copy configuration data")
            
            # Set the config name and description from onboarding wizard
            if command.app_name:
                logger.info(f"Setting config name to: {command.app_name} (was: {updated_config.get('name', 'not set')})")
                updated_config["name"] = command.app_name
            if command.app_description:
                logger.info(f"Setting config description to: {command.app_description}")
                updated_config["description"] = command.app_description
            
            # Debug: Log the updated config structure
            logger.info(f"Updated config after setting name/description: name={updated_config.get('name')}, app_id={command.app_id}")
            
            # Add/Update accounting block with business_unit and solution_code
            logger.info(f"Setting accounting info - business_unit: {command.business_unit}, solution_code: {command.solution_code}")
            logger.info(f"updated_config type: {type(updated_config)}, keys before: {list(updated_config.keys()) if hasattr(updated_config, 'keys') else 'No keys method'}")
            
            if "accounting" not in updated_config or updated_config["accounting"] is None:
                logger.info(f"Creating accounting dict in updated_config")
                updated_config["accounting"] = {}
                logger.info(f"Set accounting to empty dict, now checking value...")
                logger.info(f"updated_config['accounting'] = {updated_config['accounting']}, type = {type(updated_config['accounting'])}")
            else:
                logger.info(f"Accounting already exists: {updated_config['accounting']}")
            
            # Critical debug check
            if updated_config["accounting"] is None:
                logger.error(f"updated_config['accounting'] is None after creation for app_id: {command.app_id}")
                logger.error(f"Full updated_config: {updated_config}")
                raise Exception("Accounting dictionary is None after creation")
            
            logger.info(f"Accounting dict created successfully, type: {type(updated_config['accounting'])}")
            
            if command.business_unit is None:
                logger.error(f"command.business_unit is None for app_id: {command.app_id}")
                raise Exception("business_unit cannot be None")
            
            if command.solution_code is None:
                logger.error(f"command.solution_code is None for app_id: {command.app_id}")
                raise Exception("solution_code cannot be None")
            
            logger.info(f"About to set business_unit on accounting dict")
            updated_config["accounting"]["business_unit"] = command.business_unit
            logger.info(f"Successfully set business_unit, about to set solution_code")
            updated_config["accounting"]["solution_code"] = command.solution_code
            
            logger.info(f"Successfully set accounting info for app_id: {command.app_id}")
            
            # If we have onboarding artifacts, process them
            logger.info(f"Checking artifacts - entity_schema: {command.entity_schema is not None}, extraction_prompt: {command.extraction_prompt is not None}, pipeline_template: {command.pipeline_template is not None}")
            if any([command.entity_schema, command.extraction_prompt, command.pipeline_template]):
                logger.info(f"Processing onboarding artifacts for app_id: {command.app_id}")
                
                # Step 1: Create entity schema via PaperGlass API if provided
                if command.entity_schema:
                    entity_schema_id = await self._create_entity_schema(command)
                    logger.info(f"Created entity schema {entity_schema_id} for app_id: {command.app_id}")
                
                # Step 2: Create pipeline via Entity Extraction API if template provided
                if command.pipeline_template:
                    pipeline_key = await self._create_pipeline_from_template(command)
                    logger.info(f"Created pipeline {pipeline_key} for app_id: {command.app_id}")
                
                # Step 3: Update config with references to created artifacts
                logger.info(f"Updating config with onboarding artifacts for app_id: {command.app_id}")
                
                # Add onboarding metadata for reference
                onboarding_metadata = {
                    "business_unit": command.business_unit,
                    "solution_code": command.solution_code
                }
                
                if command.app_name:
                    onboarding_metadata["app_name"] = command.app_name
                if command.app_description:
                    onboarding_metadata["app_description"] = command.app_description
                if entity_schema_id:
                    onboarding_metadata["entity_schema_id"] = entity_schema_id
                if pipeline_key:
                    onboarding_metadata["pipeline_key"] = pipeline_key
                
                updated_config["onboarding_metadata"] = onboarding_metadata
                
                # Add entity extraction configuration
                if "entity_extraction" not in updated_config:
                    updated_config["entity_extraction"] = {
                        "enabled": True,
                        "version": "1",
                        "pipeline_default": pipeline_key or "default.start"
                    }
                else:
                    updated_config["entity_extraction"]["enabled"] = True
                    if pipeline_key:
                        updated_config["entity_extraction"]["pipeline_default"] = pipeline_key
                
                if command.extraction_prompt:
                    updated_config["entity_extraction"]["extraction_prompt"] = command.extraction_prompt
            
            # Always update the configuration via Paperglass API (with basic info and artifacts if any)
            logger.info(f"About to update config - final config name: {updated_config.get('name')}, app_id: {command.app_id}")
            
            # Extract name and description to root level for PaperGlass API
            config_name = updated_config.get('name')
            config_description = updated_config.get('description')
            
            config_update_request = AppConfigUpdateRequest(
                config=updated_config,
                name=config_name,  # Pull name to root level
                description=config_description,  # Pull description to root level
                archive_current=True,  # Archive the default config
                version_comment=f"Updated with onboarding configuration for {command.app_id}"
            )
            
            new_config = await self.paperglass_port.update_app_config(command.app_id, config_update_request)
            logger.info(f"Successfully updated config with onboarding configuration")
            logger.info(f"Updated config returned - name: {new_config.name or 'no name'}, app_id: {command.app_id}")
            
            logger.info(f"Successfully created app config for app_id: {command.app_id}")
            logger.info(f"Config ID: {new_config.id}, Active: {new_config.active}")
            
            return OnboardSaveResponse(
                success=True,
                message=f"App configuration created successfully for {command.app_id}",
                app_id=command.app_id,
                config_created=config_created,
                entity_schema_id=entity_schema_id,
                pipeline_key=pipeline_key
            )
            
        except Exception as e:
            logger.error(f"Error in save onboard config command for app_id {command.app_id}: {str(e)}")
            raise

    async def check_app_config_exists(self, query: CheckAppConfigExistsQuery) -> bool:
        """
        Check if app config exists.
        
        Args:
            query: The check app config exists query
            
        Returns:
            bool: True if config exists, False otherwise
        """
        logger.debug(f"Checking if app config exists for app_id: {query.app_id}")
        
        try:
            existing_config = await self.paperglass_port.get_app_config(query.app_id, generate_if_missing=False)
            return existing_config is not None
            
        except Exception as e:
            logger.error(f"Error checking app config existence for app_id {query.app_id}: {str(e)}")
            # In case of error, assume it doesn't exist to allow creation attempt
            return False

    async def _create_entity_schema(self, command: SaveOnboardConfigCommand) -> str:
        """
        Create entity schema via PaperGlass API using the new envelope structure.
        
        Args:
            command: The save onboard config command containing schema data
            
        Returns:
            The schema ID of the created entity schema
            
        Raises:
            Exception: If entity schema creation fails
        """
        logger.info(f"Creating entity schema for app_id: {command.app_id}")
        
        # Generate proper schema_id from app name (lowercased with spaces to hyphens)
        entity_name = command.app_name or "generated_entity"
        schema_id = entity_name.lower().replace(' ', '-').replace('_', '-')
        
        # Prepare the JSON schema with required fields for PaperGlass
        schema_data = command.entity_schema.copy()
        
        # Get the base URL from settings (environment/config)
        from settings import Settings
        settings = Settings()
        # Use the paperglass API URL directly
        base_url = settings.PAPERGLASS_API_URL
        
        # Set the required metadata fields
        schema_data['$id'] = f"{base_url}/api/schemas/{command.app_id}/{schema_id}.json"
        schema_data['x-app-id'] = command.app_id  # Ensure app_id is set correctly
        schema_data['x-schema-id'] = schema_id  # Set the schema_id
        
        # Prepare the entity schema creation request
        schema_request = EntitySchemaCreateRequest(
            name=command.entity_schema.get('title', command.app_name or "Generated Entity Schema"),
            description=command.app_description or command.entity_schema.get('description', ''),
            app_id=command.app_id,  # Use the actual app_id
            label=command.app_name,  # Use app name as label
            required_scopes=None,  # Could be extracted from schema extensions in future
            schema=schema_data  # JSON schema with proper metadata
        )
        
        # Call PaperGlass API to create the entity schema
        logger.info(f"Calling PaperGlass API to create entity schema for app_id: {command.app_id}")
        response = await self.paperglass_port.create_entity_schema(schema_request)
        
        logger.info(f"Successfully created entity schema: {response.schema_id} for app_id: {command.app_id}")
        return response.schema_id

    async def _create_pipeline_from_template(self, command: SaveOnboardConfigCommand) -> str:
        """
        Create pipeline from template via Entity Extraction API.
        
        Args:
            command: The save onboard config command containing pipeline template
            
        Returns:
            The pipeline key (scope.pipeline_id) of the created pipeline
            
        Raises:
            Exception: If pipeline creation fails
        """
        logger.info(f"Creating pipeline from template for app_id: {command.app_id}")
        
        try:
            # Generate pipeline identifiers
            scope = command.app_id
            entity_name = command.app_name or "entity"
            pipeline_id = f"{entity_name.lower().replace(' ', '_').replace('-', '_')}_extraction"
            pipeline_key = f"{scope}.{pipeline_id}"
            
            # Determine template ID (use provided template or default)
            template_id = command.pipeline_template or "default_entity_extraction_template"
            
            # Create pipeline configuration with token replacement
            pipeline_config = {
                "app_id": command.app_id,
                "entity_name": command.app_name or "Entity",
                "entity_description": command.app_description or "",
                "business_unit": command.business_unit,
                "solution_code": command.solution_code,
                "extraction_prompt": command.extraction_prompt,  # Pass the production prompt
                "token_replacements": {
                    "app_id": command.app_id,
                    "entity_name": entity_name.lower().replace(' ', '_'),
                    "business_unit": command.business_unit
                }
            }
            
            # Call Entity Extraction API to create pipeline from template
            created_pipeline = await self.entity_extraction_port.create_pipeline_from_template(
                template_id=template_id,
                scope=scope,
                pipeline_id=pipeline_id,
                pipeline_config=pipeline_config
            )
            
            logger.info(f"Successfully created pipeline {pipeline_key} from template {template_id}")
            return created_pipeline.key if created_pipeline.key else pipeline_key
            
        except Exception as e:
            logger.error(f"Error creating pipeline for app_id {command.app_id}: {str(e)}")
            raise