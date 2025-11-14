"""
Entities Router for Admin API

This router provides endpoints for entity management using hexagonal architecture and CQRS.
Entities are stored in Firestore subcollections under admin_demo_subjects/{app_id}/subjects/{subject_id}/entities
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, ValidationError
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap
from viki_shared.models.common import PaginationInfo
from google.cloud.firestore import AsyncClient
from datetime import datetime, timezone
from uuid import uuid4

from settings import Settings, get_settings
from domain.models.entity import EntityCallbackData
from application.commands.entity_commands import (
    EntityCommandHandler,
    CreateEntityCommand,
    UpdateEntityCommand,
    DeleteEntityCommand,
    ProcessDocumentCallbackCommand
)
from application.queries.entity_queries import (
    EntityQueryHandler,
    GetEntityQuery,
    ListEntitiesQuery
)
from infrastructure.adapters.entity_firestore_adapter import EntityFirestoreAdapter
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


# Request/Response Models
class DocumentProcessingCompleteRequest(BaseModel):
    """Request model for document processing complete callback from Paperglass."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str] = None
    status: str = "completed"
    timestamp: str
    run_id: str
    metadata: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None


class EntityCallbackResponse(BaseModel):
    """Response model for entity callback processing."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str] = None
    status: str
    message: str
    document_status: str
    run_id: str
    timestamp: str
    entities_received: int
    entities_saved: int
    entity_document_ids: List[str]


class EntityData(BaseModel):
    """Model for entity data."""
    id: str
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str] = None
    run_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_schema_id: Optional[str] = None
    callback_timestamp: Optional[str] = None
    callback_status: Optional[str] = None
    callback_metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    # Allow additional fields from the original entity data
    class Config:
        extra = "allow"


class EntityCreateRequest(BaseModel):
    """Request model for creating an entity."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str] = None
    run_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_schema_id: Optional[str] = None
    data: Dict[str, Any]  # The actual entity data


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""
    app_id: Optional[str] = None
    tenant_id: Optional[str] = None
    patient_id: Optional[str] = None
    document_id: Optional[str] = None
    run_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_schema_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class EntityResponse(BaseModel):
    """Response model for single entity."""
    success: bool
    message: str
    data: EntityData


class EntityListResponse(BaseModel):
    """Response model for list of entities."""
    success: bool
    message: str
    data: List[EntityData]
    total: int
    pagination: PaginationInfo


class EntityDeleteResponse(BaseModel):
    """Response model for entity deletion."""
    success: bool
    message: str
    deleted_id: str


# Dependency Functions
async def get_firestore_client(settings: Settings = Depends(get_settings)) -> AsyncClient:
    """Get Firestore client dependency."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        return AsyncClient()  # Use default database in emulator
    else:
        return AsyncClient(database=settings.GCP_FIRESTORE_DB)


async def get_entity_command_handler(settings: Settings = Depends(get_settings)) -> EntityCommandHandler:
    """Get Entity Command Handler with dependencies."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        firestore_client = AsyncClient()  # Use default database in emulator
    else:
        firestore_client = AsyncClient(database=settings.GCP_FIRESTORE_DB)
    entity_repository = EntityFirestoreAdapter(firestore_client)
    return EntityCommandHandler(entity_repository)


