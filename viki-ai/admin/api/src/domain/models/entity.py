"""
Domain models for Entity aggregate
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from viki_shared.models.common import AggBase


class Entity(AggBase):
    """
    Entity aggregate root.
    
    Note: When creating an Entity, you can optionally pass an 'id' parameter to use
    a specific identifier (e.g., when preserving entity IDs from Paperglass).
    If no 'id' is provided, AggBase will automatically generate a new UUID.
    
    Example:
        # Create with auto-generated ID
        entity = Entity(app_id="123", tenant_id="456", ...)
        
        # Create with specific ID (e.g., from Paperglass)
        entity = Entity(id="paperglass_entity_id", app_id="123", tenant_id="456", ...)
    """

    app_id: str
    tenant_id: str
    patient_id: str  # Used as subject_id in the subcollection path
    document_id: str
    entity_data: Dict[str, Any]  # The actual entity content
    source_id: Optional[str] = None
    run_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_schema_id: Optional[str] = None
    callback_timestamp: Optional[str] = None
    callback_status: Optional[str] = None
    callback_metadata: Optional[Dict[str, Any]] = None
    
    def get_subcollection_path(self) -> str:
        """Get the Firestore subcollection path for this entity."""
        return f"admin_demo_subjects/{self.app_id}/subjects/{self.patient_id}/entities"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for storage."""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "source_id": self.source_id,
            "run_id": self.run_id,
            "entity_type": self.entity_type,
            "entity_schema_id": self.entity_schema_id,
            "callback_timestamp": self.callback_timestamp,
            "callback_status": self.callback_status,
            "callback_metadata": self.callback_metadata,
            "created_at": self.created_at,
            "updated_at": self.modified_at,  # Use modified_at from AggBase
            "created_by": self.created_by,
            "modified_by": self.modified_by,
            "active": self.active,
            **self.entity_data  # Merge the actual entity content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        """Create Entity from dictionary."""
        # Extract known fields (including AggBase fields)
        known_fields = {
            "id", "app_id", "tenant_id", "patient_id", "document_id", "source_id",
            "run_id", "entity_type", "entity_schema_id", "callback_timestamp",
            "callback_status", "callback_metadata", "created_at", "updated_at",
            "modified_at", "created_by", "modified_by", "active"
        }
        
        # Separate entity data from metadata
        entity_data = {k: v for k, v in data.items() if k not in known_fields}
        
        # Prepare metadata fields for Pydantic model creation
        metadata = {k: v for k, v in data.items() if k in known_fields and k != "updated_at"}
        
        # Handle updated_at -> modified_at mapping
        if "updated_at" in data and "modified_at" not in data:
            metadata["modified_at"] = data["updated_at"]
        
        return cls(
            entity_data=entity_data,
            **metadata
        )


@dataclass
class EntityCallbackData:
    """Value object for document processing callback data."""

    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str]
    status: str
    timestamp: str
    run_id: str
    metadata: Optional[Dict[str, Any]] = None
    entities_data: Optional[list] = None
    
    def group_entities_by_type(self) -> Dict[str, list]:
        """Group entities by entity_type."""
        if not self.entities_data:
            return {}
        
        entities_by_type = {}
        for entity in self.entities_data:
            entity_type = entity.get('entity_type', 'unknown')
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        return entities_by_type