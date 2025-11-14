from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Body
from typing import Optional, Dict
import json
from kink import inject

from contracts.document_contracts import (
    DocumentResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    DocumentUploadResponse
)
from models.document_models import (
    UpdateDocumentRequest
)
from usecases.document_service import DocumentService
from usecases.document_commands import (
    CreateDocumentCommand,
    UpdateDocumentCommand,
    DeleteDocumentCommand,
    UpdateDocumentStatusCommand,
    UpdateDocumentStatusFromCallbackCommand,
    GetDocumentsQuery,
    GetDocumentQuery,
    UploadDocumentCommand
)

from dependencies.auth_dependencies import RequireAuth
from models.user import User

router = APIRouter()


@inject
async def get_document_service() -> DocumentService:
    """Dependency to get document service instance."""
    from infrastructure.bindings import get_document_service
    return get_document_service()


@router.get("/{app_id}/subjects/{subject_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    app_id: str,
    subject_id: str,
    include_deleted: bool = False,
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """List all documents for a subject"""
    query = GetDocumentsQuery(
        app_id=app_id, 
        subject_id=subject_id, 
        include_deleted=include_deleted
    )
    documents = await service.get_documents(query)
    
    return DocumentListResponse(
        success=True,
        message="Documents retrieved successfully",
        data=documents,
        total=len(documents)
    )


@router.get("/{app_id}/subjects/{subject_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    app_id: str,
    subject_id: str,
    document_id: str,
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """Get a specific document by ID"""
    query = GetDocumentQuery(app_id=app_id, subject_id=subject_id, document_id=document_id)
    document = await service.get_document(query)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        success=True,
        message="Document retrieved successfully",
        data=document
    )


@router.post("/{app_id}/subjects/{subject_id}/documents", response_model=DocumentUploadResponse)
async def upload_document(
    app_id: str,
    subject_id: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """Upload a new document"""
    # Parse metadata JSON if provided
    parsed_metadata = {}
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    
    command = UploadDocumentCommand(
        app_id=app_id,
        subject_id=subject_id,
        filename=file.filename or "unknown",
        content_type=file.content_type,
        size=file.size,
        metadata=parsed_metadata,
        uploaded_by=None  # TODO: Get from auth context when available
    )
    
    try:
        created_document = await service.handle_upload_document(command, file)
        
        return DocumentUploadResponse(
            success=True,
            message="Document uploaded successfully",
            data=created_document
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{app_id}/subjects/{subject_id}/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    app_id: str,
    subject_id: str,
    document_id: str,
    document_data: UpdateDocumentRequest,
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """Update an existing document"""
    command = UpdateDocumentCommand(
        app_id=app_id,
        subject_id=subject_id,
        document_id=document_id,
        name=document_data.name,
        metadata=document_data.metadata,
        status=document_data.status,
        modified_by=None  # TODO: Get from auth context when available
    )
    
    try:
        updated_document = await service.handle_update_document(command)
        
        if not updated_document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            success=True,
            message="Document updated successfully",
            data=updated_document
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{app_id}/subjects/{subject_id}/documents/{document_id}/status")
async def update_document_status(
    app_id: str,
    subject_id: str,
    document_id: str,
    status: str,
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """Update document processing status"""
    command = UpdateDocumentStatusCommand(
        app_id=app_id,
        subject_id=subject_id,
        document_id=document_id,
        status=status,
        modified_by=None  # TODO: Get from auth context when available
    )
    
    updated_document = await service.handle_update_document_status(command)
    
    if not updated_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        success=True,
        message="Document status updated successfully",
        data=updated_document
    )


@router.delete("/{app_id}/subjects/{subject_id}/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    app_id: str,
    subject_id: str,
    document_id: str,
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """Soft delete a document"""
    command = DeleteDocumentCommand(
        app_id=app_id,
        subject_id=subject_id,
        document_id=document_id,
        deleted_by=None  # TODO: Get from auth context when available
    )
    
    deleted = await service.handle_delete_document(command)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentDeleteResponse(
        success=True,
        message="Document deleted successfully",
        deleted_id=document_id
    )


@router.get("/{app_id}/subjects/{subject_id}/documents/{document_id}/download")
async def download_document(
    app_id: str,
    subject_id: str,
    document_id: str,
    service: DocumentService = Depends(get_document_service),
    current_user: User = RequireAuth
):
    """Get a signed URL for downloading a document"""
    query = GetDocumentQuery(app_id=app_id, subject_id=subject_id, document_id=document_id)
    document = await service.get_document(query)
    
    if not document or not document.active:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Parse GCS URI to get bucket and path
        if not document.uri.startswith("gs://"):
            raise HTTPException(status_code=400, detail="Invalid document URI")
        
        # Extract bucket and path from gs://bucket/path
        uri_parts = document.uri[5:].split("/", 1)  # Remove 'gs://'
        if len(uri_parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid document URI format")
        
        bucket_name, object_path = uri_parts
        
        # Get file storage adapter and generate signed URL
        from infrastructure.bindings import get_file_storage
        file_storage = get_file_storage()
        
        signed_url = await file_storage.get_signed_url(
            bucket_name=bucket_name,
            object_path=object_path,
            expiration_minutes=60
        )
        
        return {
            "success": True,
            "message": "Download URL generated successfully",
            "download_url": signed_url,
            "expires_in_minutes": 60
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")


@router.post("/documents/{document_id}/status-callback")
async def receive_paperglass_status_callback(
    document_id: str,
    callback_data: dict = Body(...)
):
    """
    Infrastructure endpoint for receiving Paperglass status callbacks.
    Uses proper CQRS pattern with command and application service.
    """
    try:
        # Create command from HTTP request
        command = UpdateDocumentStatusFromCallbackCommand(
            document_id=document_id,
            status=callback_data.get("status", "UNKNOWN"),
            operation_type=callback_data.get("operation_type"),
            timestamp=callback_data.get("timestamp"),
            app_id=callback_data.get("app_id"),
            tenant_id=callback_data.get("tenant_id"),
            patient_id=callback_data.get("patient_id")
        )

        # Get document status service with proper dependency injection
        from usecases.document_status_service import DocumentStatusService
        from infrastructure.bindings import get_document_repository

        document_repository = get_document_repository()
        document_status_service = DocumentStatusService(document_repository)

        # Delegate to application service
        success = await document_status_service.handle_status_update_from_callback(command)

        return {
            "success": success,
            "message": f"Document status updated to {command.status}"
        }

    except Exception as e:
        # Import here to avoid circular imports
        from usecases.document_status_service import DocumentNotFoundError

        if isinstance(e, DocumentNotFoundError):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal error processing callback")