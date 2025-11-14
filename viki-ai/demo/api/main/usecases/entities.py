from typing import List, Dict, Any, Optional
from kink import inject

from main.infrastructure.ports import IEntityRepositoryPort


@inject
async def save_entities(
    entity_id: str,
    entities_data: List[Dict[str, Any]],
    app_id: str,
    tenant_id: str,
    patient_id: str,
    document_id: str,
    entity_schema_id: str,
    entity_repository: IEntityRepositoryPort,
    run_id: Optional[str] = None,
    source_id: Optional[str] = None
) -> List[str]:
    """
    Save multiple entities to Firestore using the entity repository

    :param entity_id: The entity ID to use for the collection name
    :param entities_data: List of entity data dictionaries to save
    :param app_id: Application ID to add to each entity
    :param tenant_id: Tenant ID to add to each entity
    :param patient_id: Patient ID to add to each entity
    :param document_id: Document ID to add to each entity
    :param entity_schema_id: Entity schema ID to add to each entity
    :param run_id: Run ID to add to each entity
    :param source_id: Source ID to add to each entity
    :param entity_repository: Injected entity repository
    :return: List of document IDs of the saved entities
    """
    # Extend each entity with the common fields from EntityRequest
    extended_entities = []
    for entity_data in entities_data:
        extended_entity = {
            **entity_data,
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "document_id": document_id,
            "entity_schema_id": entity_schema_id,
            "entity_id": entity_id
        }
        # Add run_id if provided
        if run_id is not None:
            extended_entity["run_id"] = run_id
        # Add source_id if provided
        if source_id is not None:
            extended_entity["source_id"] = source_id

        extended_entities.append(extended_entity)
    
    return await entity_repository.save_entities(entity_id, extended_entities)
