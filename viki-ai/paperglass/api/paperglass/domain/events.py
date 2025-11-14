from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from uuid import uuid1
from pydantic import BaseModel, Extra, Field

from .time import now_utc
from ..domain.values import (
    BlockAnnotation,
    Chunk,
    CustomAnnotation,
    EmbeddingStrategy,
    LineAnnotation,
    NamedEntity,
    OrchestrationPriority,
    ParagraphAnnotation,
    Section,
    TokenAnnotation,
)


# Sample events


class BaseEvent(BaseModel, frozen=True, extra=Extra.forbid):
    id: str = Field(default_factory=lambda: uuid1().hex)
    type: str
    created: datetime = Field(default_factory=now_utc)


class NoteCreated(BaseEvent):
    type: str = Field('note_created', const=True)
    note_id: str


class NoteUpdated(BaseEvent):
    type: str = Field('note_updated', const=True)
    note_id: str
    new_content: str


# Real events


class DocumentCreated(BaseEvent):
    type: str = Field('document_created', const=True)
    document_id: str
    storage_uri: str
    patient_id: str
    app_id:str
    tenant_id:str
    token:Optional[str] = None
    priority:Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT

class PageSplitCreated(BaseEvent):
    type: str = Field('page_split_created', const=True)
    document_id: str
    document_operation_instance_id: str
    document_operation_definition_id: str
    app_id:str
    tenant_id:str
    patient_id:str
    page_number: int
    storage_uri: str


class DocumentChunkAdded(BaseEvent):
    type: str = Field('document_chunk_added', const=True)
    document_id: str
    chunk: Chunk


class PageResultCreated(BaseEvent):
    type: str = Field('page_result_created', const=True)
    document_id: str
    # WARNING: Page numbers are 1-indexed!
    page_number: int
    page_result_type: str
    page_result_id: str


class PageResultCompleted(BaseEvent):
    type: str = Field('page_results_completed', const=True)
    document_id: str
    page_result_id: str
    page_result_type: str


class DocumentAnnotationsCompleted(BaseEvent):
    type: str = Field('document_annotations_completed', const=True)
    id: str
    document_id: str
    page_result_id: str


class CustomAnnotationsAdded(BaseEvent):
    type: str = Field('custom_annotations_added', const=True)
    document_id: str
    custom_annotations: List[CustomAnnotation]


class DocumentChunkStructuredDataAdded(BaseEvent):
    type: str = Field('document_chunk_structured_data_added', const=True)
    document_chunk_id: str
    document_id: str
    chunk_index: int
    content: str


class DocumentChunkSectionAdded(BaseEvent):
    type: str = Field('document_chunk_section_added', const=True)
    document_id: str
    document_chunk_id: str
    chunk_index: int
    section: Section


class PageLBILabelAdded(BaseEvent):
    type: str = Field('page_lbi_label_added', const=True)
    document_id: str
    chunk_index: int
    patient_id: str
    label: str
    content: str


class NamedEntityExtracted(BaseEvent):
    type: str = Field('named_entity_extracted', const=True)
    document_chunk_id: str
    named_entity_extracted: NamedEntity
    
class OnExternalFilesEvent(BaseEvent):
    type: str = Field('on_external_files_event', const=True)
    external_file_gcs_uri: str
    raw_event: Dict[str, str]
    app_id: str
    

class UploadAttachment(BaseEvent):
    type: str = Field('upload_attachment', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    file_name: str
    storage_uri: str
    source:Literal['host','app']
    token:str

class PageClassified(BaseEvent):
    type: str = Field('page_classified', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    document_operation_instance_id: str
    document_operation_definition_id: str
    page_id: str
    labels: List[Dict[str, str]]

    def add_label(self, label: Dict[str, str]):
        self.labels.append(label)
        return self

Event = Union[
    NoteCreated,
    NoteUpdated,
    DocumentCreated,
    UploadAttachment,
    PageSplitCreated,
    PageClassified,
    OnExternalFilesEvent
]
