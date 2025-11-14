"""
Onboard Domain Models

This module contains Pydantic models for onboarding operations.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from shared.domain.models.djt_models import PipelineStatusUpdate, PipelineStatus


class StorageMetadataModel(BaseModel):
    """Metadata about a stored file."""
    content_type: str
    size_bytes: int
    storage_path: str
    created_at: str


class OnboardGenerationResult(BaseModel):
    """Result of the onboard generation process."""
    storage_metadata: StorageMetadataModel
    entity_schema: Dict[str, Any]
    extraction_prompt: Optional[str] = None
    test_extraction: Optional[Dict[str, Any]] = None


class OnboardTaskStatusUpdate(PipelineStatusUpdate):
    """Onboard-specific task status update extending the generic DJT model."""
    pass


class OnboardJobProgress(BaseModel):
    """Model for onboard job progress response."""
    job_id: str
    app_id: str
    status: str
    current_task: Optional[str] = None
    current_task_name: Optional[str] = None
    overall_progress_percentage: int = 0
    tasks: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


class OnboardSaveRequest(BaseModel):
    """Request model for saving onboarding app config."""
    app_id: str
    business_unit: str
    solution_code: str
    app_name: Optional[str] = None
    app_description: Optional[str] = None
    entity_schema: Optional[Dict[str, Any]] = None
    extraction_prompt: Optional[str] = None
    pipeline_template: Optional[str] = None
    

class OnboardSaveResponse(BaseModel):
    """Response model for onboard save endpoint."""
    success: bool
    message: str
    app_id: str
    config_created: bool
    entity_schema_id: Optional[str] = None
    pipeline_key: Optional[str] = None