from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

try:
    from viki_shared.models.base import AggBase
except ImportError:
    # Fallback if shared library is not available
    from pydantic import BaseModel, Field
    from datetime import datetime, timezone

    class AggBase(BaseModel):
        """Fallback base class if shared library unavailable"""
        id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
        created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        created_by: Optional[str] = None
        modified_by: Optional[str] = None
        active: Optional[bool] = True


class DocumentMetadata(BaseModel):
    """Document metadata key-value pairs"""
    key: str = Field(..., description="Metadata key")
    value: str = Field(..., description="Metadata value")


class Document(AggBase):
    """Document model with audit trail"""
    app_id: str = Field(..., description="Application ID this document belongs to")
    subject_id: str = Field(..., description="Subject ID this document belongs to")
    name: str = Field(..., description="Original filename")
    uri: str = Field(..., description="Google Cloud Storage URI")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Document metadata")
    status: str = Field(default="NOT_STARTED", description="Processing status: NOT_STARTED, QUEUED, IN_PROGRESS, COMPLETED, FAILED")
    content_type: Optional[str] = Field(None, description="MIME type of the document")
    size: Optional[int] = Field(None, description="File size in bytes")
    run_id: Optional[str] = Field(None, description="DJT job run ID for tracking processing status")

    @classmethod
    def create(
        cls,
        app_id: str,
        subject_id: str,
        name: str,
        uri: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        created_by: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> "Document":
        """Create a new document"""
        return cls(
            app_id=app_id,
            subject_id=subject_id,
            name=name,
            uri=uri,
            metadata=metadata or {},
            status="NOT_STARTED",
            content_type=content_type,
            size=size,
            created_by=created_by,
            run_id=run_id,
            active=True
        )

    def update_status(self, status: str, modified_by: Optional[str] = None):
        """Update document processing status"""
        self.status = status
        self.modified_at = datetime.now(timezone.utc)
        if modified_by:
            self.modified_by = modified_by

    def soft_delete(self, deleted_by: Optional[str] = None):
        """Soft delete the document"""
        self.active = False
        self.modified_at = datetime.now(timezone.utc)
        if deleted_by:
            self.modified_by = deleted_by


class CreateDocumentRequest(BaseModel):
    """Request to create a new document"""
    name: str = Field(..., description="Document filename")
    metadata: Optional[Dict[str, str]] = Field(None, description="Document metadata")


class UpdateDocumentRequest(BaseModel):
    """Request to update a document"""
    name: Optional[str] = Field(None, description="Document filename")
    metadata: Optional[Dict[str, str]] = Field(None, description="Document metadata")
    status: Optional[str] = Field(None, description="Processing status")


class DocumentUploadRequest(BaseModel):
    """Request for document upload with metadata"""
    metadata: Optional[Dict[str, str]] = Field(None, description="Document metadata")