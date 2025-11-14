from copy import deepcopy
from datetime import datetime, timezone
from difflib import SequenceMatcher
from enum import Enum
import json
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid1, uuid4

from pydantic import BaseModel, Extra, Field

from paperglass.settings import USE_JSON_SAFE_LOADS
from paperglass.domain.time import now_utc
from paperglass.domain.utils.uuid_utils import get_uuid

from .events import (
    DocumentCreated,
    NoteCreated,
    NoteUpdated,
    PageClassified,
    PageSplitCreated,
    UploadAttachment,
)
from .values import (
    Annotation,
    AnnotationToken,
    ClinicalData,
    ConditionICD10Code,
    ConditionsEvidence,
    Configuration,
    DocumentOperationStatus,
    DocumentStatusType,
    DocumentOperationType,
    EmbeddingChunkingStartegy,
    EmbeddingStrategy,
    ExtractedClinicalDataReference,
    ExtractedMedicationReference,
    HostMedicationSyncStatus,
    ImportedMedication,
    MedicationChange,
    MedicationChangeSet,
    MedicationPageProfile,
    MedicationStatus,
    MedicationValue,
    ConditionValue,
    MedispanStatus,
    OCRType,
    OrchestrationPriority,
    Origin,
    Page as PageModel,
    PageOperationStatus,
    ReconcilledMedication,
    ResolvedReconcilledMedication,
    Result,
    UserEnteredMedication,
    Score,
    StepConfigPrompt,
)
from paperglass.domain.values_http import (
    GenericExternalDocumentRepositoryApi,
)
from paperglass.domain.util_json import safe_loads
from .string_utils import safe_str
from .time import now_utc

from logging import getLogger
from paperglass.log import CustomLogger
LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)

class AppAggregate(BaseModel, extra=Extra.forbid):
    id: str
    created_at: datetime = Field(default_factory=now_utc)
    modified_at: datetime = Field(default_factory=now_utc)
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    events: List = Field(default_factory=list)

    def toExtra(self):
        # Not returning data here as the context would be lost when converting to logging extra (what does "id" mean in the context of this logging statement?)        
        o = {}        
        return o

class Aggregate(AppAggregate, extra=Extra.forbid):
    app_id:str
    tenant_id:str
    patient_id:str
    execution_id: Optional[str] = None
    document_operation_instance_id: Optional[str] = None

    events: List = Field(default_factory=list)

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,            
            "document_operation_instance_id": self.document_operation_instance_id
        }
        supero.update(o)
        return supero

class Note(Aggregate):
    title: str
    content: str

    events: List[
        Union[
            NoteCreated,
            NoteUpdated,
        ]
    ] = Field(default_factory=list)

    @classmethod
    def create(cls, title: str, content: str) -> 'Note':
        id = uuid1().hex
        instance = cls(id=id, title=title, content=content)
        instance.events.append(NoteCreated(note_id=id))
        return instance

    def update_content(self, content: str) -> None:
        self.content = content
        self.events.append(NoteUpdated(note_id=self.id, new_content=content))

"""
App level configuration
"""
class AppConfig(AppAggregate):
    app_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: Configuration = Field(default_factory=Configuration)
    active: bool = True
    @classmethod
    def create(cls, app_id:str, config:Configuration, name: Optional[str] = None, description: Optional[str] = None) -> 'AppConfig':
        id = uuid1().hex
        return cls(id=id, config=config, app_id=app_id, name=name, description=description)

class AppTenantConfig(AppConfig):
    tenant_id: str

    @classmethod
    def create(cls, app_id: str, tenant_id: str, config: Configuration) -> 'AppTenantConfig':
        id = uuid1().hex
        return cls(id=id, app_id=app_id, tenant_id=tenant_id, config=config)
    
"""
Document operation: Holds pointer to active operation instance (active_document_operation_instance_id) so we can switch between multiple runs
"""
class DocumentOperation(Aggregate):
    document_id: str
    operation_type: str = DocumentOperationType.MEDICATION_EXTRACTION.value
    active_document_operation_definition_id: Optional[str] = None
    active_document_operation_instance_id: Optional[str] = None

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str,
               active_document_operation_definition_id: str,
               active_document_operation_instance_id: str,
               operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value) -> 'DocumentOperation':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,
                   operation_type=operation_type,
                   document_id=document_id,
                   active_document_operation_definition_id=active_document_operation_definition_id,
                   active_document_operation_instance_id=active_document_operation_instance_id)

    def update_active_document_operation_instance_id(self, active_document_operation_instance_id: str,active_document_operation_definition_id: str) -> None:
        self.active_document_operation_instance_id = active_document_operation_instance_id
        self.active_document_operation_definition_id = active_document_operation_definition_id
        self.modified_at = now_utc()
        
class DocumentOperationStatusSnapshot(BaseModel):
        operation_type: DocumentOperationType
        status:DocumentOperationStatus
        start_time: Optional[str]
        end_time: Optional[str]
        orchestration_engine_version: Optional[str]="v3"
        operation_instance_id: Optional[str]
        elapsed_time: Optional[float] = None
        pipelines: Optional[List[Dict[str, Any]]] = None

class Document(Aggregate):
    
    file_name: str
    storage_uri: Optional[str]
    page_count: int
    pages: List[PageModel]
    active: bool = True
    embedding_strategy: EmbeddingStrategy = EmbeddingStrategy.DOT_PRODUCT
    embedding_chunking_strategy: EmbeddingChunkingStartegy = EmbeddingChunkingStartegy.MARKDOWN_TEXT_SPLITTER
    token: Optional[str] = None
    source_id: Optional[str] = None
    source_storage_uri:Optional[str] = None
    source_api: Optional[GenericExternalDocumentRepositoryApi] = None
    source:Optional[Literal['host','app','api']] = 'app'
    source_sha256: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT
    operation_status: Optional[Dict[DocumentOperationType,DocumentOperationStatusSnapshot]] = Field(default_factory=dict)

    @classmethod
    def create(cls, app_id:str, tenant_id:str,patient_id: str, file_name: str, pages: List[PageModel], priority:OrchestrationPriority, metadata:dict[str, Any]={}, source_sha256: str=None) -> 'Document':
        id = uuid1().hex
        instance = cls(id=id, app_id=app_id, tenant_id=tenant_id, patient_id=patient_id,file_name=file_name, page_count=len(pages), pages=pages,priority=priority, metadata=metadata, source_sha256=source_sha256)
        return instance
    
    def update_operation_status(self,operation_status_snapshot:DocumentOperationStatusSnapshot):
        # if self.operation_status.get(operation_status_snapshot.operation_type):
        #     if self.operation_status[operation_status_snapshot.operation_type].start_time and  
        if not self.operation_status.get(operation_status_snapshot.operation_type):
            self.operation_status[operation_status_snapshot.operation_type] = operation_status_snapshot
        else:
            if self.operation_status[operation_status_snapshot.operation_type].operation_instance_id == operation_status_snapshot.operation_instance_id:
                if self.operation_status[operation_status_snapshot.operation_type].status != DocumentOperationStatus.FAILED:
                    # this ensures, if for a given run if any of the asycn process failed, it stays failed for the run_id/operation instance even if
                    # other process succeeded
                    self.operation_status[operation_status_snapshot.operation_type].status = operation_status_snapshot.status
            else:
                # new instance id, so update the status
                self.operation_status[operation_status_snapshot.operation_type].status = operation_status_snapshot.status
                self.operation_status[operation_status_snapshot.operation_type].operation_instance_id = operation_status_snapshot.operation_instance_id
            self.operation_status[operation_status_snapshot.operation_type].end_time = operation_status_snapshot.end_time
        

    def mark_uploaded(self, storage_uri: str) -> None:
        if self.storage_uri:
            raise ValueError('Document already uploaded')
        self.storage_uri = storage_uri
        self.events.append(DocumentCreated(document_id=self.id,
                                           storage_uri=storage_uri,
                                           patient_id=self.patient_id,
                                           app_id=self.app_id,
                                           tenant_id=self.tenant_id,token=self.token,
                                           priority=self.priority
                                           ))

    def add_page(self, page_number, storage_uri, document_operation_instance_id:str,document_operation_definition_id:str) -> None:
        for page in self.pages:
            if page.number == page_number:
                page.storage_uri = storage_uri
        # self.events.append(PageSplitCreated(app_id=self.app_id, tenant_id=self.tenant_id,patient_id=self.patient_id,
        #                                     document_id=self.id, page_number=page_number, storage_uri=storage_uri,
        #                                     document_operation_instance_id=document_operation_instance_id,
        #                                     document_operation_definition_id=document_operation_definition_id
        #                                     ))

    def update_embedding_strategy(
        self, embedding_strategy: EmbeddingStrategy, embedding_chunking_strategy: EmbeddingChunkingStartegy
    ) -> None:
        self.embedding_strategy = embedding_strategy
        self.embedding_chunking_strategy = embedding_chunking_strategy

    def clone(self):
        dolly = deepcopy(self)
        
        dolly.id = get_uuid()
        dolly.pages = []
        dolly.active = True
        dolly.operation_status = {}
        if not dolly.metadata:
            dolly.metadata = {}
        dolly.metadata["original_document_id"] = self.id

        self.events.append(DocumentCreated(document_id=dolly.id,
                                           storage_uri=dolly.storage_uri,
                                           patient_id=dolly.patient_id,
                                           app_id=dolly.app_id,
                                           tenant_id=dolly.tenant_id,token=dolly.token,
                                           priority=dolly.priority
                                           ))
        return dolly

    def delete(self):
        self.active = False


    @property
    def is_test(self):
        return self.metadata.get("is_test", False) if self.metadata else False

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "document_id": self.id,
            "file_name": self.file_name,
            "storage_uri": self.storage_uri,
            "page_count": self.page_count,
            "source": self.source,
            "source_storage_uri": self.source_storage_uri,
            "priority": self.priority,
            "metadata": self.metadata,
        }
        supero.update(o)
        return supero

