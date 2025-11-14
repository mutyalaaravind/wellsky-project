import os
from typing import Optional, Dict, Any, List, Union
from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io

from settings import GCP_PROJECT_ID, GCS_BUCKET_NAME, USE_JSON_SAFE_LOADS
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from util.json_utils import safe_loads, JsonUtil

LOGGER = getLogger(__name__)

STORAGE_SINGLETON_ENABLE = False

class StorageAdapter:
    """Adapter for interacting with Google Cloud Storage to manage documents."""
    
    def __init__(self, project_id: Optional[str] = None, bucket_name: Optional[str] = None):
        """
        Initialize the Storage adapter.
        
        Args:
            project_id: Google Cloud project ID. If None, uses settings value.
            bucket_name: GCS bucket name. If None, uses settings value.
        """
        self.project_id = project_id or GCP_PROJECT_ID
        self.bucket_name = bucket_name or GCS_BUCKET_NAME
        
        # Initialize GCS client
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _run_in_executor(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool executor."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    async def save_document(self, 
                          document_path: str, 
                          content: Union[str, bytes], 
                          content_type: Optional[str] = None,
                          metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Save a document to Google Cloud Storage.
        
        Args:
            document_path: The path/key for the document in the bucket
            content: The document content (string or bytes)
            content_type: MIME type of the content (e.g., 'text/plain', 'application/json')
            metadata: Optional metadata dictionary to attach to the document
            
        Returns:
            The GCS URI of the saved document (gs://bucket/path)
            
        Raises:
            Exception: If there's an error saving the document
        """
        try:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name,
                "content_type": content_type,
                "metadata": metadata
            }
            
            LOGGER.debug(f"Saving document to GCS: {document_path}", extra=extra)
            
            def _upload():
                blob = self.bucket.blob(document_path)
                
                # Set metadata if provided
                if metadata:
                    blob.metadata = metadata
                
                # Upload content
                if isinstance(content, str):
                    blob.upload_from_string(content, content_type=content_type)
                else:
                    blob.upload_from_string(content, content_type=content_type)
                
                return blob.name
            
            blob_name = await self._run_in_executor(_upload)
            gcs_uri = f"gs://{self.bucket_name}/{blob_name}"
            
            LOGGER.info(f"Successfully saved document to GCS: {gcs_uri}", extra=extra)
            return gcs_uri
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error saving document to GCS: {document_path}", extra=extra)
            raise Exception(f"Error saving document '{document_path}' to GCS: {str(e)}")
    
    async def save_document_from_file(self, 
                                    document_path: str, 
                                    file_path: str,
                                    content_type: Optional[str] = None,
                                    metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Save a document to Google Cloud Storage from a local file.
        
        Args:
            document_path: The path/key for the document in the bucket
            file_path: Local file path to upload
            content_type: MIME type of the content
            metadata: Optional metadata dictionary to attach to the document
            
        Returns:
            The GCS URI of the saved document (gs://bucket/path)
            
        Raises:
            Exception: If there's an error saving the document
        """
        try:
            extra = {
                "document_path": document_path,
                "file_path": file_path,
                "bucket_name": self.bucket_name,
                "content_type": content_type,
                "metadata": metadata
            }
            
            LOGGER.debug(f"Saving file to GCS: {file_path} -> {document_path}", extra=extra)
            
            def _upload():
                blob = self.bucket.blob(document_path)
                
                # Set metadata if provided
                if metadata:
                    blob.metadata = metadata
                
                # Upload from file
                blob.upload_from_filename(file_path, content_type=content_type)
                return blob.name
            
            blob_name = await self._run_in_executor(_upload)
            gcs_uri = f"gs://{self.bucket_name}/{blob_name}"
            
            LOGGER.info(f"Successfully saved file to GCS: {gcs_uri}", extra=extra)
            return gcs_uri
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error saving file to GCS: {file_path} -> {document_path}", extra=extra)
            raise Exception(f"Error saving file '{file_path}' to GCS path '{document_path}': {str(e)}")
    
    async def retrieve_document(self, document_path: str) -> Optional[bytes]:
        """
        Retrieve a document from Google Cloud Storage.
        
        Args:
            document_path: The path/key of the document in the bucket
            
        Returns:
            Document content as bytes, or None if not found
            
        Raises:
            Exception: If there's an error retrieving the document
        """
        try:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name
            }
            
            LOGGER.debug(f"Retrieving document from GCS: {document_path}", extra=extra)
            
            def _download():
                try:
                    blob = self.bucket.blob(document_path)
                    if not blob.exists():
                        return None
                    return blob.download_as_bytes()
                except NotFound:
                    return None
            
            content = await self._run_in_executor(_download)
            
            if content is not None:
                LOGGER.debug(f"Successfully retrieved document from GCS: {document_path}", extra=extra)
            else:
                LOGGER.debug(f"Document not found in GCS: {document_path}", extra=extra)
            
            return content
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error retrieving document from GCS: {document_path}", extra=extra)
            raise Exception(f"Error retrieving document '{document_path}' from GCS: {str(e)}")
    
    async def retrieve_document_as_string(self, document_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Retrieve a document from Google Cloud Storage as a string.
        
        Args:
            document_path: The path/key of the document in the bucket
            encoding: Text encoding to use (default: utf-8)
            
        Returns:
            Document content as string, or None if not found
            
        Raises:
            Exception: If there's an error retrieving the document
        """
        content = await self.retrieve_document(document_path)
        if content is None:
            return None
        
        try:
            return content.decode(encoding)
        except UnicodeDecodeError as e:
            raise Exception(f"Error decoding document '{document_path}' with encoding '{encoding}': {str(e)}")
    
    async def retrieve_json_document(self, document_path: str, encoding: str = 'utf-8') -> Optional[Dict[str, Any]]:
        """
        Retrieve a JSON document from Google Cloud Storage as a dictionary.
        
        Args:
            document_path: The path/key of the JSON document in the bucket
            encoding: Text encoding to use (default: utf-8)
            
        Returns:
            Document content as dictionary, or None if not found
            
        Raises:
            Exception: If there's an error retrieving or parsing the JSON document
        """
        try:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name,
                "encoding": encoding
            }
            
            LOGGER.debug(f"Retrieving JSON document from GCS: {document_path}", extra=extra)
            
            # Get the document content as string
            content_str = await self.retrieve_document_as_string(document_path, encoding)
            if content_str is None:
                return None
            
            # Parse JSON using the project's JSON utilities
            if USE_JSON_SAFE_LOADS:
                json_data = safe_loads(content_str)
            else:
                json_data = JsonUtil.loads(content_str)
            
            LOGGER.debug(f"Successfully retrieved and parsed JSON document from GCS: {document_path}", extra=extra)
            return json_data
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error retrieving JSON document from GCS: {document_path}", extra=extra)
            raise Exception(f"Error retrieving JSON document '{document_path}' from GCS: {str(e)}")
    
    async def retrieve_document_to_file(self, document_path: str, local_file_path: str) -> bool:
        """
        Retrieve a document from Google Cloud Storage and save to a local file.
        
        Args:
            document_path: The path/key of the document in the bucket
            local_file_path: Local file path to save the document
            
        Returns:
            True if document was retrieved and saved, False if not found
            
        Raises:
            Exception: If there's an error retrieving the document
        """
        try:
            extra = {
                "document_path": document_path,
                "local_file_path": local_file_path,
                "bucket_name": self.bucket_name
            }
            
            LOGGER.debug(f"Retrieving document from GCS to file: {document_path} -> {local_file_path}", extra=extra)
            
            def _download():
                try:
                    blob = self.bucket.blob(document_path)
                    if not blob.exists():
                        return False
                    blob.download_to_filename(local_file_path)
                    return True
                except NotFound:
                    return False
            
            success = await self._run_in_executor(_download)
            
            if success:
                LOGGER.info(f"Successfully retrieved document from GCS to file: {document_path} -> {local_file_path}", extra=extra)
            else:
                LOGGER.debug(f"Document not found in GCS: {document_path}", extra=extra)
            
            return success
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error retrieving document from GCS to file: {document_path} -> {local_file_path}", extra=extra)
            raise Exception(f"Error retrieving document '{document_path}' from GCS to file '{local_file_path}': {str(e)}")
    
    async def delete_document(self, document_path: str) -> bool:
        """
        Delete a document from Google Cloud Storage.
        
        Args:
            document_path: The path/key of the document in the bucket
            
        Returns:
            True if document was deleted, False if not found
            
        Raises:
            Exception: If there's an error deleting the document
        """
        try:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name
            }
            
            LOGGER.debug(f"Deleting document from GCS: {document_path}", extra=extra)
            
            def _delete():
                try:
                    blob = self.bucket.blob(document_path)
                    if not blob.exists():
                        return False
                    blob.delete()
                    return True
                except NotFound:
                    return False
            
            success = await self._run_in_executor(_delete)
            
            if success:
                LOGGER.info(f"Successfully deleted document from GCS: {document_path}", extra=extra)
            else:
                LOGGER.debug(f"Document not found in GCS for deletion: {document_path}", extra=extra)
            
            return success
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error deleting document from GCS: {document_path}", extra=extra)
            raise Exception(f"Error deleting document '{document_path}' from GCS: {str(e)}")
    
    async def document_exists(self, document_path: str) -> bool:
        """
        Check if a document exists in Google Cloud Storage.
        
        Args:
            document_path: The path/key of the document in the bucket
            
        Returns:
            True if document exists, False otherwise
            
        Raises:
            Exception: If there's an error checking document existence
        """
        try:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name
            }
            
            LOGGER.debug(f"Checking if document exists in GCS: {document_path}", extra=extra)
            
            def _exists():
                blob = self.bucket.blob(document_path)
                return blob.exists()
            
            exists = await self._run_in_executor(_exists)
            
            LOGGER.debug(f"Document exists in GCS: {document_path} = {exists}", extra=extra)
            return exists
            
        except Exception as e:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name,
                "error": exceptionToMap(e)
            }
            LOGGER.error(f"Error checking if document exists in GCS: {document_path}", extra=extra)
            raise Exception(f"Error checking if document '{document_path}' exists in GCS: {str(e)}")
    
    async def list_documents(self, prefix: Optional[str] = None, delimiter: Optional[str] = None) -> List[str]:
        """
        List documents in the Google Cloud Storage bucket.
        
        Args:
            prefix: Optional prefix to filter documents
            delimiter: Optional delimiter for hierarchical listing
            
        Returns:
            List of document paths
            
        Raises:
            Exception: If there's an error listing documents
        """
        try:
            extra = {
                "bucket_name": self.bucket_name,
                "prefix": prefix,
                "delimiter": delimiter
            }
            
            LOGGER.debug(f"Listing documents in GCS bucket: {self.bucket_name}", extra=extra)
            
            def _list():
                blobs = self.client.list_blobs(self.bucket, prefix=prefix, delimiter=delimiter)
                return [blob.name for blob in blobs]
            
            document_paths = await self._run_in_executor(_list)
            
            LOGGER.debug(f"Found {len(document_paths)} documents in GCS bucket", extra=extra)
            return document_paths
            
        except Exception as e:
            extra = {
                "bucket_name": self.bucket_name,
                "prefix": prefix,
                "delimiter": delimiter,
                "error": exceptionToMap(e)
            }
            LOGGER.error(f"Error listing documents in GCS bucket: {self.bucket_name}", extra=extra)
            raise Exception(f"Error listing documents in GCS bucket '{self.bucket_name}': {str(e)}")
    
    async def get_document_metadata(self, document_path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a document in Google Cloud Storage.
        
        Args:
            document_path: The path/key of the document in the bucket
            
        Returns:
            Dictionary containing document metadata, or None if not found
            
        Raises:
            Exception: If there's an error retrieving metadata
        """
        try:
            extra = {
                "document_path": document_path,
                "bucket_name": self.bucket_name
            }
            
            LOGGER.debug(f"Getting metadata for document in GCS: {document_path}", extra=extra)
            
            def _get_metadata():
                try:
                    blob = self.bucket.blob(document_path)
                    if not blob.exists():
                        return None
                    
                    # Reload to get fresh metadata
                    blob.reload()
                    
                    return {
                        "name": blob.name,
                        "size": blob.size,
                        "content_type": blob.content_type,
                        "created": blob.time_created.isoformat() if blob.time_created else None,
                        "updated": blob.updated.isoformat() if blob.updated else None,
                        "etag": blob.etag,
                        "md5_hash": blob.md5_hash,
                        "crc32c": blob.crc32c,
                        "metadata": blob.metadata or {},
                        "generation": blob.generation,
                        "metageneration": blob.metageneration
                    }
                except NotFound:
                    return None
            
            metadata = await self._run_in_executor(_get_metadata)
            
            if metadata:
                LOGGER.debug(f"Successfully retrieved metadata for document: {document_path}", extra=extra)
            else:
                LOGGER.debug(f"Document not found for metadata retrieval: {document_path}", extra=extra)
            
            return metadata
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error getting metadata for document in GCS: {document_path}", extra=extra)
            raise Exception(f"Error getting metadata for document '{document_path}' in GCS: {str(e)}")


# Singleton instance for easy access
_storage_adapter: Optional[StorageAdapter] = None

def get_storage_adapter() -> StorageAdapter:
    """Get a singleton instance of the StorageAdapter."""
    if STORAGE_SINGLETON_ENABLE:
        global _storage_adapter
        if _storage_adapter is None:
            _storage_adapter = StorageAdapter()
        return _storage_adapter
    else:
        return StorageAdapter(
            project_id=GCP_PROJECT_ID,
            bucket_name=GCS_BUCKET_NAME
        )
