from typing import Any, BinaryIO, Dict, List, Literal, Optional, Union
from uuid import uuid1
from datetime import datetime

from paperglass.domain.values import (
    AnnotationType,
    ClinicalData,
    Configuration,
    DocumentOperationStatus,
    DocumentOperationStep,
    DocumentSettings,
    DocumentStatusType,
    EmbeddingChunkingStartegy,
    EmbeddingStrategy,
    ExtractedMedicationReference,
    MedicationStatus,
    MedicationValue,
    NamedEntityExtractionType,
    OrchestrationPriority,
    PDFParsingStrategy,
    PageOperationStatus,
    PageText,
    ReconcilledMedication,
    SearchQueryStrategy,
    Section,
    NamedEntity,
    UserEnteredMedication,
    DocumentOperationType,
    Schedule,
)
from paperglass.domain.values_http import (
    GenericExternalDocumentCreateEventRequestApi,
    GenericExternalDocumentCreateEventRequestUri,
    GenericExternalDocumentRepositoryApi,
    GenericExternalDocumentRepositoryUri,
    ExternalDocumentRepositoryType
)
from paperglass.domain.utils.token_utils import mktoken2
from paperglass.domain.models import Document, DocumentMedicationProfile, DocumentOperation, DocumentOperationInstance, DocumentOperationStatusSnapshot, ExtractedMedication, PageLabel
from paperglass.domain.models_common import EntityFilter
from paperglass.domain.model_toc import DocumentFilterState, PageTOC, DocumentPageFilterState
from paperglass.domain.model_testing import TestCase, TestResults, TestDataDetails, E2ETestCaseSummaryResults, E2ETestCase

from pydantic import BaseModel, Extra, Field
from paperglass.settings import MULTIMODAL_MODEL


# Sample commands

class BaseCommand(BaseModel, frozen=True, extra=Extra.forbid):
    id: str = Field(default_factory=lambda: uuid1().hex)
    type: str
    execution_id: Optional[str] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    idempotent_key: Optional[str] = None
    cross_transaction_error_strict_mode: Optional[bool] = True

    def toExtra(self):
        o = {
            "id": self.id,
            "type": self.type,
            "created_by": self.created_by,
        }
        return o

class AppBaseCommand(BaseCommand, frozen=True, extra=Extra.forbid):
    id: str = Field(default_factory=lambda: uuid1().hex)
    type: str
    app_id: str
    tenant_id: str
    patient_id: str
    execution_id: Optional[str] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    @property
    def token(self):
        return mktoken2(self.app_id, self.tenant_id, self.patient_id)

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "created_by": self.created_by,
        }
        supero.update(o)
        return supero
    
class DocumentBaseCommand(AppBaseCommand,frozen=True, extra=Extra.forbid):
    document_id: str
    document_operation_instance_id: str
    document_operation_definition_id:str
    step_id: str
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT
    is_test: Optional[bool] = False

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "document_id": self.document_id,
            "document_operation_instance_id": self.document_operation_instance_id,
            "document_operation_definition_id": self.document_operation_definition_id,            
            "step_id": self.step_id,
            "priority": self.priority,
            "is_test": self.is_test,
        }
        supero.update(o)
        return supero
    

class GetStatus(BaseCommand):
    type: str = Field('get_status', const=True)    

class CreateNote(BaseCommand):
    type: str = Field('create_note', const=True)
    title: str
    content: str


class UpdateNote(BaseCommand):
    type: str = Field('update_note', const=True)
    note_id: str
    content: str


class SendEmail(BaseCommand):
    type: str = Field('send_email', const=True)
    template: str
    note_id: str
    email: str


# Real commands

class CreateAppConfiguration(BaseCommand):
    type: str = Field('create_app_configuration', const=True)
    app_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: Configuration = Field(default_factory=Configuration)
    
class CreateTenantConfiguration(CreateAppConfiguration):
    type: str = Field('create_tenant_configuration', const=True)
    tenant_id:str

class UpdateAppConfiguration(BaseCommand):
    type: str = Field('update_app_configuration', const=True)
    app_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: Configuration = Field(default_factory=Configuration)
    archive_current: bool = True
    version_comment: Optional[str] = None
    
class UpdateTenantConfiguration(UpdateAppConfiguration):
    type: str = Field('update_tenant_configuration', const=True)
    tenant_id: str

class TriggerExtraction(BaseCommand):
    type: str = Field('trigger_extraction', const=True)
    patient_id: str
    app_id: str
    tenant_id: str
    source_document_storage_uri: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,            
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "source_document_storage_uri": self.source_document_storage_uri,            
        }
        supero.update(o)
        return supero

# Deprecated for future use.  Refer to StartOrchestration command instead
class Orchestrate(BaseCommand):
    type: str = Field('orchestrate', const=True)
    patient_id: str
    app_id: str
    tenant_id: str
    document_id: str
    token:str
    force_new_instance: Optional[bool] = False
    document_operation_def_id: Optional[str] = None
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,            
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "document_operation_definition_id": self.document_operation_def_id,
            "force_new_instance": self.force_new_instance,
            "priority": self.priority,
        }
        supero.update(o)
        return supero

