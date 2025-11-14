from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from .base import AggBase


class JobStatus(str, Enum):
    """Common job status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStatus(str, Enum):
    """Common pipeline status enumeration."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Metric(BaseModel):
    """Common metric model for tracking performance and statistics."""
    
    name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())
    labels: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class JobMetric(AggBase):
    """Job-specific metric tracking."""
    
    job_id: str
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseJob(AggBase):
    """Base job model with common job fields."""
    
    name: str
    status: JobStatus = JobStatus.PENDING
    priority: Optional[int] = 0
    retry_count: Optional[int] = 0
    max_retries: Optional[int] = 3
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class BasePipeline(AggBase):
    """Base pipeline model with common pipeline fields."""
    
    name: str
    description: Optional[str] = None
    status: PipelineStatus = PipelineStatus.NOT_STARTED
    config: Optional[Dict[str, Any]] = None
    steps: Optional[List[str]] = None
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaginationInfo(BaseModel):
    """Standard pagination model for API responses."""
    
    limit: int = Field(..., description="Maximum number of items per page")
    offset: int = Field(..., description="Number of items to skip")
    returned: int = Field(..., description="Number of items returned in this response")
    has_more: bool = Field(..., description="Whether there are more items available")