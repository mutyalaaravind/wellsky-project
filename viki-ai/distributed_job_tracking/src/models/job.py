from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class JobType(str, Enum):
    DATA_PROCESSING = "data_processing"
    DOCUMENT_ANALYSIS = "document_analysis"
    ENTITY_EXTRACTION = "entity_extraction"
    MEDICATION_EXTRACTION = "medication_extraction"
    CUSTOM = "custom"


class JobCreate(BaseModel):
    name: str = Field(..., description="Human-readable job name")
    job_type: JobType = Field(..., description="Type of job")
    priority: JobPriority = Field(default=JobPriority.NORMAL, description="Job priority")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Job payload data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    timeout_seconds: Optional[int] = Field(default=None, description="Job timeout in seconds")
    scheduled_at: Optional[datetime] = Field(default=None, description="When to execute the job")
    depends_on: List[str] = Field(default_factory=list, description="List of job IDs this job depends on")
    parent_job_id: Optional[str] = Field(default=None, description="Parent job ID if this is a sub-job")
    sub_jobs: List["JobCreate"] = Field(default_factory=list, description="List of sub-jobs to create")


class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Job progress percentage")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique job identifier")
    name: str = Field(..., description="Human-readable job name")
    job_type: JobType = Field(..., description="Type of job")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current job status")
    priority: JobPriority = Field(default=JobPriority.NORMAL, description="Job priority")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Job progress percentage")
    
    # Payload and results
    payload: Dict[str, Any] = Field(default_factory=dict, description="Job payload data")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Job result data")
    error_message: Optional[str] = Field(default=None, description="Error message if job failed")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")
    scheduled_at: Optional[datetime] = Field(default=None, description="When to execute the job")
    
    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_count: int = Field(default=0, description="Current retry count")
    timeout_seconds: Optional[int] = Field(default=None, description="Job timeout in seconds")
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="List of job IDs this job depends on")
    
    # Hierarchical job structure
    parent_job_id: Optional[str] = Field(default=None, description="Parent job ID if this is a sub-job")
    sub_job_ids: List[str] = Field(default_factory=list, description="List of sub-job IDs")
    is_parent_job: bool = Field(default=False, description="Whether this job has sub-jobs")
    
    # Worker information
    worker_id: Optional[str] = Field(default=None, description="ID of worker processing the job")
    worker_host: Optional[str] = Field(default=None, description="Host of worker processing the job")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobWithSubJobs(BaseModel):
    """Job model that includes its sub-jobs"""
    job: Job
    sub_jobs: List[Job] = Field(default_factory=list, description="List of sub-jobs")


class JobResponse(BaseModel):
    job: Job
    message: str = "Job operation successful"


class JobWithSubJobsResponse(BaseModel):
    job_with_sub_jobs: JobWithSubJobs
    message: str = "Job operation successful"


class JobListResponse(BaseModel):
    jobs: List[Job]
    total: int
    page: int = 1
    page_size: int = 50
    has_next: bool = False
    has_prev: bool = False


# Enable forward references for self-referencing models
JobCreate.model_rebuild()
