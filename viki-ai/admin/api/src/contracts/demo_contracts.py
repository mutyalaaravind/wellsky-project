from typing import List, Optional
from pydantic import BaseModel, Field

from model_aggregates.demo_subjects import DemoSubjectAggregate, DemoSubjectsConfigAggregate


class DemoSubjectResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[DemoSubjectAggregate] = Field(None, description="Demo subject data")


class DemoSubjectListResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[DemoSubjectAggregate] = Field(..., description="List of demo subjects")
    total: int = Field(..., description="Total number of subjects")


class DemoSubjectDeleteResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    deleted_id: str = Field(..., description="ID of the deleted subject")


class SubjectConfigResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[DemoSubjectsConfigAggregate] = Field(None, description="Subject configuration data")