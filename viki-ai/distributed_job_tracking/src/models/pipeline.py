from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
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
    """Model for updating pipeline status"""
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


class Pipeline(PipelineStatusUpdate):
    """Model for a pipeline with additional fields"""
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class PipelineResponse(BaseModel):
    """Response model for pipeline operations"""
    pipeline: Pipeline
    message: str = "Operation completed successfully"


class PipelineListItem(BaseModel):
    """Model for individual pipeline in list response"""
    id: str = Field(..., description="Pipeline identifier")
    status: PipelineStatus = Field(..., description="Aggregate status of all tasks for this pipeline")
    elapsed_time: Optional[float] = Field(None, description="Elapsed time since pipeline creation in seconds")
    is_page_level: bool = Field(..., description="True if pipeline has page-level processing (numeric task keys)")
    order: Optional[int] = Field(None, description="Execution order for this pipeline (used for sorting)")
    tasks: Dict[str, Any] = Field(..., description="Dictionary of task status data for the pipeline")


class PipelineListResponse(BaseModel):
    """Response model for listing pipelines for a run"""
    status: PipelineStatus = Field(..., description="Overall status of all pipelines (FAILED > IN_PROGRESS > COMPLETED)")
    pipeline_count: int = Field(..., description="Number of pipelines in this run")
    pipeline_ids: List[str] = Field(..., description="List of pipeline IDs in this run")
    elapsed_time: Optional[float] = Field(None, description="Elapsed time since earliest pipeline creation in seconds")
    pipelines: List[PipelineListItem] = Field(..., description="List of individual pipeline statuses")