# Command used by the UI to start orchestration (beginning with v4 with backward compatabilty to v3)
class StartOrchestration(BaseCommand):
    type: str = Field('start_orchestration', const=True)
    patient_id: str
    app_id: str
    tenant_id: str
    document_id: str    
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,            
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,            
            "priority": self.priority,
        }
        supero.update(o)
        return supero
    
class CreateTestDocument(BaseCommand):
    type: str = Field('CreateTestDocument', const=True)
    patient_id: str
    app_id: str
    tenant_id: str
    token:str
    storage_uri:str = None
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class QueueCommand(BaseCommand):
    type: str = Field('queue_command', const=True)
    command: BaseCommand
    

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "command": self.command.dict(),            
        }
        supero.update(o)
        return supero


class QueueOrchestration(BaseCommand):
    type: str = Field('queue_orchestration', const=True)
    document_operation_type: str
    document_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "document_operation_type": self.document_operation_type,
            "document_id": self.document_id,
        }
        supero.update(o)
        return supero


class QueueDeferredOrchestration(BaseCommand):
    type: str = Field('queue_deferred_orchestration', const=True)
    document_operation_type: str
    document_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "document_operation_type": self.document_operation_type,
            "document_id": self.document_id,
        }
        supero.update(o)
        return supero


class StartOrchestration(BaseCommand):
    type: str = Field('start_orchestration', const=True)
    document_operation_type: str
    document_id: str
    priority: Optional[OrchestrationPriority] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "document_operation_type": self.document_operation_type,
            "document_id": self.document_id,
            "priority": self.priority,
        }
        supero.update(o)
        return supero

class PerformGrading(BaseCommand):
    type: str = Field('perform_grading', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    document_operation_instance_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,            
            "document_id": self.document_id,
            "document_operation_instance_id": self.document_operation_instance_id,
        }
        supero.update(o)
        return supero