class HostAttachmentAggregate(Aggregate):
    id: str
    source: Optional[Literal['host','app','api']] = 'host'
    storage_uri: Optional[str] = None
    api: Optional[GenericExternalDocumentRepositoryApi] = None
    file_name: str
    token: str
    raw_event: Optional[Dict[str, Any]] = None
    storage_metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def create(cls, 
               app_id:str,
               tenant_id:str,
               patient_id:str, 
               storage_uri: str, 
               file_name: str, 
               token: str, 
               raw_event:Dict[str,str]=None,
               storage_metadata:Dict[str,Any]=None
               ) -> 'HostAttachmentAggregate':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id, storage_uri=storage_uri, file_name=file_name, token=token, raw_event=raw_event, storage_metadata=storage_metadata)

    @classmethod
    def create_api(cls, 
               app_id:str,
               tenant_id:str,
               patient_id:str, 
               api: GenericExternalDocumentRepositoryApi, 
               file_name: str, 
               token: str, 
               raw_event:Dict[str,str]=None,
               storage_metadata:Dict[str,Any]=None
               ) -> 'HostAttachmentAggregate':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id, source="api", api=api, file_name=file_name, token=token, raw_event=raw_event, storage_metadata=storage_metadata)

    def upload(self):
        if self.storage_uri:
            self.events.append(UploadAttachment(app_id=self.app_id,tenant_id=self.tenant_id,patient_id=self.patient_id,
                                                storage_uri=self.storage_uri, file_name=self.file_name, source="host", token=self.token))

class DocumentStatus(Aggregate):
    document_id: str
    page_id: Optional[str] = None
    status: DocumentStatusType
    message: str
    source_event: Optional[str] = None

    @classmethod
    def create(cls, app_id:str, tenant_id:str,patient_id:str, document_id: str, status: DocumentStatusType, message: str) -> 'DocumentStatus':
        id = uuid1().hex
        return cls(id=id, app_id=app_id, tenant_id=tenant_id,patient_id=patient_id, document_id=document_id, status=status, message=message)

class CustomPromptResult(Aggregate):
    document_id: str
    page_number: int = -1 # -1 means it is applicable to all pages
    context: Dict[str, Union[str, Dict, List, int, float]]
    prompt_input: str
    prompt_output: str
    prompt_output_data: Optional[Dict] = None

    @classmethod
    def create(cls, app_id:str,tenant_id:str,
                patient_id:str,
                document_id: str,
                page_number: int,
                context: Dict[str, str],
                prompt_input: str,
                prompt_output: str,
                document_operation_instance_id:str,
                prompt_output_data: Optional[Dict] = None,
               ) -> 'CustomPromptResult':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,
                    patient_id=patient_id, document_id=document_id,
                    page_number=page_number,
                    context=context,
                    prompt_input=prompt_input,
                    prompt_output=prompt_output,
                    document_operation_instance_id=document_operation_instance_id,
                    prompt_output_data=prompt_output_data
                   )

class Page(Aggregate):
    number: int
    storage_uri: Optional[str]
    document_id: str
    ocr_storage_uris: Optional[Dict[OCRType,str]] = {}
    text: Optional[str] = None
    rotation: float = 0

    @classmethod
    def create(cls, app_id: str, tenant_id: str,patient_id:str, number: int, storage_uri:str, document_id:str) -> 'Page':
        id = uuid1().hex
        return cls(id=id, app_id=app_id, tenant_id=tenant_id,number=number, storage_uri=storage_uri, document_id=document_id, patient_id=patient_id)

    def add_ocr(self, ocr_type, storage_uri: str) -> None:
        self.ocr_storage_uris.update({ocr_type: storage_uri})

    def add_text(self, text: str) -> None:
        self.text = text

    @staticmethod
    def get_ocr_page_line_annotations(ocr_result, start_index=None, end_index=None)->List[Annotation]:
        text = ocr_result.get("text")
        page = ocr_result.get("page")
        blocks = page.get("lines", [])
        line_annotation = []
        for block in blocks:
            if not start_index and not end_index:
                line_annotation.extend(Page.get_annotations(block, text))
            else:
                line_annotation.extend(Page.get_annotations_filtered_by_start_and_end_index(block, text, start_index, end_index))
        return line_annotation

    @staticmethod
    def get_annotations(block, text):
        segments = block.get("layout").get("textAnchor").get("textSegments")
        annotations = []

        for segment in segments:
            if Page.is_valid_vertices(block.get("layout").get("boundingPoly").get("vertices")):
                try:
                    annotations.append(
                        Annotation(
                            text_segment=text[int(segment.get("startIndex", 0)) : int(segment.get("endIndex"))],
                            vertice1=block.get("layout").get("boundingPoly").get("vertices")[0],
                            vertice2=block.get("layout").get("boundingPoly").get("vertices")[1],
                            vertice3=block.get("layout").get("boundingPoly").get("vertices")[2],
                            vertice4=block.get("layout").get("boundingPoly").get("vertices")[3],
                            normalized_vertice1=block.get("layout").get("boundingPoly").get("normalizedVertices")[0],
                            normalized_vertice2=block.get("layout").get("boundingPoly").get("normalizedVertices")[1],
                            normalized_vertice3=block.get("layout").get("boundingPoly").get("normalizedVertices")[2],
                            normalized_vertice4=block.get("layout").get("boundingPoly").get("normalizedVertices")[3],
                            orientation=block.get("layout").get("orientation"),
                            detected_languages=block.get("detectedLanguages"),
                            confidence=block.get("layout").get("confidence"),
                        )
                    )
                except Exception as e:
                    LOGGER.error("Error while getting annotations :", e)
        return annotations

    @staticmethod
    def get_annotations_filtered_by_start_and_end_index(block, text , start_index, end_index):
        segments = block.get("layout").get("textAnchor").get("textSegments")
        annotatons = []

        for segment in segments:
            if int(segment.get("startIndex", 0)) >= int(start_index) and int(segment.get("endIndex")) <= int(end_index):
                annotatons.append(
                    Annotation(
                        text_segment=text[int(segment.get("startIndex", 0)) : int(segment.get("endIndex"))],
                        vertice1=block.get("layout").get("boundingPoly").get("vertices")[0],
                        vertice2=block.get("layout").get("boundingPoly").get("vertices")[1],
                        vertice3=block.get("layout").get("boundingPoly").get("vertices")[2],
                        vertice4=block.get("layout").get("boundingPoly").get("vertices")[3],
                        normalized_vertice1=block.get("layout").get("boundingPoly").get("normalizedVertices")[0],
                        normalized_vertice2=block.get("layout").get("boundingPoly").get("normalizedVertices")[1],
                        normalized_vertice3=block.get("layout").get("boundingPoly").get("normalizedVertices")[2],
                        normalized_vertice4=block.get("layout").get("boundingPoly").get("normalizedVertices")[3],
                        orientation=block.get("layout").get("orientation"),
                        detected_languages=block.get("detectedLanguages"),
                        confidence=block.get("layout").get("confidence"),
                    )
                )
        return annotatons

    """
    some odd docs have corrupt ocr extract where x or y value is missing
    """
    @staticmethod
    def is_valid_vertices(vertices):
        for vertice in vertices:
            if not 'x' in vertice or not 'y' in vertice:
                return False
        return True
            
