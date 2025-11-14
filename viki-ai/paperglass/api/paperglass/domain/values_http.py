from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, validator, AnyUrl, Field

class ExternalDocumentRepositoryType(str,Enum):
    API = "API"
    URI = "URI"

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class GenericExternalDocumentCreateEventRequestBase(BaseModel):
    appId: str
    tenantId: str
    patientId: str
    hostFileId: str
    fileName: str
    fileType: str
    fileLength: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    createdOn: str
    updatedOn: Optional[str] = None
    sha256: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    active: Optional[bool] = True
    repositoryType: ExternalDocumentRepositoryType = ExternalDocumentRepositoryType.API

    # def validate(self):
    #     pass

class GenericExternalDocumentRepositoryApi(BaseModel):
    method: HttpMethod
    url: AnyUrl
    headers: Optional[Dict[str, str]] = {}
    body: Optional[Dict[str, Any]] = None

class GenericExternalDocumentRepositoryUri(BaseModel):
    uri: str

    @validator("uri")
    def uri_must_be_gcs(cls, uri):
        if not uri.startswith("gs://"):
            raise ValueError("URI must be a valid GCS URI starting with gs://")
        return uri

class GenericExternalDocumentCreateEventRequestApi(GenericExternalDocumentCreateEventRequestBase):
    api: GenericExternalDocumentRepositoryApi

    @validator("api")
    def body_must_be_present_for_post_put(cls, api):
        if api.method in ["POST", "PUT"] and api.body is None:
            raise ValueError("Body is required for POST and PUT requests")
        return api

class GenericExternalDocumentCreateEventRequestUri(GenericExternalDocumentCreateEventRequestBase):
    uri: GenericExternalDocumentRepositoryUri


class EntitiesSearchRequest(BaseModel):
    """
    Request model for entity search endpoint.
    """
    appId: str
    tenantId: str
    patientId: str
    documentId: Optional[str] = None
    hostAttachmentId: Optional[str] = None


class Entity(BaseModel):
    """
    Represents an extracted entity from a document.
    """
    id: str
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    document_operation_instance_id: Optional[str] = Field(None, alias="run_id")
    entity_data: Dict[str, Any]
    schema_ref: str
    entity_type: str
    confidence_score: Optional[float] = None
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class EntitiesSearchResponse(BaseModel):
    """
    Response model for entity search endpoint.
    """
    appId: str
    tenantId: str
    patientId: str
    documentIds: list[str]
    entities: List[Entity]


class ExternalDocumentCreateResponse(BaseModel):
    """
    Response model for external document creation endpoint.
    """
    message: str
    status: str = "created"
    hostFileId: Optional[str] = None


class PipelineStatus(BaseModel):
    """
    Status information for a specific pipeline.
    """
    type: str
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    failed: int = 0
    details: Optional[str] = None


class DocumentStatus(BaseModel):
    """
    Overall document processing status.
    """
    status: str
    failed: int = 0
    pipelineStatuses: Optional[List[PipelineStatus]] = None
    # For v2 async status (DocumentProgressState)
    name: Optional[str] = None
    progress: Optional[float] = None
    children: Optional[List['DocumentStatus']] = None


class DocumentStatusResponseData(BaseModel):
    """
    Strongly typed status data for document status response.
    """
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    host_attachment_id: str
    status: DocumentStatus
    metadata: Optional[Dict[str, Any]] = None


# Update forward references for self-referencing models
DocumentStatus.update_forward_refs()
