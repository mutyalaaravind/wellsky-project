"""
Pipelines Router for Admin API

This router provides endpoints for managing pipeline configurations via the entity extraction service.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap
from viki_shared.models.common import PaginationInfo

from contracts.entity_extraction_contracts import EntityExtractionPipeline
from adapters.entity_extraction_adapter import EntityExtractionAdapter
from settings import Settings, get_settings
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


class PipelineData(BaseModel):
    """Pydantic model for pipeline data in API responses."""
    id: str
    key: str
    name: str
    description: Optional[str] = None
    scope: str
    version: Optional[str] = None
    output_entity: Optional[str] = None
    tasks: List[Dict[str, Any]]
    auto_publish_entities_enabled: Optional[bool] = True
    labels: Optional[List[str]] = []
    app_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    active: bool = True


class PipelineResponse(BaseModel):
    """API response wrapper for single pipeline."""
    success: bool
    message: str
    data: PipelineData


class PipelineListResponse(BaseModel):
    """API response wrapper for list of pipelines."""
    success: bool
    message: str
    data: List[PipelineData]
    total: int


class PipelineCreateRequest(BaseModel):
    """Request model for creating/updating a pipeline."""
    key: str
    name: str
    description: Optional[str] = None
    scope: str = "default"
    version: Optional[str] = None
    output_entity: Optional[str] = None
    tasks: List[Dict[str, Any]]
    auto_publish_entities_enabled: Optional[bool] = True
    labels: Optional[List[str]] = []
    app_id: Optional[str] = None


class PipelineDeleteResponse(BaseModel):
    """Response model for pipeline deletion."""
    success: bool
    message: str
    deleted_id: str


def convert_to_pipeline_data(pipeline: EntityExtractionPipeline) -> PipelineData:
    """Convert EntityExtractionPipeline to PipelineData for API responses."""
    return PipelineData(
        id=pipeline.id,
        key=pipeline.key,
        name=pipeline.name,
        description=pipeline.description,
        scope=pipeline.scope,
        version=pipeline.version,
        output_entity=pipeline.output_entity,
        tasks=pipeline.tasks,
        auto_publish_entities_enabled=pipeline.auto_publish_entities_enabled,
        labels=pipeline.labels,
        app_id=pipeline.app_id,
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
        created_by=pipeline.created_by,
        modified_by=pipeline.modified_by,
        active=pipeline.active
    )


async def get_entity_extraction_adapter(settings: Settings = Depends(get_settings)) -> EntityExtractionAdapter:
    """Dependency to get Entity Extraction adapter instance."""
    return EntityExtractionAdapter(settings)


@router.get(
    "",
    response_model=PipelineListResponse,
    summary="List Pipeline Configurations",
    description="Retrieve all pipeline configurations with optional filtering by app_id, labels, etc."
)
async def list_pipelines(
    app_id: Optional[str] = Query(None, description="Filter by app_id - only pipelines with the specified app_id will be returned"),
    labels: Optional[List[str]] = Query(None, description="Filter by labels - only pipelines containing ALL specified labels will be returned"),
    adapter: EntityExtractionAdapter = Depends(get_entity_extraction_adapter),
    current_user: User = RequireAuth
) -> PipelineListResponse:
    """
    List all pipeline configurations with optional filtering.
    
    This endpoint retrieves pipeline configurations from the entity extraction service
    with support for filtering by app_id and labels.
    
    Args:
        app_id: Filter pipelines by application ID
        labels: Filter pipelines by labels (must contain ALL specified labels)
        
    Returns:
        PipelineListResponse containing the list of pipeline configurations
        
    Raises:
        HTTPException: If error retrieving pipelines (500/503)
    """
    extra = {
        "operation": "list_pipelines",
        "filters": {
            "app_id": app_id,
            "labels": labels
        },
        "endpoint": "/api/v1/pipelines"
    }
    
    try:
        logger.debug(f"Listing pipelines with filters: app_id={app_id}, labels={labels}", extra=extra)
        
        # Get pipelines from entity extraction service
        pipelines = await adapter.get_pipeline_configs(labels=labels, app_id=app_id)
        
        extra.update({
            "pipelines_found": len(pipelines),
            "total_returned": len(pipelines)
        })
        
        logger.debug(f"Successfully retrieved {len(pipelines)} pipeline configurations", extra=extra)
        
        return PipelineListResponse(
            success=True,
            message=f"Successfully retrieved {len(pipelines)} pipeline configurations",
            data=[convert_to_pipeline_data(p) for p in pipelines],
            total=len(pipelines)
        )
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error listing pipeline configurations: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Entity extraction service unavailable: {str(e)}"
            )
        elif "service error" in str(e):
            raise HTTPException(
                status_code=502,
                detail=f"Failed to retrieve pipelines from entity extraction service: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error listing pipeline configurations: {str(e)}"
            )


@router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Get Pipeline Configuration",
    description="Retrieve a specific pipeline configuration by its unique ID."
)
async def get_pipeline(
    pipeline_id: str = Path(..., description="Pipeline identifier"),
    adapter: EntityExtractionAdapter = Depends(get_entity_extraction_adapter),
    current_user: User = RequireAuth
) -> PipelineResponse:
    """
    Get pipeline configuration by ID.
    
    This endpoint retrieves a specific pipeline configuration from the entity extraction service
    using the pipeline's unique identifier.
    
    Args:
        pipeline_id: The unique identifier of the pipeline
        
    Returns:
        PipelineResponse containing the pipeline configuration data
        
    Raises:
        HTTPException: If pipeline not found (404) or error retrieving pipeline (500)
    """
    extra = {
        "operation": "get_pipeline",
        "pipeline_id": pipeline_id,
        "endpoint": f"/api/v1/pipelines/{pipeline_id}"
    }
    
    try:
        logger.debug(f"Retrieving pipeline configuration for ID: {pipeline_id}", extra=extra)
        
        # Get pipeline from entity extraction service by ID
        pipeline = await adapter._get_pipeline_by_id(pipeline_id)
        
        if pipeline is None:
            extra["pipeline_found"] = False
            logger.warning(f"Pipeline configuration not found for ID: {pipeline_id}", extra=extra)
            
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline configuration not found for ID: {pipeline_id}"
            )
        
        extra.update({
            "pipeline_found": True,
            "pipeline_key": pipeline.key,
            "pipeline_name": pipeline.name,
            "pipeline_scope": pipeline.scope
        })
        
        logger.debug(f"Successfully retrieved pipeline configuration for ID: {pipeline_id}", extra=extra)
        
        return PipelineResponse(
            success=True,
            message="Pipeline configuration retrieved successfully",
            data=convert_to_pipeline_data(pipeline)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error retrieving pipeline configuration for ID {pipeline_id}: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Entity extraction service unavailable: {str(e)}"
            )
        elif "service error" in str(e):
            raise HTTPException(
                status_code=502,
                detail=f"Failed to retrieve pipeline from entity extraction service: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error retrieving pipeline configuration: {str(e)}"
            )


@router.post(
    "",
    response_model=PipelineResponse,
    summary="Create or Update Pipeline Configuration",
    description="Create a new pipeline configuration or update an existing one in the entity extraction service."
)
async def create_or_update_pipeline(
    pipeline_data: PipelineCreateRequest,
    adapter: EntityExtractionAdapter = Depends(get_entity_extraction_adapter),
    current_user: User = RequireAuth
) -> PipelineResponse:
    """
    Create or update a pipeline configuration.
    
    This endpoint creates a new pipeline configuration or updates an existing one
    in the entity extraction service. The operation is determined by whether a
    pipeline with the given scope and key already exists.
    
    Args:
        pipeline_data: The pipeline configuration data
        
    Returns:
        PipelineResponse containing the created/updated pipeline configuration
        
    Raises:
        HTTPException: If validation fails (422) or error creating/updating pipeline (500)
    """
    extra = {
        "operation": "create_or_update_pipeline",
        "pipeline_key": pipeline_data.key,
        "pipeline_scope": pipeline_data.scope,
        "pipeline_name": pipeline_data.name,
        "endpoint": "/api/v1/pipelines"
    }
    
    try:
        logger.debug(f"Creating or updating pipeline: {pipeline_data.scope}.{pipeline_data.key}", extra=extra)
        
        # Prepare the configuration data for the entity extraction service
        config_data = pipeline_data.model_dump(exclude_none=True)
        
        # The entity extraction service expects the pipeline data directly
        # We'll use their create/update endpoint
        import httpx
        from viki_shared.utils.gcp_auth import get_service_account_identity_token
        
        # Get settings for entity extraction URL
        from settings import get_settings
        settings = await get_settings()
        entity_extraction_url = settings.ENTITY_EXTRACTION_API_URL
        
        # Get authentication token
        try:
            auth_token = await get_service_account_identity_token(target_audience=entity_extraction_url)
        except Exception:
            auth_token = ""
        
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Use the entity extraction service's create endpoint
        url = f"{entity_extraction_url}/api/config/pipelines"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=config_data)
            response.raise_for_status()
            response_data = response.json()
        
        # Parse the response from the entity extraction service
        created_pipeline = EntityExtractionPipeline(
            id=response_data.get("document_id", ""),
            key=response_data.get("pipeline_key", pipeline_data.key),
            name=pipeline_data.name,
            description=pipeline_data.description,
            scope=response_data.get("scope", pipeline_data.scope),
            version=pipeline_data.version,
            output_entity=pipeline_data.output_entity,
            tasks=pipeline_data.tasks,
            auto_publish_entities_enabled=pipeline_data.auto_publish_entities_enabled,
            labels=pipeline_data.labels,
            app_id=pipeline_data.app_id,
            active=True
        )
        
        extra.update({
            "pipeline_created": True,
            "operation_result": response_data.get("operation", "unknown"),
            "document_id": response_data.get("document_id")
        })
        
        logger.debug(f"Successfully created/updated pipeline: {pipeline_data.scope}.{pipeline_data.key}", extra=extra)
        
        return PipelineResponse(
            success=True,
            message=f"Pipeline configuration {response_data.get('operation', 'processed')} successfully",
            data=convert_to_pipeline_data(created_pipeline)
        )
        
    except httpx.HTTPStatusError as e:
        extra["error"] = {
            "status_code": e.response.status_code,
            "response_text": e.response.text
        }
        logger.error(f"HTTP error creating/updating pipeline: {e.response.status_code} - {e.response.text}", extra=extra)
        
        if e.response.status_code == 422:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid pipeline configuration: {e.response.text}"
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=f"Entity extraction service error: {e.response.status_code}"
            )
            
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error creating/updating pipeline configuration: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Entity extraction service unavailable: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error creating/updating pipeline configuration: {str(e)}"
            )


@router.delete(
    "/{pipeline_id}",
    response_model=PipelineDeleteResponse,
    summary="Delete Pipeline Configuration",
    description="Delete (soft delete) a pipeline configuration by its unique ID."
)
async def delete_pipeline(
    pipeline_id: str = Path(..., description="Pipeline identifier"),
    adapter: EntityExtractionAdapter = Depends(get_entity_extraction_adapter),
    current_user: User = RequireAuth
) -> PipelineDeleteResponse:
    """
    Delete a pipeline configuration by ID.
    
    This endpoint performs a soft delete of the specified pipeline configuration
    in the entity extraction service. The pipeline will be marked as inactive
    but not permanently removed.
    
    Args:
        pipeline_id: The unique identifier of the pipeline to delete
        
    Returns:
        PipelineDeleteResponse confirming the deletion
        
    Raises:
        HTTPException: If pipeline not found (404) or error deleting pipeline (500)
    """
    extra = {
        "operation": "delete_pipeline",
        "pipeline_id": pipeline_id,
        "endpoint": f"/api/v1/pipelines/{pipeline_id}"
    }
    
    try:
        logger.debug(f"Deleting pipeline configuration for ID: {pipeline_id}", extra=extra)
        
        # Call the entity extraction service delete endpoint directly
        import httpx
        from viki_shared.utils.gcp_auth import get_service_account_identity_token
        
        # Get settings for entity extraction URL
        from settings import get_settings
        settings = await get_settings()
        entity_extraction_url = settings.ENTITY_EXTRACTION_API_URL
        
        # Get authentication token
        try:
            auth_token = await get_service_account_identity_token(target_audience=entity_extraction_url)
        except Exception:
            auth_token = ""
        
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Use the entity extraction service's delete endpoint
        url = f"{entity_extraction_url}/api/config/pipelines/{pipeline_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(url, headers=headers)
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pipeline configuration not found for ID: {pipeline_id}"
                )
            
            response.raise_for_status()
            response_data = response.json()
        
        extra.update({
            "pipeline_deleted": True,
            "delete_result": response_data
        })
        
        logger.debug(f"Successfully deleted pipeline configuration for ID: {pipeline_id}", extra=extra)
        
        return PipelineDeleteResponse(
            success=True,
            message="Pipeline configuration deleted successfully",
            deleted_id=pipeline_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except httpx.HTTPStatusError as e:
        extra["error"] = {
            "status_code": e.response.status_code,
            "response_text": e.response.text
        }
        logger.error(f"HTTP error deleting pipeline: {e.response.status_code} - {e.response.text}", extra=extra)
        
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline configuration not found for ID: {pipeline_id}"
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=f"Entity extraction service error: {e.response.status_code}"
            )
            
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error deleting pipeline configuration for ID {pipeline_id}: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Entity extraction service unavailable: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error deleting pipeline configuration: {str(e)}"
            )