class ClassifiedPage(Aggregate):
    document_id: str
    page_id: str
    page_text: str
    page_number: Optional[int] = -1
    labels: List[Dict[str, str]] = Field(default_factory=list)

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str, page_id: str, page_text: str, page_number: int) -> 'ClassifiedPage':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,
                   tenant_id=tenant_id,
                   patient_id=patient_id,
                   document_id=document_id,
                   page_id=page_id,
                   page_text=page_text,
                   page_number=page_number)

    def add_label(self, label: str, content: str, document_operation_instance_id: str, document_operation_definition_id) -> None:
        self.labels.append({label: content})
        # if not self.events:
        #     self.events.append(PageClassified(app_id=self.app_id, tenant_id=self.tenant_id,patient_id=self.patient_id,
        #                                     document_id=self.document_id,
        #                                     document_operation_instance_id=document_operation_instance_id,
        #                                     document_operation_definition_id=document_operation_definition_id,
        #                                     page_id=self.page_id, labels=self.labels))
        # else:
        #     events:PageClassified = [event for event in self.events if isinstance(event, PageClassified)]
        #     for event in events:
        #         event:PageClassified = event
        #         event.add_label({label: content})

class PageLabel(str, Enum):
        DEMOGRAPHICS = 'demographics'
        MEDICATIONS = 'medications'
        DIAGNOSES = 'diagnoses'
        PROCEDURES = 'procedures'
        SYMPTOMS = 'symptoms'
        MEDICAL_HISTORY = 'medical_history'
        FAMILY_HISTORY = 'family_history'
        ALLERGIES = 'allergies'
        VITALS = 'vitals'
        VISITS = 'visits'
        LAB_RESULTS = 'lab_results'
        RISK_FACTORS = 'risk_factors'
        FOLLOW_UP_PLANS = 'follow_up_plans'
        PATIENT_EDUCATION = 'patient_education'
        IMMUNIZATIONS = 'immunizations'
        CONDITIONS = "conditions"

class VectorIndex(BaseModel):
    id: str
    allow_list: List[str]
    data: str
    embedding_strategy: EmbeddingStrategy
    embedding_chunking_strategy: EmbeddingChunkingStartegy

class VectorSearchResult(BaseModel):
    id: str
    allow_list: List[str]
    distance: float

    @property
    def annotation_proxy(self):
        page_result_id = self.id.split('#!@$')[0]
        text = self.id.split('#!@$')[1]
        normalized_vertices = [
            {'x': x.split(",")[0], 'y': x.split(",")[1]} for x in self.id.split('#!@$')[2].split('-')
        ]
        return {
            "page_result_id": page_result_id,
            "text": text,
            "normalized_vertices": normalized_vertices,
            "distance": self.distance,
            "x": float(normalized_vertices[0]['x']),
            "y": float(normalized_vertices[0]['y']),
            "width": float(normalized_vertices[2]['x']) - float(normalized_vertices[0]['x']),
            "height": float(normalized_vertices[2]['y']) - float(normalized_vertices[0]['y']),
        }

# Document Operations related models
"""
"""
class DocumentOperationStrategy(BaseModel):
    id: str
    name: str
    document_workflow_id: str
    description: str

"""
"""
class DocumentOperationDefinition(AppAggregate):
    name: str
    operation_type: str #medical-extraction|medical-coding|medical-annotation
    operation_name: str
    description: str
    document_workflow_id: str #maps to application workflow
    step_config: Dict[str, Dict[str, str | Dict] | Any] = Field(default_factory=dict)
    disabled: bool = False

    @classmethod
    def create(cls,name: str, operation_type: str, operation_name: str,
               description: str, document_workflow_id: str,
               step_config:Dict[str, Dict[str, str]]) -> 'DocumentOperationDefinition':
        id = uuid1().hex
        return cls(id=id, name=name, operation_type=operation_type,
                   operation_name=operation_name, description=description,
                   document_workflow_id=document_workflow_id,step_config=step_config)

    def get_step_config(self, step_id:str) -> Dict[str, str | Dict] | Any:
        configdict = self.step_config.get(step_id) if self.step_config else None
        return StepConfigPrompt(**configdict) if configdict else None


"""
Document operation instance: Holds the current state of the operation
"""
class DocumentOperationInstance(Aggregate):
    document_id: str
    document_operation_definition_id: str
    start_date: str
    end_date: Optional[str]=None
    status: Optional[DocumentOperationStatus] = None
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str,
               document_operation_definition_id: str, start_date: str,
               end_date: str,
               status: DocumentOperationStatus,
               priority: OrchestrationPriority) -> 'DocumentOperationInstance':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,
                   document_id=document_id,
                   document_operation_definition_id=document_operation_definition_id,
                   start_date=start_date, end_date=end_date,
                   status=status,
                   priority=priority)

    def update_status(self, status: DocumentOperationStatus) -> None:
        self.status = status
        if status == DocumentOperationStatus.COMPLETED:
            self.end_date = now_utc()

class DocumentOperationInstanceLog(Aggregate):
    document_id: str
    document_operation_definition_id: str
    document_operation_instance_id: str
    step_id: str
    status: DocumentOperationStatus
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    elapsed_time: Optional[float] = None
    context: Optional[Dict[str, Union[str, Dict, List, int, float, None]]] = Field(default_factory=dict)
    page_number: Optional[int] = None    

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str, document_operation_instance_id: str, document_operation_definition_id:str,step_id: str, status: DocumentOperationStatus, start_datetime: datetime, context: Dict[str, Union[str, Dict, List, int, float]], page_number: int = -1) -> 'DocumentOperationInstanceLog':
        id = uuid1().hex
        end_datetime = None
        elapsed_time = None        
        if start_datetime:
            try:
                end_datetime = now_utc()
                elapsed_time = (end_datetime - start_datetime).total_seconds()
            except Exception as e:
                LOGGER.error("Error calculating elapsed time for step %s in document operation log (swallowed as this will only not set start/end/elapsed_time): %s", step_id, e)

        return cls(id=id, app_id=app_id,tenant_id=tenant_id,
                   patient_id=patient_id,
                   document_id=document_id,
                   document_operation_instance_id=document_operation_instance_id,
                   document_operation_definition_id=document_operation_definition_id,
                   step_id=step_id, status=status, 
                   start_datetime=start_datetime,
                   end_datetime=end_datetime,
                   elapsed_time=elapsed_time,
                   page_number=page_number,
                   context=context)

    def unique_identifier(self):
        return f"{self.document_id}-{self.document_operation_instance_id}-{self.step_id}-{str(self.page_number) if self.page_number else '-1'}"

#ToDo: separate domain
class UserEnteredMedicationAggregate(Aggregate):
    id: str
    patient_id: str
    medication: MedicationValue
    document_id: Optional[str]
    medication_status: MedicationStatus
    medication_profile_reconcilled_medication_id: Optional[str]
    change_sets: MedicationChangeSet | List[MedicationChangeSet] | None
    deleted:Optional[bool] = False
    extracted_medication_references: Optional[List[ExtractedMedicationReference]]

    @classmethod
    def create(cls, app_id:str,tenant_id:str,
               patient_id:str,
               medication:MedicationValue,
               medication_status:MedicationStatus,
               created_by:str, modified_by:str,
               document_id:str,
               medication_profile_reconcilled_medication_id:str=None,
               extracted_medication_references:List[ExtractedMedicationReference]=None
               ) -> 'UserEnteredMedication':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,
                    created_by=created_by, modified_by=modified_by,
                    medication=medication,
                    medication_status=medication_status,
                    medication_profile_reconcilled_medication_id=medication_profile_reconcilled_medication_id,
                    document_id=document_id,
                    extracted_medication_references=extracted_medication_references
                    )

    def update(self,old_values:'UserEnteredMedicationAggregate', new_values):
        allowed_fields = ['name', 'dosage', 'frequency', 'route', 'start_date', 'end_date','startDate', 'endDate']
        changes = []
        for field in allowed_fields:
            if field == "name" and new_values.get(field):
                    changes.append(MedicationChange(field=field, old_value=old_values.medication.name, new_value=new_values[field]))
            if field == "dosage" and new_values.get(field):
                changes.append(MedicationChange(field=field, old_value=self.medication.dosage, new_value=new_values[field]))
            if field == "route" and new_values.get(field):
                changes.append(MedicationChange(field=field, old_value=self.medication.route, new_value=new_values[field]))
            if field == "instructions" and new_values.get(field):
                changes.append(MedicationChange(field=field, old_value=self.medication.instructions, new_value=new_values[field]))
            if field == "frequency" and new_values.get(field):
                changes.append(MedicationChange(field=field, old_value=self.medication.frequency, new_value=new_values[field]))
            if (field == "start_date" or field == "startDate") and new_values.get(field):
                changes.append(MedicationChange(field="start_date", old_value=self.medication.start_date, new_value=new_values[field]))
            if (field == "end_date" or field == "endDate") and new_values.get(field):
                changes.append(MedicationChange(field="end_date", old_value=self.medication.start_date, new_value=new_values[field]))
            if (field == "discontinued_date" or field == "discontinuedDate") and new_values.get(field):
                changes.append(MedicationChange(field="end_date", old_value=self.medication.discontinued_date, new_value=new_values[field]))
        if changes:
            self.change_sets = self.change_sets or [] + [MedicationChangeSet(changes=changes)]

    def delete(self):
        self.deleted = True
        self.change_sets = self.change_sets or [] + [MedicationChangeSet(changes=[
            MedicationChange(field='deleted', old_value=False, new_value=True),
        ])]

    def un_delete(self):
        self.deleted = False
        self.change_sets = self.change_sets or [] + [MedicationChangeSet(changes=[
            MedicationChange(field='deleted', old_value=True, new_value=False),
        ])]

