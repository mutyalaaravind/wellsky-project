"""
Contracts for Paperglass API integration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class AppConfigResponse(BaseModel):
    """Response model for App Config from Paperglass API."""
    id: str
    app_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: Dict[str, Any]
    active: bool = True
    created_at: datetime
    modified_at: datetime
    created_by: Optional[str] = None
    modified_by: Optional[str] = None


class AppConfigUpdateRequest(BaseModel):
    """Request model for updating App Config."""
    config: Dict[str, Any]
    name: Optional[str] = None
    description: Optional[str] = None
    archive_current: bool = True
    version_comment: Optional[str] = None


class EntitySchemaCreateRequest(BaseModel):
    """Request model for creating Entity Schema via PaperGlass API /api/admin/entity_schema."""
    name: str = Field(..., description="Human-readable name for the entity schema")
    description: Optional[str] = Field(None, description="Description of the entity schema")
    app_id: str = Field(..., description="Application ID this schema belongs to")
    label: Optional[str] = Field(None, description="UI-friendly label for the schema")
    required_scopes: Optional[Dict[str, list]] = Field(None, description="Scope-specific required fields mapping")
    schema: Dict[str, Any] = Field(..., description="Pure JSON schema without meta attributes")


class EntitySchemaCreateResponse(BaseModel):
    """Response model for Entity Schema creation."""
    success: bool
    schema_id: str
    message: str
    id: Optional[str] = None
    title: Optional[str] = None
    app_id: Optional[str] = None


class PaperglassPort(ABC):
    """Port interface for Paperglass API operations."""
    
    @abstractmethod
    async def get_app_config(self, app_id: str, generate_if_missing: bool = False) -> Optional[AppConfigResponse]:
        """
        Get app configuration for the given app_id.
        
        Args:
            app_id: The application identifier
            generate_if_missing: Generate default config if not found
            
        Returns:
            AppConfigResponse if found, None if not found
            
        Raises:
            Exception: If there's an error calling the API
        """
        pass

    @abstractmethod
    async def list_app_configs(self, limit: int = 50, offset: int = 0) -> List[AppConfigResponse]:
        """
        List all app configurations with pagination.
        
        Args:
            limit: Maximum number of configs to return (default: 50)
            offset: Number of configs to skip (default: 0)
            
        Returns:
            List of AppConfigResponse objects
            
        Raises:
            Exception: If there's an error calling the API
        """
        pass

    @abstractmethod
    async def update_app_config(self, app_id: str, config_update: AppConfigUpdateRequest) -> AppConfigResponse:
        """
        Update app configuration for the given app_id.
        
        Args:
            app_id: The application identifier
            config_update: The configuration update request
            
        Returns:
            Updated AppConfigResponse
            
        Raises:
            Exception: If there's an error calling the API
        """
        pass

    @abstractmethod
    async def create_entity_schema(self, schema_request: EntitySchemaCreateRequest) -> EntitySchemaCreateResponse:
        """
        Create a new entity schema via PaperGlass API.

        Args:
            schema_request: The entity schema creation request

        Returns:
            EntitySchemaCreateResponse with creation details

        Raises:
            Exception: If there's an error calling the API
        """
        pass

    @abstractmethod
    async def get_document_status(self, document_id: str, app_id: str, tenant_id: str, patient_id: str) -> Dict[str, Any]:
        """
        Get document processing status from PaperGlass API.

        Args:
            document_id: The document identifier
            app_id: Application ID for context
            tenant_id: Tenant ID for context
            patient_id: Patient ID for context

        Returns:
            Dict containing document status including progress from DJT

        Raises:
            Exception: If there's an error calling the API
        """
        pass