from fastapi import APIRouter, HTTPException, Request, Depends, Query
from adapters.firestore import search_pipeline_config, list_active_pipeline_configs, get_firestore_adapter
from usecases.pipeline_config import create_or_update_pipeline_config, delete_pipeline_config_by_id, create_pipeline_config
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from models.pipeline_config import pipeline_config_to_dict, validate_pipeline_config
from typing import Dict, Any

LOGGER = getLogger(__name__)

# Create router for config endpoints
router = APIRouter(prefix="/config", tags=["configuration"])

@router.get("/pipelines")
async def list_all_pipeline_configs(
    labels: list[str] = Query(None, description="Filter by labels - only configs containing ALL specified labels will be returned"),
    app_id: str = Query(None, description="Filter by app_id - only configs with the specified app_id will be returned")
):
    """List all active pipeline configurations in the system."""
    try:
        configs = await list_active_pipeline_configs(labels=labels, app_id=app_id)
        return {
            "configurations": [pipeline_config_to_dict(config) for config in configs],
            "count": len(configs),
            "filters": {
                "labels": labels,
                "app_id": app_id
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pipeline configurations: {str(e)}"
        )

@router.get("/pipelines/{scope}/{pipeline_key}")
async def get_pipeline_config(scope: str, pipeline_key: str):
    """Retrieve a pipeline configuration from Firestore by scope and key."""
    try:
        config = await search_pipeline_config(scope, pipeline_key)
        if config is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Pipeline configuration not found for scope '{scope}' and key '{pipeline_key}'"
            )
        return config.dict(exclude_none=True)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pipeline configuration: {str(e)}"
        )

@router.post("/pipelines/{scope}/{pipeline_key}")
async def create_or_update_pipeline_config_endpoint(
    scope: str,
    pipeline_key: str,
    config_data: dict,
    request: Request
):
    """Create or update a pipeline configuration in Firestore."""
    
    extra = {
        "http_request": {
            "method": "POST",
            "url": f"/api/config/{scope}/{pipeline_key}",
            "body": config_data,
            "headers": dict(request.headers),
        },
        "scope": scope,
        "pipeline_key": pipeline_key
    }
    
    try:
        # Use the pipeline config usecase
        result = await create_or_update_pipeline_config(scope, pipeline_key, config_data)
        
        # Build response
        response = {
            "message": f"Pipeline configuration {result.operation} successfully",
            "scope": scope,
            "pipeline_key": pipeline_key,
            "document_id": result.document_id,
            "operation": result.operation,
            "configuration": result.config.dict(exclude_none=True)
        }
        
        # Include archive information if this was an update
        if result.archived_config_id:
            response["archived_config_id"] = result.archived_config_id
        
        return response
        
    except ValueError as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Validation error in pipeline configuration", extra)
        raise HTTPException(
            status_code=422,
            detail=f"Invalid pipeline configuration: {str(e)}"
        )
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Error saving pipeline configuration", extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving pipeline configuration: {str(e)}"
        )

@router.get("/pipelines/{pipeline_id}")
async def get_pipeline_config_by_id(
    pipeline_id: str
):
    """Retrieve a pipeline configuration by its unique ID."""
    
    extra = {
        "pipeline_id": pipeline_id
    }
    
    try:
        LOGGER.info(f"Retrieving pipeline configuration by ID: {pipeline_id}", extra=extra)
        
        adapter = get_firestore_adapter()
        config = await adapter.get_pipeline_config(pipeline_id)
        if config is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Pipeline configuration not found for ID '{pipeline_id}'"
            )
        
        LOGGER.info(f"Successfully retrieved pipeline configuration: {pipeline_id}", extra=extra)
        return config.dict(exclude_none=True)
        
    except HTTPException:
        raise
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error retrieving pipeline configuration by ID: {pipeline_id}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pipeline configuration: {str(e)}"
        )

@router.post("/pipelines")
async def create_pipeline_config_endpoint(
    config_data: dict,
    request: Request
):
    """Create a new pipeline configuration."""
    
    extra = {
        "http_request": {
            "method": "POST",
            "url": "/api/config/pipelines",
            "body": config_data,
            "headers": dict(request.headers),
        }
    }
    
    try:
        LOGGER.info("Creating new pipeline configuration", extra=extra)
        
        # Use the application layer to create the configuration
        result = await create_pipeline_config(config_data)
        
        LOGGER.info(f"Successfully created pipeline configuration", extra=extra)
        return result
        
    except ValueError as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Validation error in pipeline configuration", extra=extra)
        raise HTTPException(
            status_code=422,
            detail=f"Invalid pipeline configuration: {str(e)}"
        )
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Error creating pipeline configuration", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error creating pipeline configuration: {str(e)}"
        )

@router.delete("/pipelines/{pipeline_id}")
async def delete_pipeline_config_by_id_endpoint(
    pipeline_id: str
):
    """Delete (soft delete) a pipeline configuration by its unique ID."""
    
    extra = {
        "pipeline_id": pipeline_id
    }
    
    try:
        LOGGER.info(f"Deleting pipeline configuration by ID: {pipeline_id}", extra=extra)
        
        # Use the application layer to delete the configuration
        result = await delete_pipeline_config_by_id(pipeline_id)
        
        LOGGER.info(f"Successfully deleted pipeline configuration: {pipeline_id}", extra=extra)
        return result
        
    except ValueError as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Pipeline configuration not found: {pipeline_id}", extra=extra)
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error deleting pipeline configuration by ID: {pipeline_id}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting pipeline configuration: {str(e)}"
        )