class ExtractedMedication(Aggregate):
    id: str
    document_id: str
    page_id: str
    route: Optional[str]
    reason: Optional[str]
    explaination: Optional[str]
    document_reference: str
    page_number: int
    active: bool = True
    change_sets: List[MedicationChangeSet] = Field(default_factory=list)
    deleted: bool = False
    medication: MedicationValue
    medispan_medication: Optional[MedicationValue] = None
    medispan_status: MedispanStatus = MedispanStatus.NONE
    medispan_id: Optional[str] = None
    score: Optional[float] = None

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str,
                page_id: str,
                document_reference:str, page_number:int,
                extracted_medication_value:MedicationValue,
                medispan_medication:MedicationValue,
                medispan_status:MedispanStatus,
                medispan_id:str,
                score: float = None,
                reason:str=None,explaination:str=None,active=True) -> 'ExtractedMedication':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id,
                    page_id=page_id,
                    medication=extracted_medication_value,
                    document_reference=document_reference,
                    page_number=page_number,reason=reason,explaination=explaination,
                    active=active,
                    medispan_medication=medispan_medication,
                    medispan_status=medispan_status,
                    medispan_id=medispan_id,
                    score=score)

    @property
    def resolved_medication(self) -> MedicationValue:
        return MedicationValue(name=self.medispan_medication.name if self.medispan_medication else self.medication.name,
                                dosage=self.medispan_medication.dosage if self.medispan_medication and self.medispan_medication.dosage  else self.medication.dosage,
                                route=self.medispan_medication.route if self.medispan_medication else self.medication.route,
                                frequency =self.medication.frequency,
                                instructions=self.medication.instructions,
                                form=self.medispan_medication.form if self.medispan_medication else self.medication.form,
                                start_date=self.medication.start_date,
                                end_date=self.medication.end_date,
                                discontinued_date=self.medication.discontinued_date,
                                strength = self.medispan_medication.strength if self.medispan_medication else self.medication.strength,
                                medispan_id=self.medispan_id,
                            )

    def set_dosage(self, dosage: str) -> None:
        self.medication.dosage = dosage

    def set_instructions(self, instructions: str) -> None:
        self.medication.instructions = instructions

    def set_medispan_medication(self, medispan_medication: MedicationValue) -> None:
        self.medispan_medication = medispan_medication
        if medispan_medication:
            self.set_medispan_id(medispan_medication.medispan_id)
        else:
            self.set_medispan_id(None)

    def set_medispan_status(self, medispan_status: MedispanStatus) -> None:
        self.medispan_status = medispan_status

    def set_medispan_id(self, medispan_id: str) -> None:
        self.medispan_id = medispan_id

class ExtractedConditions(Aggregate):
    id: str
    document_id: str
    page_id: Optional[str]
    document_reference: Optional[str]
    page_number: Optional[int]
    condition: ConditionValue
    
    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str,
                page_id: str,page_number:str,
                extracted_condition_value:ConditionValue,
                ) -> 'ExtractedConditions':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id,
                    page_id=page_id,page_number=page_number,
                    condition=extracted_condition_value)        



class ImportedMedicationAggregate(Aggregate):
    id: str
    medication: MedicationValue
    host_medication_id:str
    medispan_id:str | None
    active:Optional[bool] = True
    original_payload:Dict

    @classmethod
    def create(cls, app_id:str,
                tenant_id:str,
                patient_id:str,
                medication: MedicationValue,
                host_medication_id:str,
                medispan_id:str,
                original_payload:Dict,
                created_by:str,
                modified_by:str
                ) -> 'ImportedMedicationAggregate':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    medication=medication,
                    host_medication_id=host_medication_id,
                    medispan_id=medispan_id,
                    original_payload=original_payload,
                    created_by=created_by,
                    modified_by=modified_by
                )
class ImportedGeneralMedicationAggregate(Aggregate):
    id: str
    medication: MedicationValue    
    host_medication_id:str
    catalog_type: Optional[Literal['medispan', 'merative']] = 'medispan'
    catalog_id: Optional[str] = None
    medispan_id:str | None    
    active:Optional[bool] = True
    original_payload:Dict

    @classmethod
    def create(cls, app_id:str,
                tenant_id:str,
                patient_id:str,
                medication: MedicationValue,
                host_medication_id:str,
                catalog_type: str,
                catalog_id: str,
                medispan_id:str,
                original_payload:Dict,
                created_by:str,
                modified_by:str
                ) -> 'ImportedGeneralMedicationAggregate':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    medication=medication,
                    host_medication_id=host_medication_id,
                    catalog_type=catalog_type,
                    catalog_id=catalog_id,
                    medispan_id=medispan_id,
                    original_payload=original_payload,
                    created_by=created_by,
                    modified_by=modified_by
                )


