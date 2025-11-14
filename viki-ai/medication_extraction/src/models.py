from datetime import datetime
from difflib import SequenceMatcher
from enum import Enum
import re
from typing import Any, List, Optional, Literal
from uuid import uuid1
from utils.date import now_utc
from pydantic import BaseModel,Field

class OrchestrationPriority(str, Enum):
    DEFAULT="default"
    HIGH="high"
    NONE="none"
    QUARANTINE="quarantine"

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
        rerank_settings: Optional['MedispanMatchConfig.RerankSettings'] = None
    
    v2_enabled_tenants: Optional[List[str]] = None
    v2_enabled_globally: Optional[bool] = False
    v2_repo: Optional[Literal["alloydb", "firestore", "alloydb-wcircuitbreaker"]] = "firestore"
    catalog: Optional[Literal["medispan", "merative"]] = "medispan"
    v2_settings: Optional[MedispanMatchV2Settings] = None
    
class Document(BaseModel):
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    storage_uri: str
    priority:Optional[OrchestrationPriority] = OrchestrationPriority.DEFAULT
    created_at: datetime
    medispan_adapter_settings: Optional[MedispanMatchConfig] = None
    # created_by: str
    # modified_at: str
    # modified_by: str
    
class Page(BaseModel):
    storage_uri: str
    page_number: int
    total_pages: int
    run_id: str
    
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
    start_date: Optional[str]=None
    end_date: Optional[str]=None
    discontinued_date: Optional[str]=None
    is_long_standing: Optional[bool] = False
    is_nonstandard_dose: Optional[bool] = False
    
    def remove_multiple_spaces(self,input_string: str) -> str:
        # Use a regular expression to replace multiple spaces with a single space
        result = re.sub(r'\s+', ' ', input_string)
        return result

    @property
    def is_valid(self):
        return self.name and (self.dosage or self.strength or self.form or self.route or self.frequency or self.instructions or self.start_date or self.end_date or self.discontinued_date)

    @property
    def fully_qualified_name(self):
        value = f'{self.name} {self.strength or ""} {self.form or ""} {self.route or ""}'
        return self.remove_multiple_spaces(value)

    @property

    def to_string_with_instructions(self):
        value = f"{self.name or ''} {self.route or ''} {self.strength or ''} {self.form or ''} {self.dosage or ''} {self.frequency or ''} {self.instructions or ''}"
        return self.remove_multiple_spaces(value)

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

class MedispanStatus(str,Enum):
    MATCHED = 'MATCHED'
    UNMATCHED = 'UNMATCHED'
    PARTIAL_MATCH = 'PARTIAL_MATCH'
    NONE='NONE'
    ERRORED='ERRORED'

class ExtractedMedication(BaseModel):
    id: str
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    page_id: str
    route: Optional[str] = ""
    reason: Optional[str] = ""
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
    document_operation_instance_id: Optional[str] = None
    
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
                                medispan_id = self.medispan_id
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
 
class MedispanMedicationValue(MedicationValue):
    medispan_id: str
    
class MedispanDrug(BaseModel):
    id: Optional[str]
    NameDescription: str
    GenericName: str
    Route: Optional[str]
    Strength: Optional[str]
    StrengthUnitOfMeasure: Optional[str] = None
    Dosage_Form: str
    Aliases: Optional[List[str]] = []

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

class OperationMeta(BaseModel):
    type: str
    step: str
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    iteration: Optional[int] = 0
    
class DocumentOperationStep(str,Enum):
    RUN_STARTED = 'RUN_STARTED'
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
    STATUS_UPDATE = "STATUS_UPDATE"

MedispanMatchConfig.RerankSettings.model_rebuild()
MedispanMatchConfig.MedispanMatchV2Settings.model_rebuild()
MedispanMatchConfig.model_rebuild()
