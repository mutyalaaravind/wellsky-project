from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SimpleJobCreate(BaseModel):
    """Model for creating a simple job entry"""
    app_id: str = Field(..., description="Application ID")
    tenant_id: str = Field(..., description="Tenant ID")
    patient_id: str = Field(..., description="Patient ID")
    document_id: str = Field(..., description="Document ID")
    run_id: str = Field(..., description="Run ID - used as part of Redis key")
    name: str = Field(..., description="Job name")
    pages: int = Field(..., ge=1, description="Number of pages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SimpleJob(SimpleJobCreate):
    """Model for a simple job with additional fields"""
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class SimpleJobResponse(BaseModel):
    """Response model for simple job operations"""
    job: SimpleJob
    message: str = "Operation completed successfully"


class SimpleJobUpdate(BaseModel):
    """Model for updating a simple job"""
    app_id: Optional[str] = None
    tenant_id: Optional[str] = None
    patient_id: Optional[str] = None
    document_id: Optional[str] = None
    name: Optional[str] = None
    pages: Optional[int] = Field(None, ge=1)
    metadata: Optional[Dict[str, Any]] = None