async def get_entity_query_handler(settings: Settings = Depends(get_settings)) -> EntityQueryHandler:
    """Get Entity Query Handler with dependencies."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        firestore_client = AsyncClient()  # Use default database in emulator
    else:
        firestore_client = AsyncClient(database=settings.GCP_FIRESTORE_DB)
    entity_repository = EntityFirestoreAdapter(firestore_client)
    return EntityQueryHandler(entity_repository)




@router.post(
    "/callback",
    response_model=EntityCallbackResponse,
    summary="Process Document Processing Complete Callback",
    description="Handle callback from Paperglass when document processing is complete and save entities to subcollections."
)
async def process_document_complete_callback(
    callback_request: DocumentProcessingCompleteRequest,
    command_handler: EntityCommandHandler = Depends(get_entity_command_handler),
    current_user: User = RequireAuth
) -> EntityCallbackResponse:
    """
    Process document processing complete callback from Paperglass.
    
    Saves entities to Firestore subcollection at:
    /admin_demo_subjects/{app_id}/subjects/{subject_id}/entities
    
    Args:
        callback_request: The callback payload from Paperglass
        firestore_client: Firestore client dependency
        
    Returns:
        EntityCallbackResponse with processing status and results
        
    Raises:
        HTTPException: If validation fails (422) or processing error (500)
    """
    extra = {
        "operation": "process_document_complete_callback",
        "app_id": callback_request.app_id,
        "tenant_id": callback_request.tenant_id,
        "patient_id": callback_request.patient_id,
        "document_id": callback_request.document_id,
        "source_id": callback_request.source_id,
        "status": callback_request.status,
        "run_id": callback_request.run_id,
        "timestamp": callback_request.timestamp,
        "entities_count": len(callback_request.data) if callback_request.data else 0,
        "data_is_none": callback_request.data is None,
        "endpoint": "/api/v1/entities"
    }
    
    try:
        # Enhanced callback reception logging with structured data
        callback_reception_info = {
            "callback_request": {
                "app_id": callback_request.app_id,
                "tenant_id": callback_request.tenant_id,
                "patient_id": callback_request.patient_id,
                "document_id": callback_request.document_id,
                "source_id": callback_request.source_id,
                "status": callback_request.status,
                "timestamp": callback_request.timestamp,
                "run_id": callback_request.run_id,
                "has_metadata": bool(callback_request.metadata),
                "metadata_keys": list(callback_request.metadata.keys()) if callback_request.metadata else []
            },
            "entities_payload": {
                "has_data": bool(callback_request.data),
                "data_is_none": callback_request.data is None,
                "data_is_empty_list": callback_request.data == [],
                "entity_count": len(callback_request.data) if callback_request.data else 0,
                "data_type": type(callback_request.data).__name__ if callback_request.data is not None else "NoneType"
            }
        }

        # Add entity sample for debugging
        if callback_request.data and len(callback_request.data) > 0:
            first_entity = callback_request.data[0]
            callback_reception_info["entities_payload"]["first_entity_sample"] = {
                "keys": list(first_entity.keys()) if isinstance(first_entity, dict) else "not_dict",
                "type": type(first_entity).__name__,
                "has_id": "id" in first_entity if isinstance(first_entity, dict) else False,
                "id_value": first_entity.get("id") if isinstance(first_entity, dict) else None,
                "preview": str(first_entity)[:200] if first_entity else None
            }
            
            # Count how many entities have IDs from Paperglass
            entities_with_ids = sum(1 for e in callback_request.data if isinstance(e, dict) and "id" in e)
            callback_reception_info["entities_payload"]["entities_with_paperglass_ids"] = entities_with_ids

        logger.info("Received document processing complete callback for Admin API", extra={
            **extra,
            **callback_reception_info
        })
        
        # Process callback using command handler
        callback_data = EntityCallbackData(
            app_id=callback_request.app_id,
            tenant_id=callback_request.tenant_id,
            patient_id=callback_request.patient_id,
            document_id=callback_request.document_id,
            source_id=callback_request.source_id,
            status=callback_request.status,
            timestamp=callback_request.timestamp,
            run_id=callback_request.run_id,
            metadata=callback_request.metadata,
            entities_data=callback_request.data
        )
        
        command = ProcessDocumentCallbackCommand(callback_data=callback_data)
        result = await command_handler.handle_process_document_callback(command)
        
        saved_entities_count = result["entities_saved"]
        saved_doc_ids = result["entity_document_ids"]
        
        # Prepare response
        response_data = EntityCallbackResponse(
            app_id=callback_request.app_id,
            tenant_id=callback_request.tenant_id,
            patient_id=callback_request.patient_id,
            document_id=callback_request.document_id,
            source_id=callback_request.source_id,
            status="processed",
            message="Document processing complete callback processed successfully",
            document_status=callback_request.status,
            run_id=callback_request.run_id,
            timestamp=callback_request.timestamp,
            entities_received=len(callback_request.data) if callback_request.data else 0,
            entities_saved=saved_entities_count,
            entity_document_ids=saved_doc_ids
        )
        
        # Enhanced success logging with processing details
        processing_success_info = {
            "processing_results": {
                "entities_received": len(callback_request.data) if callback_request.data else 0,
                "entities_saved": saved_entities_count,
                "entity_document_ids": saved_doc_ids,
                "success_rate": saved_entities_count / len(callback_request.data) if callback_request.data else 0,
                "subcollection_path": f"admin_demo_subjects/{callback_request.app_id}/subjects/{callback_request.patient_id}/entities"
            },
            "database_operation": {
                "collection": "admin_demo_subjects",
                "app_id": callback_request.app_id,
                "subject_id": callback_request.patient_id,
                "subcollection": "entities",
                "operation_type": "bulk_create"
            }
        }

        logger.info("Successfully processed document processing complete callback for Admin API", extra={
            **extra,
            **processing_success_info
        })
        
        return response_data
        
    except ValidationError as e:
        # Enhanced validation error logging
        validation_error_info = {
            "error_type": "ValidationError",
            "error_details": exceptionToMap(e),
            "callback_payload": {
                "app_id": getattr(callback_request, 'app_id', 'unknown'),
                "document_id": getattr(callback_request, 'document_id', 'unknown'),
                "status": getattr(callback_request, 'status', 'unknown'),
                "has_data": bool(getattr(callback_request, 'data', None))
            },
            "http_response": {
                "status_code": 422,
                "error_message": f"Invalid callback payload: {str(e)}"
            }
        }
        logger.error(f"Validation error in Admin API document processing callback: {str(e)}", extra={
            **extra,
            **validation_error_info
        })
        raise HTTPException(
            status_code=422,
            detail=f"Invalid callback payload: {str(e)}"
        )
    except Exception as e:
        # Enhanced general error logging
        general_error_info = {
            "error_type": type(e).__name__,
            "error_details": exceptionToMap(e),
            "callback_processing_stage": "unknown",  # This could be enhanced to track where in processing the error occurred
            "callback_payload": {
                "app_id": getattr(callback_request, 'app_id', 'unknown'),
                "document_id": getattr(callback_request, 'document_id', 'unknown'),
                "status": getattr(callback_request, 'status', 'unknown'),
                "entity_count": len(getattr(callback_request, 'data', [])) if getattr(callback_request, 'data', None) else 0
            },
            "http_response": {
                "status_code": 500,
                "error_message": f"Failed to process callback: {str(e)}"
            }
        }
        logger.error(f"Error processing Admin API document complete callback: {str(e)}", extra={
            **extra,
            **general_error_info
        })
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process callback: {str(e)}"
        )


@router.get(
    "",
    response_model=EntityListResponse,
    summary="List Entities",
    description="List entities from a specific subcollection with optional filtering."
)
async def list_entities(
    app_id: str = Query(..., description="Application ID"),
    subject_id: str = Query(..., description="Subject ID (patient_id)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entities to return"),
    offset: int = Query(0, ge=0, description="Number of entities to skip"),
    query_handler: EntityQueryHandler = Depends(get_entity_query_handler),
    current_user: User = RequireAuth
) -> EntityListResponse:
    """
    List entities from a specific subcollection.

    Args:
        app_id: Application ID for the collection path
        subject_id: Subject ID (patient_id) for the collection path
        entity_type: Optional filter by entity type
        source_id: Optional filter by source ID
        limit: Maximum number of entities to return
        offset: Number of entities to skip
        query_handler: Entity query handler dependency

    Returns:
        EntityListResponse with list of entities and pagination info

    Raises:
        HTTPException: If query fails (500)
    """
    extra = {
        "operation": "list_entities",
        "app_id": app_id,
        "subject_id": subject_id,
        "entity_type": entity_type,
        "source_id": source_id,
        "limit": limit,
        "offset": offset
    }
    
    try:
        logger.info("Listing entities", extra=extra)
        
        query = ListEntitiesQuery(
            app_id=app_id,
            subject_id=subject_id,
            entity_type=entity_type,
            source_id=source_id,
            limit=limit,
            offset=offset
        )
        
        entities = await query_handler.handle_list_entities(query)
        
        # Convert entities to response data
        entity_data_list = []
        for entity in entities:
            entity_dict = entity.to_dict()
            # Convert datetime objects to ISO strings
            if "created_at" in entity_dict and hasattr(entity_dict["created_at"], "isoformat"):
                entity_dict["created_at"] = entity_dict["created_at"].isoformat()
            if "updated_at" in entity_dict and hasattr(entity_dict["updated_at"], "isoformat"):
                entity_dict["updated_at"] = entity_dict["updated_at"].isoformat()
            if "modified_at" in entity_dict and hasattr(entity_dict["modified_at"], "isoformat"):
                entity_dict["modified_at"] = entity_dict["modified_at"].isoformat()
            
            entity_data_list.append(EntityData(**entity_dict))
        
        pagination = PaginationInfo(
            limit=limit,
            offset=offset,
            returned=len(entity_data_list),
            has_more=len(entity_data_list) == limit  # Simple heuristic
        )
        
        response = EntityListResponse(
            success=True,
            message=f"Successfully retrieved {len(entity_data_list)} entities",
            data=entity_data_list,
            total=len(entity_data_list),  # This is the returned count, not total in DB
            pagination=pagination
        )
        
        logger.info(f"Successfully listed {len(entity_data_list)} entities", extra={**extra, "entities_count": len(entity_data_list)})
        return response
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error listing entities: {str(e)}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list entities: {str(e)}"
        )


@router.get(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Get Entity",
    description="Get a specific entity by ID."
)
async def get_entity(
    entity_id: str = Path(..., description="Entity ID"),
    app_id: str = Query(..., description="Application ID"),
    subject_id: str = Query(..., description="Subject ID (patient_id)"),
    query_handler: EntityQueryHandler = Depends(get_entity_query_handler),
    current_user: User = RequireAuth
) -> EntityResponse:
    """
    Get a specific entity by ID.
    
    Args:
        entity_id: Entity ID
        app_id: Application ID for the collection path
        subject_id: Subject ID (patient_id) for the collection path
        query_handler: Entity query handler dependency
        
    Returns:
        EntityResponse with entity data
        
    Raises:
        HTTPException: If entity not found (404) or query fails (500)
    """
    extra = {
        "operation": "get_entity",
        "entity_id": entity_id,
        "app_id": app_id,
        "subject_id": subject_id
    }
    
    try:
        logger.info("Getting entity", extra=extra)
        
        query = GetEntityQuery(
            app_id=app_id,
            subject_id=subject_id,
            entity_id=entity_id
        )
        
        entity = await query_handler.handle_get_entity(query)
        
        if not entity:
            logger.info(f"Entity not found: {entity_id}", extra=extra)
            raise HTTPException(
                status_code=404,
                detail=f"Entity not found: {entity_id}"
            )
        
        # Convert entity to response data
        entity_dict = entity.to_dict()
        # Convert datetime objects to ISO strings
        if "created_at" in entity_dict and hasattr(entity_dict["created_at"], "isoformat"):
            entity_dict["created_at"] = entity_dict["created_at"].isoformat()
        if "updated_at" in entity_dict and hasattr(entity_dict["updated_at"], "isoformat"):
            entity_dict["updated_at"] = entity_dict["updated_at"].isoformat()
        if "modified_at" in entity_dict and hasattr(entity_dict["modified_at"], "isoformat"):
            entity_dict["modified_at"] = entity_dict["modified_at"].isoformat()
        
        entity_data = EntityData(**entity_dict)
        
        response = EntityResponse(
            success=True,
            message=f"Successfully retrieved entity: {entity_id}",
            data=entity_data
        )
        
        logger.info(f"Successfully retrieved entity: {entity_id}", extra=extra)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error getting entity: {str(e)}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get entity: {str(e)}"
        )


@router.post(
    "",
    response_model=EntityResponse,
    summary="Create Entity",
    description="Create a new entity."
)
async def create_entity(
    request: EntityCreateRequest,
    command_handler: EntityCommandHandler = Depends(get_entity_command_handler),
    current_user: User = RequireAuth
) -> EntityResponse:
    """
    Create a new entity.
    
    Args:
        request: Entity creation request
        command_handler: Entity command handler dependency
        
    Returns:
        EntityResponse with created entity data
        
    Raises:
        HTTPException: If creation fails (500)
    """
    extra = {
        "operation": "create_entity",
        "app_id": request.app_id,
        "patient_id": request.patient_id,
        "entity_type": request.entity_type
    }
    
    try:
        logger.info("Creating entity", extra=extra)
        
        command = CreateEntityCommand(
            app_id=request.app_id,
            tenant_id=request.tenant_id,
            patient_id=request.patient_id,
            document_id=request.document_id,
            entity_data=request.data,
            run_id=request.run_id,
            entity_type=request.entity_type,
            entity_schema_id=request.entity_schema_id
        )
        
        entity_id = await command_handler.handle_create_entity(command)
        
        # Return the created entity (re-query it to get the full data)
        query = GetEntityQuery(
            app_id=request.app_id,
            subject_id=request.patient_id,
            entity_id=entity_id
        )
        
        # Get query handler to retrieve the created entity (reuse the injected command_handler's repository)
        query_handler = EntityQueryHandler(command_handler.entity_repository)
        
        entity = await query_handler.handle_get_entity(query)
        
        if not entity:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created entity"
            )
        
        # Convert entity to response data
        entity_dict = entity.to_dict()
        # Convert datetime objects to ISO strings
        if "created_at" in entity_dict and hasattr(entity_dict["created_at"], "isoformat"):
            entity_dict["created_at"] = entity_dict["created_at"].isoformat()
        if "updated_at" in entity_dict and hasattr(entity_dict["updated_at"], "isoformat"):
            entity_dict["updated_at"] = entity_dict["updated_at"].isoformat()
        if "modified_at" in entity_dict and hasattr(entity_dict["modified_at"], "isoformat"):
            entity_dict["modified_at"] = entity_dict["modified_at"].isoformat()
        
        entity_data = EntityData(**entity_dict)
        
        response = EntityResponse(
            success=True,
            message=f"Successfully created entity: {entity_id}",
            data=entity_data
        )
        
        logger.info(f"Successfully created entity: {entity_id}", extra={**extra, "entity_id": entity_id})
        return response
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error creating entity: {str(e)}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create entity: {str(e)}"
        )


@router.put(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Update Entity",
    description="Update an existing entity."
)
async def update_entity(
    entity_id: str = Path(..., description="Entity ID"),
    request: EntityUpdateRequest = ...,
    app_id: str = Query(..., description="Application ID"),
    subject_id: str = Query(..., description="Subject ID (patient_id)"),
    command_handler: EntityCommandHandler = Depends(get_entity_command_handler),
    current_user: User = RequireAuth
) -> EntityResponse:
    """
    Update an existing entity.
    
    Args:
        entity_id: Entity ID
        request: Entity update request
        app_id: Application ID for the collection path
        subject_id: Subject ID (patient_id) for the collection path
        command_handler: Entity command handler dependency
        
    Returns:
        EntityResponse with updated entity data
        
    Raises:
        HTTPException: If entity not found (404) or update fails (500)
    """
    extra = {
        "operation": "update_entity",
        "entity_id": entity_id,
        "app_id": app_id,
        "subject_id": subject_id
    }
    
    try:
        logger.info("Updating entity", extra=extra)
        
        command = UpdateEntityCommand(
            app_id=app_id,
            patient_id=subject_id,
            entity_id=entity_id,
            tenant_id=request.tenant_id,
            document_id=request.document_id,
            entity_data=request.data,
            run_id=request.run_id,
            entity_type=request.entity_type,
            entity_schema_id=request.entity_schema_id
        )
        
        await command_handler.handle_update_entity(command)
        
        # Return the updated entity (re-query it to get the full data)
        query = GetEntityQuery(
            app_id=app_id,
            subject_id=subject_id,
            entity_id=entity_id
        )
        
        # Get query handler to retrieve the updated entity (reuse the injected command_handler's repository)
        query_handler = EntityQueryHandler(command_handler.entity_repository)
        
        entity = await query_handler.handle_get_entity(query)
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity not found after update: {entity_id}"
            )
        
        # Convert entity to response data
        entity_dict = entity.to_dict()
        # Convert datetime objects to ISO strings
        if "created_at" in entity_dict and hasattr(entity_dict["created_at"], "isoformat"):
            entity_dict["created_at"] = entity_dict["created_at"].isoformat()
        if "updated_at" in entity_dict and hasattr(entity_dict["updated_at"], "isoformat"):
            entity_dict["updated_at"] = entity_dict["updated_at"].isoformat()
        if "modified_at" in entity_dict and hasattr(entity_dict["modified_at"], "isoformat"):
            entity_dict["modified_at"] = entity_dict["modified_at"].isoformat()
        
        entity_data = EntityData(**entity_dict)
        
        response = EntityResponse(
            success=True,
            message=f"Successfully updated entity: {entity_id}",
            data=entity_data
        )
        
        logger.info(f"Successfully updated entity: {entity_id}", extra=extra)
        return response
        
    except ValueError as e:
        logger.info(f"Entity not found for update: {entity_id}", extra=extra)
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error updating entity: {str(e)}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update entity: {str(e)}"
        )


@router.delete(
    "/{entity_id}",
    response_model=EntityDeleteResponse,
    summary="Delete Entity",
    description="Delete an entity by ID."
)
async def delete_entity(
    entity_id: str = Path(..., description="Entity ID"),
    app_id: str = Query(..., description="Application ID"),
    subject_id: str = Query(..., description="Subject ID (patient_id)"),
    command_handler: EntityCommandHandler = Depends(get_entity_command_handler),
    current_user: User = RequireAuth
) -> EntityDeleteResponse:
    """
    Delete an entity by ID.
    
    Args:
        entity_id: Entity ID
        app_id: Application ID for the collection path
        subject_id: Subject ID (patient_id) for the collection path
        command_handler: Entity command handler dependency
        
    Returns:
        EntityDeleteResponse confirming deletion
        
    Raises:
        HTTPException: If entity not found (404) or deletion fails (500)
    """
    extra = {
        "operation": "delete_entity",
        "entity_id": entity_id,
        "app_id": app_id,
        "subject_id": subject_id
    }
    
    try:
        logger.info("Deleting entity", extra=extra)
        
        command = DeleteEntityCommand(
            app_id=app_id,
            patient_id=subject_id,
            entity_id=entity_id
        )
        
        await command_handler.handle_delete_entity(command)
        
        response = EntityDeleteResponse(
            success=True,
            message=f"Successfully deleted entity: {entity_id}",
            deleted_id=entity_id
        )
        
        logger.info(f"Successfully deleted entity: {entity_id}", extra=extra)
        return response
        
    except ValueError as e:
        logger.info(f"Entity not found for deletion: {entity_id}", extra=extra)
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error deleting entity: {str(e)}", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete entity: {str(e)}"
        )