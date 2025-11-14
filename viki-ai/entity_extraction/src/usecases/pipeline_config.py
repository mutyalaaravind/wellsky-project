"""
Use case for pipeline configuration management.
"""
from typing import Optional, Dict, Any, Tuple
from models.pipeline_config import PipelineConfig, validate_pipeline_config
from adapters.firestore import search_pipeline_config_no_cache, save_pipeline_config, archive_pipeline_config, invalidate_pipeline_config_cache, mark_pipeline_config_inactive, delete_inactive_pipeline_configs, get_pipeline_config, get_firestore_adapter
from adapters.cloud_tasks import CloudTaskAdapter
from usecases.queue_management import QueueManagementService
from util.custom_logger import getLogger
from util.exception import exceptionToMap
import settings

LOGGER = getLogger(__name__)


def increment_version(version: str) -> str:
    """
    Increment the last component of a semantic version string.
    
    Args:
        version: Semantic version string (e.g., "1.0", "1.0.0", "2.0.1")
        
    Returns:
        Incremented version string
        
    Raises:
        ValueError: If the last component is not numeric
    """
    parts = version.split('.')
    if not parts:
        raise ValueError(f"Invalid version format: {version}")
    
    try:
        # Try to increment the last component
        last_component = int(parts[-1])
        parts[-1] = str(last_component + 1)
        return '.'.join(parts)
    except ValueError:
        raise ValueError(f"Cannot increment version '{version}': last component '{parts[-1]}' is not numeric")


class PipelineConfigResult:
    """Result object for pipeline configuration operations."""
    
    def __init__(self, 
                 config: PipelineConfig, 
                 document_id: str, 
                 operation: str, 
                 archived_config_id: Optional[str] = None):
        self.config = config
        self.document_id = document_id
        self.operation = operation
        self.archived_config_id = archived_config_id