class CreateDefaultMedicationDocumentOperationDefinition(BaseCommand):#make it medication specific
    type: str = Field('create_default_document_operation_definition', const=True)
    app_id: str
    tenant_id: str
    name: str = 'medical-extraction'
    operation_type: str = DocumentOperationType.MEDICATION_EXTRACTION.value #medical-extraction|medical-coding|medical-annotation
    operation_name: str = DocumentOperationType.MEDICATION_EXTRACTION.value
    description: str = DocumentOperationType.MEDICATION_EXTRACTION.value
    document_workflow_id: str = "default"
    step_config: Dict[str, Dict[str, str | Dict ] | Any] = {
        DocumentOperationStep.TEXT_EXTRACTION.value:{
                "model":"gemini-1.5-flash-001",
                "prompt":"""
                            You are expert medical transcriber. 
                            Taking each page of the document attached, 
                            can you extract comprehensive details with all the text elements on the given page?
                            
                            Output expected:
                            Page: #X
                            Comprehensive Details:
                            **[section header]**
                                [section comprehensive details]
                            """,
                "description":"Extract text from the document",
            },
        DocumentOperationStep.CLASSIFICATION.value:{
                "model":"gemini-1.5-flash-001",
                "prompt":"", #ToDo: make it null
                "description":"Classify the document",
            },
        DocumentOperationStep.EVIDENCE_CREATION.value:{
                "model":"gemini-1.5-flash-001",
                "prompt":"""
                'Below is the table that contains tokens found on page along with their normalized AABB coordinates (x1, y1, x2, y2)',
                'These texts are spatially arranged as a set of rows with consistent structure across all content on the page. ',
                'Therefore, when mapping, take into account the spatial arrangement and output the bounding box coordinates that are located close together and not something from different row.',
                '```',
                <table></table>,
                '```',
                'We are looking for a sequence of those blocks that are located close to each other and show the following texts:',
                *<medications></medications>,
                'RULES:',
                '- For each requested text, provide all table entries that show this text.',
                '- For each requested text, print result as markdown table with 6 columns: text, x1, y1, x2, y2.',
                '- Markdown tables must be headerless - only data.',
                '- Each row should look as follows: "| text | x1 | y1 | x2 | y2|"',
                '- Do not include any header titles or other markdown formatting: only markdown tables.',
                '- Separate tables from each other with a triple dash ("---").',
                        """,
                "description":"Extract Medications from the document",
            },
        DocumentOperationStep.MEDICATIONS_EXTRACTION.value:{
                "model":"gemini-1.5-flash-001",
                "prompt":"""
                        Please study this context:\n\n<content></content>\n\n
                        please extract medications as array of JSON with keys as name, strength, dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions,explanation, document_reference and page_number. 
                        Please do not include any markup other than JSON.
                        Please format start_date and end_date as mm/dd/yyyy.
                        """,
                "description":"Extract Medications from the document",
            },
        DocumentOperationStep.MEDISPAN_MATCHING.value:{
                "model":"gemini-1.5-pro-001",
                "prompt": """
                        For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
                        1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match
                        2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
                        3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
                        4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
                        5) Otherwise, return "{}" and specific what attributes were not found

                        Only return the best match from the list. If no match is found, return "{}"

                        Only return the best match from the list. If no match is found, return "{}"

                        GIVEN MEDICATION:
                        {SEARCH_TERM}

                        MATCH LIST:
                        """,
                "description:":"Medispan matching step",
        },        
        DocumentOperationStep.NORMALIZE_MEDICATIONS.value:{
                "model":"gemini-1.5-flash-001",
                "prompt":"""
                        MEDICATION:
                        {search_term}
                        As an expert healthcare worker, given the provided MEDICATION, extract from this string elements of the medication including:
                        Name: Name of the medication
                        Route: The way the medication is introduced to the patient and consists of values like Oral, Topical, Subcutaneous, Intravenous, Injection, Rectal, etc.
                        Strength: The concentration of the medication expressed in weight or volume.  Examples include 100 MG, 300 MCG, 10 ML, 15 GM, 20 mEq, etc.
                        Form: The medication form.  Examples include Tablet, Capsule, Solution, Capsule Delayed Release, Enema, etc.
                        Dose: The amount of the medication to take.  This is the number or number range preceding the frequency.
                        Frequency: How frequently the patient should take the medication
                        Instructions: Any other data in the medication string not accounted by the other fields
                        
                        Here are examples of the medication string and how to parse into separate tokens:
                            Medication:  Dexmethylphenidate HCl Oral 5 MG Tablet 1 Daily at breakfast
                            Output:
                                Name: Dexmethylphenidate HCl
                                Route: Oral
                                Strength: 5 MG
                                Form: Tablet
                                Dose: 1
                                Frequency: Daily
                                Instructions: at breakfast
                        
                            Medication:  Methylphenidate Oral 10mg Tablet 1-2 Daily as needed
                            Output:
                                Name: Dexmethylphenidate HCl
                                Route: Oral
                                Strength: 10 MG
                                Form: Tablet
                                Dose: 1
                                Frequency: Daily
                                Instructions: at breakfast
                        
                            Medication:  Lansoprazole Oral Capsule Delayed Release 15 MG 2-3 daily NOT TO EXCEED 2 CAPSULES IN AN 8 HOUR PERIOD
                            Output:
                                Name: Lansoprazole
                                Route: Oral
                                Strength: 15 MG
                                Form: Capsule
                                Dose: 2-3
                                Frequency: Daily
                                Instructions: NOT TO EXCEED 2 CAPSULES IN AN 8 HOUR PERIOD
                        
                        Output the normalized medication in the following json format:
                        {
                            "name": "**Name",
                            "route": "**Route",
                            "strength": "**Strength",
                            "form": "**Form",
                            "dosage": "**Dose",
                            "frequency": "**Frequency",
                            "instructions": "**Instructions"
                        }
                                                """,
                "description":"Normalize medications (fine tuned extraction)",
            },
        DocumentOperationStep.ALLERGIES_EXTRACTION.value:{
            "model":"gemini-1.5-flash-001",
            "prompt":"""
                    Act as a intelligent healthcare extractor and Extract allergies information from <content></content> in separate JSON.
                    Extract Allergy profile for :
                    1. NKA (Food / Drug / Latex / Environmental)
                    2. Allergies and Sensitivities -Extract information on Substance and Reaction

                    Do not include any explanation in the reply. Only include the extracted information in the reply

                    The expcted JSON return type is as below:
                    [{
                        "reaction": "reaction1",
                        "substance": "substance1",
                    },
                    {
                        "reaction": "reaction2",
                        "substance": "substance2",
                    }
                    ]
                    """,
            "description":"Extract Allergies",
        },
        DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value:{
            "model":"gemini-1.5-flash-001",
            "prompt":"""
                    Act as a intelligent healthcare extractor and Extract Immunization information from <content></content> in separate JSON for below
                    1. Pneumonia
                    2. Flu
                    3. Tetanus
                    4. TB
                    5. TB Exposure
                    6. Hepatatis B

                    Below  Are the Rules:
                    1. Extract the Immunization details like Yes for taken and No for not taken/not known
                    2. Include the date of immunization (formated as mm/dd/yyyy)
                    3. In case of additional immunization which you don't see in above table add that under additional tab
                    4. Save original_extracted_string (shortened) string for each immunization. 

                    Do not include any explanation in the reply. Only include the extracted information in the reply
                    The expected JSON return type is as below (for example):
                    [{
                        "name": "Flu",
                        "status": "yes",
                        "date": "01/01/2022",
                        "orginal_extracted_string": ""
                    },
                    {
                        "name": "TB",
                        "status": "yes | no | unknown",
                        "date": "01/01/2022",
                        "original_extracted_string": ""
                    }
                    ]

                    """,
            "description":"Extract Immunizations",
        }
        }

class AutoCreateDocumentOperationDefinition(BaseCommand):
    type: str = Field('autocreate_document_operation_definition', const=True)
    document_operation_type: DocumentOperationType
    
class UpdateDocumentStatusSnapshot(AppBaseCommand):
    type: str = Field('update_document_status', const=True)
    document_id: str
    doc_operation_status_snapshot: DocumentOperationStatusSnapshot

