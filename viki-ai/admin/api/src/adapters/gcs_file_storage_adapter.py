"""
Google Cloud Storage File Storage Adapter

This module implements the FileStoragePort interface using Google Cloud Storage.
It provides the infrastructure layer implementation for file storage operations.
"""

import asyncio
from typing import BinaryIO
from google.cloud import storage
from google.cloud.exceptions import NotFound
from viki_shared.utils.logger import getLogger

from contracts.file_storage_contracts import (
    FileStoragePort,
    StorageLocation,
    StorageMetadata,
    FileStorageError,
    FileNotFoundError,
    FileUploadError
)

logger = getLogger(__name__)


class GCSFileStorageAdapter:
    """
    Google Cloud Storage implementation of FileStoragePort.
    
    This adapter wraps the Google Cloud Storage client and provides
    async operations for file storage following the hexagonal architecture pattern.
    """

    def __init__(self, storage_client: storage.Client):
        """
        Initialize the GCS adapter.
        
        Args:
            storage_client: Google Cloud Storage client instance
        """
        self._client = storage_client
        logger.info("GCS File Storage Adapter initialized")

    async def upload_file(
        self,
        location: StorageLocation,
        content: BinaryIO,
        content_type: str
    ) -> StorageMetadata:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            location: The storage location (bucket + path)
            content: The file content as a binary stream
            content_type: MIME type of the file
            
        Returns:
            StorageMetadata: Metadata about the uploaded file
            
        Raises:
            FileUploadError: If upload fails
        """
        try:
            logger.info(f"Uploading file to GCS: bucket={location.bucket}, path={location.path}")
            
            # Run the synchronous GCS upload in a thread pool to make it async
            metadata = await asyncio.get_event_loop().run_in_executor(
                None,
                self._upload_file_sync,
                location,
                content,
                content_type
            )
            
            logger.info(f"Successfully uploaded file: {location.path} ({metadata.size_bytes} bytes)")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {location.path}", exc_info=True)
            raise FileUploadError(f"Failed to upload file: {str(e)}") from e

    def _upload_file_sync(
        self,
        location: StorageLocation,
        content: BinaryIO,
        content_type: str
    ) -> StorageMetadata:
        """
        Synchronous implementation of file upload.
        
        This method performs the actual GCS upload operation.
        """
        # Get the bucket
        bucket = self._client.bucket(location.bucket)
        
        # Create blob (file) in the bucket
        blob = bucket.blob(location.path)
        
        # Set content type
        blob.content_type = content_type
        
        # Upload the file content
        content.seek(0)  # Ensure we're at the beginning of the stream
        blob.upload_from_file(content, content_type=content_type)
        
        # Reload to get updated metadata
        blob.reload()
        
        # Return metadata
        return StorageMetadata(
            content_type=blob.content_type or content_type,
            size_bytes=blob.size or 0,
            etag=blob.etag or "",
            created_at=blob.time_created.isoformat() if blob.time_created else ""
        )

    async def file_exists(self, location: StorageLocation) -> bool:
        """
        Check if a file exists at the given location.
        
        Args:
            location: The storage location to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            logger.debug(f"Checking if file exists: bucket={location.bucket}, path={location.path}")
            
            exists = await asyncio.get_event_loop().run_in_executor(
                None,
                self._file_exists_sync,
                location
            )
            
            logger.debug(f"File exists check result: {location.path} = {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking file existence: {location.path}", exc_info=True)
            raise FileStorageError(f"Failed to check file existence: {str(e)}") from e

    def _file_exists_sync(self, location: StorageLocation) -> bool:
        """
        Synchronous implementation of file existence check.
        """
        try:
            bucket = self._client.bucket(location.bucket)
            blob = bucket.blob(location.path)
            return blob.exists()
        except Exception:
            return False

    async def get_file_metadata(self, location: StorageLocation) -> StorageMetadata:
        """
        Get metadata for a file without downloading its content.
        
        Args:
            location: The storage location
            
        Returns:
            StorageMetadata: Metadata about the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            FileStorageError: If operation fails
        """
        try:
            logger.debug(f"Getting file metadata: bucket={location.bucket}, path={location.path}")
            
            metadata = await asyncio.get_event_loop().run_in_executor(
                None,
                self._get_file_metadata_sync,
                location
            )
            
            logger.debug(f"Retrieved metadata for: {location.path}")
            return metadata
            
        except NotFound:
            logger.warning(f"File not found: {location.path}")
            raise FileNotFoundError(f"File not found: {location.path}")
        except Exception as e:
            logger.error(f"Failed to get file metadata: {location.path}", exc_info=True)
            raise FileStorageError(f"Failed to get file metadata: {str(e)}") from e

    def _get_file_metadata_sync(self, location: StorageLocation) -> StorageMetadata:
        """
        Synchronous implementation of file metadata retrieval.
        """
        bucket = self._client.bucket(location.bucket)
        blob = bucket.blob(location.path)
        
        # This will raise NotFound if the file doesn't exist
        blob.reload()
        
        return StorageMetadata(
            content_type=blob.content_type or "",
            size_bytes=blob.size or 0,
            etag=blob.etag or "",
            created_at=blob.time_created.isoformat() if blob.time_created else ""
        )