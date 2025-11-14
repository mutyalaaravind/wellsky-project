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


class SaveOnboardConfigCommand(BaseCommand):
    """Command to save onboard app configuration"""
    type: str = "SaveOnboardConfig"
    app_id: str = Field(..., description="Application ID")
    business_unit: str = Field(..., description="Business unit code")
    solution_code: str = Field(..., description="Solution code")
    app_name: Optional[str] = Field(None, description="Application name")
    app_description: Optional[str] = Field(None, description="Application description")
    entity_schema: Optional[dict] = Field(None, description="Generated JSON schema for entity extraction")
    extraction_prompt: Optional[str] = Field(None, description="Generated extraction prompt")
    pipeline_template: Optional[str] = Field(None, description="Selected pipeline template")


# Queries (for CQRS read side)
class CheckAppConfigExistsQuery(BaseModel):
    """Query to check if app config exists"""
    app_id: str = Field(..., description="Application ID")