class DocumentStateChange(AppBaseCommand):
    type: str = Field('document_state_change', const=True)
    document: Document
    operation_type: DocumentOperationType
    status: PageOperationStatus | DocumentOperationStatus

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "document_id": self.document.id,
            "source_id": self.document.source_id,
            "status": self.status.value
        }
        supero.update(o)
        return supero

class CreateOrUpdateDocumentOperation(AppBaseCommand):
    type: str = Field('create_document_operation', const=True)
    document_id:str
    operation_type: Optional[str] =  DocumentOperationType.MEDICATION_EXTRACTION.value # in future, this could be medical coding or other extraction types 
    active_document_operation_definition_id: Optional[str] = None
    active_document_operation_instance_id: Optional[str] = None
    status: Optional[DocumentOperationStatus]

class CreateDocumentOperationInstance(AppBaseCommand):
    type: str = Field('create_document_operation_instance', const=True)
    document_id: str
    document_operation_definition_id:str
    status: Optional[DocumentOperationStatus] = None
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "document_operation_definition_id": self.document_operation_definition_id,
            "priority": self.priority,
        }
        supero.update(o)
        return supero

class UpdateDocumentOperationInstance(AppBaseCommand):
    type: str = Field('update_document_operation_instance', const=True)
    id: str
    document_id: str    
    status: Optional[DocumentOperationStatus] = DocumentOperationStatus.NOT_STARTED

class CreateDocumentOperationInstanceLog(DocumentBaseCommand):
    type: str = Field('create_document_operation_instance_log', const=True)
    step_id: str
    status: DocumentOperationStatus
    description: str
    page_number: Optional[int] = -1
    context: Dict[str, Union[str, Dict, List, int, float]]

class DocumentSpawnRevision(BaseCommand):
    type: str = Field('document_spawn_revision', const=True)
    document: Document

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "original_document_id": self.document.id if self.document else None,
        }
        supero.update(o)
        return supero  

class ExecuteGenericPromptStep(DocumentBaseCommand):
    type: str = Field('execute_generic_prompt_step', const=True)
    operation_type: str
    operation_step: str
    doc_storage_uri: str
    context: Dict[str, str]
    prompt_document_execution_strategy: Optional[str] = "reference" # Remove post test as we should always prefer reference over embed    

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "operation_type": self.operation_type,
            "operation_step": self.operation_step,
            "doc_storage_uri": self.doc_storage_uri,
            "prompt_document_execution_strategy": self.prompt_document_execution_strategy,
        }
        supero.update(o)
        return supero

class ExecuteCustomPrompt(DocumentBaseCommand):
    type: str = Field('execute_prompt', const=True)
    prompt: str
    system_prompts: Optional[List[str]] = None
    doc_storage_uri: str
    model: str
    page_number: int  = -1 # -1 means applicable to all pages
    context: Dict[str, str]
    step_id: DocumentOperationStep = DocumentOperationStep.CUSTOM_STEP

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "doc_storage_uri": self.doc_storage_uri,
            "page_number": self.page_number,
            
        }
        supero.update(o)
        return supero

class AssembleTOC(DocumentBaseCommand):
    type: str = Field('assemble_toc', const=True)
    pageTOCs: List[PageTOC] = []       
    context: Dict[str, str] = {}
    step_id: DocumentOperationStep = DocumentOperationStep.TOC_ASSEMBLY

class LogPageProfileFilterState(AppBaseCommand, extra=Extra.forbid):
    type: str = Field('log_page_profile_state', const=True)
    # Keys are:
    # - DocumentId
    # - "profileType"
    # - ProfileType (e.g. medication)
    # - PageIndex
    state: Dict[str, Dict[str, Dict[str, Dict[str, DocumentPageFilterState]]]]
    user_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "user_id": self.user_id,
        }
        supero.update(o)
        return supero

class GetDocument(AppBaseCommand):
    type: str = Field('get_document', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,            
        }
        supero.update(o)
        return supero

class GetDocumentLogs(AppBaseCommand):
    type: str = Field('get_document_logs', const=True)    
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    filter: Optional[EntityFilter] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,            
        }
        supero.update(o)
        return supero


class CreateDocument(BaseCommand):
    class Config:
        # Allow arbitrary types (in our case - BinaryIO)
        arbitrary_types_allowed = True

    type: str = Field('create_document', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    file_name: str
    # File is a readable asyncio stream
    file: Any  # type: BinaryIO
    token:Optional[str] = None
    source_id: Optional[str] = None
    source_storage_uri:Optional[str] = None
    source_api: Optional[GenericExternalDocumentRepositoryApi] = None
    source:Optional[Literal['app','host', 'api']] = 'app'
    metadata: Optional[Dict[str, Any]] = None
    priority: Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "file_name": self.file_name,
            "source_id": self.source_id,
            "source_storage_uri": self.source_storage_uri,
            "source": self.source,
            "metadata": self.metadata,
            "priority": self.priority,           
        }
        supero.update(o)
        return supero

class ExternalCreateDocumentTask(CreateDocument):
    sha256: Optional[str]
    
    def toExtra(self):
        supero = super().toExtra()
        supero.update({
            "sha256": self.sha256,
        })
        return supero

