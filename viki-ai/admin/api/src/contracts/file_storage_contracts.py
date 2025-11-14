"""
File Storage Contracts

This module defines the contracts (interfaces) for file storage operations
following hexagonal architecture principles.
"""

from abc import ABC, abstractmethod
from typing import Protocol, BinaryIO
from dataclasses import dataclass


@dataclass(frozen=True)
class StorageLocation:
    """Represents a location in storage (bucket + path)."""
    bucket: str
    path: str


@dataclass(frozen=True)
class StorageMetadata:
    """Metadata about a stored file."""
    content_type: str
    size_bytes: int
    etag: str
    created_at: str


class FileStoragePort(Protocol):
    """
    Port interface for file storage operations.
    
    This interface defines the contract that any file storage implementation
    must follow, allowing for different storage backends (GCS, S3, etc.).
    """

    async def upload_file(
        self,
        location: StorageLocation,
        content: BinaryIO,
        content_type: str
    ) -> StorageMetadata:
        """
        Upload a file to storage.
        
        Args:
            location: The storage location (bucket + path)
            content: The file content as a binary stream
            content_type: MIME type of the file
            
        Returns:
            StorageMetadata: Metadata about the uploaded file
            
        Raises:
            FileStorageError: If upload fails
        """
        ...

    async def file_exists(self, location: StorageLocation) -> bool:
        """
        Check if a file exists at the given location.
        
        Args:
            location: The storage location to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        ...

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
        ...


class FileStorageError(Exception):
    """Base exception for file storage operations."""
    pass


class FileNotFoundError(FileStorageError):
    """Raised when a requested file is not found."""
    pass


class FileUploadError(FileStorageError):
    """Raised when file upload fails."""
    pass