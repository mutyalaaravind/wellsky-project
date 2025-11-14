"""
Entity command models and handlers (CQRS - Command side)
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

from viki_shared.utils.logger import getLogger
from domain.models.entity import Entity, EntityCallbackData
from domain.ports.entity_ports import IEntityRepositoryPort

logger = getLogger(__name__)


@dataclass
class CreateEntityCommand:
    """Command to create a new entity."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    entity_data: Dict[str, Any]
    source_id: Optional[str] = None
    run_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_schema_id: Optional[str] = None


@dataclass
class UpdateEntityCommand:
    """Command to update an existing entity."""
    app_id: str
    patient_id: str
    entity_id: str
    tenant_id: Optional[str] = None
    document_id: Optional[str] = None
    entity_data: Optional[Dict[str, Any]] = None
    run_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_schema_id: Optional[str] = None


@dataclass
class DeleteEntityCommand:
    """Command to delete an entity."""
    app_id: str
    patient_id: str
    entity_id: str


@dataclass
class ProcessDocumentCallbackCommand:
    """Command to process document processing complete callback."""
    callback_data: EntityCallbackData


class EntityCommandHandler:
    """Handler for entity commands."""
    
    def __init__(self, entity_repository: IEntityRepositoryPort):
        self.entity_repository = entity_repository
    
    async def handle_create_entity(self, command: CreateEntityCommand) -> str:
        """
        Handle create entity command.
        
        Args:
            command: Create entity command
            
        Returns:
            Entity ID of the created entity
        """
        extra = {
            "operation": "create_entity",
            "app_id": command.app_id,
            "patient_id": command.patient_id,
            "entity_type": command.entity_type
        }
        
        logger.info("Handling create entity command", extra=extra)
        
        # Create entity aggregate (id, created_at, modified_at handled by AggBase)
        entity = Entity(
            app_id=command.app_id,
            tenant_id=command.tenant_id,
            patient_id=command.patient_id,
            document_id=command.document_id,
            source_id=command.source_id,
            entity_data=command.entity_data,
            run_id=command.run_id,
            entity_type=command.entity_type,
            entity_schema_id=command.entity_schema_id
        )
        
        # Save through repository
        entity_id = await self.entity_repository.save_entity(entity)
        
        logger.info(f"Successfully created entity: {entity_id}", extra={**extra, "entity_id": entity_id})
        return entity_id
    
    async def handle_update_entity(self, command: UpdateEntityCommand) -> None:
        """
        Handle update entity command.
        
        Args:
            command: Update entity command
        """
        extra = {
            "operation": "update_entity",
            "app_id": command.app_id,
            "patient_id": command.patient_id,
            "entity_id": command.entity_id
        }
        
        logger.info("Handling update entity command", extra=extra)
        
        # Get existing entity
        existing_entity = await self.entity_repository.get_entity(
            command.app_id, command.patient_id, command.entity_id
        )
        
        if not existing_entity:
            raise ValueError(f"Entity not found: {command.entity_id}")
        
        # Update entity fields
        if command.tenant_id is not None:
            existing_entity.tenant_id = command.tenant_id
        if command.document_id is not None:
            existing_entity.document_id = command.document_id
        if command.entity_data is not None:
            existing_entity.entity_data.update(command.entity_data)
        if command.run_id is not None:
            existing_entity.run_id = command.run_id
        if command.entity_type is not None:
            existing_entity.entity_type = command.entity_type
        if command.entity_schema_id is not None:
            existing_entity.entity_schema_id = command.entity_schema_id
        
        # Update modified_at (AggBase handles this automatically, but we can set it explicitly)
        existing_entity.modified_at = datetime.utcnow()
        
        # Save through repository
        await self.entity_repository.update_entity(existing_entity)
        
        logger.info(f"Successfully updated entity: {command.entity_id}", extra=extra)
    
    async def handle_delete_entity(self, command: DeleteEntityCommand) -> None:
        """
        Handle delete entity command.
        
        Args:
            command: Delete entity command
        """
        extra = {
            "operation": "delete_entity",
            "app_id": command.app_id,
            "patient_id": command.patient_id,
            "entity_id": command.entity_id
        }
        
        logger.info("Handling delete entity command", extra=extra)
        
        # Check if entity exists
        existing_entity = await self.entity_repository.get_entity(
            command.app_id, command.patient_id, command.entity_id
        )
        
        if not existing_entity:
            raise ValueError(f"Entity not found: {command.entity_id}")
        
        # Delete through repository
        await self.entity_repository.delete_entity(
            command.app_id, command.patient_id, command.entity_id
        )
        
        logger.info(f"Successfully deleted entity: {command.entity_id}", extra=extra)
    
    async def handle_process_document_callback(self, command: ProcessDocumentCallbackCommand) -> dict:
        """
        Handle document processing callback command.
        
        Args:
            command: Process document callback command
            
        Returns:
            Processing result summary
        """
        callback_data = command.callback_data
        
        extra = {
            "operation": "process_document_callback",
            "app_id": callback_data.app_id,
            "patient_id": callback_data.patient_id,
            "document_id": callback_data.document_id,
            "run_id": callback_data.run_id,
            "entities_count": len(callback_data.entities_data) if callback_data.entities_data else 0
        }
        
        logger.info("Handling document processing callback", extra=extra)
        
        if not callback_data.entities_data:
            logger.info("No entities in callback data", extra=extra)
            return {
                "entities_received": 0,
                "entities_saved": 0,
                "entity_document_ids": []
            }
        
        # Group entities by type
        entities_by_type = callback_data.group_entities_by_type()
        
        all_entities = []
        saved_doc_ids = []
        
        # Create entity aggregates for each type
        for entity_type, entities_data in entities_by_type.items():
            type_entities = []
            
            for entity_data in entities_data:
                # Extract the original entity ID from Paperglass if it exists
                paperglass_entity_id = entity_data.get('id')
                
                # Create a copy of entity_data without the 'id' field to avoid duplication
                # The 'id' should be stored as the entity's primary identifier, not in entity_data
                entity_data_clean = {k: v for k, v in entity_data.items() if k != 'id'}
                
                # Build entity kwargs
                entity_kwargs = {
                    "app_id": callback_data.app_id,
                    "tenant_id": callback_data.tenant_id,
                    "patient_id": callback_data.patient_id,
                    "document_id": callback_data.document_id,
                    "source_id": callback_data.source_id,
                    "entity_data": entity_data_clean,
                    "run_id": callback_data.run_id,
                    "entity_type": entity_type,
                    "entity_schema_id": f"document_processing_callback_{entity_type}",
                    "callback_timestamp": callback_data.timestamp,
                    "callback_status": callback_data.status,
                    "callback_metadata": callback_data.metadata
                }
                
                # If Paperglass provided an entity ID, use it; otherwise let AggBase generate one
                if paperglass_entity_id:
                    entity_kwargs["id"] = paperglass_entity_id
                    logger.debug(f"Using Paperglass entity ID: {paperglass_entity_id}", extra={
                        "operation": "create_entity_from_callback",
                        "entity_type": entity_type,
                        "paperglass_id": paperglass_entity_id
                    })
                else:
                    logger.info("No entity ID found in Paperglass entity data, generating new ID", extra={
                        "operation": "create_entity_from_callback",
                        "entity_type": entity_type,
                        "entity_data_keys": list(entity_data.keys())
                    })
                
                entity = Entity(**entity_kwargs)
                type_entities.append(entity)
            
            all_entities.extend(type_entities)
        
        # Save all entities in batch
        saved_doc_ids = await self.entity_repository.save_entities_batch(all_entities)
        
        result = {
            "entities_received": len(callback_data.entities_data),
            "entities_saved": len(saved_doc_ids),
            "entity_document_ids": saved_doc_ids
        }
        
        logger.info("Successfully processed document callback", extra={**extra, **result})
        return result