class UpdateDocumentPriority(BaseCommand):
    type: str = Field('create_document', const=True)    
    document_id: str
    priority: OrchestrationPriority

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "document_id": self.document_id,
            "priority": self.priority,           
        }
        supero.update(o)
        return supero
    
class SplitPages(DocumentBaseCommand):
    type: str = Field('split_pages', const=True)
    step_id: DocumentOperationStep = DocumentOperationStep.SPLIT_PAGES
    

class CreatePage(DocumentBaseCommand):
    type: str = Field('create_page', const=True)
    storage_uri: str
    page_number: int
    step_id: DocumentOperationStep = DocumentOperationStep.CREATE_PAGE

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "storage_uri": self.storage_uri,
        }
        supero.update(o)
        return supero

class PerformOCR(DocumentBaseCommand):
    type: str = Field('perform_ocr', const=True)
    page_id: str
    step_id: DocumentOperationStep = DocumentOperationStep.PERFORM_OCR

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_id": self.page_id,
        }
        supero.update(o)
        return supero

class ExtractText(DocumentBaseCommand):
    type: str = Field('extract_text', const=True)
    page_id: str
    page_number: int
    pdf_parsing_strategy: PDFParsingStrategy = PDFParsingStrategy.MULTI_MODAL
    prompt: str
    model: str
    step_id: DocumentOperationStep = DocumentOperationStep.TEXT_EXTRACTION

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "page_id": self.page_id,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero
    
class ExtractTextAndClassify(DocumentBaseCommand):
    type: str = Field('extract_text_and_classify', const=True)
    page_id: str
    page_number: int
    pdf_parsing_strategy: PDFParsingStrategy = PDFParsingStrategy.MULTI_MODAL
    prompt: str
    model: str
    step_id: DocumentOperationStep = DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION
    
    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "page_id": self.page_id,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero


class ClassifyPage(DocumentBaseCommand):
    type: str = Field('classify', const=True)
    page_id: str
    page_text: str
    page_number: Optional[int] = -1
    model: str
    prompt:str
    step_id: DocumentOperationStep = DocumentOperationStep.CLASSIFICATION
    
    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "page_id": self.page_id,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero


class GetDocumentPDFURL(BaseCommand):
    type: str = Field('get_document_pdf_url', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
        }
        supero.update(o)
        return supero

class ExtractMedication(DocumentBaseCommand):
    type: str = Field('extract_medication', const=True)
    page_id: str
    page_number:int
    labelled_content: List[str]
    prompt:str
    model:str
    step_id: DocumentOperationStep = DocumentOperationStep.MEDICATIONS_EXTRACTION

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "page_id": self.page_id,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero

class ExtractConditions(DocumentBaseCommand):
    type: str = Field('extract_conditions', const=True)
    page_id: str
    page_number:int
    labelled_content: List[str]
    prompt:str
    model:str
    step_id: DocumentOperationStep = DocumentOperationStep.CONDITIONS_EXTRACTION

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "page_id": self.page_id,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero

class MedispanMatching(DocumentBaseCommand):
    type: str = Field('medispan_matching', const=True)
    extracted_medications:Optional[List[ExtractedMedication]] = None
    page_id: Optional[str] = None
    page_number: Optional[int] = None
    prompt: str
    model: Optional[str] = MULTIMODAL_MODEL
    step_id: DocumentOperationStep = DocumentOperationStep.MEDISPAN_MATCHING

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,
            "page_id": self.page_id,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero

class NormalizeMedications(DocumentBaseCommand):
    type: str = Field('normalize_medications', const=True)
    extracted_medications:Optional[List[ExtractedMedication]] = None
    prompt: str
    model: Optional[str] = MULTIMODAL_MODEL
    step_id: DocumentOperationStep = DocumentOperationStep.NORMALIZE_MEDICATIONS
    page_number: Optional[int] = -1

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_number": self.page_number,            
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero

class CreateorUpdateMedicationProfile(DocumentBaseCommand):
    type: str = Field('create_medication_profile', const=True)
    user_entered_medication:Optional[UserEnteredMedication] = None
    extracted_medications:Optional[List[ExtractedMedication]] = None
    step_id: DocumentOperationStep = DocumentOperationStep.MEDICATION_PROFILE_CREATION

    
class CreateEvidence(DocumentBaseCommand):
    type: str = Field('create_evidence', const=True)
    page_id: str
    page_number:int
    medications: List[str]
    document_operation_instance_id: str
    model:str
    prompt:str
    step_id: DocumentOperationStep = DocumentOperationStep.EVIDENCE_CREATION

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "page_id": self.page_id,
            "page_number": self.page_number,            
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero

class FindMedication(BaseCommand):
    app_id: str
    tenant_id: str
    type: str = Field('find_medication', const=True)
    term: str
    enable_llm: Optional[bool] = False
    max_results: Optional[int] = 100

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "term": self.term,
            "enable_llm": self.enable_llm,
            "max_results": self.max_results,
        }
        supero.update(o)
        return supero

