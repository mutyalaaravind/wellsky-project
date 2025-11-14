"""
FastAPI router for paperglass API endpoints.
This module provides the api_router that is included in the main FastAPI app.
"""
import json
from typing import Union
from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError

from .rest import RestAdapter
from ...infrastructure.ports import IQueryPort
from ...interface.ports import ICommandHandlingPort
from ...infrastructure.adapters.google import FirestoreQueryAdapter
from ...usecases.command_handling import CommandHandlingUseCase
from ...settings import GCP_FIRESTORE_DB
from ...domain.models_common import GenericMessage
from ...domain.values_http import (
    GenericExternalDocumentCreateEventRequestBase,
    GenericExternalDocumentCreateEventRequestApi,
    GenericExternalDocumentCreateEventRequestUri,
    ExternalDocumentRepositoryType,
    EntitiesSearchRequest,
    EntitiesSearchResponse,
    ExternalDocumentCreateResponse,
    Entity,
)
from ...domain.values import DocumentStatusResponse
from ...usecases.commands import ImportHostAttachmentFromExternalApiTask, ImportHostAttachmentFromExternalApi
from ...log import CustomLogger
from ...interface.fastapi_security import RequireAnyAuth, RequireServiceAuth, RequireUserAuth

LOGGER2 = CustomLogger(__name__)

# Create the main API router
api_router = APIRouter()

# Create the REST adapter (Starlette app with all the routes)
rest_adapter = RestAdapter()

# Mount the REST adapter under /api prefix
api_router.mount("/api", rest_adapter)

# Dependency function to get IQueryPort
def get_query_port() -> IQueryPort:
    return FirestoreQueryAdapter(GCP_FIRESTORE_DB)

# Dependency function to get ICommandHandlingPort
def get_command_port() -> ICommandHandlingPort:
    return CommandHandlingUseCase()

# Repository type mapping for external document creation
REPOSITORY_TYPE_MAP = {
    "API": GenericExternalDocumentCreateEventRequestApi,
    "URI": GenericExternalDocumentCreateEventRequestUri
}

# Health and status endpoints
@api_router.get("/health")
async def health_check():
    """
    Health check endpoint for the paperglass API.
    Returns basic health status without requiring authentication.
    """
    return {"status": "OK", "message": "Paperglass API is healthy"}

@api_router.get("/api/health")
async def api_health_check():
    """
    API health check endpoint.
    Returns basic health status without requiring authentication.
    """
    return {"status": "OK", "message": "Paperglass API is healthy"}

@api_router.get("/api/status")
async def api_status_check():
    """
    API status check endpoint.
    Returns basic status without requiring authentication.
    """
    return {"status": "OK", "message": "Paperglass API is operational"}

