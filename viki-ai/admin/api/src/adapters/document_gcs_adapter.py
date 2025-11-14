from typing import Dict, Optional, Any
from fastapi import UploadFile

try:
    from viki_shared.adapters.gcs_adapter import GCSAdapter
except ImportError:
    # Fallback if shared library is not available
    from .gcs_file_storage_adapter import GCSFileStorageAdapter as GCSAdapter

from infrastructure.document_ports import FileStoragePort


class DocumentGCSAdapter(FileStoragePort):
    """Document-specific GCS adapter using shared GCS functionality"""

    def __init__(self, gcs_adapter: GCSAdapter):
        self._gcs_adapter = gcs_adapter

    async def upload_file(
        self,
        bucket_name: str,
        object_path: str,
        file: UploadFile,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload a file to GCS with metadata"""
        return await self._gcs_adapter.upload_file(
            bucket_name=bucket_name,
            object_path=object_path,
            file=file,
            metadata=metadata
        )

    async def download_file(self, bucket_name: str, object_path: str) -> bytes:
        """Download a file from GCS"""
        return await self._gcs_adapter.download_file(bucket_name, object_path)

    async def delete_file(self, bucket_name: str, object_path: str) -> bool:
        """Delete a file from GCS"""
        return await self._gcs_adapter.delete_file(bucket_name, object_path)

    async def get_file_metadata(self, bucket_name: str, object_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from GCS"""
        return await self._gcs_adapter.get_file_metadata(bucket_name, object_path)

    async def get_signed_url(
        self, 
        bucket_name: str, 
        object_path: str, 
        expiration_minutes: int = 60
    ) -> str:
        """Generate a signed URL for temporary access to a file"""
        return await self._gcs_adapter.get_signed_url(
            bucket_name=bucket_name,
            object_path=object_path,
            expiration_minutes=expiration_minutes,
            method="GET"
        )