class FindMedicationWithLLMFilter(BaseCommand):
    type: str = Field('find_medication_with_llm_filter', const=True)
    term: str
    enable_llm: Optional[bool] = False    

class CreateMedication(BaseCommand):
    type: str = Field('create_medication', const=True)

    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    # page_id: str
    values: dict

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
        }
        supero.update(o)
        return supero

class UpdateMedication(BaseCommand):
    type: str = Field('update_medication', const=True)
    medication_id: str
    values: dict

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "medication_id": self.medication_id,
        }
        supero.update(o)
        return supero

class DeleteMedication(BaseCommand):
    type: str = Field('delete_medication', const=True)
    medication_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "medication_id": self.medication_id,
        }
        supero.update(o)
        return supero

class UndeleteMedication(BaseCommand):
    type: str = Field('undelete_medication', const=True)
    medication_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "medication_id": self.medication_id,
        }
        supero.update(o)
        return supero

class CreateDocumentMedicationProfileCommand(BaseCommand):
    type: str = Field('create_document_medication_profile', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    page_id: str
    key: str
    values: dict
    user_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "page_id": self.page_id,
            "user_id": self.user_id,
        }
        supero.update(o)
        return supero

class DeleteDocumentMedicationProfileCommand(BaseCommand):
    type: str = Field('delete_document_medication_profile', const=True)
    key: str

class AddUserEnteredMedication(BaseCommand):
    type: str = Field('add_medication_profile', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    medication:MedicationValue
    medication_status:MedicationStatus
    extracted_medication_references:Optional[List[ExtractedMedicationReference]] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "medication": self.medication.dict() if self.medication else None,
        }
        supero.update(o)
        return supero

class UpdateUserEnteredMedication(BaseCommand):
    type: str = Field('add_medication_profile', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    medication_profile_reconcilled_medication_id: str
    medication:MedicationValue
    medication_status:MedicationStatus
    extracted_medication_references:Optional[List[ExtractedMedicationReference]] = None
    #changed_values: Optional[Dict[str,str | None]]

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "medication": self.medication.dict() if self.medication else None,
        }
        supero.update(o)
        return supero

class DeleteReconcilledMedication(BaseCommand):
    type: str = Field('delete_reconcilled_medication', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    medication_profile_reconcilled_medication_id: str
    
    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "medication_profile_reconcilled_medication_id": self.medication_profile_reconcilled_medication_id,            
        }
        supero.update(o)
        return supero

class UnDeleteReconcilledMedication(DeleteReconcilledMedication):
    type: str = Field('un_delete_reconcilled_medication', const=True)

class ImportMedications(BaseCommand):
    type: str = Field('import_medications', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    ehr_token: str

    def toExtra(self):
        supero = super().toExtra()
        o = {            
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,            
        }
        supero.update(o)
        return supero

class UpdateHostMedications(BaseCommand):
    type: str = Field('update_host_medications', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    ehr_token: str
    medication_dict: Dict
    profileFilter: Optional[DocumentFilterState] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
        }
        supero.update(o)
        return supero

class ImportHostAttachments(BaseCommand):
    type: str = Field('import_host_attachments', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    ehr_token: str
    api_token: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
        }
        supero.update(o)
        return supero
    
class ImportHostAttachmentFromExternalStorageUri(BaseCommand):
    type: str = Field('import_host_attachment_from_external_storage_uri', const=True)
    app_id: str
    external_storage_uri: str
    raw_event: Dict[str, str]
    source_id: Optional[str] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "external_storage_uri": self.external_storage_uri,
            "raw_event": self.raw_event,
        }
        supero.update(o)
        return supero

class ImportHostAttachmentFromExternalApi(BaseCommand):
    type: str = Field('import_host_attachment_from_external_api', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    source_id: Optional[str] = None
    file_name: str
    file_type: str
    created_on: str
    updated_on: Optional[str] = None
    sha256: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    active: Optional[bool] = True
    repository_type: ExternalDocumentRepositoryType = ExternalDocumentRepositoryType.API
    api: Optional[GenericExternalDocumentRepositoryApi] = None
    uri: Optional[GenericExternalDocumentRepositoryUri] = None
    raw_event: Union[GenericExternalDocumentCreateEventRequestApi, GenericExternalDocumentCreateEventRequestUri]

    @classmethod
    def from_request(cls, request: Union[GenericExternalDocumentCreateEventRequestApi, GenericExternalDocumentCreateEventRequestUri]):
        if isinstance(request, GenericExternalDocumentCreateEventRequestApi):
            return cls(
                app_id=request.appId,
                tenant_id=request.tenantId,
                patient_id=request.patientId,
                source_id=request.hostFileId,
                file_name=request.fileName,
                file_type=request.fileType,
                created_on=request.createdOn,
                updated_on=request.updatedOn,
                sha256=request.sha256,
                metadata=request.metadata,
                active=request.active,
                repository_type=ExternalDocumentRepositoryType.API,
                api=request.api,
                uri=None,
                raw_event=request
            )
        elif isinstance(request, GenericExternalDocumentCreateEventRequestUri):
            return cls(
                app_id=request.appId,
                tenant_id=request.tenantId,
                patient_id=request.patientId,
                source_id=request.hostFileId,
                file_name=request.fileName,
                file_type=request.fileType,
                created_on=request.createdOn,
                updated_on=request.updatedOn,
                sha256=request.sha256,
                metadata=request.metadata,
                active=request.active,
                repository_type=ExternalDocumentRepositoryType.URI,
                api=None,
                uri=request.uri,
                raw_event=request
            )
        else:
            raise ValueError(f"Unsupported request type: {type(request)}")

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "source_id": self.source_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "created_on": self.created_on,
            "updated_on": self.updated_on,
            "sha256": self.sha256,
            "metadata": self.metadata,
            "active": self.active,
            "repository_type": self.repository_type.value,
            "api": self.api.dict() if self.api else None,
            "uri": self.uri.dict() if self.uri else None,
            "raw_event": self.raw_event.dict() if self.raw_event else None,
        }
        supero.update(o)
        return supero

