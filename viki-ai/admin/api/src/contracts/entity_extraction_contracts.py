"""
Contracts for Entity Extraction Service
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class EntityExtractionPipeline:
    """Model for entity extraction pipeline configuration."""
    
    def __init__(
        self,
        id: str,
        key: str,
        name: str,
        description: Optional[str] = None,
        scope: str = "default",
        version: Optional[str] = None,
        output_entity: Optional[str] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
        auto_publish_entities_enabled: Optional[bool] = True,
        labels: Optional[List[str]] = None,
        app_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        created_by: Optional[str] = None,
        modified_by: Optional[str] = None,
        active: bool = True
    ):
        self.id = id
        self.key = key
        self.name = name
        self.description = description
        self.scope = scope
        self.version = version
        self.output_entity = output_entity
        self.tasks = tasks or []
        self.auto_publish_entities_enabled = auto_publish_entities_enabled
        self.labels = labels or []
        self.app_id = app_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.modified_by = modified_by
        self.active = active

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "version": self.version,
            "output_entity": self.output_entity,
            "tasks": self.tasks,
            "auto_publish_entities_enabled": self.auto_publish_entities_enabled,
            "labels": self.labels,
            "app_id": self.app_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }


class LlmExecuteRequest(BaseModel):
    """Request model for LLM execution."""
    gs_uri: str
    system_instructions: Optional[str] = None
    prompt: str
    json_schema: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    model_parameters: Optional[Dict[str, Any]] = None


class LlmExecuteResponse(BaseModel):
    """Response model for LLM execution."""
    success: bool
    content: Optional[Dict[str, Any]] = None
    raw_response: Optional[str] = None
    error_message: Optional[str] = None
    execution_metadata: Optional[Dict[str, Any]] = None


class EntityExtractionPort(ABC):
    """Port for entity extraction service operations."""

    @abstractmethod
    async def get_pipeline_configs(
        self,
        labels: Optional[List[str]] = None,
        app_id: Optional[str] = None
    ) -> List[EntityExtractionPipeline]:
        """
        Get pipeline configurations with optional filtering.
        
        Args:
            labels: Optional list of labels to filter by (configs must have ALL labels)
            app_id: Optional app_id to filter by
            
        Returns:
            List of EntityExtractionPipeline objects
        """
        pass

    @abstractmethod
    async def get_templates(self) -> List[EntityExtractionPipeline]:
        """
        Get template pipeline configurations (app_id=GLOBAL, label=template).
        
        Returns:
            List of template EntityExtractionPipeline objects
        """
        pass

    @abstractmethod
    async def execute_llm(self, request: LlmExecuteRequest) -> LlmExecuteResponse:
        """
        Execute LLM prompt with document processing.
        
        Args:
            request: LLM execution request containing GS URI, prompt, and schema
            
        Returns:
            LlmExecuteResponse with generated content and metadata
        """
        pass

    @abstractmethod
    async def get_pipeline_by_key(self, scope: str, pipeline_key: str) -> Optional[EntityExtractionPipeline]:
        """
        Get a specific pipeline configuration by scope and key.
        
        Args:
            scope: Scope/namespace of the pipeline
            pipeline_key: Key identifier of the pipeline
            
        Returns:
            EntityExtractionPipeline object if found, None otherwise
        """
        pass

    @abstractmethod
    async def create_pipeline_from_template(
        self,
        template_id: str,
        scope: str,
        pipeline_id: str,
        pipeline_config: Dict[str, Any]
    ) -> EntityExtractionPipeline:
        """
        Create a new pipeline by cloning from a template with customizations.
        
        Args:
            template_id: ID of the template pipeline to clone from
            scope: Scope/namespace for the new pipeline (typically app_id)
            pipeline_id: Unique identifier for the new pipeline within the scope
            pipeline_config: Configuration overrides and customizations for the pipeline
            
        Returns:
            EntityExtractionPipeline object representing the created pipeline
            
        Raises:
            Exception: If pipeline creation fails
        """
        pass