"""
Models for Distributed Job Tracking (DJT) service communication - Shared Library

These models mirror the structure used by the DJT service for API communication
and can be used across all services that interact with DJT.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class PipelineStatus(str, Enum):
    """Enum for pipeline status values"""
    UNKNOWN = 'UNKNOWN'
    NOT_STARTED = 'NOT_STARTED'
    QUEUED = 'QUEUED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class PipelineStatusUpdate(BaseModel):
    """Model for updating pipeline status in DJT service"""
    id: Optional[str] = Field(None, description="Unique pipeline identifier")
    status: PipelineStatus = Field(..., description="Pipeline status")
    page_number: Optional[int] = Field(None, ge=1, description="Page number for this pipeline (optional)")
    order: Optional[int] = Field(None, description="Execution order for this pipeline (used for sorting)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional pipeline metadata")
    
    # Job creation fields (for auto-creating job if it doesn't exist)
    app_id: str = Field(..., description="Application ID")
    tenant_id: str = Field(..., description="Tenant ID")
    patient_id: str = Field(..., description="Patient ID")
    document_id: str = Field(..., description="Document ID")
    pages: int = Field(..., ge=1, description="Number of pages")