class MedicationProfile(Aggregate):
    id:str
    patient_id: str
    medications:Optional[List[ReconcilledMedication]] = Field(default_factory=list)

    @classmethod
    def create(cls,app_id,tenant_id,patient_id):
        id = uuid1().hex
        return cls(id=id,app_id=app_id,tenant_id=tenant_id,patient_id=patient_id)

    '''
    This function returns final medication list to be rendered in thhe UI
    '''
    def get_resolved_reconcilled_medications(self, doc_operations:List[DocumentOperation],duplicate_extracted_medications:List[ExtractedMedication]=None) -> 'List[ResolvedReconcilledMedication]':
        # return imported medication Value or user entered medication value or extracted medication value
        resolved_reconcilled_medications:List[ResolvedReconcilledMedication] = []
        for reconcilled_medication in self.medications:
            reconcilled_medication:ReconcilledMedication = reconcilled_medication
            if reconcilled_medication.is_valid:
                if reconcilled_medication.extracted_medication_reference is None:
                    LOGGER.warning("extracted_medication_reference is None for reconcilled medication %s.  Converting to empty list", reconcilled_medication.id)
                    reconcilled_medication.extracted_medication_reference = []
                if duplicate_extracted_medications:
                    # we do this so that a imported or user entered medication show up in UI and a matching/duplicate
                    # extracted medication is shown inline to the same with reference (as cirlce with page number in UI)
                    # previously a matching extracted medication would show up as separate record
                    for duplicate_extracted_medication in duplicate_extracted_medications:
                        if duplicate_extracted_medication.resolved_medication.matches(reconcilled_medication.resolved_medication):
                            reconcilled_medication.extracted_medication_reference.append(ExtractedMedicationReference(
                                document_id=duplicate_extracted_medication.document_id,
                                extracted_medication_id=duplicate_extracted_medication.id,
                                document_operation_instance_id=duplicate_extracted_medication.document_operation_instance_id,
                                page_number=duplicate_extracted_medication.page_number
                            ))
                resolved_reconcilled_medications.append(ResolvedReconcilledMedication(
                    id = reconcilled_medication.id,
                    origin= reconcilled_medication.resolved_origin, # imported or user_entered or extracted
                    medication=reconcilled_medication.resolved_medication, # imported or user_entered or extracted
                    medispan_id = reconcilled_medication.resolved_medispan_id,
                    extracted_medication_reference = reconcilled_medication.resolve_extraction_references(doc_operations), # get's relevant extraction references based on active document operation instance id
                    change_sets = reconcilled_medication.user_entered_medication.change_sets if reconcilled_medication.user_entered_medication else None,
                    medication_status = reconcilled_medication.user_entered_medication.medication_status if reconcilled_medication.user_entered_medication else None, #backward compatibility
                    deleted = reconcilled_medication.deleted,
                    host_linked = reconcilled_medication.host_linked,
                    unlisted = reconcilled_medication.unlisted,
                    modified_by = reconcilled_medication.user_entered_medication.modified_by if reconcilled_medication.user_entered_medication else None,
                ))
        return resolved_reconcilled_medications

    def get_resolved_reconcilled_medications_merged_with_extracted_medications(self, doc_operations:List[DocumentOperation], extracted_medications:List[ExtractedMedication], config: Configuration) -> 'List[ResolvedReconcilledMedication]':

        reconcilled_extracted_medication_references = []
        resolved_reconcilled_medications:List[ResolvedReconcilledMedication] = deepcopy(self.get_resolved_reconcilled_medications(doc_operations))
        
        for resolved_reconcilled_medication in resolved_reconcilled_medications:
            reconcilled_extracted_medication_references.extend([x.extracted_medication_id for x in resolved_reconcilled_medication.extracted_medication_reference])

        delta_extracted_medications_to_be_reconcilled:List[ExtractedMedication] = []
        duplicate_extracted_medications:List[ExtractedMedication] = []

        for extracted_medication in extracted_medications:

            if extracted_medication.deleted:
                continue

            if extracted_medication.id in reconcilled_extracted_medication_references:
                # already part of medication profile so skip
                continue

            if True in ([x.medication.matches(extracted_medication.resolved_medication) for x in resolved_reconcilled_medications]):
                # already part of medication profile so skip
                # ???update extractedReferences [from different operation instance across pages and docs]
                # reconcile process dedupes among extracted medications only. This step is to ensure we dedup between extracted and user entered/imported
                # and if there is a duplicate we ignore since user entered or imported wins over extracted
                # for now we want duplicates to show in number. frontend should show at UI deduped
                duplicate_extracted_medications.append(extracted_medication)
                continue
                

            delta_extracted_medications_to_be_reconcilled.append(extracted_medication)

        
        # this call dedups among extracted medication (no user entered or imported) in memory
        self.reconcile_extracted_medications(delta_extracted_medications_to_be_reconcilled, config)

        return self.get_resolved_reconcilled_medications(doc_operations,duplicate_extracted_medications)

    def get_resolved_reconcilled_medication_from_extracted_medication(self, extracted_medication:ExtractedMedication) -> Optional[ResolvedReconcilledMedication]:
        return ResolvedReconcilledMedication(
            id = extracted_medication.id,
            origin= Origin.EXTRACTED,
            medication=extracted_medication.resolved_medication,
            medispan_id = extracted_medication.medispan_id,
            extracted_medication_reference = [ExtractedMedicationReference(
                document_id=extracted_medication.document_id,
                extracted_medication_id=extracted_medication.id,
                document_operation_instance_id=extracted_medication.document_operation_instance_id,
                page_number=extracted_medication.page_number
            )],
            change_sets = None,
            medication_status = None,
            deleted = extracted_medication.deleted,
            host_linked = False,
            unlisted = False,
            modified_by = None
        )

    def get_page_profiles(self, document_id:str, doc_operation:DocumentOperation) -> List['MedicationPageProfile']:
        medications_page_count = {}
        medications_page_profile = []
        resolved_reconcilled_medications:List[ResolvedReconcilledMedication] = self.get_resolved_reconcilled_medications([doc_operation])
        for medication in resolved_reconcilled_medications:
            medication:ResolvedReconcilledMedication = medication
            for extracted_med_ref in medication.extracted_medication_reference:
                extracted_med_ref:ExtractedMedicationReference = extracted_med_ref
                if extracted_med_ref.document_id == document_id and doc_operation.active_document_operation_instance_id == extracted_med_ref.document_operation_instance_id:

                    medications_page_count[extracted_med_ref.page_number] = medications_page_count.get(extracted_med_ref.page_number, 0) + 1

        for page_number, count in medications_page_count.items():
            medications_page_profile.append(
                MedicationPageProfile(
                    page_profile_number=page_number,
                    has_items=True,
                    number_of_items=count,
                    items=[]
            ))


        return medications_page_profile

    def get_page_profiles_merged_with_extracted_medications(self, document_id:str, doc_operation:DocumentOperation, extracted_medications:List[ExtractedMedication], config:Configuration) -> List['MedicationPageProfile']:
        medications_page_count = {}
        medications_page_profile = []
        resolved_reconcilled_medications:List[ResolvedReconcilledMedication] = self.get_resolved_reconcilled_medications_merged_with_extracted_medications([doc_operation],extracted_medications,config)
        extracted_med_ref_ids = []
        for medication in resolved_reconcilled_medications:
            medication:ResolvedReconcilledMedication = medication
            for extracted_med_ref in medication.extracted_medication_reference:
                extracted_med_ref:ExtractedMedicationReference = extracted_med_ref

                # add medication.origin == Origin.EXTRACTED and to below condition to return only extracted counts
                if extracted_med_ref.document_id == document_id and doc_operation.active_document_operation_instance_id == extracted_med_ref.document_operation_instance_id:
                    if extracted_med_ref.extracted_medication_id not in extracted_med_ref_ids:
                        extracted_med_ref_ids.append(extracted_med_ref.extracted_medication_id)
                        medications_page_count[extracted_med_ref.page_number] = medications_page_count.get(extracted_med_ref.page_number, 0) + 1

        for page_number, count in medications_page_count.items():
            medications_page_profile.append(
                MedicationPageProfile(
                    page_profile_number=page_number,
                    has_items=True,
                    number_of_items=count,
                    items=[]
            ))


        return medications_page_profile

    """
    add new extracted_medication_reference if doesnt exist
    """
    def reconcile_extracted_medications(self, extracted_medications:List[ExtractedMedication], config:Configuration) -> ReconcilledMedication:
        reconcilled_medication_record:ReconcilledMedication=None
        for extracted_medication in extracted_medications:
            if extracted_medication.deleted:
                continue

            reconcilled_medication_record:ReconcilledMedication= self._get_reconcilled_medication_record(extracted_medication)
            LOGGER.debug("Reconcilled medication record: %s", extracted_medication.medispan_medication)
            # no reconcilled medication record found, create new
            
            if not reconcilled_medication_record:
                reconcilled_medication_record = ReconcilledMedication(
                        # id=uuid1().hex,
                        id=extracted_medication.id,
                        document_references=[extracted_medication.document_reference],
                        medication=MedicationValue(name=extracted_medication.medispan_medication.name if extracted_medication.medispan_medication else extracted_medication.medication.name,
                                                    name_original=extracted_medication.medication.name,
                                                    dosage=extracted_medication.medispan_medication.dosage if extracted_medication.medispan_medication and extracted_medication.medispan_medication.dosage  else extracted_medication.medication.dosage,
                                                    route=extracted_medication.medispan_medication.route if extracted_medication.medispan_medication else extracted_medication.medication.route,
                                                    frequency =extracted_medication.medication.frequency,
                                                    instructions=extracted_medication.medication.instructions,
                                                    form=extracted_medication.medispan_medication.form if extracted_medication.medispan_medication else extracted_medication.medication.form,
                                                    start_date=extracted_medication.medication.start_date,
                                                    end_date=extracted_medication.medication.end_date,
                                                    discontinued_date=extracted_medication.medication.discontinued_date,
                                                    strength = extracted_medication.medispan_medication.strength if extracted_medication.medispan_medication else extracted_medication.medication.strength,
                                                    ),
                        medispan_id=extracted_medication.medispan_id or extracted_medication.medispan_medication.medispan_id if extracted_medication.medispan_medication else None,
                        medispan_status=extracted_medication.medispan_status,
                        latest_start_date=extracted_medication.medication.start_date,
                        latest_end_date=extracted_medication.medication.end_date,
                        latest_dicontinued_date=extracted_medication.medication.discontinued_date,
                        extracted_medication_reference=[ExtractedMedicationReference(
                            document_id=extracted_medication.document_id,
                            extracted_medication_id=extracted_medication.id,
                            document_operation_instance_id=extracted_medication.document_operation_instance_id,
                            page_number=extracted_medication.page_number
                        )]
                    )

                self.medications.append(reconcilled_medication_record)
            else:
                # reconcilled medication record found, update start date, end date and extracted medication reference
                extracted_medication_reference_found = False
                # idempotent check: check if this ecxtracted medication exist in the extracted_medication_reference
                # for given operation instance id
                for extracted_medication_reference in reconcilled_medication_record.extracted_medication_reference:
                    extracted_medication_reference:ExtractedMedicationReference= extracted_medication_reference
                    if extracted_medication_reference.extracted_medication_id == extracted_medication.id and \
                        extracted_medication_reference.document_id == extracted_medication.document_id and \
                        extracted_medication_reference.page_number == extracted_medication.page_number:
                        # if extracted reference is same as reconcilled medication reference, lets update dosage??
                        reconcilled_medication_record.medication.dosage = extracted_medication.medication.dosage

                    if extracted_medication_reference.extracted_medication_id == extracted_medication.id and \
                        extracted_medication_reference.document_id == extracted_medication.document_id and \
                        extracted_medication_reference.page_number == extracted_medication.page_number and \
                        extracted_medication_reference.document_operation_instance_id == extracted_medication.document_operation_instance_id:
                        extracted_medication_reference_found=True
                        reconcilled_medication_record.medication.dosage = extracted_medication.medication.dosage
                        break

                if extracted_medication_reference_found:
                    # no need to reprocess as its duplicate
                    continue

                # extracted medication document reference updated in reconcilled medication record if not already exists
                if extracted_medication.document_reference not in reconcilled_medication_record.document_references:
                    reconcilled_medication_record.document_references.append(extracted_medication.document_reference)


                reconcilled_medication_record.extracted_medication_reference.append(ExtractedMedicationReference(
                    document_id=extracted_medication.document_id,
                    extracted_medication_id=extracted_medication.id,
                    document_operation_instance_id=extracted_medication.document_operation_instance_id,
                    page_number=extracted_medication.page_number
                ))

                # update latest start date and end date
                data_format = "%m/%d/%Y"
                try:
                    if extracted_medication.start_date:
                        extracted_start_data = datetime.strptime(extracted_medication.start_date, data_format)
                        if reconcilled_medication_record.latest_start_date:
                            reconcilled_start_date = datetime.strptime(reconcilled_medication_record.latest_start_date, data_format)
                            if extracted_start_data > reconcilled_start_date:
                                reconcilled_medication_record.latest_start_date = extracted_medication.start_date
                        else:
                            reconcilled_medication_record.latest_start_date = extracted_medication.start_date

                    if extracted_medication.end_date:
                        extracted_end_data = datetime.strptime(extracted_medication.end_date, data_format)
                        if reconcilled_medication_record.latest_end_date:
                            reconcilled_end_date = datetime.strptime(reconcilled_medication_record.latest_end_date, data_format)
                            if extracted_end_data > reconcilled_end_date:
                                reconcilled_medication_record.latest_end_date = extracted_medication.end_date
                        else:
                            reconcilled_medication_record.latest_end_date = extracted_medication.end_date

                    if extracted_medication.discontinued_date:
                        extracted_discontinued_data = datetime.strptime(extracted_medication.discontinued_date, data_format)
                        if reconcilled_medication_record.latest_discontinued_date:
                            reconcilled_discontinued_date = datetime.strptime(reconcilled_medication_record.latest_discontinued_date, data_format)
                            if extracted_discontinued_data > reconcilled_discontinued_date:
                                reconcilled_medication_record.latest_discontinued_date = extracted_medication.discontinued_date
                        else:
                            reconcilled_medication_record.latest_discontinued_date = extracted_medication.discontinued_date
                except:
                    # ToDo: handle date format fix
                    pass

        return reconcilled_medication_record
    """
    add or update user_entered_medication if it doesnt exist
    """
    def add_user_entered_medication(self, user_entered_medication:UserEnteredMedicationAggregate, edit_type:str="updated"):
        reconcilled_medication_record_found = False
        for reconcilled_medication in self.medications:
            # extracted medication match scenario
            if not reconcilled_medication.user_entered_medication and \
                not reconcilled_medication.imported_medication and \
                    not reconcilled_medication.deleted and \
                        reconcilled_medication.medication.matches(user_entered_medication.medication):
                reconcilled_medication_record_found = True
                reconcilled_medication.user_entered_medication = UserEnteredMedication(
                    medication=user_entered_medication.medication,
                    edit_type= edit_type,
                    change_sets= user_entered_medication.change_sets,
                    medication_status=user_entered_medication.medication_status,
                    modified_by=user_entered_medication.modified_by,
                    modified_at=user_entered_medication.modified_at,
                    document_id=user_entered_medication.document_id
                )
                return reconcilled_medication
        if not reconcilled_medication_record_found:
            reconcilled_medication_record = ReconcilledMedication(
                id=uuid1().hex,
                medication=user_entered_medication.medication,
                document_references=[user_entered_medication.document_id],
                extracted_medication_reference=user_entered_medication.extracted_medication_references,
                user_entered_medication = UserEnteredMedication(
                    medication=user_entered_medication.medication,
                    edit_type= edit_type,
                    change_sets= user_entered_medication.change_sets,
                    medication_status=user_entered_medication.medication_status,
                    modified_by=user_entered_medication.modified_by,
                    modified_at=user_entered_medication.modified_at,
                    document_id=user_entered_medication.document_id
                )
            )
            self.medications.append(reconcilled_medication_record)
            return reconcilled_medication_record

    """
    add or update imported_medications if it doesnt exist
    """
    def reconcile_imported_medications(self, imported_medication:ImportedMedicationAggregate)->Result:
        reconcilled_medication_record_found = False
        reconcilled_medication_record_id = None
        host_med_id: str = imported_medication.host_medication_id
        reconcilled_status = False
        context = {}
        LOGGER.info("reconcilling for imported medication %s", json.dumps(json.loads(imported_medication.json()), indent=2))
        for reconcilled_medication in self.medications:
            LOGGER.info("Matching host_med_id %s to Reconciled medication: %s", host_med_id, json.dumps(json.loads(reconcilled_medication.json()), indent=2))
            # First match based on the host system id
            if (reconcilled_medication.host_medication_sync_status and reconcilled_medication.host_medication_sync_status.host_medication_unique_identifier==host_med_id) or \
                (reconcilled_medication.imported_medication and reconcilled_medication.imported_medication.host_medication_id == host_med_id):
                # No need to do anything as this imported medication already has a link to an existing medication
                LOGGER.debug("Preexisting host_medication_id link to existing medication")
                reconcilled_medication_record_found = True
                reconcilled_status = False
                reconcilled_medication_record_id = reconcilled_medication.id
                context["reconcilled_medication.host_medication_sync_status"] = reconcilled_medication.host_medication_sync_status
                break

            # If the reconcilled medication doesn't have a host system id, match based on string matching
            if reconcilled_medication.resolved_medication.matches(imported_medication.medication):
                reconcilled_medication.imported_medication = ImportedMedication(
                    imported_medication_id=imported_medication.id,
                    host_medication_id=imported_medication.host_medication_id,
                    medispan_id=imported_medication.medispan_id,
                    medication=imported_medication.medication,
                    modified_by=imported_medication.modified_by
                )
                reconcilled_medication_record_found = True
                reconcilled_status = True
                reconcilled_medication_record_id = reconcilled_medication.id
                break

        if not reconcilled_medication_record_found:
            LOGGER.debug("Could not match to existing medication.  Creating a new reconcilled medication...")
            reconcilled_medication_record = ReconcilledMedication(
                id=uuid1().hex,
                medication=imported_medication.medication,
                imported_medication = ImportedMedication(
                    imported_medication_id=imported_medication.id,
                    host_medication_id=imported_medication.host_medication_id,
                    medispan_id=imported_medication.medispan_id,
                    medication=imported_medication.medication,
                    modified_by=imported_medication.modified_by
                )
            )
            reconcilled_status = True
            reconcilled_medication_record_id = reconcilled_medication_record.id
            self.medications.append(reconcilled_medication_record)

        return Result(success=True, return_data={"imported_medication_record":imported_medication,
                                                 "reconcilled_medication_record_id":reconcilled_medication_record_id,
                                                 "reconcilled_medication_record_found":reconcilled_medication_record_found,
                                                 "reconcilled_status":reconcilled_status,
                                                 "context":context})

    def delete_reconcilled_medication(self,reconcilled_medication_id:str):
        for reconcilled_medication in self.medications:
            if reconcilled_medication.id == reconcilled_medication_id:
                reconcilled_medication.delete()
                break

    def un_delete_reconcilled_medication(self,reconcilled_medication_id:str):
        for reconcilled_medication in self.medications:
            if reconcilled_medication.id == reconcilled_medication_id:
                reconcilled_medication.un_delete()
                break

    def update_host_medication_sync_status(self, reconcilled_medication_id:str, host_medication_sync_status:HostMedicationSyncStatus):
        for reconcilled_medication in self.medications:
            if reconcilled_medication.id == reconcilled_medication_id:
                reconcilled_medication.host_medication_sync_status = host_medication_sync_status
                break

    def delete_medications_from_deleted_document(self, document:Document):
        if not document.active:
            for reconcilled_medication in self.medications:
                if not reconcilled_medication.host_linked and document.id in reconcilled_medication.document_references:
                    reconcilled_medication.delete()

    """
    update medispan value if exists otherwise None
    """
    def resolve_medispan(self, medispan_medication:MedicationValue,medispan_id:str):
        if not medispan_medication:
            pass

    def get_reconcilled_medication(self, reconcilled_medication_id:str):
        for reconcilled_medication in self.medications:
            if reconcilled_medication.id == reconcilled_medication_id:
                LOGGER.debug("Found reconciled medication for id %s: %s", reconcilled_medication_id, reconcilled_medication)
                if reconcilled_medication and reconcilled_medication.medication and reconcilled_medication.medication.medispan_id:
                    reconcilled_medication.medispan_id = reconcilled_medication.medication.medispan_id

                return reconcilled_medication
        return

    """
    business invariant based logic that finds the right reconcilled record
    from the list
    """
    def _get_reconcilled_medication_record(self,extracted_medication:ExtractedMedication)->ReconcilledMedication:

        def does_match_reconcilled_medication_record(x:ReconcilledMedication,extracted_medication:ExtractedMedication):
            return not x.deleted and x.resolved_origin == Origin.EXTRACTED and x.resolved_medication.matches(extracted_medication.medispan_medication or extracted_medication.medication)

        
        matched_medication_record_list = list(filter(lambda x: does_match_reconcilled_medication_record(x,extracted_medication),self.medications))
        if matched_medication_record_list:
            return matched_medication_record_list[0]
        return None

