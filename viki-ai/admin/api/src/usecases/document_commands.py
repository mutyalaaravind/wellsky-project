from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CreateDocumentCommand(BaseModel):
    """Command to create a new document"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    name: str = Field(..., description="Document filename")
    uri: str = Field(..., description="Google Cloud Storage URI")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    content_type: Optional[str] = Field(None, description="MIME type")
    size: Optional[int] = Field(None, description="File size in bytes")
    created_by: Optional[str] = Field(None, description="User creating the document")


class UpdateDocumentCommand(BaseModel):
    """Command to update a document"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    document_id: str = Field(..., description="Document ID to update")
    name: Optional[str] = Field(None, description="Document filename")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    status: Optional[str] = Field(None, description="Processing status")
    modified_by: Optional[str] = Field(None, description="User modifying the document")


class DeleteDocumentCommand(BaseModel):
    """Command to delete a document"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    document_id: str = Field(..., description="Document ID to delete")
    deleted_by: Optional[str] = Field(None, description="User deleting the document")


class UpdateDocumentStatusCommand(BaseModel):
    """Command to update document status"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    document_id: str = Field(..., description="Document ID")
    status: str = Field(..., description="New processing status")
    modified_by: Optional[str] = Field(None, description="User updating the status")


class GetDocumentsQuery(BaseModel):
    """Query to get documents for a subject"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    include_deleted: bool = Field(default=False, description="Include soft-deleted documents")


class GetDocumentQuery(BaseModel):
    """Query to get a specific document"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    document_id: str = Field(..., description="Document ID")


class UploadDocumentCommand(BaseModel):
    """Command to handle document upload"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME type")
    size: Optional[int] = Field(None, description="File size in bytes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    uploaded_by: Optional[str] = Field(None, description="User uploading the document")


class UpdateDocumentStatusFromCallbackCommand(BaseModel):
    """Command to update document status from Paperglass callback"""
    document_id: str = Field(..., description="Document ID")
    status: str = Field(..., description="New processing status from Paperglass")
    operation_type: Optional[str] = Field(None, description="Processing operation type")
    timestamp: Optional[str] = Field(None, description="Callback timestamp")
    app_id: Optional[str] = Field(None, description="Application ID")
    tenant_id: Optional[str] = Field(None, description="Tenant ID")
    patient_id: Optional[str] = Field(None, description="Patient/Subject ID")

    class Config:
        frozen = True