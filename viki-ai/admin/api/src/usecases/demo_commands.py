from typing import Optional
from pydantic import BaseModel, Field
from uuid import uuid1


class BaseCommand(BaseModel):
    """Base command following CQRS pattern"""
    id: str = Field(default_factory=lambda: uuid1().hex)
    type: str
    created_by: Optional[str] = None
    execution_id: Optional[str] = None

    class Config:
        frozen = True


class CreateDemoSubjectCommand(BaseCommand):
    """Command to create a new demo subject"""
    type: str = "CreateDemoSubject"
    app_id: str = Field(..., description="Application ID")
    name: str = Field(..., description="Subject name")


class UpdateDemoSubjectCommand(BaseCommand):
    """Command to update a demo subject"""
    type: str = "UpdateDemoSubject"
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")
    name: str = Field(..., description="Subject name")


class DeleteDemoSubjectCommand(BaseCommand):
    """Command to delete a demo subject"""
    type: str = "DeleteDemoSubject"
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")


class UpdateSubjectConfigCommand(BaseCommand):
    """Command to update subject configuration"""
    type: str = "UpdateSubjectConfig"
    app_id: str = Field(..., description="Application ID")
    label: str = Field(..., description="Subject label")


# Queries (for CQRS read side)
class GetDemoSubjectsQuery(BaseModel):
    """Query to get demo subjects for an app"""
    app_id: str = Field(..., description="Application ID")


class GetDemoSubjectQuery(BaseModel):
    """Query to get a specific demo subject"""
    app_id: str = Field(..., description="Application ID")
    subject_id: str = Field(..., description="Subject ID")


class GetSubjectConfigQuery(BaseModel):
    """Query to get subject configuration"""
    app_id: str = Field(..., description="Application ID")