class ImportHostAttachmentFromExternalApiTask(ImportHostAttachmentFromExternalApi):
    type: str = Field('import_host_attachment_from_external_api_task', const=True)

    def to_action_command(self):
        o_dict = self.dict()
        o_dict.pop('id')
        o_dict.pop('type')
        return ImportHostAttachmentFromExternalApi(**o_dict)

    def toExtra(self):
        supero = super().toExtra()        
        return supero

class GetHostMedicationClassifications(BaseCommand):
    type: str = Field('get_host_medication_classifications', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    ehr_token: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,            
        }
        supero.update(o)
        return supero

class QueueE2ETest(BaseCommand):
    type: str = Field('queue_e2e_test', const=True)
    mode: Optional[str] = "sample"
    sample_size: Optional[int] = None
    filename: Optional[str] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "mode": self.mode,
            "sample_size": self.sample_size,
            "filename": self.filename
        }
        supero.update(o)
        return supero

class RunE2ETest(AppBaseCommand):
    type: str = Field('run_e2e_test', const=True)
    mode: Optional[str] = "sample"
    sample_size: Optional[int] = None
    filename: Optional[str] = None
    run_id: Optional[str] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "mode": self.mode,
            "sample_size": self.sample_size,
            "filename": self.filename,
            "run_id": self.run_id,
        }
        supero.update(o)
        return supero

class CreateE2ETestCaseSummaryResults(BaseCommand):
    type: str = Field('create_e2e_test_case_summary_results', const=True)
    summary_testcase_results: E2ETestCaseSummaryResults

class CreateTestCaseFromDocument(BaseCommand):
    type: str = Field('create_test_case_from_document', const=True)
    document_id: str

class AssessTestCaseResults(BaseCommand):
    type: str = Field('assess_test_case_results', const=True)
    mode: str
    run_id: str
    testcase_id: str    
    document: Document
    start_date: datetime
    is_assess_summary: Optional[bool] = True

class ReassessTestCaseSummaryResults(BaseCommand):
    type: str = Field('reassess_test_case_summary_results', const=True)
    run_id: str

class ReassessTestCaseSummaryResults(BaseCommand):
    type: str = Field('reassess_test_case_summary_results', const=True)
    run_id: str

class AssessTestCaseSummaryResults(BaseCommand):
    type: str = Field('assess_test_case_summary_results', const=True)
    run_id: str    

class ConfirmE2ETest(BaseCommand):
    type: str = Field('queue_e2e_test', const=True)
    document_id: str    

class LoadTestPoke(AppBaseCommand):
    type: str = Field('LoadTestPoke', const=True)
    loadtest_type: Optional[str] = "default"
    document_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "loadtest_type": self.loadtest_type,
            "document_id": self.document_id,
            "metadata": self.metadata
        }
        supero.update(o)
        return supero

class SaveTestResults(BaseCommand):
    type: str = Field('save_test_results', const=True)
    app_id: str
    tenant_id: str
    patient_id: str    
    test_results: TestResults

class CreateGoldenDatasetTest(BaseCommand):
    type: str = Field('create_golden_dataset_test', const=True)
    test_data: TestDataDetails    

class CreateClinicalData(AppBaseCommand):
    type: str = Field('create_clinical_data', const=True)
    document_id: str
    document_operation_instance_id: str
    page_id: str
    page_number: int
    clinical_data_type: str
    clinical_data: List[Dict]

class ExtractClinicalData(DocumentBaseCommand):
    type: str = Field('extract_clinical_data', const=True)
    clinical_data_type:str
    page_id: str
    page_number:int
    labelled_content: List[str]
    prompt:str
    model:str
    step_id: DocumentOperationStep = DocumentOperationStep.ALLERGIES_EXTRACTION

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "page_id": self.page_id,
            "page_number": self.page_number,
            "model": {
                "name": self.model,
            }
        }
        supero.update(o)
        return supero

class ExtractConditionsData(DocumentBaseCommand):
    type: str = Field('extract_conditions_data', const=True)
    page_texts: List[PageText]
    step_id: DocumentOperationStep = DocumentOperationStep.CONDITIONS_EXTRACTION
    
