import os
from typing import Optional, Dict, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from aiocache import cached, Cache, caches

from models.pipeline_config import PipelineConfig, validate_pipeline_config
from models.app_config import AppConfigCache
from settings import GCP_PROJECT_ID, GCP_FIRESTORE_DB, FIRESTORE_EMULATOR_HOST
from util.date_utils import now_utc
from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)

FIRESTORE_SINGLETON_ENABLE = False

class FirestoreAdapter:
    """Adapter for interacting with Firestore to retrieve pipeline configurations."""
    
    def __init__(self, project_id: Optional[str] = None, database: Optional[str] = None):
        """
        Initialize the Firestore adapter.
        
        Args:
            project_id: Google Cloud project ID. If None, uses settings value.
            database: Firestore database name. If None, uses settings value.
        """
        self.project_id = project_id or GCP_PROJECT_ID
        self.database = database or GCP_FIRESTORE_DB
        
        # Initialize Firestore client
        if FIRESTORE_EMULATOR_HOST:
            # When using emulator, use the emulator project ID and don't specify database
            emulator_project = "google-cloud-firestore-emulator"
            LOGGER.info(f"Using Firestore emulator at {FIRESTORE_EMULATOR_HOST} with project '{emulator_project}' and default database")
            self.client = firestore.Client(project=emulator_project)
        else:
            LOGGER.info(f"Using production Firestore with project '{self.project_id}' and database '{self.database}'")
            self.client = firestore.Client(project=self.project_id, database=self.database)
        
        self.collection_name = "entity_extraction_config"
        self.archive_collection_name = "entity_extraction_config_archive"
        self.app_config_collection_name = "entity_extraction_app_config"
    
    async def get_pipeline_config(self, config_id: str) -> Optional[PipelineConfig]:
        """
        Retrieve a pipeline configuration from Firestore by ID.
        
        Args:
            config_id: The unique ID of the pipeline configuration
            
        Returns:
            PipelineConfig object if found, None otherwise
            
        Raises:
            Exception: If there's an error retrieving or parsing the configuration
        """
        try:
            # Query for documents matching the ID
            collection_ref = self.client.collection(self.collection_name)
            
            # Create query with filter for id
            query = collection_ref.where(
                filter=FieldFilter("id", "==", config_id)
            )
            
            # Execute query
            docs = query.stream()
            
            # Get the first matching document
            for doc in docs:
                doc_data = doc.to_dict()
                if doc_data:
                    # Validate and return the pipeline configuration
                    return validate_pipeline_config(doc_data)
            
            # No matching document found
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving pipeline config for ID '{config_id}': {str(e)}")
    
    async def search_pipeline_config(self, scope: str, pipeline_key: str) -> Optional[PipelineConfig]:
        """
        Search for a pipeline configuration from Firestore by scope and key.
        
        Args:
            scope: The scope of the pipeline (e.g., 'default', 'medical', etc.)
            pipeline_key: The key identifier of the pipeline
            
        Returns:
            PipelineConfig object if found, None otherwise
            
        Raises:
            Exception: If there's an error retrieving or parsing the configuration
        """
        try:
            
            extra = {
                "scope": scope,
                "pipeline_key": pipeline_key
            }

            LOGGER.debug("Searching for pipeline config with scope '%s' and key '%s'", scope, pipeline_key, extra=extra)

            # Query for documents matching both scope and key
            collection_ref = self.client.collection(self.collection_name)
            
            # Create query with filters for scope and key
            query = collection_ref.where(
                filter=FieldFilter("scope", "==", scope)
            ).where(
                filter=FieldFilter("key", "==", pipeline_key)
            )
            
            # Execute query
            docs = query.stream()
            
            # Get the first matching document
            for doc in docs:
                doc_data = doc.to_dict()
                if doc_data:
                    # Validate and return the pipeline configuration
                    pipeline_config = validate_pipeline_config(doc_data)
                    LOGGER.debug(f"Found pipeline config: {pipeline_config}", extra=extra)
                    return pipeline_config
            
            # No matching document found
            return None
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error searching pipeline config for scope '{scope}' and key '{pipeline_key}': {str(e)}", extra=extra)
            raise Exception(f"Error searching pipeline config for scope '{scope}' and key '{pipeline_key}': {str(e)}")
    
    async def list_pipeline_configs(self, scope: Optional[str] = None) -> list[PipelineConfig]:
        """
        List all pipeline configurations, optionally filtered by scope.
        
        Args:
            scope: Optional scope filter
            
        Returns:
            List of PipelineConfig objects
            
        Raises:
            Exception: If there's an error retrieving configurations
        """
        try:
            collection_ref = self.client.collection(self.collection_name)
            
            if scope:
                query = collection_ref.where(filter=FieldFilter("scope", "==", scope))
                docs = query.stream()
            else:
                docs = collection_ref.stream()
            
            configs = []
            for doc in docs:
                doc_data = doc.to_dict()
                if doc_data:
                    try:
                        config = validate_pipeline_config(doc_data)
                        configs.append(config)
                    except Exception as e:
                        # Log the error but continue processing other documents
                        print(f"Warning: Failed to parse pipeline config from document {doc.id}: {str(e)}")
            
            return configs
            
        except Exception as e:
            raise Exception(f"Error listing pipeline configs for scope '{scope}': {str(e)}")
    
    async def list_active_pipeline_configs(self, labels: Optional[list[str]] = None, app_id: Optional[str] = None) -> list[PipelineConfig]:
        """
        List all active pipeline configurations in the system.
        
        Args:
            labels: Optional list of labels to filter by. Only configs containing ALL labels will be returned.
            app_id: Optional app_id to filter by.
        
        Returns:
            List of active PipelineConfig objects
            
        Raises:
            Exception: If there's an error retrieving configurations
        """
        try:
            collection_ref = self.client.collection(self.collection_name)
            
            # Start with active filter
            query = collection_ref.where(
                filter=FieldFilter("active", "in", [True, None])
            )
            
            # Add app_id filter if provided
            if app_id:
                query = query.where(filter=FieldFilter("app_id", "==", app_id))
            
            docs = query.stream()
            
            configs = []
            for doc in docs:
                doc_data = doc.to_dict()
                if doc_data:
                    try:
                        config = validate_pipeline_config(doc_data)
                        # Double-check that the config is active (in case active field is missing)
                        if getattr(config, 'active', True):
                            # Apply labels filter if provided
                            if labels:
                                config_labels = getattr(config, 'labels', []) or []
                                # Check if all required labels are present in config labels
                                if all(label in config_labels for label in labels):
                                    configs.append(config)
                            else:
                                configs.append(config)
                    except Exception as e:
                        # Log the error but continue processing other documents
                        print(f"Warning: Failed to parse pipeline config from document {doc.id}: {str(e)}")
            
            return configs
            
        except Exception as e:
            raise Exception(f"Error listing active pipeline configs: {str(e)}")
    
    async def save_pipeline_config(self, config: PipelineConfig, document_id: Optional[str] = None) -> str:
        """
        Save a pipeline configuration to Firestore.
        
        Args:
            config: The PipelineConfig object to save
            document_id: Optional document ID. If None, uses format "{id}-{version}".
            
        Returns:
            The document ID of the saved configuration
            
        Raises:
            Exception: If there's an error saving the configuration
        """
        # Use the standard document ID format if not provided
        if document_id is None:            
            document_id = f"{config.scope}.{config.key}-{config.version}"
            LOGGER.debug("No document ID provided, using default format based on config ID and version: %s", document_id)

        config.id = document_id  
        
        extra = {
            "config_key": config.key,
            "config_scope": config.scope,
            "config_id": config.id,
            "config_version": config.version,
            "document_id": document_id,
            "collection": self.collection_name
        }
        
        try:
            LOGGER.info(f"Attempting to save pipeline config '{config.key}' to Firestore with document ID '{document_id}'", extra=extra)
            
            collection_ref = self.client.collection(self.collection_name)
            
            # Convert config to dictionary
            config_dict = config.dict(exclude_none=True)
            
            # Use the specified document ID
            doc_ref = collection_ref.document(document_id)
            doc_ref.set(config_dict)
            
            # Verify the document was actually saved
            saved_doc = doc_ref.get()
            if not saved_doc.exists:
                raise Exception(f"Document {document_id} was not saved successfully")
            
            LOGGER.info(f"Successfully saved pipeline config with document ID: {document_id}", extra=extra)
            return document_id
                
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error saving pipeline config '{config.key}': {str(e)}", extra=extra)
            raise Exception(f"Error saving pipeline config '{config.key}': {str(e)}")
    
    async def archive_pipeline_config(self, config: PipelineConfig) -> str:
        """
        Archive a pipeline configuration to the archive collection.
        
        Args:
            config: The PipelineConfig object to archive
            
        Returns:
            The document ID of the archived configuration
            
        Raises:
            Exception: If there's an error archiving the configuration
        """
        extra = {
            "config_key": config.key,
            "config_scope": config.scope,
            "archive_collection": self.archive_collection_name,
            "client_database": getattr(self.client, '_database', 'unknown'),
            "client_project": getattr(self.client, 'project', 'unknown'),
            "emulator_host": FIRESTORE_EMULATOR_HOST
        }
        
        try:
            LOGGER.info(f"Starting archive process for pipeline config '{config.key}' to collection '{self.archive_collection_name}'", extra=extra)
            LOGGER.info(f"Client details - Project: {extra['client_project']}, Database: {extra['client_database']}, Emulator: {extra['emulator_host']}", extra=extra)
            
            archive_collection_ref = self.client.collection(self.archive_collection_name)
            LOGGER.debug(f"Created collection reference for '{self.archive_collection_name}'", extra=extra)
            
            # Convert config to dictionary and add archive metadata
            config_dict = config.dict(exclude_none=True)
            config_dict["archived_at"] = now_utc()
            config_dict["original_scope"] = config.scope
            config_dict["original_key"] = config.key
            
            LOGGER.debug(f"Prepared config dictionary with {len(config_dict)} fields", extra=extra)
            LOGGER.debug(f"Archive metadata: archived_at={config_dict['archived_at']}, original_scope={config_dict['original_scope']}, original_key={config_dict['original_key']}", extra=extra)
            
            # Save to archive collection with same document ID format as active collection
            archive_doc_id = config.id
            LOGGER.debug("Adding document to archive collection with ID: %s", archive_doc_id, extra=extra)
            
            doc_ref = archive_collection_ref.document(archive_doc_id)
            doc_ref.set(config_dict)
            
            LOGGER.info("Document added with ID: %s", archive_doc_id, extra=extra)
            
            # Verify the document was actually saved
            LOGGER.debug("Verifying document %s was saved...", archive_doc_id, extra=extra)
            saved_doc = doc_ref.get()
            if not saved_doc.exists:
                raise Exception(f"Archive document {archive_doc_id} was not saved successfully")
            
            saved_data = saved_doc.to_dict()
            LOGGER.info(f"Document verification successful. Saved document has {len(saved_data)} fields", extra=extra)
            
            extra["archive_document_id"] = archive_doc_id
            LOGGER.info(f"Successfully archived pipeline config with archive document ID: {archive_doc_id}", extra=extra)
            return archive_doc_id
                
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error archiving pipeline config '{config.key}': {str(e)}", extra=extra)
            raise Exception(f"Error archiving pipeline config '{config.key}': {str(e)}")

    async def mark_pipeline_config_inactive(self, config: PipelineConfig) -> bool:
        """
        Mark a pipeline configuration as inactive in Firestore.
        
        Args:
            config: The PipelineConfig object to mark as inactive
            
        Returns:
            True if the config was marked as inactive, False if not found
            
        Raises:
            Exception: If there's an error updating the configuration
        """
        extra = {
            "config_key": config.key,
            "config_scope": config.scope,
            "config_id": config.id,
            "config_version": config.version
        }
        
        try:
            LOGGER.info("Marking pipeline config '%s' (ID: %s) as inactive", config.key, config.id, extra=extra)
            
            collection_ref = self.client.collection(self.collection_name)
            
            # Query for documents matching the specific ID
            query = collection_ref.where(
                filter=FieldFilter("id", "==", config.id)
            )
            
            docs = query.stream()
            updated = False
            
            for doc in docs:
                # Update the document to mark it as inactive
                doc.reference.update({"active": False})
                updated = True
                LOGGER.debug("Marked document %s as inactive", doc.id, extra=extra)
            
            if updated:
                LOGGER.info("Successfully marked pipeline config '%s' (ID: %s) as inactive", config.key, config.id, extra=extra)
            else:
                LOGGER.warning("No documents found to mark as inactive for config '%s' (ID: %s)", config.key, config.id, extra=extra)
            
            return updated
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error("Error marking pipeline config '%s' (ID: %s) as inactive: %s", config.key, config.id, str(e), extra=extra)
            raise Exception(f"Error marking pipeline config '{config.key}' (ID: {config.id}) as inactive: {str(e)}")

    async def delete_pipeline_config(self, scope: str, pipeline_key: str) -> bool:
        """
        Delete a pipeline configuration from Firestore.
        
        Args:
            scope: The scope of the pipeline
            pipeline_key: The key identifier of the pipeline
            
        Returns:
            True if a document was deleted, False if no matching document was found
            
        Raises:
            Exception: If there's an error deleting the configuration
        """
        try:
            collection_ref = self.client.collection(self.collection_name)
            
            # Query for documents matching both scope and key
            query = collection_ref.where(
                filter=FieldFilter("scope", "==", scope)
            ).where(
                filter=FieldFilter("key", "==", pipeline_key)
            )
            
            docs = query.stream()
            deleted = False
            
            for doc in docs:
                doc.reference.delete()
                deleted = True
            
            return deleted
            
        except Exception as e:
            raise Exception(f"Error deleting pipeline config for scope '{scope}' and key '{pipeline_key}': {str(e)}")

    async def delete_inactive_pipeline_configs(self, scope: str, pipeline_key: str) -> int:
        """
        Delete all inactive versions of a pipeline configuration from Firestore.
        
        Args:
            scope: The scope of the pipeline
            pipeline_key: The key identifier of the pipeline
            
        Returns:
            Number of documents deleted
            
        Raises:
            Exception: If there's an error deleting the configurations
        """
        extra = {
            "scope": scope,
            "pipeline_key": pipeline_key
        }
        
        try:
            LOGGER.info(f"Deleting inactive pipeline configs for scope '{scope}' and key '{pipeline_key}'", extra=extra)
            
            collection_ref = self.client.collection(self.collection_name)
            
            # Query for documents matching scope, key, and inactive status
            query = collection_ref.where(
                filter=FieldFilter("scope", "==", scope)
            ).where(
                filter=FieldFilter("key", "==", pipeline_key)
            ).where(
                filter=FieldFilter("active", "==", False)
            )
            
            docs = query.stream()
            deleted_count = 0
            
            for doc in docs:
                doc_data = doc.to_dict()
                version = doc_data.get('version', 'unknown')
                doc.reference.delete()
                deleted_count += 1
                LOGGER.debug(f"Deleted inactive document {doc.id} (version: {version})", extra=extra)
            
            LOGGER.info(f"Successfully deleted {deleted_count} inactive pipeline configs", extra=extra)
            return deleted_count
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error deleting inactive pipeline configs: {str(e)}", extra=extra)
            raise Exception(f"Error deleting inactive pipeline configs for scope '{scope}' and key '{pipeline_key}': {str(e)}")

    # App Config Caching Methods
    
    async def get_app_config_cache(self, app_id: str) -> Optional[AppConfigCache]:
        """
        Retrieve cached app configuration from Firestore.
        
        Args:
            app_id: The application identifier
            
        Returns:
            AppConfigCache object if found and not expired, None otherwise
        """
        extra = {
            "app_id": app_id,
            "operation": "get_app_config_cache",
            "collection": self.app_config_collection_name
        }
        
        try:
            LOGGER.debug(f"Retrieving cached app config for app_id: {app_id}", extra=extra)
            
            collection_ref = self.client.collection(self.app_config_collection_name)
            doc_ref = collection_ref.document(app_id)
            
            doc = doc_ref.get()
            if not doc.exists:
                LOGGER.debug(f"No cached app config found for app_id: {app_id}", extra=extra)
                return None
            
            doc_data = doc.to_dict()
            if not doc_data:
                LOGGER.warning(f"Empty document for app_id: {app_id}", extra=extra)
                return None
            
            # Convert from Firestore format
            app_config = AppConfigCache.from_firestore_dict(doc_data)
            
            # Check if cache is expired
            if app_config.is_cache_expired():
                LOGGER.info(f"Cached app config for app_id {app_id} has expired, removing", extra=extra)
                # Remove expired cache entry
                await self.delete_app_config_cache(app_id)
                return None
            
            LOGGER.debug(f"Successfully retrieved valid cached app config for app_id: {app_id}", extra=extra)
            return app_config
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error retrieving cached app config for app_id {app_id}: {str(e)}", extra=extra)
            # Return None rather than raise - cache failures shouldn't break the system
            return None
    
    async def save_app_config_cache(self, app_config: AppConfigCache) -> bool:
        """
        Save app configuration to cache in Firestore.
        
        Args:
            app_config: The AppConfigCache object to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        extra = {
            "app_id": app_config.app_id,
            "operation": "save_app_config_cache",
            "collection": self.app_config_collection_name,
            "ttl_seconds": app_config.ttl_seconds
        }
        
        try:
            LOGGER.debug(f"Saving app config cache for app_id: {app_config.app_id}", extra=extra)
            
            collection_ref = self.client.collection(self.app_config_collection_name)
            doc_ref = collection_ref.document(app_config.app_id)
            
            # Update cache metadata
            app_config.cached_at = now_utc()
            app_config.updated_at = now_utc()
            
            # Convert to Firestore format
            config_dict = app_config.to_firestore_dict()
            
            # Save to Firestore
            doc_ref.set(config_dict)
            
            LOGGER.info(f"Successfully saved app config cache for app_id: {app_config.app_id}", extra=extra)
            return True
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error saving app config cache for app_id {app_config.app_id}: {str(e)}", extra=extra)
            return False
    
    async def delete_app_config_cache(self, app_id: str) -> bool:
        """
        Delete cached app configuration from Firestore.
        
        Args:
            app_id: The application identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        extra = {
            "app_id": app_id,
            "operation": "delete_app_config_cache",
            "collection": self.app_config_collection_name
        }
        
        try:
            LOGGER.debug(f"Deleting app config cache for app_id: {app_id}", extra=extra)
            
            collection_ref = self.client.collection(self.app_config_collection_name)
            doc_ref = collection_ref.document(app_id)
            
            doc_ref.delete()
            
            LOGGER.info(f"Successfully deleted app config cache for app_id: {app_id}", extra=extra)
            return True
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error deleting app config cache for app_id {app_id}: {str(e)}", extra=extra)
            return False
    
    async def update_app_config_cache(self, app_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields in cached app configuration.
        
        Args:
            app_id: The application identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        extra = {
            "app_id": app_id,
            "operation": "update_app_config_cache",
            "collection": self.app_config_collection_name,
            "update_fields": list(updates.keys())
        }
        
        try:
            LOGGER.debug(f"Updating app config cache for app_id: {app_id}", extra=extra)
            
            collection_ref = self.client.collection(self.app_config_collection_name)
            doc_ref = collection_ref.document(app_id)
            
            # Add updated timestamp
            updates["updated_at"] = now_utc().isoformat()
            
            doc_ref.update(updates)
            
            LOGGER.info(f"Successfully updated app config cache for app_id: {app_id}", extra=extra)
            return True
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error updating app config cache for app_id {app_id}: {str(e)}", extra=extra)
            return False


# Singleton instance for easy access
_firestore_adapter: Optional[FirestoreAdapter] = None

def get_firestore_adapter() -> FirestoreAdapter:
    """Get a singleton instance of the FirestoreAdapter."""
    if FIRESTORE_SINGLETON_ENABLE:
        global _firestore_adapter
        if _firestore_adapter is None:
            _firestore_adapter = FirestoreAdapter()
        return _firestore_adapter
    else:
        return FirestoreAdapter(
            project_id=GCP_PROJECT_ID,
            database=GCP_FIRESTORE_DB
        )


# Convenience functions
async def get_pipeline_config(config_id: str) -> Optional[PipelineConfig]:
    """Convenience function to get a pipeline configuration by ID."""
    adapter = get_firestore_adapter()
    return await adapter.get_pipeline_config(config_id)


@cached(ttl=60, cache=Cache.MEMORY)
async def search_pipeline_config(scope: str, pipeline_key: str) -> Optional[PipelineConfig]:
    """Convenience function to search for a pipeline configuration."""
    adapter = get_firestore_adapter()
    return await adapter.search_pipeline_config(scope, pipeline_key)


async def search_pipeline_config_no_cache(scope: str, pipeline_key: str) -> Optional[PipelineConfig]:
    """Convenience function to search for a pipeline configuration without caching."""
    adapter = get_firestore_adapter()
    return await adapter.search_pipeline_config(scope, pipeline_key)


async def invalidate_pipeline_config_cache(scope: str, pipeline_key: str) -> None:
    """Invalidate the cache for a specific pipeline configuration."""
    try:
        # Use aiocache's delete method to invalidate the specific cache entry
        # The cache key is generated by aiocache based on function name and parameters
        
        # Generate the cache key that aiocache would use for this function call
        # The format is typically: namespace:function_name:hash_of_args
        import hashlib
        import json
        
        # Create a consistent key based on function name and arguments
        args_str = json.dumps([scope, pipeline_key], sort_keys=True)
        args_hash = hashlib.md5(args_str.encode()).hexdigest()
        cache_key = f"adapters.firestore:search_pipeline_config:{args_hash}"
        
        # Get the default cache instance
        cache = caches.get("default") or Cache(Cache.MEMORY)
        await cache.delete(cache_key)
        LOGGER.info(f"Invalidated cache for pipeline config scope='{scope}', key='{pipeline_key}' with key: {cache_key}")
    except Exception as e:
        LOGGER.warning(f"Failed to invalidate cache for pipeline config scope='{scope}', key='{pipeline_key}': {str(e)}")
        # Fallback: try to clear the entire cache
        try:
            cache = caches.get("default") or Cache(Cache.MEMORY)
            await cache.clear()
            LOGGER.info("Cleared entire cache as fallback")
        except Exception as fallback_e:
            LOGGER.error(f"Failed to clear cache entirely: {str(fallback_e)}")


async def list_pipeline_configs(scope: Optional[str] = None) -> list[PipelineConfig]:
    """Convenience function to list pipeline configurations."""
    adapter = get_firestore_adapter()
    return await adapter.list_pipeline_configs(scope)


async def list_active_pipeline_configs(labels: Optional[list[str]] = None, app_id: Optional[str] = None) -> list[PipelineConfig]:
    """Convenience function to list all active pipeline configurations."""
    adapter = get_firestore_adapter()
    return await adapter.list_active_pipeline_configs(labels, app_id)


async def save_pipeline_config(config: PipelineConfig, document_id: Optional[str] = None) -> str:
    """Convenience function to save a pipeline configuration."""
    adapter = get_firestore_adapter()
    return await adapter.save_pipeline_config(config, document_id)


async def archive_pipeline_config(config: PipelineConfig) -> str:
    """Convenience function to archive a pipeline configuration."""
    adapter = get_firestore_adapter()
    return await adapter.archive_pipeline_config(config)


async def mark_pipeline_config_inactive(config: PipelineConfig) -> bool:
    """Convenience function to mark a pipeline configuration as inactive."""
    adapter = get_firestore_adapter()
    return await adapter.mark_pipeline_config_inactive(config)


async def delete_pipeline_config(scope: str, pipeline_key: str) -> bool:
    """Convenience function to delete a pipeline configuration."""
    adapter = get_firestore_adapter()
    return await adapter.delete_pipeline_config(scope, pipeline_key)


async def delete_inactive_pipeline_configs(scope: str, pipeline_key: str) -> int:
    """Convenience function to delete all inactive versions of a pipeline configuration."""
    adapter = get_firestore_adapter()
    return await adapter.delete_inactive_pipeline_configs(scope, pipeline_key)
