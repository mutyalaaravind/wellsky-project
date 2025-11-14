from copy import deepcopy
from datetime import datetime
from difflib import SequenceMatcher
from enum import Enum
import json
from typing import Any, Dict, List, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import DocumentOperation

import sys
import pydantic
from pydantic import BaseModel, Extra


from pydantic import BaseModel
from pydantic.types import List
from typing import Optional
from pydantic import BaseModel, Field

from paperglass.domain.service import extract_json
from paperglass.domain.time import now_utc
from paperglass.domain.string_utils import remove_multiple_spaces

from paperglass.settings import (
    MEDICATION_MATCHING_THRESHOLD,
    E2E_TEST_ASSERTION_ACCURACY_GOOD_UPPER,
    E2E_TEST_ASSERTION_ACCURACY_GOOD_LOWER,
    E2E_TEST_ASSERTION_RECALL_GOOD_UPPER,
    E2E_TEST_ASSERTION_RECALL_GOOD_LOWER,
    E2E_TEST_ASSERTION_F1_GOOD_UPPER,
    E2E_TEST_ASSERTION_F1_GOOD_LOWER,
)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

class Vector2(BaseModel):
    x: int
    y: int

    def __str__(self):
        return f"{self.x},{self.y}"


class Vector2Normalized(BaseModel):
    x: float
    y: float

    def __str__(self):
        return f"{self.x},{self.y}"


class Rect(BaseModel):
    tl: Vector2
    br: Vector2


class Page(BaseModel):
    # WARNING: Page numbers are 1-indexed!
    number: int
    mediabox: Rect
    storage_uri: str = None

class OCRType(str, Enum):
    raw="raw"
    line="line"
    token="token"
    paragraph="paragraph"
    block="block"

class DocumentOperationType(str,Enum):
    DEFAULT = "default"
    MEDICATION_EXTRACTION = "medication_extraction"
    TOC = "toc"
    MEDICATION_GRADER = "medication_grader"
    CONDITION_EXTRACTION = "conditions_extraction"
    ENTITY_EXTRACTION = "entity_extraction"

DOCUMENT_OPERATION_TYPES = [
    DocumentOperationType.MEDICATION_EXTRACTION,
    DocumentOperationType.TOC,
    DocumentOperationType.MEDICATION_GRADER,
    DocumentOperationType.CONDITION_EXTRACTION,
    DocumentOperationType.ENTITY_EXTRACTION
]

class DocumentOperationStatus(str,Enum):
    UNKNOWN = 'UNKNOWN'
    NOT_STARTED = 'NOT_STARTED'
    QUEUED = 'QUEUED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    
class PageOcrStatus(str,Enum):
    NOT_STARTED = 'NOT_STARTED'
    QUEUED = 'QUEUED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    

class PageOperationStatus(str,Enum):
    QUEUED = 'QUEUED'
    IN_PROGRESS = 'IN_PROGRESS'
    FAILED = 'FAILED'
    COMPLETED = 'COMPLETED'

class DocumentOperationStep(str,Enum):
    DOCUMENT_CREATED = 'DOCUMENT_CREATED'
    DOCUMENT_OPERATION_INSTANCE_CREATED = 'DOCUMENT_OPERATION_INSTANCE_CREATED'
    SPLIT_PAGES = 'SPLIT_PAGES'
    CREATE_PAGE = 'CREATE_PAGE'
    PERFORM_OCR = 'PERFORM_OCR'
    TEXT_EXTRACTION = 'TEXT_EXTRACTION'
    TEXT_EXTRACTION_AND_CLASSIFICATION = 'TEXT_EXTRACTION_AND_CLASSIFICATION'
    CLASSIFICATION = 'CLASSIFICATION'
    MEDICATIONS_EXTRACTION = 'MEDICATIONS_EXTRACTION'
    MEDISPAN_MATCHING = 'MEDISPAN_MATCHING'
    EVIDENCE_CREATION = 'EVIDENCE_CREATION'
    NORMALIZE_MEDICATIONS = 'NORMALIZE_MEDICATIONS'
    MEDICATION_PROFILE_CREATION = 'MEDICATION_PROFILE_CREATION'
    CUSTOM_STEP = 'CUSTOM_STEP',
    TOC_SECTION_EXTRACTION = 'TOC_SECTION_EXTRACTION',
    TOC_ASSEMBLY = 'TOC_ASSEMBLY'
    ALLERGIES_EXTRACTION = 'ALLERGIES_EXTRACTION'
    IMMUNIZATIONS_EXTRACTION = 'IMMUNIZATIONS_EXTRACTION'
    EXTRACTED_MEDICATION_GRADER = 'EXTRACTED_MEDICATION_GRADER'
    CONDITIONS_EXTRACTION = "CONDITIONS_EXTRACTION"
    PERFORM_GRADING = "PERFORM_GRADING"

class DocumentProgressState(BaseModel):
    name: str
    status: DocumentOperationStatus = DocumentOperationStatus.NOT_STARTED
    progress: Optional[float] = -1.0
    children: Optional[List['DocumentProgressState']] = []

    def calculate(self):
        # First, recursively calculate all children
        for child in self.children:
            child.calculate()
            
        if self.children:
            total_progress = 0.0
            children_with_determinable_progress = 0
            
            for child in self.children:
                if child.progress >= 0:
                    total_progress += child.progress
                    children_with_determinable_progress += 1
            
            # If no children have determinable progress, set parent progress to -1
            if children_with_determinable_progress == 0:
                self.progress = -1.0
            else:
                self.progress = total_progress / children_with_determinable_progress
            
            # Synthesize parent status based on children's statuses with precedence order:
            # FAILED > IN_PROGRESS > UNKNOWN > COMPLETED > QUEUED > NOT_STARTED
            status_precedence = {
                DocumentOperationStatus.NOT_STARTED: 1,
                DocumentOperationStatus.QUEUED: 2,
                DocumentOperationStatus.COMPLETED: 3,
                DocumentOperationStatus.UNKNOWN: 4,
                DocumentOperationStatus.IN_PROGRESS: 5,
                DocumentOperationStatus.FAILED: 6
            }
            
            # Find the highest precedence status among children
            highest_precedence = 0
            synthesized_status = DocumentOperationStatus.NOT_STARTED
            
            for child in self.children:
                child_precedence = status_precedence.get(child.status, 0)
                if child_precedence > highest_precedence:
                    highest_precedence = child_precedence
                    synthesized_status = child.status
            
            self.status = synthesized_status
        else:
            # Set progress based on status, unless it was explicitly set to -1.0 (indicating progress cannot be determined)
            if self.progress == -1.0:
                # Progress cannot be determined, leave as -1.0
                pass
            else:
                # Set progress based on status
                if self.status == DocumentOperationStatus.COMPLETED:
                    self.progress = 1.0
                elif self.status == DocumentOperationStatus.FAILED:
                    self.progress = 0.0
                elif self.status == DocumentOperationStatus.IN_PROGRESS:
                    # For in-progress items without children, we can't determine exact progress
                    # so we use a default of 0.5 (halfway)
                    self.progress = 0.5
                else:
                    self.progress = 0.0

