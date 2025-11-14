from typing import List, Optional
from pydantic import BaseModel, Field

from model_aggregates.documents import DocumentAggregate


class DocumentResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[DocumentAggregate] = Field(None, description="Document data")


class DocumentListResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[DocumentAggregate] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")


class DocumentDeleteResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    deleted_id: str = Field(..., description="ID of the deleted document")


class DocumentUploadResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[DocumentAggregate] = Field(None, description="Uploaded document data")
    upload_url: Optional[str] = Field(None, description="GCS upload URL if applicable")