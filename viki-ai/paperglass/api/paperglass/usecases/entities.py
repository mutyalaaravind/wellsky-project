"""
Entity handling business logic for importing and persisting entities.
"""
import json
from typing import Dict, List, Union, Any
from collections import Counter
from log import getLogger

from ..infrastructure.ports import IUnitOfWorkManagerPort
from ..domain.model_entities import EntityAggregate
from ..domain.model_entity_toc import DocumentEntityTOC
from ..domain.utils.exception_utils import exceptionToMap

LOGGER = getLogger(__name__)


async def import_entities(entity_wrapper: Dict[str, Any], uow) -> Dict[str, Any]:
    """
    Import and persist entities from EntityWrapper to Firestore using UOW pattern.
    Also creates TOC entries for entity extraction counts.
    
    Args:
        entity_wrapper: Dictionary containing entities data
        uow: Unit of Work for database operations
        
    Returns:
        Dictionary with import results
    """
    extra = {}
    try:
        # Create EntityAggregate instances from the wrapper
        entity_aggregates = EntityAggregate.create_from_entity_wrapper(entity_wrapper)
        
        if not entity_aggregates:
            LOGGER.warning("No entities found in EntityWrapper")
            return {
                'success': True,
                'message': 'No entities to process',
                'processed_count': 0
            }
        
        # Extract metadata for TOC creation
        app_id = entity_wrapper.get('app_id')
        tenant_id = entity_wrapper.get('tenant_id')
        patient_id = entity_wrapper.get('patient_id')
        document_id = entity_wrapper.get('document_id')
        run_id = entity_wrapper.get('run_id')
        
        # Count entities by category/type and by page, and track schema URIs
        page_entity_counts = {}
        document_level_counts = Counter()
        schema_uri_map = {}  # Map entity_type to schema_uri
        
        for entity_aggregate in entity_aggregates:
            entity_type = entity_aggregate.entity_type
            page_number = entity_aggregate.page_number
            schema_ref = entity_aggregate.schema_ref
            
            # Track schema URI for this entity type
            if entity_type and schema_ref:
                schema_uri_map[entity_type] = schema_ref
            
            if page_number is not None:
                # Page-level count
                if page_number not in page_entity_counts:
                    page_entity_counts[page_number] = Counter()
                page_entity_counts[page_number][entity_type] += 1
            else:
                # Document-level count (fallback for entities without page info)
                document_level_counts[entity_type] += 1
        
        # Create TOC entry if we have the required metadata
        if all([app_id, tenant_id, patient_id, document_id, run_id]):
            if page_entity_counts:
                # Create page-level TOC entries
                # Convert Counter objects to regular dicts
                page_counts_dict = {
                    page_num: dict(counts) for page_num, counts in page_entity_counts.items()
                }
                toc_aggregate = DocumentEntityTOC.create_with_page_counts(
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    document_id=document_id,
                    run_id=run_id,
                    page_entity_counts=page_counts_dict,
                    schema_uri_map=schema_uri_map
                )
                uow.register_new(toc_aggregate)
                LOGGER.debug(f"Registered page-level TOC entry for document {document_id} with page counts: {page_counts_dict}")
            elif document_level_counts:
                # Fallback to document-level counts if no page info available
                toc_aggregate = DocumentEntityTOC.create(
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    document_id=document_id,
                    run_id=run_id,
                    entity_counts=dict(document_level_counts),
                    schema_uri_map=schema_uri_map
                )
                uow.register_new(toc_aggregate)
                LOGGER.debug(f"Registered document-level TOC entry for document {document_id} with counts: {dict(document_level_counts)}")
        
        # Persist entities using UOW
        for entity_aggregate in entity_aggregates:
            uow.register_new(entity_aggregate)
            LOGGER.debug(f"Registered entity {entity_aggregate.id} for persistence in collection {entity_aggregate.get_collection_name()}")
        
        processed_count = len(entity_aggregates)
        
        # Calculate total entity counts for logging and response
        total_entity_counts = Counter()
        for page_counts in page_entity_counts.values():
            total_entity_counts.update(page_counts)
        total_entity_counts.update(document_level_counts)
        
        LOGGER.info(f"Successfully processed {processed_count} entities with TOC counts: {dict(total_entity_counts)}")
        
        return {
            'success': True,
            'message': f'Successfully processed {processed_count} entities',
            'processed_count': processed_count,
            'entity_counts': dict(total_entity_counts)
        }
        
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        msg = f"Error importing entities: {str(e)}"
        LOGGER.error(msg, extra=extra)
        return {
            'success': False,
            'message': msg,
            'processed_count': 0
        }