class CreateorUpdatePageOperation(DocumentBaseCommand):
    type: str = Field('create_page_operation', const=True)
    page_number: int
    page_id: str
    extraction_type: PageLabel
    extraction_status: PageOperationStatus
    
    def toExtra(self):
        supero = super().toExtra()
        o = {
            "page_id": self.page_id,
            "page_number": self.page_number,
            "extraction_type": self.extraction_type,
            "extraction_status": self.extraction_status,
        }
        supero.update(o)
        return supero
    
class CheckForAllPageOperationExtractionCompletion(DocumentBaseCommand):
    type: str = Field('page_operation_completed', const=True)
    
class CreateOrUpdateEntityRetryConfiguration(BaseCommand):
    type: str = Field('create_or_update_retry_configuration', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    document_operation_instance_id: str
    retry_entity_type: str
    retry_entity_id: str
    retry_count: int = 0 

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "document_operation_instance_id": self.document_operation_instance_id,            
        }
        supero.update(o)
        return supero


class CreateEntitySchema(BaseCommand):
    type: str = Field('create_entity_schema', const=True)
    entity_schema_dict: Dict[str, Any]

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "entity_schema_id": self.entity_schema_dict.get("id"),
            "entity_schema_title": self.entity_schema_dict.get("title"),
            "app_id": self.entity_schema_dict.get("app_id", "GLOBAL"),
        }
        supero.update(o)
        return supero


class DeleteEntitySchema(BaseCommand):
    type: str = Field('delete_entity_schema', const=True)
    schema_id: str

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "schema_id": self.schema_id,
        }
        supero.update(o)
        return supero


class ImportEntities(BaseCommand):
    type: str = Field('import_entities', const=True)
    entity_wrapper: Dict[str, Any]

    def toExtra(self):
        supero = super().toExtra()
        entities = self.entity_wrapper.get('entities', [])
        entity_count = len(entities) if isinstance(entities, list) else (1 if entities else 0)
        o = {
            "entity_count": entity_count,
            "has_entities": bool(entities),
        }
        supero.update(o)
        return supero


class CreateEntityTOC(BaseCommand):
    type: str = Field('create_entity_toc', const=True)
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    run_id: str
    entity_counts: Optional[Dict[str, int]] = None  # Document-level counts
    page_entity_counts: Optional[Dict[int, Dict[str, int]]] = None  # Page-level counts
    schema_uri_map: Optional[Dict[str, str]] = None  # Map entity type to schema URI

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "app_id": self.app_id,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "document_id": self.document_id,
            "run_id": self.run_id,
            "entity_counts": self.entity_counts,
            "page_entity_counts": self.page_entity_counts,
            "schema_uri_map": self.schema_uri_map,
        }
        supero.update(o)
        return supero


class ProcessOnboardingWizard(BaseCommand):
    class Config:
        # Allow arbitrary types (in our case - BinaryIO)
        arbitrary_types_allowed = True

    type: str = Field('process_onboarding_wizard', const=True)
    business_unit: str
    solution_id: str
    app_id: str
    entity_name: str
    entity_data_description: str
    extraction_prompt: str
    peak_docs_per_minute: float
    processing_time_sla_max: int
    pdf_file: Any  # type: BinaryIO

    def toExtra(self):
        supero = super().toExtra()
        o = {
            "business_unit": self.business_unit,
            "solution_id": self.solution_id,
            "app_id": self.app_id,
            "entity_name": self.entity_name,
            "entity_data_description": self.entity_data_description,
            "extraction_prompt": self.extraction_prompt,
            "peak_docs_per_minute": self.peak_docs_per_minute,
            "processing_time_sla_max": self.processing_time_sla_max,
        }
        supero.update(o)
        return supero


Command = Union[
    CreateNote,
    UpdateNote,
    SendEmail,
    GetStatus,
    GetDocument,
    CreateDocument,
    SplitPages,
    GetDocumentPDFURL,
    ExtractMedication,
    FindMedication,
    Orchestrate,
    CreateTestDocument,
    CreateEvidence,
    UpdateMedication,
    DeleteMedication,
    UndeleteMedication,    
    CreateDocumentMedicationProfileCommand,
    DeleteDocumentMedicationProfileCommand,
    LogPageProfileFilterState,
    ExecuteGenericPromptStep,
    CreateClinicalData,
    ExtractClinicalData,
    ExtractConditionsData,
    CreateorUpdatePageOperation,
    CheckForAllPageOperationExtractionCompletion,
    ImportHostAttachmentFromExternalStorageUri,
    ImportHostAttachmentFromExternalApi,
    ImportHostAttachmentFromExternalApiTask,
    QueueE2ETest,
    RunE2ETest,
    AssessTestCaseResults,
    AssessTestCaseSummaryResults,
    ReassessTestCaseSummaryResults,
    CreateE2ETestCaseSummaryResults,
    CreateOrUpdateEntityRetryConfiguration,
    CreateEntitySchema,
    DeleteEntitySchema,
    ImportEntities,
    CreateEntityTOC,
    ProcessOnboardingWizard,
    UpdateAppConfiguration,
    UpdateTenantConfiguration
]
