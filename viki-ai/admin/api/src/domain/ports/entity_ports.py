"""
Ports for Entity operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.entity import Entity, EntityCallbackData


class IEntityRepositoryPort(ABC):
    """Port for entity repository operations."""
    
    @abstractmethod
    async def save_entity(self, entity: Entity) -> str:
        """
        Save a single entity to the repository.
        
        Args:
            entity: Entity to save
            
        Returns:
            Document ID of the saved entity
        """
        pass
    
    @abstractmethod
    async def save_entities_batch(self, entities: List[Entity]) -> List[str]:
        """
        Save multiple entities in a batch transaction.
        
        Args:
            entities: List of entities to save
            
        Returns:
            List of document IDs of saved entities
        """
        pass
    
    @abstractmethod
    async def get_entity(self, app_id: str, subject_id: str, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.
        
        Args:
            app_id: Application ID
            subject_id: Subject ID (patient_id)
            entity_id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_entities(
        self,
        app_id: str,
        subject_id: str,
        entity_type: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Entity]:
        """
        List entities from a specific subcollection.

        Args:
            app_id: Application ID
            subject_id: Subject ID (patient_id)
            entity_type: Optional filter by entity type
            source_id: Optional filter by source ID
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def update_entity(self, entity: Entity) -> None:
        """
        Update an existing entity.
        
        Args:
            entity: Entity with updated data
        """
        pass
    
    @abstractmethod
    async def delete_entity(self, app_id: str, subject_id: str, entity_id: str) -> None:
        """
        Delete an entity by ID.
        
        Args:
            app_id: Application ID
            subject_id: Subject ID (patient_id)
            entity_id: Entity ID
        """
        pass


class IEntityCallbackHandlerPort(ABC):
    """Port for handling entity callbacks from external services."""
    
    @abstractmethod
    async def process_document_callback(self, callback_data: EntityCallbackData) -> dict:
        """
        Process document processing complete callback.
        
        Args:
            callback_data: Callback data from external service
            
        Returns:
            Processing result summary
        """
        pass