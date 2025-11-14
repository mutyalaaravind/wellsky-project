from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SubjectConfig(BaseModel):
    """Configuration for demo subjects in an app"""
    app_id: str = Field(..., description="Application ID this config belongs to")
    label: str = Field(default="Subject", description="Label to use for subjects (e.g., 'Patient', 'Contract')")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")


class DemoSubject(BaseModel):
    """Individual demo subject"""
    id: str = Field(..., description="Unique identifier for the subject")
    app_id: str = Field(..., description="Application ID this subject belongs to")
    name: str = Field(..., description="Name of the subject")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft deletion timestamp")


class CreateSubjectRequest(BaseModel):
    """Request to create a new demo subject"""
    name: str = Field(..., description="Name of the subject")


class UpdateSubjectRequest(BaseModel):
    """Request to update a demo subject"""
    name: str = Field(..., description="Name of the subject")


class UpdateSubjectConfigRequest(BaseModel):
    """Request to update subject configuration"""
    label: str = Field(..., description="Label to use for subjects")