class ExtractedMedicationGrade(Aggregate):
    extracted_medication_id: str
    document_id: str
    page_number: int
    document_operation_instance_id: str
    medication_extraction_document_operation_instance_id: Optional[str] = None
    medication: MedicationValue
    medispan_id: Optional[str] = None
    score: Score
    fields_with_issues: List[str] = Field(default_factory=list)

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,extracted_medication_id: str, document_id: str, page_number: int,
                document_operation_instance_id: str, medication: MedicationValue, medispan_id: str, score: Score, fields_with_issues: List[str]) -> 'ExtractedMedicationGrade':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,extracted_medication_id=extracted_medication_id,
                   document_id=document_id, page_number=page_number,
                   document_operation_instance_id=document_operation_instance_id,
                   medication=medication, medispan_id=medispan_id, score=score, fields_with_issues=fields_with_issues)

class MedispanLocalCache(Aggregate):
    id:str
    search_term:str
    medication_suggestions:List[Dict[str,str]]

    @classmethod
    def create(cls, search_term:str,medication_suggestions:List[Dict[str,str]]) -> 'MedispanLocalCache':
        id = uuid1().hex
        return cls(id=id,
                   search_term=search_term,
                   medication_suggestions=medication_suggestions)

"""
Legacy Medication Model
we will migrate on fly to new ExtractedMedication Model and MedicationProfile model
"""
class Medication(Aggregate):
    id: str
    key: Optional[str]
    document_id: str
    page_id: str
    name: str
    medispan_id: Optional[str] = None
    original_name: Optional[str] = None
    dosage: Optional[str]
    route: Optional[str]
    frequency: Optional[str]
    route: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    reason: Optional[str]
    explaination: Optional[str]
    document_reference: str
    page_number: int
    active: bool = True
    change_sets: List[MedicationChangeSet] = Field(default_factory=list)
    deleted: bool = False

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str, page_id: str,
                name:str, dosage:str, frequency:str,
                route:str, start_date:str, end_date:str,
                document_reference:str, page_number:int,
                reason:str=None,explaination:str=None,active=True) -> 'Medication':
        id = uuid1().hex
        o = cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id,
                page_id=page_id,
                medication=MedicationValue(name=name, dosage=dosage, route=route),
                frequency=frequency,
                start_date=start_date,
                end_date=end_date,
                document_reference=document_reference,
                page_number=page_number,
                reason=reason,
                explaination=explaination,
                active=active)
        o.original_name = name
        o.key = o.generate_key()
        return o

    def generate_key(self):
        KEY_SEPARATOR = '|'
        key = []
        key.append(safe_str(self.document_id))
        key.append(safe_str(self.page_id))
        key.append(safe_str(self.name))
        key.append(safe_str(self.dosage))
        key.append(safe_str(self.route))
        key.append(safe_str(self.frequency))
        key.append(safe_str(self.start_date))
        key.append(safe_str(self.end_date))

        k = KEY_SEPARATOR.join(key)
        k = k.upper()

        return k

    def update(self, **kwargs):
        if self.deleted:
            raise ValueError('Medication is deleted, cannot update')
        allowed_fields = ['name', 'dosage', 'frequency', 'route', 'start_date', 'end_date', 'reason', 'explaination']
        changes = []
        for field in kwargs:
            if field in allowed_fields:
                if field == 'name' and self.original_name is None:
                    self.original_name = self.name
                if getattr(self, field) != kwargs[field]:
                    changes.append(MedicationChange(field=field, old_value=getattr(self, field), new_value=kwargs[field]))
                    setattr(self, field, kwargs[field])
            else:
                raise ValueError(f'Field {field} not allowed for update')
        self.change_sets = self.change_sets + [MedicationChangeSet(changes=changes)]
        self.key = self.generate_key()

    def delete(self):
        if self.deleted:
            raise ValueError('Medication already deleted')
        self.deleted = True
        self.change_sets = self.change_sets + [MedicationChangeSet(changes=[
            MedicationChange(field='deleted', old_value=False, new_value=True),
        ])]

    def undelete(self):
        if not self.deleted:
            raise ValueError('Medication not deleted')
        self.deleted = False
        self.change_sets = self.change_sets + [MedicationChangeSet(changes=[
            MedicationChange(field='deleted', old_value=False, new_value=True),
        ])]

    def deactivate(self) -> None:
        self.active = False

    @staticmethod
    def toJSON(data):
        result = {}
        try:
            if USE_JSON_SAFE_LOADS:
                result = safe_loads(data)
            else:
                result=json.loads(data)
            
        except Exception as e:
            extra = {
                "error": str(e),
                "data": data,
            }
            LOGGER2.warning("Error in parsing Medication JSON data: %s", e, extra=extra)
            balanced_json = extract_json(data)
            extra = {
                "balanced_json": balanced_json,
            }
            LOGGER2.debug("Second pass at parsing Medication JSON data", extra=extra)
            result=balanced_json
        return result
    

