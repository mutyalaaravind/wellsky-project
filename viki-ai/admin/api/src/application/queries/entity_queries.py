"""
Entity query models and handlers (CQRS - Query side)
"""

from dataclasses import dataclass
from typing import List, Optional

from viki_shared.utils.logger import getLogger
from domain.models.entity import Entity
from domain.ports.entity_ports import IEntityRepositoryPort

logger = getLogger(__name__)


@dataclass
class GetEntityQuery:
    """Query to get an entity by ID."""
    app_id: str
    subject_id: str
    entity_id: str


@dataclass
class ListEntitiesQuery:
    """Query to list entities with filters."""
    app_id: str
    subject_id: str
    entity_type: Optional[str] = None
    source_id: Optional[str] = None
    limit: int = 50
    offset: int = 0


class EntityQueryHandler:
    """Handler for entity queries."""
    
    def __init__(self, entity_repository: IEntityRepositoryPort):
        self.entity_repository = entity_repository
    
    async def handle_get_entity(self, query: GetEntityQuery) -> Optional[Entity]:
        """
        Handle get entity query.
        
        Args:
            query: Get entity query
            
        Returns:
            Entity if found, None otherwise
        """
        extra = {
            "operation": "get_entity",
            "app_id": query.app_id,
            "subject_id": query.subject_id,
            "entity_id": query.entity_id
        }
        
        logger.debug("Handling get entity query", extra=extra)
        
        entity = await self.entity_repository.get_entity(
            query.app_id, query.subject_id, query.entity_id
        )
        
        if entity:
            logger.debug(f"Successfully retrieved entity: {query.entity_id}", extra=extra)
        else:
            logger.debug(f"Entity not found: {query.entity_id}", extra=extra)
        
        return entity
    
    async def handle_list_entities(self, query: ListEntitiesQuery) -> List[Entity]:
        """
        Handle list entities query.
        
        Args:
            query: List entities query
            
        Returns:
            List of entities
        """
        extra = {
            "operation": "list_entities",
            "app_id": query.app_id,
            "subject_id": query.subject_id,
            "entity_type": query.entity_type,
            "source_id": query.source_id,
            "limit": query.limit,
            "offset": query.offset
        }
        
        logger.debug("Handling list entities query", extra=extra)
        
        entities = await self.entity_repository.list_entities(
            app_id=query.app_id,
            subject_id=query.subject_id,
            entity_type=query.entity_type,
            source_id=query.source_id,
            limit=query.limit,
            offset=query.offset
        )
        
        logger.debug(f"Successfully retrieved {len(entities)} entities", extra={**extra, "entities_count": len(entities)})
        return entities