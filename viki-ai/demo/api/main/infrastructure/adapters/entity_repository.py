from typing import List, Dict, Any
from google.cloud.firestore import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone

from main.infrastructure.ports import IEntityRepositoryPort


class EntityRepository(IEntityRepositoryPort):
    def __init__(self, db_name: str):
        self.client = AsyncClient(database=db_name)

    async def save_entities(self, entity_id: str, entities_data: List[Dict[str, Any]]):
        """
        Save multiple entities to Firestore collection demo_entity_{entity_id} using batch transaction
        
        :param entity_id: The entity ID to use for the collection name
        :param entities_data: List of entity data dictionaries to save
        :return: List of document IDs of the saved entities
        """
        if not entities_data:
            return []
        
        # Create collection reference using entity_id
        collection_name = f"demo_entity_{entity_id}"
        collection_ref = self.client.collection(collection_name)
        
        # Use batch transaction for atomic writes
        batch = self.client.batch()
        doc_ids = []
        
        current_time = datetime.now(timezone.utc)
        
        for entity_data in entities_data:
            # Generate a unique document ID
            doc_id = uuid4().hex
            doc_ids.append(doc_id)
            
            # Add metadata to the entity data
            entity_with_metadata = {
                **entity_data,
                "id": doc_id,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            # Add to batch
            doc_ref = collection_ref.document(doc_id)
            batch.set(doc_ref, entity_with_metadata)
        
        # Commit the batch
        await batch.commit()
        
        return doc_ids
