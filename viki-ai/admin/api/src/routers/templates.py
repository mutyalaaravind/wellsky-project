"""
Templates Router for Admin API

This router provides endpoints for fetching pipeline templates from entity extraction service.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from kink import di
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap

from contracts.entity_extraction_contracts import EntityExtractionPort
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


class TemplateResponse(BaseModel):
    """Response model for template data."""
    id: str
    key: str
    name: str
    description: str = None
    scope: str = "global"
    app_id: str = None
    labels: List[str] = []


class TemplatesListResponse(BaseModel):
    """Response model for templates list endpoint."""
    success: bool
    message: str
    data: List[TemplateResponse]
    count: int


@router.get(
    "/templates",
    response_model=TemplatesListResponse,
    summary="Get pipeline templates",
    description="Fetch pipeline templates from entity extraction service (app_id=GLOBAL, label=template)."
)
async def get_templates(current_user: User = RequireAuth) -> TemplatesListResponse:
    """
    Get pipeline templates from entity extraction service.
    
    This endpoint fetches pipeline configurations that are marked as templates
    (app_id=GLOBAL and label=template) from the entity extraction service.
    
    Returns:
        List of template configurations
    """
    extra = {
        "operation": "get_templates",
        "endpoint": "/api/v1/templates"
    }
    
    try:
        logger.debug("Fetching pipeline templates from entity extraction service", extra=extra)
        
        # Get entity extraction service from dependency injection
        entity_extraction_service = di[EntityExtractionPort]
        
        # Fetch templates
        templates = await entity_extraction_service.get_templates()
        
        # Convert to response format
        template_responses = [
            TemplateResponse(
                id=template.id,
                key=template.key,
                name=template.name,
                description=template.description or "",
                scope=template.scope,
                app_id=template.app_id,
                labels=template.labels
            )
            for template in templates
        ]
        
        extra.update({
            "templates_count": len(template_responses),
            "templates": [{"id": t.id, "key": t.key, "name": t.name} for t in template_responses]
        })
        
        logger.debug(f"Successfully retrieved {len(template_responses)} pipeline templates", extra=extra)
        
        return TemplatesListResponse(
            success=True,
            message="Templates retrieved successfully",
            data=template_responses,
            count=len(template_responses)
        )
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error fetching pipeline templates: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error
        if "Entity extraction service error" in str(e):
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch templates from entity extraction service: {str(e)}"
            )
        elif "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Entity extraction service unavailable: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error fetching templates: {str(e)}"
            )