async def search_entities(app_id: str, tenant_id: str, patient_id: str, document_id: str = None, host_attachment_id: str = None, query = None):
    """
    Search for entities in documents.
    
    Args:
        app_id: The application ID
        tenant_id: The tenant ID
        patient_id: The patient ID
        document_id: Optional document ID to search in
        host_attachment_id: Optional host attachment ID to search in
        query: Query port for database operations
        
    Returns:
        Dict containing:
        - documentIds: List of document IDs that were searched
        - entities: Dict mapping entity types to lists of entities
        
    Raises:
        ValueError: If neither document_id nor host_attachment_id is provided, or if document is not found
    """
    from ..domain.utils.exception_utils import exceptionToMap
    
    extra = {
        "app_id": app_id,
        "tenant_id": tenant_id,
        "patient_id": patient_id,
        "document_id": document_id,
        "host_attachment_id": host_attachment_id
    }
    
    try:
        # Determine which document(s) to search
        documents_to_search = []
        
        if document_id:
            # Search specific document by ID
            document = await query.get_document(document_id)
            if not document:
                raise ValueError(f"No document found for document_id: {document_id}")
            documents_to_search.append(document)
            
        elif host_attachment_id:
            # Search document by host attachment ID (source_id)
            document = await query.get_document_by_source_id(host_attachment_id, app_id=app_id, tenant_id=tenant_id, patient_id=patient_id)
            if not document:
                raise ValueError(f"No document found for host_attachment_id: {host_attachment_id}")
            documents_to_search.append(document)
            
        else:
            # If neither is provided, search all documents for the patient
            # This could be expensive, so we might want to limit this in the future
            all_docs = await query.list_documents(patient_id)  # Use list_documents instead
            # Limit to first 100 documents to avoid performance issues
            documents_to_search = all_docs[:100] if len(all_docs) > 100 else all_docs
        
        if not documents_to_search:
            raise ValueError("No documents found to search")
        
        # Extract document IDs
        document_ids = [doc["id"] if isinstance(doc, dict) else doc.id for doc in documents_to_search]
        
        # Initialize entities dictionary
        entities = {}
        
        # Find all entity types that were extracted from the document(s)
        entity_types = set()
        
        for doc in documents_to_search:
            doc_id = doc["id"] if isinstance(doc, dict) else doc.id
            
            try:
                # Get entity TOC for this document to find what entity types were extracted
                entity_toc_list = await query.get_document_entity_toc_by_document_id(doc_id)
                
                if entity_toc_list:
                    # Process each TOC entry (there might be multiple runs)
                    LOGGER.debug(f"Found {len(entity_toc_list)} entity TOC entries for document {doc_id}: {json.dumps(entity_toc_list, indent=2)}", extra=extra)
                    for toc_entry in entity_toc_list:
                        # Get entity counts from the TOC entry
                        entries = toc_entry.get('entries', {})

                        for entry in entries:
                            # Extract entity type from the entry
                            entity_type = entry.get('category')
                            if entity_type:
                                entity_types.add(entity_type)                                                
                else:
                    LOGGER.warning(f"No entity TOC found for document {doc_id}", extra=extra)

            except Exception as e:
                # Log the error but continue with other documents
                entity_extra = extra.copy()
                entity_extra.update({
                    "document_id": doc_id,
                    "error": exceptionToMap(e)
                })
                LOGGER.warning(f"Error retrieving entity TOC for document {doc_id}: {e}", extra=entity_extra)
        
        # Convert entity types set to list for consistent ordering
        entity_types_list = sorted(list(entity_types))
        
        # Initialize entities list to collect all entities
        entities = []
        
        # Retrieve actual entities for each discovered entity type
        for entity_type in entity_types_list:
            try:
                # Get entities for this type across all documents
                for doc in documents_to_search:
                    doc_id = doc["id"] if isinstance(doc, dict) else doc.id
                    
                    # Use the infrastructure method to get entities
                    doc_entities = await query.get_entities_by_document_and_entity_type(doc_id, entity_type)
                    
                    # Add the entities to our results
                    entities.extend(doc_entities)
                        
            except Exception as e:
                # Log error but continue with other entity types
                type_extra = extra.copy()
                type_extra.update({
                    "entity_type": entity_type,
                    "error": exceptionToMap(e)
                })
                LOGGER.warning(f"Error processing entity type {entity_type}: {e}", extra=type_extra)
        
        LOGGER.info(f"Successfully searched entities for {len(document_ids)} documents. Found entity types: {entity_types_list}. Retrieved {len(entities)} total entities.", extra=extra)
        
        return {
            "documentIds": document_ids,
            "entities": entities
        }
        
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error searching entities: {str(e)}", extra=extra)
        raise