class Schedule(str,Enum):
    OFFHOURS_1 = 'OFFHOURS_1'



class MedicationValidationRules(BaseModel):
    skipImportedValidation: bool = True
    validateMedispanId: bool = True
    validateClassification: bool = True
    validateStatusReason: bool = True
    validateDosage: bool = True
    validateName: bool = True
    validateDates: bool = True
    errorMessages: Dict[str, List[str]] = {
        "medispanId": ["Please either select unlisted or search and select medication."],
        "classification": ["Classification is missing."],
        "statusReason": ["Please fill/update the reason for none of the above status. If already filled, please ignore"],
        "dosage": ["Amount/Dose is missing."],
        "name": ["Medication name is missing."],
        "startDate": ["Start Date is missing."],
        "startDateWithEndDate": ["Start Date is required if End Date is provided"]
    }

    @classmethod
    def get_default_validation_rules(cls):
        return cls(
            skipImportedValidation=True,
            validateMedispanId=True,
            validateClassification=True,
            validateStatusReason=True,
            validateDosage=True,
            validateName=True,
            validateDates=True,
            errorMessages={
                "medispanId": ["Please either select unlisted or search and select medication."],
                "classification": ["Classification is missing."],
                "statusReason": ["Please fill/update the reason for none of the above status. If already filled, please ignore"],
                "dosage": ["Amount/Dose is missing."],
                "name": ["Medication name is missing."],
                "startDate": ["Start Date is missing."],
                "startDateWithEndDate": ["Start Date is required if End Date is provided"]
            }
        )

# class MedicationValue(BaseModel):
#     name:str
#     dosage:Optional[str]=None
#     route:Optional[str]=None

class MedispanStatus(str,Enum):
    MATCHED = 'MATCHED'
    UNMATCHED = 'UNMATCHED'
    PARTIAL_MATCH = 'PARTIAL_MATCH'
    NONE='NONE'
    ERRORED='ERRORED'


class Chunk(BaseModel):
    storage_uri: str
    index: int
    pages: List[Page]


class AnnotationType(str, Enum):
    LINE = "line"
    BLOCK = "block"
    TOKEN = "token"
    PARAGRAPH = "paragraph"
    CUSTOM = "manual"

# document.status.created
# document.page.status.created
# document.execution.split_pages.created
# document.page.execution.ocr.created
class DocumentStatusType(str, Enum):
    DOCUMENT_EXECUTION_STARTED = "document_execution_started"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_CREATION_FAILED = "document_failed"
    PAGES_SPLITTING_CREATED = "pages_splitting_created"
    PAGES_SPLITTING_COMPLETED = "pages_splitting_completed"
    PAGES_SPLITTING_FAILED = "pages_splitting_failed"
    PAGE_CREATION_COMPLETED = "page_creation_completed"
    PAGE_CREATION_FAILED = "page_creation_failed"
    PAGE_OCR_PERFORM_COMPLETED = "page_ocr_perform_completed"
    PAGE_OCR_PERFORM_FAILED = "page_ocr_perform_failed"
    TEXT_EXTRACTION_COMPLETED = "page_text_created"
    TEXT_EXTRACTION_FAILED = "page_text_failed"
    PAGE_CLASSIFICATION_COMPLETED = "page_classification_completed"
    PAGE_CLASSIFICATION_FAILED = "page_classification_failed"
    MEDICATIONS_EXTRACTION_COMPLETED = "medications_extraction_completed"
    MEDICATIONS_EXTRACTION_FAILED = "medications_extraction_failed"
    EVIDENCE_CREATION_COMPLETED = "evidence_creation_completed"
    EVIDENCE_CREATION_FAILED = "evidence_creation_failed"
    COMPLETED = "completed"
    FAILED = "failed"


from collections import namedtuple


