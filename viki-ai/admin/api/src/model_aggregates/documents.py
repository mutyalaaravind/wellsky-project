from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


class BaseAggregate(BaseModel):
    """Base aggregate following DDD patterns"""
    id: str = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    events: List = Field(default_factory=list, description="Domain events")

    def mark_event(self, event):
        """Mark domain event for publishing"""
        self.events.append(event)

    def clear_events(self):
        """Clear domain events after publishing"""
        self.events.clear()


class DocumentAggregate(BaseAggregate):
    """Aggregate for individual document"""
    app_id: str = Field(..., description="Application ID this document belongs to")
    subject_id: str = Field(..., description="Subject ID this document belongs to")
    name: str = Field(..., description="Original filename")
    uri: str = Field(..., description="Google Cloud Storage URI")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    status: str = Field(default="NOT_STARTED", description="Processing status: NOT_STARTED, QUEUED, IN_PROGRESS, COMPLETED, FAILED")
    content_type: Optional[str] = Field(None, description="MIME type of the document")
    size: Optional[int] = Field(None, description="File size in bytes")
    active: bool = Field(default=True, description="Whether the document is active (false = soft deleted)")
    created_by: Optional[str] = Field(None, description="User who created the document")
    modified_by: Optional[str] = Field(None, description="User who last modified the document")

    @classmethod
    def create(
        cls,
        app_id: str,
        subject_id: str,
        name: str,
        uri: str,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        created_by: Optional[str] = None
    ) -> "DocumentAggregate":
        """Create a new document"""
        now = datetime.utcnow()
        return cls(
            id=uuid4().hex,
            app_id=app_id,
            subject_id=subject_id,
            name=name,
            uri=uri,
            metadata=metadata or {},
            status="NOT_STARTED",
            content_type=content_type,
            size=size,
            active=True,
            created_by=created_by,
            created_at=now,
            updated_at=now
        )

    def update_status(self, status: str, modified_by: Optional[str] = None):
        """Update document processing status"""
        if not self.active:
            raise ValueError("Cannot update inactive document")
        self.status = status
        self.updated_at = datetime.utcnow()
        if modified_by:
            self.modified_by = modified_by

    def update_metadata(self, metadata: Dict[str, Any], modified_by: Optional[str] = None):
        """Update document metadata"""
        if not self.active:
            raise ValueError("Cannot update inactive document")
        self.metadata = metadata
        self.updated_at = datetime.utcnow()
        if modified_by:
            self.modified_by = modified_by

    def soft_delete(self, deleted_by: Optional[str] = None):
        """Soft delete the document by setting active=false"""
        if not self.active:
            raise ValueError("Document already deleted")
        self.active = False
        self.updated_at = datetime.utcnow()
        if deleted_by:
            self.modified_by = deleted_by

    @property
    def is_deleted(self) -> bool:
        """Check if document is deleted"""
        return not self.active

    @property
    def gcs_bucket_name(self) -> str:
        """Extract bucket name from GCS URI"""
        if self.uri.startswith("gs://"):
            return self.uri.split("/")[2]
        return ""

    @property
    def gcs_object_path(self) -> str:
        """Extract object path from GCS URI"""
        if self.uri.startswith("gs://"):
            parts = self.uri.split("/", 3)
            return parts[3] if len(parts) > 3 else ""
        return ""