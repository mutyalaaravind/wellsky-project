from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from fastapi import UploadFile

from model_aggregates.documents import DocumentAggregate


class DocumentRepositoryPort(ABC):
    """Port for document repository operations"""

    @abstractmethod
    async def save(self, document: DocumentAggregate) -> None:
        """Save a document to the repository"""
        pass

    @abstractmethod
    async def get_by_id(self, app_id: str, subject_id: str, document_id: str) -> Optional[DocumentAggregate]:
        """Get a document by its ID"""
        pass

    @abstractmethod
    async def get_by_subject(
        self, 
        app_id: str, 
        subject_id: str, 
        include_deleted: bool = False
    ) -> List[DocumentAggregate]:
        """Get all documents for a subject"""
        pass

    @abstractmethod
    async def delete_by_id(self, app_id: str, subject_id: str, document_id: str) -> bool:
        """Hard delete a document from the repository"""
        pass

    @abstractmethod
    async def find_by_document_id(self, document_id: str) -> Optional[DocumentAggregate]:
        """Find a document by its ID across all app_ids and subject_ids"""
        pass


class FileStoragePort(ABC):
    """Port for file storage operations (GCS)"""

    @abstractmethod
    async def upload_file(
        self,
        bucket_name: str,
        object_path: str,
        file: UploadFile,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to cloud storage
        Returns: GCS URI (gs://bucket/path)
        """
        pass

    @abstractmethod
    async def download_file(self, bucket_name: str, object_path: str) -> bytes:
        """Download a file from cloud storage"""
        pass

    @abstractmethod
    async def delete_file(self, bucket_name: str, object_path: str) -> bool:
        """Delete a file from cloud storage"""
        pass

    @abstractmethod
    async def get_file_metadata(self, bucket_name: str, object_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from cloud storage"""
        pass

    @abstractmethod
    async def get_signed_url(
        self, 
        bucket_name: str, 
        object_path: str, 
        expiration_minutes: int = 60
    ) -> str:
        """Generate a signed URL for temporary access to a file"""
        pass