class AnnotationToken(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    text: str
    index: Optional[int]
    orientation: Optional[str]


class Annotation(BaseModel):
    text_segment: str
    vertice1: Vector2
    vertice2: Vector2
    vertice3: Vector2
    vertice4: Vector2
    normalized_vertice1: Vector2Normalized
    normalized_vertice2: Vector2Normalized
    normalized_vertice3: Vector2Normalized
    normalized_vertice4: Vector2Normalized
    confidence: float
    orientation: str
    # detected_languages: List[Dict[str,any]]

    def value(self):
        return {
            "x": self.normalized_vertice1['x'],
            "y": self.normalized_vertice1['y'],
            "width": self.normalized_vertice2['x'] - self.normalized_vertice1['x'],
            "height": self.normalized_vertice3['y'] - self.normalized_vertice1['y'],
            "text": self.text_segment,
        }

    def token(self):
        return AnnotationToken(
            x1=min(
                self.normalized_vertice1.x,
                self.normalized_vertice2.x,
                self.normalized_vertice3.x,
                self.normalized_vertice4.x,
            ),
            y1=min(
                self.normalized_vertice1.y,
                self.normalized_vertice2.y,
                self.normalized_vertice3.y,
                self.normalized_vertice4.y,
            ),
            x2=max(
                self.normalized_vertice1.x,
                self.normalized_vertice2.x,
                self.normalized_vertice3.x,
                self.normalized_vertice4.x,
            ),
            y2=max(
                self.normalized_vertice1.y,
                self.normalized_vertice2.y,
                self.normalized_vertice3.y,
                self.normalized_vertice4.y,
            ),
            text=self.text_segment,
            orientation=self.orientation,
        )


class LineAnnotation(Annotation):
    type: AnnotationType = AnnotationType.LINE


class BlockAnnotation(Annotation):
    type: AnnotationType = AnnotationType.BLOCK


class TokenAnnotation(Annotation):
    type: AnnotationType = AnnotationType.TOKEN


class ParagraphAnnotation(Annotation):
    type: AnnotationType = AnnotationType.PARAGRAPH


class CustomAnnotation(Annotation):
    type: AnnotationType = AnnotationType.CUSTOM


## FHIR Value objects


def get_class(classname):
    v = sys.modules.get(f'domain.{classname.lower()}')
    cls = getattr(v, classname)
    return cls


class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(cls, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        # for base in bases:
        # annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class CustomBaseModel(BaseModel, metaclass=AllOptional):
    # common to all models
    id: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class HttpError(CustomBaseModel):
    reason: str
    status_code: int
    message: str


class Name(CustomBaseModel):
    family: str
    given: List[str]


class Coding(CustomBaseModel):
    code: str
    display: str
    system: str
    version: str


class CodeableConcept(CustomBaseModel):
    text: str
    coding: List[Coding]


class Identifier(CustomBaseModel):
    system: str
    value: str
    use: Optional[str]


class Quantity(CustomBaseModel):
    value: float
    unit: str
    system: str
    code: str


class Reference(BaseModel, metaclass=AllOptional):
    reference: str


class Period(CustomBaseModel):
    start: str
    end: str


class Author(CustomBaseModel):
    authorReference: Reference
    authorString: str


class AnnotationFhir(CustomBaseModel):
    time: str
    text: str
    author: Author


class CodeableReference(CustomBaseModel):
    reference: Reference
    concept: CodeableConcept


class Address(CustomBaseModel):
    use: str
    type: str
    text: str
    line: List[str]
    city: str
    district: str
    state: str
    postalCode: str
    country: str


class Telecom(CustomBaseModel):
    system: str
    value: str
    use: str


class Attachment(CustomBaseModel):
    contentType: str
    language: str
    data: str
    url: str
    size: int
    hash: str
    title: str
    creation: str


class Content(CustomBaseModel):
    attachment: Attachment


class Extension(CustomBaseModel):
    url: str
    valueString: str
    valueCoding: Coding


class StatusHistory(CustomBaseModel):
    status: str
    period: Period


class ClassHistory(CustomBaseModel):
    classCode: Optional["Coding"] = Field(None, alias="class")
    period: Period

    class Config:
        allow_population_by_field_name = True


class Participant(CustomBaseModel):
    type: List[CodeableConcept]
    period: Period
    individual: Reference


class EncounterDuration(CustomBaseModel):
    value: float
    currency: str


class Diagnosis(CustomBaseModel):
    condition: Reference
    use: CodeableConcept
    rank: int


class Hospitalization(CustomBaseModel):
    preAdmissionIdentifier: Identifier
    origin: Reference
    admitSource: CodeableConcept
    reAdmission: CodeableConcept
    dietPreference: List[CodeableConcept]
    specialCourtesy: List[CodeableConcept]
    specialArrangement: List[CodeableConcept]
    destination: Reference
    dischargeDisposition: CodeableConcept


class EncounterLocation(CustomBaseModel):
    location: Reference
    status: str
    physicalType: CodeableConcept
    period: Period


class Meta(BaseModel, metaclass=AllOptional):
    # include this field in all classes wherever we want to get lastUpdated date from FHIR resources
    lastUpdated: str


class EmbeddingChunkingStartegy(int, Enum):
    MULTI_MODAL = 0
    MARKDOWN_TEXT_SPLITTER = 1
    NLTK_TEXT_SPLITTER = 2


class Section(BaseModel):
    index: str
    name: str
    details: Optional[str]
    summary: Optional[str]
    question: Optional[str]
    embedding_chunk_strategy: Optional[EmbeddingChunkingStartegy]


class PromptStats(BaseModel):
    model: str
    max_output_tokens: int
    temperature: float
    top_p: float
    prompt_length: int
    prompt_tokens: int
    billing_total_tokens: Optional[int] = None
    billing_total_billable_characters: Optional[int] = None
    response_length: int
    response_tokens: int
    elapsed_time: float
    hasImage: Optional[bool] = False
    hasBinaryData: Optional[bool] = False


class PromptAuditLog(BaseModel):
    input_prompt: str
    output: str
    config: dict
    model: str
    safety_settings: dict
    error: str
    createdAt: str
    projectId: str
    location: str
    prompt_stats: Optional[PromptStats] = None
    metadata: Optional[Dict[str, Any]] = {}


class DocumentSearchResult(BaseModel):
    document_id: str
    doc_url: str
    snippets: str
    snippets_summary: Optional[str]
    distance: float
    embedding_chunk_strategy: Optional[int]


class PDFParsingStrategy(int, Enum):
    MULTI_MODAL = 0
    UNSTRUCTURED = 1


class EmbeddingStrategy(int, Enum):
    DOT_PRODUCT = 0
    COSINE = 1


class EmbeddingModal(int, Enum):
    TEXT_EMBEDDING = 0
    PUBMED_EMBEDDING = 1


class SearchQueryStrategy(str, Enum):
    BY_QUESTION = "question"
    BY_SUMMARY = "summary"
    BY_DETAILS = "details"


class NamedEntityExtractionType(str, Enum):
    MEDICATIONS = "medications"
    # DIAGNOSIS = "diagnosis"
    # SYMPTOMS = "symptoms"
    # PROCEDURES = "procedures"
    # LABS = "labs"
    # VITALS = "vitals"
    # ALLERGIES = "allergies"
    # IMMUNIZATIONS = "immunizations"
    # SOCIAL_HISTORY = "social_history"
    # FAMILY_HISTORY = "family_history"
    # MEDICAL_HISTORY = "medical_history"
    # SURGICAL_HISTORY = "surgical_history"
    # CURRENT_MEDICATIONS = "current_medications"
    # PAST_MEDICATIONS = "past_medications"
    # CURRENT_DIAGNOSIS = "current_diagnosis"
    # PAST_DIAGNOSIS = "past_diagnosis"
    # CURRENT_SYMPTOMS = "current_symptoms"
    # PAST_SYMPTOMS = "past_symptoms"
    # CURRENT_PROCEDURES = "current_procedures"
    # PAST_PROCEDURES = "past_procedures"
    # CURRENT_LABS = "current_labs"
    # PAST_LABS = "past_labs"
    # CURRENT_VITALS = "current_vitals"
    # PAST_VITALS = "past_vitals"
    # CURRENT_ALLERGIES = "current_allergies"
    # PAST_ALLERGIES = "past_allergies"
    # CURRENT_IMMUNIZATIONS = "current_immunizations"
    # PAST_IMMUNIZATIONS = "past_immunizations"
    # CURRENT_SOCIAL_HISTORY = "current_social_history"
    # PAST_SOCIAL_HISTORY = "past_social_history"
    # CURRENT_FAMILY_HISTORY = "current_family_history"
    # PAST_FAMILY_HISTORY = "past_family_history"
    # CURRENT_MEDICAL_HISTORY = "current_medical_history"
    # PAST_MEDICAL_HISTORY = "past_medical_history"
    # CURRENT_SURGICAL_HISTORY = "current_surgical_history"
    # PAST_SURGICAL_HISTORY = "past_surgical_history"
    # CURRENT_MEDICATIONS = "current_medications"
    # PAST_MEDICATIONS = "past_medications"
    # CURRENT_DIAGNOSIS = "current_diagnosis"
    # PAST_DIAGNOSIS = "past_diagnosis"
    # CURRENT_SYMPTOMS = "current_symptoms"
    # PAST_SYMPTOMS = "past_symptoms"
    # CURRENT_PROCEDURES = "current_procedures"


class NamedEntity(BaseModel):
    type: NamedEntityExtractionType
    extraction_input_prompt: str
    extraction_output: str

    def toJSON(self):
        result = []
        try:
            result.extend(json.loads(self.extraction_output))
        except Exception as e:
            balanced_json = extract_json(self.extraction_output)
            result.extend(balanced_json)
        return result



LANGUAGE_MODEL_LIST: List[str]=["text-bison-32k@002"]
MULTI_MODAL_LIST: List[str]=["gemini-1.5-flash-001","gemini-1.5-pro-preview-0409"]

class ModelType(int, Enum):
    LANGUAGE = 0
    MULTI_MODAL = 1

class LLMModel(BaseModel):
    model_type:ModelType = ModelType.LANGUAGE
    model: str = LANGUAGE_MODEL_LIST[0]

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_rule()

    def validate_rule(self):
        if self.model_type == ModelType.LANGUAGE:
            if self.model not in LANGUAGE_MODEL_LIST:
                raise ValueError(f"Model {self.model} not in {LANGUAGE_MODEL_LIST}")
        elif self.model_type == ModelType.MULTI_MODAL:
            if self.model not in MULTI_MODAL_LIST:
                raise ValueError(f"Model {self.model} not in {MULTI_MODAL_LIST}")

class DocumentSettings(BaseModel):
    patient_id: str
    page_text_extraction_model: LLMModel = LLMModel(model_type=ModelType.MULTI_MODAL,model=MULTI_MODAL_LIST[0])
    page_classification_model: LLMModel = LLMModel(model_type=ModelType.MULTI_MODAL,model=MULTI_MODAL_LIST[0])
    classification_based_retreival_model:LLMModel = LLMModel(model_type=ModelType.MULTI_MODAL,model=MULTI_MODAL_LIST[0])
    evidence_linking_model:LLMModel = LLMModel(model_type=ModelType.MULTI_MODAL,model=MULTI_MODAL_LIST[0])


class MedicationChange(BaseModel):
    class Meta:
        frozen = True

    # TODO: Keep track of the user who made the change?
    field: str
    old_value: Any | None
    new_value: Any


class MedicationChangeSet(BaseModel):
    class Meta:
        frozen = True

    changes: List[MedicationChange]
    created_at: datetime | None = Field(default_factory=now_utc)

class MedicationValue(BaseModel):
    name:str
    name_original:Optional[str]=None
    medispan_id: Optional[str]=None
    classification: Optional[str] = None
    dosage:Optional[str]=""
    strength:Optional[str]=""
    form:Optional[str]=""
    route:Optional[str]=""
    frequency: Optional[str]=""
    instructions: Optional[str]=""
    start_date: Optional[str]
    end_date: Optional[str]=None
    discontinued_date: Optional[str]
    is_long_standing: Optional[bool] = False
    is_nonstandard_dose: Optional[bool] = False
    catalogId: Optional[str]=None
    catalogType: Optional[str]=None

    def __init__(self, **data):
        super().__init__(**data)
        if self.catalogId is None:
            self.catalogId = self.medispan_id
        if self.start_date is None:
            self.start_date = data.get('startDate')
        if self.discontinued_date is None:
            self.discontinued_date = data.get('discontinueDate')
        # Only override if not already set by parent constructor
        if self.is_long_standing is None:
            self.is_long_standing = data.get('isLongStanding')
        if self.is_nonstandard_dose is None:
            self.is_nonstandard_dose = data.get('isNonStandardDose')
    @property
    def is_valid(self):
        return self.name and (self.dosage or self.strength or self.form or self.route or self.frequency or self.instructions or self.start_date or self.end_date or self.discontinued_date)

    @property
    def fully_qualified_name(self):
        value = f'{self.name} {self.strength or ""} {self.form or ""} {self.route or ""}'
        return remove_multiple_spaces(value)

    @property

    def to_string_with_instructions(self):
        value = f"{self.name or ''} {self.route or ''} {self.strength or ''} {self.form or ''} {self.dosage or ''} {self.frequency or ''} {self.instructions or ''}"
        return remove_multiple_spaces(value)

    @property
    def to_string(self):
        return f"{self.name} {self.route} {self.strength} {self.form} {self.dosage} {self.frequency} {self.instructions}"

    def matches(self,medication: 'MedicationValue'):
        if medication is None:
            return False

        if self.medispan_id:
            return self._listed_match(medication)
        else:
            return self._unlisted_match(medication)

    def match_ignore_medispanid(self,medication: 'MedicationValue'):
        if medication is None:
            return False

        return self._unlisted_match(medication)


    def match_score(self,medication: 'MedicationValue'):
        name_match_ratio = None
        dosage_match_ratio = None
        route_match_ratio = None
        form_match_ratio = None
        frequency_match_ratio = None
        instructions_match_ratio = None
        strength_match_ratio = None
        if self.name and medication.name:
            name_match_ratio = SequenceMatcher(None, self.name, medication.name).ratio()
        if self.dosage and medication.dosage:
            dosage_match_ratio = SequenceMatcher(None, self.dosage, medication.dosage).ratio()
        if self.route and medication.route:
            route_match_ratio = SequenceMatcher(None, self.route, medication.route).ratio()
        if self.form and medication.form:
            form_match_ratio = SequenceMatcher(None, self.form, medication.form).ratio()
        if self.strength and medication.strength:
            strength_match_ratio = SequenceMatcher(None, self.strength, medication.strength).ratio()
        # if self.frequency and medication.frequency:
        #     frequency_match_ratio = SequenceMatcher(None, self.frequency, medication.frequency).ratio()
        if self.instructions and medication.instructions:
            instructions_match_ratio = SequenceMatcher(None, self.instructions, medication.instructions).ratio()

        return name_match_ratio*3 + (strength_match_ratio if strength_match_ratio else 0) + (dosage_match_ratio if dosage_match_ratio else 0) + (route_match_ratio*2 if route_match_ratio else 0)  + (form_match_ratio if form_match_ratio else 0) + (instructions_match_ratio if instructions_match_ratio else 0)

    def diff(self, medication: 'MedicationValue')->MedicationChangeSet:
        change_list:List[MedicationChange] = []
        if self.name != medication.name:
            change_list.append(MedicationChange(field='name', old_value=self.name, new_value=medication.name))
        if medication.dosage and self.dosage != medication.dosage:
            change_list.append(MedicationChange(field='dosage', old_value=self.dosage, new_value=medication.dosage))
        if medication.route and self.route != medication.route:
            change_list.append(MedicationChange(field='route', old_value=self.route, new_value=medication.route))
        if medication.form and self.form != medication.form:
            change_list.append(MedicationChange(field='form', old_value=self.form, new_value=medication.form))
        if medication.start_date and self.start_date != medication.start_date:
            change_list.append(MedicationChange(field='start_date', old_value=self.start_date, new_value=medication.start_date))
        if medication.end_date and self.end_date != medication.end_date:
            change_list.append(MedicationChange(field='end_date', old_value=self.end_date, new_value=medication.end_date))
        if medication.discontinued_date and self.end_date != medication.discontinued_date:
            change_list.append(MedicationChange(field='discontinued_date', old_value=self.discontinued_date, new_value=medication.discontinued_date))
        if medication.strength and self.strength != medication.strength:
            change_list.append(MedicationChange(field='strength', old_value=self.strength, new_value=medication.strength))
        if medication.frequency and self.frequency != medication.frequency:
            change_list.append(MedicationChange(field='frequency', old_value=self.frequency, new_value=medication.frequency))
        if medication.instructions and self.instructions != medication.instructions:
            change_list.append(MedicationChange(field='instructions', old_value=self.instructions, new_value=medication.instructions))
        if medication.classification and self.classification != medication.classification:
            change_list.append(MedicationChange(field='classification', old_value=self.classification, new_value=medication.classification))
        return MedicationChangeSet(changes=change_list,created_at=now_utc())

    def _listed_match(self, medication:'MedicationValue'):
        return self.medispan_id == medication.medispan_id

    def _unlisted_match(self, medication:'MedicationValue'):
        import re
        self_medication_full_qualified_name = f'{self.name} {self.route if self.route else ""} {self.form if self.form else ""} {self.strength if self.strength and self.strength not in self.name else ""} {self.instructions if self.instructions and self.instructions not in ["None"] else ""} {self.classification if self.classification else ""}'
        medication_full_qualified_name = f'{medication.name}  {medication.route if medication.route else ""} {medication.form if medication.form else ""} {medication.strength if medication.strength and medication.strength not in medication.name else ""} {medication.instructions if medication.instructions and medication.instructions not in ["None"] else ""} {medication.classification if medication.classification else ""}'

        # match_ratio = SequenceMatcher(None,self_medication_full_qualified_name, medication_full_qualified_name).ratio()

        # LOGGER.debug("Matching ratio (%s) :: this: %s  test: %s", match_ratio, self_medication_full_qualified_name, medication_full_qualified_name)

        # return match_ratio > MEDICATION_MATCHING_THRESHOLD
        return re.sub(r'\s+', ' ', self_medication_full_qualified_name.lower()) == re.sub(r'\s+', ' ', medication_full_qualified_name.lower())

class ConditionValue(BaseModel):
    condition: str
    diagnosis_date: Optional[str] = None
    specific_details: Optional[str] = None

    @property
    def is_valid(self):
        return self.condition and (self.diagnosis_date or self.specific_details )

    @property
    def fully_qualified_name(self):
        value = f'{self.condition} {self.diagnosis_date or ""} {self.specific_details or ""}'
        return remove_multiple_spaces(value)

    @property

    def to_string_with_instructions(self):
        value = f"{self.condition or ''} {self.diagnosis_date or ''} {self.specific_details or ''}"
        return remove_multiple_spaces(value)

    @property
    def to_string(self):
        return f"{self.condition} {self.diagnosis_date} {self.specific_details}"



class MedispanStatus(str,Enum):
    MATCHED = 'MATCHED'
    UNMATCHED = 'UNMATCHED'
    PARTIAL_MATCH = 'PARTIAL_MATCH'
    NONE='NONE'
    ERRORED='ERRORED'

class MedispanMedicationValue(MedicationValue):
    medispan_id: str

class MedispanMatchMedicationLogEntry(BaseModel):
    search_term: str


class MedicationStatus(BaseModel):
    status: Optional[str] = None
    status_reason: Optional[str] = None
    status_reason_explaination: Optional[str] = None

class UserEnteredMedication(BaseModel):
    medication: MedicationValue
    medispan_id: Optional[str]
    edit_type: Literal['added', 'updated', 'deleted', 'imported'] # remove imported
    change_sets: MedicationChangeSet | List[MedicationChangeSet] | None
    medication_status:MedicationStatus
    modified_by: str
    modified_at: datetime = Field(default_factory=now_utc)
    start_date: Optional[str]
    end_date: Optional[str]
    document_id:str

class ExtractedMedicationReference(BaseModel):
    document_id:str
    extracted_medication_id:str
    document_operation_instance_id:str
    page_number:int

class HostMedication(BaseModel):
    patient_id:str
    host_medication_id:str
    medispan_id:str
    medication:MedicationValue
    order_date:Optional[str]
    start_date:Optional[str]
    end_date:Optional[str]
    discontinued_date:Optional[str]
    original_payload:Dict

class HostMedicationAddModel(BaseModel):
    modified_by:str
    medispan_id:Optional[str]
    medicationInstructions:Optional[str]
    medicationName:str
    dose: Optional[str]
    startDate:Optional[str]
    discontinueDate:Optional[str]
    is_long_standing: Optional[bool] = False
    is_nonstandard_dose: Optional[bool] = False

class HostFreeformMedicationAddModel(BaseModel):
    modified_by:str
    medispan_id:Optional[str]
    medicationInstructions:Optional[str]
    medicationName:str
    dose: str | None
    startDate:Optional[str]
    discontinueDate:Optional[str]
    classification_id: Optional[str]
    is_long_standing: Optional[bool] = False

class HostMedicationUpdateModel(BaseModel):
    host_medication_id:str
    modified_by:str
    medispan_id:Optional[str]
    medicationInstructions:Optional[str]
    medicationName:str
    dose: Optional[str]
    oldStartDate:Optional[str]
    newStartDate:Optional[str]
    oldDiscontinueDate:Optional[str]
    newDiscontinueDate:Optional[str]
    is_long_standing: Optional[bool] = False
    is_nonstandard_dose: Optional[bool] = False

class ImportedMedication(BaseModel):
    imported_medication_id:str
    host_medication_id:str
    medispan_id:str | None
    medication:MedicationValue
    modified_by: str
    modified_at: datetime = Field(default_factory=now_utc)

class HostMedicationSyncStatus(BaseModel):
    last_synced_at:datetime
    host_medication_unique_identifier:str

class Score(BaseModel):
    overall: Optional[float] = None
    details: Optional[Dict] = {}

class Origin(str,Enum):
    IMPORTED = 'imported'
    USER_ENTERED = 'user_entered'
    EXTRACTED = 'extracted'

class MedispanStrategy(str,Enum):
    VECTOR_SEARCH = 'vector-search'
    FIRE_STORE = 'firestore'
    MEDISPAN = 'medispan'
    MEDISPAN_CACHED = 'medispan-cached'

class FilterStrategy(str,Enum):
    LLM = 'llm'
    LOGIC = 'logic' # Older filter logic

class ConfigurationKey(str,Enum):
    MEDISPAN_LLM_FILTER = 'medispan-llm-filter'

class ResolvedReconcilledMedication(BaseModel):
    id: str
    origin: Origin = None
    medication:MedicationValue
    medispan_id: Optional[str]
    extracted_medication_reference: Optional[List[ExtractedMedicationReference]] = Field(default_factory=list)
    change_sets: MedicationChangeSet | List[MedicationChangeSet] | None
    medication_status:MedicationStatus | None #backward compatibility
    deleted:Optional[bool] = False
    unlisted: Optional[bool] = False
    host_linked:Optional[bool] = False
    modified_by: Optional[str] = None


class ReconcilledMedication(BaseModel):
    id: str
    origin: Optional[str] = None
    origin_evidence: Optional[ExtractedMedicationReference] = None #export and user edit operation of extracted medication results in updating of this field
    latest_start_date: Optional[str]
    latest_end_date: Optional[str]
    latest_discontinued_date: Optional[str]
    document_references: List[str] = Field(default_factory=list)
    medispan_id: Optional[str] # extracted medication stores medispan_id here
    medispan_status: MedispanStatus=MedispanStatus.NONE
    classification: Optional[str] = None # Later: remove from here since its part of medication VO
    medication:MedicationValue # extracted medication
    user_entered_medication:Optional[UserEnteredMedication]
    extracted_medication_reference: Optional[List[ExtractedMedicationReference]] = Field(default_factory=list) #new config will not save it
    imported_medication:Optional[ImportedMedication]
    host_medication_sync_status:Optional[HostMedicationSyncStatus]
    score: Optional[Score]
    deleted:Optional[bool] = False

    @property
    def resolved_medication(self) -> MedicationValue:
        # FUTURE: needs update when edit allowed after importing
        return self._resolved_imported_medication_vo or self._resolved_user_entered_medication_vo or self._resolved_extracted_medication_vo

    @property
    def resolved_medispan_id(self) -> MedicationValue:
        return self.resolved_medication.medispan_id

    @property
    def resolved_host_identifier(self):
        if self.imported_medication:
            return self.imported_medication.host_medication_id
        if self.host_medication_sync_status:
            return self.host_medication_sync_status.host_medication_unique_identifier

    @property
    def unlisted(self) -> bool:
        return False if self.resolved_medispan_id and self.resolved_medispan_id != "0" else True

    @property
    def host_linked(self) -> bool:
        return True if self.resolved_host_identifier else False

    @property
    def _resolved_imported_medication_vo(self) -> MedicationValue:
        if self.imported_medication:
            imported_medication:ImportedMedication = deepcopy(self.imported_medication)
            imported_medication.medication.medispan_id = imported_medication.medispan_id
            return imported_medication.medication
        elif self.host_medication_sync_status:
            return self._resolved_user_entered_medication_vo or self._resolved_extracted_medication_vo

    @property
    def _resolved_user_entered_medication_vo(self) -> MedicationValue:
        if self.user_entered_medication:
            user_entered_medication:UserEnteredMedication = deepcopy(self.user_entered_medication)
            user_entered_medication.medispan_id = user_entered_medication.medication.medispan_id
            return user_entered_medication.medication
        return None

    @property
    def _resolved_extracted_medication_vo(self) -> MedicationValue:
        if self.medication:
            extracted_medication_vo:MedicationValue = deepcopy(self.medication)
            extracted_medication_vo.medispan_id = self.medispan_id
            return extracted_medication_vo
        return None

    @property
    def resolved_origin(self) -> 'Origin':
        if self.imported_medication:
            return Origin.IMPORTED
        if self.user_entered_medication:
            return Origin.USER_ENTERED
        return Origin.EXTRACTED

    @property
    def is_valid(self) -> bool:
        return self.resolved_medication.is_valid


    def resolve_extraction_references(self, doc_operations:List['DocumentOperation']) -> List[ExtractedMedicationReference]:
        resolved_extracted_refs = []
        if self.extracted_medication_reference:
            for extracted_ref in self.extracted_medication_reference:
                extracted_ref:ExtractedMedicationReference = extracted_ref
                for doc_operation in doc_operations:
                    # Add null check to handle cases where doc_operation is None
                    # This can happen when documents have entity extraction but not medication extraction
                    if doc_operation is not None and \
                        doc_operation.active_document_operation_instance_id == extracted_ref.document_operation_instance_id and \
                        doc_operation.document_id == extracted_ref.document_id:
                        resolved_extracted_refs.append(extracted_ref)
        return resolved_extracted_refs

    def delete(self):
        self.deleted = True

    def un_delete(self):
        self.deleted = False

    def update_imported_medication(self, importedMedication:ImportedMedication):
        self.imported_medication = importedMedication

    def update_user_entered_medication(self, user_entered_medication:UserEnteredMedication):
        self.user_entered_medication = user_entered_medication

class OrchestrationPriority(str, Enum):
    DEFAULT="default"
    HIGH="high"
    NONE="none"
    QUARANTINE="quarantine"


class StepConfig(BaseModel):
    description: str

class StepConfigPrompt(StepConfig):
    model: str
    prompt: str
    prompt_system: Optional[str] = None

class Result(BaseModel):
    success: bool
    error_message: str | None = None
    return_data: Any | None = None

class HostAttachment(BaseModel):
    host_attachment_id:str
    storage_uri: str
    file_name: str
    active: bool = True

class HostAttachmentMetadata(BaseModel):
    host_attachment:HostAttachment
    patient_id: str
    tenant_id: str

class MedicationPageProfileItems(BaseModel):
        name: str

class MedicationPageProfile(BaseModel):
    page_profile_number: int
    has_items: bool
    number_of_items: int
    items: List[MedicationPageProfileItems]

class VectorSearchResponseItem(BaseModel):
    id: str
    distance: float
    data: Optional[dict]

class RuleAction(BaseModel):
    id: str
    params: Dict[str, Any]
    priority: int

class RuleExtra(BaseModel):
    actions: List[RuleAction]

class Rule(BaseModel):
    name: str
    conditions: Dict[str, Any]
    extra: Optional[RuleExtra] = None

class RuleSet(BaseModel):    
    key: str
    rules: List[Rule]
    default_actions: Optional[List[RuleAction]] = []

class OcrTriggerTouchPoint(BaseModel):
        bubble_click: Optional[bool] = False
        page_click: Optional[bool] = False
        evidence_link_click: Optional[bool] = False
        
class IntegrationCallbackConfiguration(BaseModel):
    enabled: bool = False
    endpoint: Optional[str] = None
    status_callback: Optional[str] = None
    embed_entities_enabled: bool = False
    cloudtask_enabled: bool = True
    headers: dict[str, str] = {}

class IntegrationConfiguration(BaseModel):
    base_url: str
    endpoints: dict[str, str] = {}
    callback: Optional[IntegrationCallbackConfiguration] = None

class Configuration(BaseModel):
    integration: Optional[IntegrationConfiguration] = None

    class Accounting(BaseModel):
        business_unit: Optional[str] = None
        solution_code: Optional[str] = None

    class Extraction(BaseModel):
        class Retry(BaseModel):
            offhours_retry_enabled: bool = False
        retry: Retry = Retry()
    
    class TokenValidationConfig(BaseModel):
        enabled: Optional[bool] = False
        jwks_url: Optional[str] = None

    class OnDemandOcrConfig(BaseModel):
        enabled: Optional[bool] = False
        disable_orchestration_processing: Optional[bool] = False
        processing_mode_async: Optional[bool] = False
        touch_points: Optional[OcrTriggerTouchPoint] = None
    
    class RetryConfig(BaseModel):
        max_retries: int = 5
        enabled: bool = False

    class ExternalFilesConfig(BaseModel):
        enabled:Optional[bool] = False
        uploaded_date_cut_off_window_in_days:Optional[int] = 0

    class ExposureRules:
        exposed_to_ui = ["extract_immunizations",
                         "extract_allergies",
                         "extract_conditions",
                         "extraction_persisted_to_medication_profile",
                         "use_pagination",
                         "ui_control_upload_enable",
                         "ui_nonstandard_dose_enable",
                         "ui_classification_enable",
                         "on_demand_external_files_config",
                         "ui_hide_medication_tab",
                         "ui_document_action_extract_enable",
                         "ui_document_action_extract_statuses",
                         "ui_document_action_upsert_goldendataset_test_enable",
                         "ui_host_linked_delete_enable",
                         "ui_longstanding_enable",
                         "use_async_document_status",
                         "use_client_side_filtering",
                         "orchestration_engine_version",
                         "ocr_trigger_config",
                         "validation_rules"]  
 
        
    class MedispanMatchConfig(BaseModel):
        class RerankSettings(BaseModel):
            enabled: Optional[bool] = False
            rerank_strength_enabled: Optional[bool] = False
            rerank_form_enabled: Optional[bool] = False
            strength_ranking_eligible_forms: Optional[List[str]] = ["tablet", "capsule", "powder"]
            similarity_threshold: Optional[float] = 0.7
        
        class MedispanMatchV2Settings(BaseModel):
            similarity_threshold: Optional[float] = 0.7
            total_results: Optional[int] = 5
            rerank_settings: Optional['Configuration.MedispanMatchConfig.RerankSettings'] = None
        
        v2_enabled_tenants: Optional[List[str]] = None
        v2_enabled_globally: Optional[bool] = False
        v2_repo: Optional[Literal["alloydb", "firestore", "alloydb-wcircuitbreaker"]] = "alloydb"
        catalog: Optional[Literal["medispan", "merative"]] = "medispan"
        v2_settings: Optional[MedispanMatchV2Settings] = None

    # Used 
    class MedicationExtractionConfig(BaseModel):
        enabled: Optional[bool] = False
        version: Optional[str] = "v4"
        parallel_test_enabled: Optional[bool] = False  # Used to enable parallel processing in tests (e.g. for testing model or prompt changes in parallel)

        @classmethod
        def get_default(cls):
            default_config = cls(
                enabled=False,
                version="v4",
                parallel_test_enabled=False
            )
            return default_config
    class EntityExtractionConfig(BaseModel):

        enabled: Optional[bool] = False
        version: Optional[str] = "1"
        pipeline_default: Optional[str] = "default.start"


        @classmethod
        def get_default(cls):
            default_config = cls(
                enabled=False,
                version="1",
                pipeline_default="default.start"
            )
            return default_config

    # Used by Frontend
    accounting: Optional[Accounting] = None
    extract_immunizations: bool = False
    extract_allergies: bool = False
    extract_conditions: Optional[bool] = False
    extraction_persisted_to_medication_profile: bool = False    
    use_pagination:Optional[bool] = True
    token_validation: Optional[TokenValidationConfig] = TokenValidationConfig()
    ui_control_upload_enable: Optional[bool] = False
    ui_nonstandard_dose_enable: Optional[bool] = False
    ui_classification_enable: Optional[bool] = True
    on_demand_external_files_config: Optional[ExternalFilesConfig] = None
    ui_hide_medication_tab: Optional[bool] = False
    ui_document_action_extract_enable: Optional[bool] = False
    ui_document_action_extract_statuses: Optional[List[str]] = ["QUEUED","IN_PROGRESS","NOT_STARTED","FAILED"]
    ui_document_action_upsert_goldendataset_test_enable: Optional[bool] = False
    ui_host_linked_delete_enable: Optional[bool] = False
    ui_longstanding_enable: Optional[bool] = True
    use_async_document_status: Optional[bool] = True
    use_client_side_filtering: Optional[bool] = False
    orchestration_engine_version:Optional[str] = "v3"
    ocr_trigger_config: Optional[OnDemandOcrConfig] = None
    validation_rules: Optional[MedicationValidationRules] = MedicationValidationRules.get_default_validation_rules()

    # Used by backend
    use_v3_orchestration_engine: Optional[bool] = True
    tenant_allow_list:Optional[List[str]] = None
    tenant_allow_list_check_enabled: Optional[bool] = True
    quarantine_enabled: Optional[bool] = False
    use_ordered_events: Optional[bool] = False
    retry_config: Optional[RetryConfig] = None
    use_extract_and_classify_strategy: Optional[bool] = False
    enable_ocr: Optional[bool] = True
    orchestration_confirm_evidence_linking_enabled: Optional[bool] = False
    medispan_matching_version: Optional[str] = "2"
    evidence_weak_matching_enabled: Optional[bool] = False
    evidence_weak_matching_firsttoken_enabled: Optional[bool] = False
    evidence_weak_matching_cleansing_regex: Optional[List[str]] = ["^\\d+\\.\\s*"]        
    enable_v4_orchestration_engine_parallel_processing: Optional[bool] = False
    medispan_match_config: Optional[MedispanMatchConfig] = None
    meddb_catalog: Optional[Literal["medispan", "merative"]] = "medispan" # This is deprecated, in future we will use medispan_match_config.catalog instead
    licenses: Optional[List[str]] = ["pipeline.medication"]
    medication_extraction: Optional[MedicationExtractionConfig] = MedicationExtractionConfig.get_default()
    entity_extraction: Optional[EntityExtractionConfig] = EntityExtractionConfig.get_default()
    
    rulesets: Optional[Dict[str, RuleSet]] = None
    extraction: Extraction = Extraction()


    def get_ui_settings(self):
        field_list = self.ExposureRules.exposed_to_ui
        config_dict = self.dict()
        o = {}
        for field in field_list:
            o[field] = config_dict[field]
        return o

    # Tells pydantic to ignore any extra fields that are not defined in the model
    class Config:
        extra = Extra.ignore


class ConfigurationTest(BaseModel):
    id:str
    name:Optional[str]
    active: Optional[bool] = False
    test_type:str
    test_conditions: Optional[Dict[str,Any]] = None
    input_data:Optional[Dict[str,Any]] = None

class ClinicalData(BaseModel):
    type: str
    data: List[Dict]

class ExtractedClinicalDataReference(BaseModel):
    document_id: str
    document_operation_instance_id: str
    page_number: int
    extracted_clinical_data_id: str

class PageText(BaseModel):
    pageNumber: int
    text: Optional[str] = ""


class ConditionsEvidence(BaseModel):
    end_position: int
    evidence_reference: str
    evidence_snippet: str
    start_position: int
    document_id: str
    page_number: int

class ConditionICD10Code(BaseModel):
    category: str
    description: Optional[str]
    icd_code: str


class ChangedEntity(BaseModel):
    is_new: bool
    is_dirty: bool
    is_removed:bool
    value: object

class ChangeTracker(BaseModel):

    entities: List[ChangedEntity] = []
    commands: List = []
    name: Optional[str] = "no_name"

    def register_new(self, value: object):
        changed_entity = ChangedEntity(is_new=True, is_dirty=False, is_removed=False, value=value)
        self.entities.append(changed_entity)

    def register_dirty(self,  value: object):
        changed_entity = ChangedEntity(is_new=False, is_dirty=True, is_removed=False, value=value)
        self.entities.append(changed_entity)

    def register_removed(self,  value: object):
        changed_entity = ChangedEntity(is_new=False, is_dirty=False, is_removed=True, value=value)
        self.entities.append(changed_entity)

    def create_command(self, value: object):
        self.commands.append(value)


class DocumentStatusResponse(BaseModel):
    """
    Response model for document status API endpoint.
    Contains all the relevant information about a document's status.
    """
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    host_attachment_id: str
    status: 'DocumentProgressState'  # Strongly typed status using DocumentProgressState
    metadata: Optional[Dict[str, Any]] = None  # Document metadata


class AccuracyAssessment(BaseModel):

    accurate_items: List[Any] = []
    not_accurate_items: List[Any] = []
    recalled_items: List[Any] = []
    not_recalled_items: List[Any] = []

    subelement_accuracy_assessments: List['AccuracyAssessment'] = []

    def calc_accuracy(self):
        total_items = len(self.accurate_items) + len(self.not_accurate_items)
        if total_items == 0:
            return 0
        return len(self.accurate_items) / total_items
    
    def calc_recall(self):
        total_items = len(self.recalled_items) + len(self.not_recalled_items)
        if total_items == 0:
            return 0
        return len(self.recalled_items) / total_items
    
    def calc_f1(self):
        accuracy = self.calc_accuracy()
        recall = self.calc_recall()
        if accuracy + recall == 0:
            return 0
        return 2 * (accuracy * recall) / (accuracy + recall)
    
    def get_summary(self):
        return {
            "is_pass": self.is_pass,
            "accuracy": self.calc_accuracy(),
            "recall": self.calc_recall(),
            "f1": self.calc_f1()
        }
    
    @property
    def is_pass(self):
        is_fail = False
        if self.calc_accuracy() < E2E_TEST_ASSERTION_ACCURACY_GOOD_LOWER or self.calc_accuracy() > E2E_TEST_ASSERTION_ACCURACY_GOOD_UPPER:
            is_fail = True
        if self.calc_recall() < E2E_TEST_ASSERTION_RECALL_GOOD_LOWER or self.calc_recall() > E2E_TEST_ASSERTION_RECALL_GOOD_UPPER:
            is_fail = True
        if self.calc_f1() < E2E_TEST_ASSERTION_F1_GOOD_LOWER or self.calc_f1() > E2E_TEST_ASSERTION_F1_GOOD_UPPER:
            is_fail = True
            
        return not is_fail

    def add(self, item: 'AccuracyAssessment'):
        self.subelement_accuracy_assessments.append(item)

        self.accurate_items.extend(item.accurate_items)
        self.not_accurate_items.extend(item.not_accurate_items)
        self.recalled_items.extend(item.recalled_items)
        self.not_recalled_items.extend(item.not_recalled_items)

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d["summary"] = self.get_summary()
        return d

Configuration.MedispanMatchConfig.RerankSettings.update_forward_refs()
Configuration.MedispanMatchConfig.MedispanMatchV2Settings.update_forward_refs()
Configuration.MedispanMatchConfig.update_forward_refs()
Configuration.update_forward_refs()