class Conditions(Aggregate):
    id: str
    key: Optional[str]
    document_id: str
    page_id: str
    condition: str
    diagnosis_date: Optional[str]
    specific_details: Optional[str]
    document_reference: str
    page_number: int
    
    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str, page_id: str,
                condition:str, diagnosis_date:str, specific_details:str,
                document_reference:str, page_number:int,
                reason:str=None,explaination:str=None,active=True) -> 'Conditions':
        id = uuid1().hex
        o = cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id,
                page_id=page_id,
                Condition=ConditionValue(condition=condition, diagnosis_date=diagnosis_date, specific_details=specific_details),
                document_reference=document_reference,
                page_number=page_number,
                reason=reason,
                explaination=explaination,
                active=active)
        o.condition = condition
        o.key = o.generate_key()
        return o

    def generate_key(self):
        KEY_SEPARATOR = '|'
        key = []
        key.append(safe_str(self.document_id))
        key.append(safe_str(self.page_id))
        key.append(safe_str(self.condition))
        key.append(safe_str(self.diagnosis_date))
        key.append(safe_str(self.specific_details))
        k = KEY_SEPARATOR.join(key)
        k = k.upper()

        return k

    @staticmethod
    def toJSON(data):
        result = {}
        try:
            result=json.loads(data)
        except Exception as e:
            balanced_json = extract_json(data)
            result=balanced_json
        return result    


class Certification(BaseModel):

    isCertified: bool = False
    category: str
    comments: Optional[str] = None
    createdBy: str
    createdDate: datetime
    changedBy: Optional[str] = None
    changedDate: Optional[datetime] = None

    @classmethod
    def create(cls, isCertified: bool, category: str, comments: Optional[str], createdBy: str) -> 'Certification':
        return cls(isCertified=isCertified, category=category, comments=comments, createdBy=createdBy, createdDate=now_utc())

class DocumentMedicationProfile2(Medication):
    medication_status: Optional[str] = None
    medication_status_reason: Optional[str] = None
    medication_status_reason_explaination: Optional[str] = None

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,
                document_id: str, page_id: str,
                name:str, dosage:str,
                frequency:str, route:str, start_date:str, end_date:str,document_reference:str,
                page_number:int,
                medication_status:str, medication_status_reason:str, medication_status_reason_explaination:str,
                medispan_id: str = None,
                reason:str=None,explaination:str=None,active=True
                ) -> 'DocumentMedicationProfile2':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id, page_id=page_id,
                   medispan_id=medispan_id,
                   name=name, dosage=dosage, frequency=frequency, route=route, start_date=start_date, end_date=end_date,
                   document_reference=document_reference, page_number=page_number,reason=reason,explaination=explaination,active=active,
                   medication_status=medication_status,
                   medication_status_reason=medication_status_reason,
                   medication_status_reason_explaination=medication_status_reason_explaination)

    def update(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)