async def create_or_update_pipeline_config(scope: str, pipeline_key: str, config_data: Dict[str, Any]) -> PipelineConfigResult:
    """
    Create or update a pipeline configuration with version management and archiving.
    
    Args:
        scope: The scope of the pipeline
        pipeline_key: The key identifier of the pipeline
        config_data: The configuration data dictionary
        
    Returns:
        PipelineConfigResult with the operation details
        
    Raises:
        ValueError: If validation fails or version cannot be incremented
        Exception: If there's an error saving or archiving the configuration
    """
    extra = {
        "scope": scope,
        "pipeline_key": pipeline_key,
        "operation": "create_or_update_pipeline_config"
    }
    
    try:
        # Ensure the config data has the correct scope, key, and synthesized id
        config_data["scope"] = scope
        config_data["key"] = pipeline_key
        config_data["id"] = f"{scope}.{pipeline_key}-{config_data.get('version', '1.0.0')}"
        
        # Check if configuration already exists
        existing_config = await search_pipeline_config_no_cache(scope, pipeline_key)
        is_update = existing_config is not None
        
        # Validate the pipeline configuration
        config = validate_pipeline_config(config_data)

        # Handle version logic for updates
        archive_id = None
        if is_update:
            LOGGER.debug("Existing pipeline configuration found. Preparing to update.", extra=extra)
            existing_version = existing_config.version
            new_version = config.version
            
            if new_version is None or existing_version == new_version:
                # Same version or missing version - auto-increment
                try:
                    incremented_version = increment_version(existing_version)
                    config.version = incremented_version
                    LOGGER.debug(f"Auto-incremented version from {existing_version} to {incremented_version}", extra=extra)
                except ValueError as e:
                    # Cannot increment version - prevent update
                    extra.update({"error": exceptionToMap(e)})
                    LOGGER.error(f"Cannot increment version: {str(e)}", extra=extra)
                    raise ValueError(f"Cannot update configuration: {str(e)}")
            else:
                LOGGER.debug(f"New version does not equal old version.  Not auto incrementing: Existing: {existing_version} New: {new_version}", extra=extra)
        else:
            LOGGER.debug("No existing pipeline configuration found. Preparing to create.", extra=extra)

        # Step 1: Save the new configuration first (to avoid race conditions)
        LOGGER.debug("Saving new pipeline configuration: %s", config, extra=extra)
        document_id = await save_pipeline_config(config)
        LOGGER.debug(f"Saved new pipeline configuration with document ID: {document_id}", extra=extra)
        
        # Complete workflow for updating configuration (after new config is saved):
        if is_update:
            # Step 2: Mark the existing configuration as inactive
            LOGGER.debug("Marking existing pipeline config as inactive", extra=extra)
            await mark_pipeline_config_inactive(existing_config)
            
            # Step 3: Archive the existing configuration
            archive_id = await archive_pipeline_config(existing_config)
            LOGGER.debug("Archived existing pipeline configuration with ID: %s", archive_id, extra=extra)
            
            # Step 4: Delete all inactive versions from the active collection
            LOGGER.debug("Deleting inactive pipeline configs from active collection", extra=extra)
            deleted_count = await delete_inactive_pipeline_configs(scope, pipeline_key)
            LOGGER.debug(f"Successfully deleted {deleted_count} inactive pipeline configs from active collection", extra)
        elif config.version is None:
            config.version = "1.0.0"  # Default version for new configurations

        
        # Invalidate cache after successful save
        await invalidate_pipeline_config_cache(scope, pipeline_key)
        
        # Verify the configuration was actually saved by reading it back
        verification_config = await search_pipeline_config_no_cache(scope, pipeline_key)
        if verification_config is None:
            raise Exception(f"Failed to verify saved configuration for scope '{scope}' and key '{pipeline_key}'")
        
        # Log the operation
        operation = "updated" if is_update else "created"
        extra.update({
            "document_id": document_id,
            "archive_id": archive_id,
            "verification_successful": True
        })
        LOGGER.info(f"Pipeline configuration {operation} for scope '{scope}' and key '{pipeline_key}'", extra=extra)
        
        # Auto-provision queues for the pipeline (non-blocking)
        await _auto_provision_pipeline_queues(config)
        
        return PipelineConfigResult(
            config=config,
            document_id=document_id,
            operation=operation,
            archived_config_id=archive_id
        )
        
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Error in create_or_update_pipeline_config", extra=extra)
        raise Exception(f"Error processing pipeline configuration: {str(e)}")


async def delete_pipeline_config_by_id(pipeline_id: str) -> Dict[str, Any]:
    """
    Delete (soft delete) a pipeline configuration by its unique ID.
    
    Args:
        pipeline_id: The unique ID of the pipeline configuration
        
    Returns:
        Dict with deletion details
        
    Raises:
        ValueError: If pipeline not found
        Exception: If there's an error during deletion
    """
    extra = {
        "pipeline_id": pipeline_id,
        "operation": "delete_pipeline_config_by_id"
    }
    
    try:
        LOGGER.info(f"Deleting pipeline configuration by ID: {pipeline_id}", extra=extra)
        
        # First, get the pipeline configuration to ensure it exists
        config = await get_pipeline_config(pipeline_id)
        if config is None:
            raise ValueError(f"Pipeline configuration not found for ID '{pipeline_id}'")
        
        extra.update({
            "scope": config.scope,
            "key": config.key,
            "version": config.version
        })
        
        # Perform soft delete (mark as inactive)
        await mark_pipeline_config_inactive(config)
        
        # Invalidate cache for this pipeline configuration
        await invalidate_pipeline_config_cache(config.scope, config.key)
        
        result = {
            "message": "Pipeline configuration deleted successfully",
            "pipeline_id": pipeline_id,
            "scope": config.scope,
            "key": config.key,
            "version": config.version,
            "deleted": True
        }
        
        LOGGER.info(f"Successfully deleted pipeline configuration: {pipeline_id}", extra=extra)
        return result
        
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error deleting pipeline configuration by ID: {pipeline_id}", extra=extra)
        raise Exception(f"Error deleting pipeline configuration: {str(e)}")


