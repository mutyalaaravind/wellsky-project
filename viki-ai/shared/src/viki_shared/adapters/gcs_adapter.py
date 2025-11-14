import io
import asyncio
from typing import Dict, Optional, Any, Union, List
from datetime import datetime, timedelta
from fastapi import UploadFile
from google.cloud import storage
from google.cloud.storage import Blob
import google.auth
from google.auth.transport import requests


class GCSAdapter:
    """Generic Google Cloud Storage adapter for file operations"""

    def __init__(self, storage_client: Optional[storage.Client] = None, cloud_provider: str = "google"):
        self._storage_client = storage_client or storage.Client()
        self.cloud_provider = cloud_provider

    async def upload_file(
        self,
        bucket_name: str,
        object_path: str,
        file: Union[UploadFile, bytes, str],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to GCS with metadata
        
        Args:
            bucket_name: GCS bucket name
            object_path: Path within the bucket
            file: File to upload (UploadFile, bytes, or string)
            content_type: MIME type of the file
            metadata: Custom metadata to attach to the file
            
        Returns:
            GCS URI (gs://bucket/path)
        """
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        
        # Set metadata on the blob
        if metadata:
            blob.metadata = metadata
        
        # Handle different file types
        if hasattr(file, 'read') and hasattr(file, 'content_type'):
            # This is likely an UploadFile or similar file-like object
            # Set content type from file if not provided
            if not content_type and hasattr(file, 'content_type') and file.content_type:
                content_type = file.content_type
            
            # Upload from file-like object
            file_content = await file.read()
            blob.upload_from_string(file_content, content_type=content_type)
        elif isinstance(file, bytes):
            # Upload from bytes
            blob.upload_from_string(file, content_type=content_type)
        elif isinstance(file, str):
            # Upload from string (text content)
            blob.upload_from_string(file, content_type=content_type or "text/plain")
        else:
            raise ValueError(f"Unsupported file type: {type(file)}")
        
        # Return GCS URI
        return f"gs://{bucket_name}/{object_path}"

    async def upload_from_file_path(
        self,
        bucket_name: str,
        object_path: str,
        local_file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file from local file system to GCS
        
        Args:
            bucket_name: GCS bucket name
            object_path: Path within the bucket
            local_file_path: Local file system path
            content_type: MIME type of the file
            metadata: Custom metadata to attach to the file
            
        Returns:
            GCS URI (gs://bucket/path)
        """
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        
        # Set metadata on the blob
        if metadata:
            blob.metadata = metadata
        
        # Set content type if provided
        if content_type:
            blob.content_type = content_type
        
        # Upload from file
        blob.upload_from_filename(local_file_path)
        
        # Return GCS URI
        return f"gs://{bucket_name}/{object_path}"

    async def download_file(self, bucket_name: str, object_path: str) -> bytes:
        """Download a file from GCS as bytes"""
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found: gs://{bucket_name}/{object_path}")
        
        return blob.download_as_bytes()

    async def download_to_file(self, bucket_name: str, object_path: str, local_file_path: str) -> bool:
        """Download a file from GCS to local file system"""
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found: gs://{bucket_name}/{object_path}")
        
        blob.download_to_filename(local_file_path)
        return True

    async def delete_file(self, bucket_name: str, object_path: str) -> bool:
        """Delete a file from GCS"""
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        
        if not blob.exists():
            return False
        
        blob.delete()
        return True

    async def file_exists(self, bucket_name: str, object_path: str) -> bool:
        """Check if a file exists in GCS"""
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        return blob.exists()

    async def get_file_metadata(self, bucket_name: str, object_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from GCS"""
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        
        if not blob.exists():
            return None
        
        # Reload to get the latest metadata
        blob.reload()
        
        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "created": blob.time_created,
            "updated": blob.updated,
            "metadata": blob.metadata or {},
            "etag": blob.etag,
            "md5_hash": blob.md5_hash,
            "bucket": blob.bucket.name,
            "generation": blob.generation,
        }

    def _generate_signed_url_sync(
        self,
        bucket_name: str,
        object_path: str,
        expiration_minutes: int,
        method: str
    ) -> str:
        """
        Synchronous helper to generate signed URL.

        This method handles both Cloud Run and local development credentials:
        - Cloud Run: Uses IAM signBlob API with service_account_email
        - Local: Uses v4 signing without service_account_email (compatible with impersonated credentials)
        """
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(object_path)

        # For GET requests, check if file exists
        if method.upper() == "GET" and not blob.exists():
            raise FileNotFoundError(f"File not found: gs://{bucket_name}/{object_path}")

        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)

        if self.cloud_provider == "google":
            # Cloud Run approach: Use IAM API with service_account_email
            # This works in Cloud Run without requiring a service account key file
            credentials, _ = google.auth.default()
            auth_request = requests.Request()
            credentials.refresh(auth_request)

            service_account_email = credentials.service_account_email
            return blob.generate_signed_url(
                expiration=expiration,
                service_account_email=service_account_email,
                access_token=credentials.token,
                method=method.upper()
            )
        else:
            # Local development: Use v4 signing without service_account_email
            # This works with impersonated credentials from gcloud auth application-default login
            return blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method=method.upper(),
            )

    async def get_signed_url(
        self,
        bucket_name: str,
        object_path: str,
        expiration_minutes: int = 60,
        method: str = "GET"
    ) -> str:
        """
        Generate a signed URL for temporary access to a file

        Args:
            bucket_name: GCS bucket name
            object_path: Path within the bucket
            expiration_minutes: URL expiration time in minutes
            method: HTTP method (GET, PUT, POST, DELETE)

        Returns:
            Signed URL

        Note:
            This method works correctly in Cloud Run by using the IAM signBlob API
            instead of requiring a private key. The credentials are refreshed and
            the service account email + access token are passed to generate_signed_url().
        """
        # Run the synchronous signing operation in a thread pool
        return await asyncio.get_event_loop().run_in_executor(
            None,
            self._generate_signed_url_sync,
            bucket_name,
            object_path,
            expiration_minutes,
            method
        )

    async def list_files(
        self, 
        bucket_name: str, 
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in a GCS bucket
        
        Args:
            bucket_name: GCS bucket name
            prefix: Filter results to objects beginning with this prefix
            delimiter: Used to group results by common prefixes
            max_results: Maximum number of results to return
            
        Returns:
            List of file metadata dictionaries
        """
        bucket = self._storage_client.bucket(bucket_name)
        
        blobs = bucket.list_blobs(
            prefix=prefix,
            delimiter=delimiter,
            max_results=max_results
        )
        
        files = []
        for blob in blobs:
            files.append({
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "metadata": blob.metadata or {},
                "etag": blob.etag,
                "md5_hash": blob.md5_hash,
            })
        
        return files

    def parse_gcs_uri(self, gcs_uri: str) -> tuple[str, str]:
        """
        Parse a GCS URI into bucket and object path
        
        Args:
            gcs_uri: GCS URI in format gs://bucket/path
            
        Returns:
            Tuple of (bucket_name, object_path)
        """
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI format: {gcs_uri}")
        
        parts = gcs_uri[5:].split("/", 1)  # Remove 'gs://' and split once
        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URI format: {gcs_uri}")
        
        return parts[0], parts[1]

    async def copy_file(
        self,
        source_bucket: str,
        source_path: str,
        dest_bucket: str,
        dest_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Copy a file from one GCS location to another
        
        Args:
            source_bucket: Source bucket name
            source_path: Source object path
            dest_bucket: Destination bucket name
            dest_path: Destination object path
            metadata: Optional metadata to set on the destination
            
        Returns:
            GCS URI of the destination file
        """
        source_bucket_obj = self._storage_client.bucket(source_bucket)
        source_blob = source_bucket_obj.blob(source_path)
        
        if not source_blob.exists():
            raise FileNotFoundError(f"Source file not found: gs://{source_bucket}/{source_path}")
        
        dest_bucket_obj = self._storage_client.bucket(dest_bucket)
        dest_blob = dest_bucket_obj.blob(dest_path)
        
        # Copy the blob
        dest_blob = source_bucket_obj.copy_blob(source_blob, dest_bucket_obj, dest_path)
        
        # Set metadata if provided
        if metadata:
            dest_blob.metadata = metadata
            dest_blob.patch()
        
        return f"gs://{dest_bucket}/{dest_path}"