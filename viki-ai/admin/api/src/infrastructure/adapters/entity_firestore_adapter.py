"""
Firestore adapter for Entity operations
"""

from typing import List, Optional
from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

from viki_shared.utils.logger import getLogger
from domain.models.entity import Entity
from domain.ports.entity_ports import IEntityRepositoryPort

logger = getLogger(__name__)


class EntityFirestoreAdapter(IEntityRepositoryPort):
    """Firestore implementation of the entity repository port."""
    
    def __init__(self, firestore_client: AsyncClient):
        self.client = firestore_client
    
    def _get_entities_collection_ref(self, app_id: str, subject_id: str):
        """Get reference to the entities subcollection."""
        return (
            self.client
            .collection("admin_demo_subjects")
            .document(app_id)
            .collection("subjects")
            .document(subject_id)
            .collection("entities")
        )
    
    def _convert_firestore_doc_to_entity(self, doc) -> Entity:
        """Convert Firestore document to Entity domain model."""
        data = doc.to_dict()
        
        # Convert Firestore datetime objects to Python datetime instances
        datetime_fields = ["created_at", "updated_at", "modified_at"]
        for field in datetime_fields:
            if field in data and data[field] is not None:
                if hasattr(data[field], "timestamp"):
                    # Firestore DatetimeWithNanoseconds to Python datetime
                    data[field] = datetime.fromtimestamp(data[field].timestamp())
                elif isinstance(data[field], datetime):
                    # Already a datetime, just remove timezone
                    data[field] = data[field].replace(tzinfo=None)
        
        return Entity.from_dict(data)
    
    async def _ensure_parent_documents_exist(self, app_id: str, patient_id: str) -> None:
        """Ensure that parent documents exist in the Firestore hierarchy."""
        # Create app document if it doesn't exist
        app_doc_ref = self.client.collection("admin_demo_subjects").document(app_id)
        app_doc = await app_doc_ref.get()
        if not app_doc.exists:
            app_data = {
                "app_id": app_id,
                "id": app_id,
                "label": f"Auto-created app: {app_id}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await app_doc_ref.set(app_data)
            logger.debug(f"Created parent app document: {app_id}")
        
        # Create subject document if it doesn't exist
        subject_doc_ref = (
            self.client
            .collection("admin_demo_subjects")
            .document(app_id)
            .collection("subjects")
            .document(patient_id)
        )
        subject_doc = await subject_doc_ref.get()
        if not subject_doc.exists:
            subject_data = {
                "app_id": app_id,
                "id": patient_id,
                "name": f"Auto-created subject: {patient_id}",
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await subject_doc_ref.set(subject_data)
            logger.debug(f"Created parent subject document: {patient_id}")

    async def save_entity(self, entity: Entity) -> str:
        """Save a single entity to Firestore."""
        extra = {
            "operation": "save_entity",
            "entity_id": entity.id,
            "app_id": entity.app_id,
            "patient_id": entity.patient_id,
            "subcollection_path": entity.get_subcollection_path()
        }
        
        logger.debug("Saving entity to Firestore", extra=extra)
        
        # Ensure parent documents exist first
        await self._ensure_parent_documents_exist(entity.app_id, entity.patient_id)
        
        entities_ref = self._get_entities_collection_ref(entity.app_id, entity.patient_id)
        doc_ref = entities_ref.document(entity.id)
        
        entity_data = entity.to_dict()
        await doc_ref.set(entity_data)
        
        logger.debug(f"Successfully saved entity: {entity.id}", extra=extra)
        return entity.id
    
    async def save_entities_batch(self, entities: List[Entity]) -> List[str]:
        """Save multiple entities in a batch transaction."""
        if not entities:
            return []
        
        extra = {
            "operation": "save_entities_batch",
            "entities_count": len(entities),
            "app_id": entities[0].app_id if entities else None,
            "patient_id": entities[0].patient_id if entities else None
        }
        
        logger.debug("Saving entities batch to Firestore", extra=extra)
        
        # Group entities by subcollection path for efficiency
        entities_by_path = {}
        for entity in entities:
            path_key = f"{entity.app_id}/{entity.patient_id}"
            if path_key not in entities_by_path:
                entities_by_path[path_key] = []
            entities_by_path[path_key].append(entity)
        
        # Ensure parent documents exist for all paths
        for path_key in entities_by_path.keys():
            app_id, patient_id = path_key.split("/")
            await self._ensure_parent_documents_exist(app_id, patient_id)
        
        # Use batch transaction for atomic writes
        batch = self.client.batch()
        doc_ids = []
        
        for path_key, path_entities in entities_by_path.items():
            app_id, patient_id = path_key.split("/")
            entities_ref = self._get_entities_collection_ref(app_id, patient_id)
            
            for entity in path_entities:
                doc_ref = entities_ref.document(entity.id)
                entity_data = entity.to_dict()
                batch.set(doc_ref, entity_data)
                doc_ids.append(entity.id)
        
        # Commit the batch
        await batch.commit()
        
        logger.debug(f"Successfully saved {len(doc_ids)} entities in batch", extra={**extra, "saved_doc_ids": doc_ids})
        return doc_ids
    
    async def get_entity(self, app_id: str, subject_id: str, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        extra = {
            "operation": "get_entity",
            "app_id": app_id,
            "subject_id": subject_id,
            "entity_id": entity_id
        }
        
        logger.debug("Getting entity from Firestore", extra=extra)
        
        entities_ref = self._get_entities_collection_ref(app_id, subject_id)
        doc = await entities_ref.document(entity_id).get()
        
        if not doc.exists:
            logger.debug(f"Entity not found: {entity_id}", extra=extra)
            return None
        
        entity = self._convert_firestore_doc_to_entity(doc)
        logger.debug(f"Successfully retrieved entity: {entity_id}", extra=extra)
        return entity
    
    async def list_entities(
        self,
        app_id: str,
        subject_id: str,
        entity_type: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Entity]:
        """List entities from a specific subcollection."""
        extra = {
            "operation": "list_entities",
            "app_id": app_id,
            "subject_id": subject_id,
            "entity_type": entity_type,
            "source_id": source_id,
            "limit": limit,
            "offset": offset
        }
        
        logger.debug("Listing entities from Firestore", extra=extra)
        
        entities_ref = self._get_entities_collection_ref(app_id, subject_id)
        query = entities_ref.limit(limit).offset(offset)
        
        if entity_type:
            query = query.where(filter=FieldFilter("entity_type", "==", entity_type))

        if source_id:
            query = query.where(filter=FieldFilter("source_id", "==", source_id))

        # Order by created_at for consistent pagination
        query = query.order_by("created_at")
        
        docs = query.stream()
        entities = []
        
        async for doc in docs:
            entity = self._convert_firestore_doc_to_entity(doc)
            entities.append(entity)
        
        logger.debug(f"Successfully retrieved {len(entities)} entities", extra={**extra, "entities_count": len(entities)})
        return entities
    
    async def update_entity(self, entity: Entity) -> None:
        """Update an existing entity."""
        extra = {
            "operation": "update_entity",
            "entity_id": entity.id,
            "app_id": entity.app_id,
            "patient_id": entity.patient_id
        }
        
        logger.debug("Updating entity in Firestore", extra=extra)
        
        entities_ref = self._get_entities_collection_ref(entity.app_id, entity.patient_id)
        doc_ref = entities_ref.document(entity.id)
        
        entity_data = entity.to_dict()
        await doc_ref.set(entity_data)  # Use set to completely replace the document
        
        logger.debug(f"Successfully updated entity: {entity.id}", extra=extra)
    
    async def delete_entity(self, app_id: str, subject_id: str, entity_id: str) -> None:
        """Delete an entity by ID."""
        extra = {
            "operation": "delete_entity",
            "app_id": app_id,
            "subject_id": subject_id,
            "entity_id": entity_id
        }
        
        logger.debug("Deleting entity from Firestore", extra=extra)
        
        entities_ref = self._get_entities_collection_ref(app_id, subject_id)
        doc_ref = entities_ref.document(entity_id)
        
        await doc_ref.delete()
        
        logger.debug(f"Successfully deleted entity: {entity_id}", extra=extra)