async def create_pipeline_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new pipeline configuration.
    
    Args:
        config_data: The configuration data dictionary
        
    Returns:
        Dict with creation details
        
    Raises:
        ValueError: If validation fails
        Exception: If there's an error saving the configuration
    """
    extra = {
        "operation": "create_pipeline_config"
    }
    
    try:
        LOGGER.info("Creating new pipeline configuration", extra=extra)
        
        # Validate the pipeline configuration
        pipeline_config = validate_pipeline_config(config_data)
        
        extra.update({
            "scope": pipeline_config.scope,
            "key": pipeline_config.key,
            "pipeline_id": pipeline_config.id
        })
        
        # Save the configuration to Firestore
        document_id = await save_pipeline_config(pipeline_config)
        
        # Invalidate cache for this pipeline configuration
        await invalidate_pipeline_config_cache(pipeline_config.scope, pipeline_config.key)
        
        result = {
            "message": "Pipeline configuration created successfully",
            "document_id": document_id,
            "pipeline_id": pipeline_config.id,
            "scope": pipeline_config.scope,
            "key": pipeline_config.key,
            "version": pipeline_config.version,
            "configuration": pipeline_config.dict(exclude_none=True)
        }
        
        LOGGER.info(f"Successfully created pipeline configuration with ID: {pipeline_config.id}", extra=extra)
        
        # Auto-provision queues for the pipeline (non-blocking)
        await _auto_provision_pipeline_queues(pipeline_config)
        
        return result
        
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Error creating pipeline configuration", extra=extra)
        raise Exception(f"Error creating pipeline configuration: {str(e)}")


async def _auto_provision_pipeline_queues(pipeline_config: PipelineConfig) -> None:
    """
    Auto-provision cloud task queues for a pipeline configuration.
    
    This function runs asynchronously and non-blocking. If queue provisioning
    fails, it logs the error but doesn't fail the pipeline creation/update.
    
    Args:
        pipeline_config: The pipeline configuration to provision queues for
    """
    extra = {
        "operation": "_auto_provision_pipeline_queues",
        "pipeline_id": pipeline_config.id,
        "pipeline_key": pipeline_config.key,
        "pipeline_scope": pipeline_config.scope
    }
    
    try:
        LOGGER.info(f"Starting queue auto-provisioning for pipeline {pipeline_config.key}", extra=extra)
        
        # Initialize the queue management service
        firestore_adapter = get_firestore_adapter()
        cloud_tasks_adapter = CloudTaskAdapter()
        
        # Get PaperGlass API URL from settings if available
        paperglass_api_url = getattr(settings, 'PAPERGLASS_API_URL', None)
        
        queue_service = QueueManagementService(
            firestore_adapter=firestore_adapter,
            cloud_tasks_adapter=cloud_tasks_adapter,
            paperglass_api_url=paperglass_api_url
        )
        
        # Provision queues for the pipeline
        result = await queue_service.provision_queues_for_pipeline(pipeline_config)
        
        # Log the results
        extra.update({
            "total_created": result.total_created,
            "total_existing": result.total_existing,
            "total_failed": result.total_failed,
            "success": result.success,
            "duration_seconds": result.duration_seconds
        })
        
        if result.success:
            LOGGER.info(f"Queue auto-provisioning completed successfully for pipeline {pipeline_config.key}", extra=extra)
        else:
            LOGGER.warning(f"Queue auto-provisioning completed with failures for pipeline {pipeline_config.key}: {result.error_message}", extra=extra)
        
        # Close resources
        await cloud_tasks_adapter.close()
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error(f"Error during queue auto-provisioning for pipeline {pipeline_config.key}: {str(e)}", extra=extra)
        # Don't re-raise - queue provisioning failures shouldn't break pipeline operations