class DocumentMedicationProfile(Aggregate):
    id: str
    document_id: str
    page_id: str
    medication_key: str
    certification: Certification
    active: bool = True

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str, page_id: str, medication_key: str, certification: Certification) -> 'DocumentMedicationProfile':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id, page_id=page_id, medication_key=medication_key, certification=certification)


class MedispanDrug(BaseModel):
    id: Optional[str]
    NameDescription: str
    GenericName: str
    Route: str
    Strength: Optional[str]
    StrengthUnitOfMeasure: Optional[str] = None
    Dosage_Form: str

    @classmethod
    def create(cls,
               ExternalDrugId: str,
               NameDescritption: str,
               GenericName: str,
               Route: str,
               Strength: str,
               StrengthUnitOfMeasure: str,
               Dosage_Form: str) -> 'MedispanDrug':

        return cls(id=ExternalDrugId, NameDescription=NameDescritption, GenericName=GenericName, Route=Route, Strength=Strength, StrengthUnitOfMeasure=StrengthUnitOfMeasure, Dosage_Form=Dosage_Form)

    def to_dict(self):
        response = {
            "id": self.id,
            "full_name": self.NameDescription,
            "generic_name": self.GenericName,
            "brand_name": self.NameDescription,
            "route": self.Route,
            "form": self.Dosage_Form,
            "strength": {
                "value": self.Strength,
                "unit": self.StrengthUnitOfMeasure
            },
            "package": {
                "size": 1.0,
                "unit": "EA",
                "quantity": 30
            },
            "meta": {
                "count": 3,
                "externalDrugIds": [
                    "40139.0",
                    "40139.0",
                    "40139.0"
                ]
            },
            "score": {}
        }
        return response

class Evidences(Aggregate):
    id: str
    document_id: str
    page_id: str
    page_number: int
    evidences: List[AnnotationToken]
    active: bool = True

    @classmethod
    def create(cls, app_id:str,tenant_id:str,patient_id:str,document_id: str, page_id: str, page_number:int,evidences,active=True) -> 'Evidences':
        id = uuid1().hex
        return cls(id=id, app_id=app_id,tenant_id=tenant_id,patient_id=patient_id,document_id=document_id, page_id=page_id, evidences=evidences, page_number=page_number, active=active)

    def deactivate(self) -> None:
        self.active = False


class ReferenceItem:
    id: str
    name: str
    description: Optional[str] = None

    def __init__(self, id: str, name: str, description: Optional[str]=None):
        self.id = id
        self.name = name
        self.description = description

class ReferenceList:
    id: str
    name: str
    items: list[ReferenceItem] = []

    def __init__(self, items: list[ReferenceItem]):
        self.items = items

class ConfigurationSettings(AppAggregate):
    id: str
    code: str
    settings: Dict[str, Any]
    active: Optional[bool] = True

    @classmethod
    def create(cls, code: str, settings: Dict[str, Any]) -> 'ConfigurationSettings':
        id = uuid1().hex
        return cls(id=id, code=code, settings=settings)

    def update(self, settings: Dict[str, Any]):
        self.settings = settings

    def delete(self):
        self.active = False

    def undelete(self):
        self.active = True

def RawJSONDecoder(index):
    class _RawJSONDecoder(json.JSONDecoder):
        end = None

        def decode(self, s, *_):
            data, self.__class__.end = self.raw_decode(s, index)
            return data

    return _RawJSONDecoder

def extract_json(s, index=0):
    while (index := s.find('{', index)) != -1 or (index := s.find('[', index)) != -1:
        try:
            yield json.loads(s, cls=(decoder := RawJSONDecoder(index)))
            index = decoder.end
        except json.JSONDecodeError:
            index += 1



"""
{
    "items":[
            "type":"allergies",
            "data":[{},{},{}]
        ]
}
"""
class ExtractedClinicalData(Aggregate):
    document_id: str
    document_operation_instance_id:str
    page_id: str
    page_number:int
    clinical_data_type: str
    clinical_data: List[Dict]

    @classmethod
    def create(cls, app_id:str, tenant_id:str, patient_id:str,
               page_id:str,page_number:int,
               document_id:str,document_operation_instance_id:str,
               clinical_data_type:str,
               clinical_data:List[Dict]) -> 'ExtractedClinicalData':
        id = uuid1().hex
        return cls(id=id,
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    page_id=page_id,
                    page_number=page_number,
                    document_id=document_id,
                    document_operation_instance_id=document_operation_instance_id,
                    clinical_data_type = clinical_data_type,
                    clinical_data = clinical_data
                )

class MedicalCodingRawData(Aggregate):
    document_id: str
    document_operation_instance_id:str
    medical_coding_data: Optional[Dict | List] = None
    input_fhir_data: Optional[Dict] = None

    @classmethod
    def create(cls, app_id:str, tenant_id:str, patient_id:str,
               document_id:str,document_operation_instance_id:str,
               medical_coding_data:Dict,input_fhir_data:Dict) -> 'MedicalCodingRawData':
        id = uuid1().hex
        return cls(id=id,
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    document_id=document_id,
                    document_operation_instance_id=document_operation_instance_id,
                    medical_coding_data = medical_coding_data,
                    input_fhir_data = input_fhir_data
                )


class MedicalCoding(BaseModel):
    pass

class ExtractedClinicalDataDeduped(Aggregate):
    clinical_data: Dict
    clinical_data_type: str
    references: List[ExtractedClinicalDataReference]

class ExtractedCondition(BaseModel):
    evidences: List[ConditionsEvidence]
    icd10_codes: List[ConditionICD10Code]
    category: str

class PageOperation(Aggregate):
    document_id: str
    page_number: int
    page_id: str
    extraction_type:PageLabel
    extraction_status: PageOperationStatus


    @classmethod
    def create(cls, app_id:str, tenant_id:str, patient_id:str,
                document_id:str,document_operation_instance_id:str,
                page_id:str,page_number:int,
                extraction_type:PageLabel,extraction_status:PageOperationStatus,
                created_by:str, modified_by:str) -> 'PageOperation':
        id = uuid1().hex
        return cls(id=id,
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    document_id=document_id,
                    document_operation_instance_id=document_operation_instance_id,
                    page_id=page_id,
                    page_number=page_number,
                    extraction_type=extraction_type,
                    extraction_status=extraction_status,
                    created_by=created_by,
                    modified_by=modified_by
                )
        
class EntityRetryConfig(Aggregate):
    retry_entity_id: str
    retry_entity_type: str
    retry_count: int
    document_id: str
    
    @classmethod
    def create(cls, app_id:str, tenant_id:str, patient_id:str,document_id:str,document_operation_instance_id:str,
                retry_entity_id:str, retry_entity_type:str, retry_count:int) -> 'EntityRetryConfig':
        id = uuid1().hex
        return cls(id=id,
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    retry_entity_id=retry_entity_id,
                    retry_entity_type=retry_entity_type,
                    retry_count=retry_count,
                    document_id=document_id,
                    document_operation_instance_id=document_operation_instance_id
                )
    
class OperationMeta(BaseModel):
    type: str
    step: str
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    iteration: Optional[int] = 0
    document_operation_def_id: Optional[str] = None
    document_operation_instance_id: Optional[str] = None
    priority: Optional[str] = None

class StatusCode(str, Enum):
    OK = "OK"
    FAILED = "FAILED"

class Status(BaseModel):
    status: StatusCode
    message: Optional[str] = None
    children: Optional[List['Status']] = []

    @classmethod
    def create(cls,  status: StatusCode, message: Optional[str]=None) -> 'Status':
        return cls(status=status, message=message)

class DocumentAssessment(BaseModel):
    created_at: str
    processing_time: float
    is_delayed: bool
    document_id: str
    processing_time_unit: str

Configuration.MedispanMatchConfig.RerankSettings.update_forward_refs()
Configuration.MedispanMatchConfig.MedispanMatchV2Settings.update_forward_refs()
Configuration.MedispanMatchConfig.update_forward_refs()
Configuration.update_forward_refs()

AppConfig.update_forward_refs()


class DocumentOrchestrationAgent():

    document: Optional[str] = None
    config: Optional[Configuration] = None

    def __init__(self, document: Document = None, config: Configuration = None):
        self.document = document
        self.config = config

    async def orchestrate(self, document_id: str):
        raise NotImplementedError