# External API endpoints
@api_router.get("/api/v1/documents/status", response_model=DocumentStatusResponse)
async def get_document_status_by_host_attachment_id(
    host_attachment_id: str = Query(..., description="Host attachment ID to look up document status"),
    app_id: str = Query(..., description="Application ID"),
    tenant_id: str = Query(..., description="Tenant ID"),
    patient_id: str = Query(..., description="Patient ID"),
    query: IQueryPort = Depends(get_query_port),
    token: str = RequireAnyAuth
) -> DocumentStatusResponse:
    """
    Get document status by host attachment ID.
    
    This endpoint retrieves the processing status of a document using its host attachment ID.
    The response includes detailed status information about document processing pipelines,
    metadata, and current processing state.
    
    Args:
        host_attachment_id: The host attachment ID to look up document status
        app_id: Application ID for the request
        tenant_id: Tenant ID for the request  
        patient_id: Patient ID for the request
        
    Returns:
        DocumentStatusResponse: Detailed document status information
        
    Raises:
        HTTPException: 404 if document not found, 500 for processing errors
    """
    from ...usecases.documents import get_document_status_by_host_attachment_id
    
    try:
        result = await get_document_status_by_host_attachment_id(
            app_id, tenant_id, patient_id, host_attachment_id, query
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/api/v1/documents/external/create", response_model=ExternalDocumentCreateResponse)
async def create_external_document(
    request: Union[GenericExternalDocumentCreateEventRequestApi, GenericExternalDocumentCreateEventRequestUri],
    commands: ICommandHandlingPort = Depends(get_command_port),
    query: IQueryPort = Depends(get_query_port),
    token: str = RequireServiceAuth
) -> ExternalDocumentCreateResponse:
    """
    Create a document from an external source.
    
    This endpoint accepts external document creation requests and processes them
    through the document import pipeline. The request must include API configuration
    for retrieving the document content.
    
    Args:
        request: Document creation request with API configuration
        
    Returns:
        ExternalDocumentCreateResponse: Creation status and details
        
    Raises:
        HTTPException: 400 for validation errors, 500 for processing errors
    """
    from ...domain.utils.exception_utils import exceptionToMap
    
    extra = {
        "source_id": request.hostFileId,
        "app_id": request.appId,
        "tenant_id": request.tenantId,
        "patient_id": request.patientId
    }
    try:
        LOGGER2.debug('Received document external create event: %s', request.dict(), extra=extra)

        if request.repositoryType not in [ExternalDocumentRepositoryType.API, ExternalDocumentRepositoryType.URI]:                
            raise ValueError(f"Unsupported repositoryType {request.repositoryType}")

        # This will call ExternalCreateDocumentTask which will in turn call the ImportHostAttachmentFromExternalApi
        command = ImportHostAttachmentFromExternalApiTask.from_request(request)
        
        await commands.handle_command(command)

        extra = {
            "data": request.dict(),
            "repository_type": request.repositoryType,
        }
        LOGGER2.debug('Processed document external create event: %s', request.dict(), extra=extra)

        return ExternalDocumentCreateResponse(
            message="Document creation request processed successfully",
            status="created",
            hostFileId=request.hostFileId
        )
    
    except ValidationError as e:
        extra = {
            "error": exceptionToMap(e),
        }
        LOGGER2.error('Validation error processing external document create event', exc_info=True, extra=extra)

        msg = GenericMessage("Validation error processing external document create event", str(e))
        return JSONResponse(msg.to_dict(), status_code=400)

    except ValueError as e:
        extra = {
            "error": exceptionToMap(e),
        }
        LOGGER2.error('Validation error processing external document create event', exc_info=True, extra=extra)

        msg = GenericMessage("Validation error processing external document create event", str(e))
        return JSONResponse(msg.to_dict(), status_code=400)

    except Exception as e:
        extra = {                
            "error": exceptionToMap(e),
        }
        LOGGER2.error('Error processing external document create event', exc_info=True, extra=extra)            
        
        msg = GenericMessage("Error processing external document create event", str(e))
        return JSONResponse(msg.to_dict(), status_code=500)


@api_router.post("/api/v1/entities/search")
async def search_entities_endpoint(
    request: EntitiesSearchRequest,
    query: IQueryPort = Depends(get_query_port),
    token: str = RequireAnyAuth
) -> EntitiesSearchResponse:
    """
    Search for entities in documents.
    """
    LOGGER2.info(
        'Entities search request received: appId=%s, tenantId=%s, patientId=%s, documentId=%s, hostAttachmentId=%s',
        request.appId,
        request.tenantId,
        request.patientId,
        request.documentId,
        request.hostAttachmentId
    )
    
    try:
        # Import and call the usecase function
        from ...usecases.entities import search_entities
        
        result = await search_entities(
            app_id=request.appId,
            tenant_id=request.tenantId,
            patient_id=request.patientId,
            document_id=request.documentId,
            host_attachment_id=request.hostAttachmentId,
            query=query
        )
        
        # Convert raw entity dictionaries to Entity objects
        entity_objects = []
        for entity_dict in result["entities"]:
            try:
                # Create Entity object from the dictionary data
                entity_obj = Entity(
                    id=entity_dict.get("id", ""),
                    app_id=entity_dict.get("app_id", request.appId),
                    tenant_id=entity_dict.get("tenant_id", request.tenantId),
                    patient_id=entity_dict.get("patient_id", request.patientId),
                    document_id=entity_dict.get("document_id"),
                    page_number=entity_dict.get("page_number"),
                    document_operation_instance_id=entity_dict.get("document_operation_instance_id"),
                    entity_data=entity_dict.get("entity_data", {}),
                    schema_ref=entity_dict.get("schema_ref", ""),
                    entity_type=entity_dict.get("entity_type", "unknown"),
                    confidence_score=entity_dict.get("confidence_score"),
                    active=entity_dict.get("active", True),
                    created_at=entity_dict.get("created_at"),
                    updated_at=entity_dict.get("updated_at")
                )
                entity_objects.append(entity_obj)
            except Exception as e:
                LOGGER2.warning(f"Failed to convert entity to Entity object: {e}, entity_dict: {entity_dict}")
                # Skip invalid entities rather than failing the entire request
                continue

        # Create response using the result from usecase
        response = EntitiesSearchResponse(
            appId=request.appId,
            tenantId=request.tenantId,
            patientId=request.patientId,
            documentIds=result["documentIds"],
            entities=entity_objects
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        LOGGER2.error(f"Error searching entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
