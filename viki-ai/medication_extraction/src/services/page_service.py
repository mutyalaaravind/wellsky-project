import json
import re
import traceback
from typing import List
from uuid import uuid4

from settings import (
    STEP_CLASSIFY_LLM_MODEL,
    STEP_EXTRACTMEDICATION_LLM_MODEL,
)

from adapters.llm import StandardPromptAdapter
from adapters.storage import StorageAdapter
from adapters.doc_ai import DocumentAIAdapter
from services.medispan_service import MedispanMatchService
from settings import GCS_BUCKET_NAME
from models import Document, ExtractedMedication, MedicationValue, MedispanStatus, Page
import settings
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from prompts import PromptTemplates
from utils.custom_logger import getLogger

LOGGER = getLogger(__name__)


class PageService:
    def __init__(self, document:Document, page:Page, medication_extraction_model=None, medispan_model=None):
        self.document = document
        self.page = page
        self.storage = StorageAdapter()
        self.medication_extraction_model = medication_extraction_model
        self.medispan_model = medispan_model


    @staticmethod
    def classify_prompt():
        return PromptTemplates.CLASSIFY
    
    @staticmethod
    def classify_model():
        LOGGER.debug("Classify Model: %s", STEP_CLASSIFY_LLM_MODEL)
        return STEP_CLASSIFY_LLM_MODEL
    
    @staticmethod
    def extract_medications_prompt():
        return PromptTemplates.EXTRACT_MEDICATIONS
            
    def extract_medications_model(self):
        LOGGER.debug("Extract Medications Model: %s", self.medication_extraction_model or STEP_EXTRACTMEDICATION_LLM_MODEL)
        return self.medication_extraction_model or STEP_EXTRACTMEDICATION_LLM_MODEL

    async def classify(self):
        prompts = [self.classify_prompt(), (self.page.storage_uri, "application/pdf")]

        metadata = self.document.dict()
        metadata.update({
            "step": "CLASSIFICATION",
            "page_number": self.page.page_number,
            "iteration": 0,
            "run_id": self.page.run_id
        })
        
        result = await StandardPromptAdapter().multi_modal_predict_2(
                                                        items=prompts, 
                                                        model=PageService.classify_model(),
                                                        #response_mime_type = "application/text",
                                                        metadata=metadata)
        base_path = await self.storage.get_base_path(self.document)
        await self.storage.write_text(GCS_BUCKET_NAME, 
                               f"{base_path}/classified_text/{self.page.run_id}/{self.page.page_number}.txt", result)
        
        return result
        
    async def does_medication_exist(self, classified_result:str):
        if classified_result:
            medications_match = re.search(r'<MEDICATIONS>(.*?)</MEDICATIONS>', classified_result, re.DOTALL)
            medications = medications_match.group(1) if medications_match else None
            conditions_match = re.search(r'<CONDITIONS>(.*?)</CONDITIONS>', classified_result, re.DOTALL)
            conditions = conditions_match.group(1) if conditions_match else None
            LOGGER.warning(f"Medications: {medications}")
            return True if medications else False
        return False
    
    async def get_config(self, app_id: str):
        # Initialize Firestore client
        db = firestore.Client(
            project=settings.GCP_PROJECT_ID,
            database=settings.GCP_FIRESTORE_DB
        )
        
        # Query the paperglass_app_config collection
        config_ref = db.collection('paperglass_app_config')
        query = config_ref.where(filter=FieldFilter('app_id', '==', app_id)).limit(1)
        docs = query.stream()
        
        # Get the first matching document
        config = None
        for doc in docs:
            config = doc.to_dict()
            break
        
        if config:                
            return config
        else:
            print(f"No configuration found for app_id: {app_id}")
            return None
    
    async def medication(self):

        metadata = self.document.model_dump()
        config = await self.get_config(self.document.app_id)
        
        # Base metadata without config-dependent fields
        metadata_update = {
            "step": "MEDICATIONS_EXTRACTION",
            "page_number": self.page.page_number,
            "iteration": 0,
            "run_id": self.page.run_id,
            "domain_id": "extract-medication",
        }
        
        # Add config-dependent fields if config exists
        if config and config.get("config") and config.get("config").get("accounting"):
            accounting = config.get("config").get("accounting")
            metadata_update.update({
                "business_unit": accounting.get("business_unit", "unknown"),
                "solution_id": accounting.get("solution_id", "unknown")
            })
            
        metadata.update(metadata_update)

        prompts = [(self.page.storage_uri, "application/pdf"),PageService.extract_medications_prompt()]
        result = await StandardPromptAdapter().multi_modal_predict_2(prompts,model=self.extract_medications_model(), metadata=metadata)
        extracted_medications:List[ExtractedMedication] = []
        
        result = StandardPromptAdapter.extract_json_from_response(result)
        LOGGER.warning(f"Medications: {result}")
        
        if result:
            
            for medication in result:
                if medication.get("name"):
                    extracted_medication_value = MedicationValue(
                                                                name=medication.get("name"),
                                                                strength=str(medication.get("strength")) if medication.get("strength") else medication.get("strength"),
                                                                dosage=str(medication.get("dosage")) if medication.get("dosage") else medication.get("dosage"),
                                                                route=medication.get("route"),
                                                                frequency=str(medication.get("frequency")) if medication.get("frequency") else medication.get("frequency"),
                                                                instructions=medication.get("instructions") or medication.get("frequency"), # HHH maps frequency to instrutions
                                                                form = medication.get("form"),
                                                                start_date=medication.get("start_date"),
                                                                end_date=medication.get("end_date"),
                                                                discontinued_date=medication.get("discontinued_date"),
                                                            )
                    extracted_medication = ExtractedMedication(
                        id = uuid4().hex,
                        app_id=self.document.app_id, 
                        tenant_id=self.document.tenant_id,
                        patient_id=self.document.patient_id,
                        document_id=self.document.document_id,
                        page_id=str(self.page.page_number),
                        medication=extracted_medication_value,
                        explaination=medication.get("explanation") or medication.get("explaination"),
                        document_reference=self.document.document_id,
                        page_number=self.page.page_number,
                        medispan_medication=None,
                        medispan_id=None,
                        medispan_status=MedispanStatus.NONE,
                        score=None,
                        document_operation_instance_id=self.page.run_id
                    )
                    extracted_medications.append(extracted_medication)
                else:
                    LOGGER.warning(f"Invalid Medication: {medication}")
        
        base_path = await self.storage.get_base_path(self.document)
        await self.storage.write_text(GCS_BUCKET_NAME, 
                               f"{base_path}/extracted_medications/{self.page.run_id}/{self.page.page_number}.json", 
                               json.dumps([x.model_dump() for x in extracted_medications]),
                               content_type="application/json")
        return extracted_medications
    
    
    async def medispan_match(self):
        base_path = await self.storage.get_base_path(self.document)
        extracted_medications = await self.storage.read_text(GCS_BUCKET_NAME, f"{base_path}/extracted_medications/{self.page.run_id}/{self.page.page_number}.json")
        medispan_matched_medications = []
        try:
            extracted_medications = json.loads(extracted_medications)
            extracted_medications = [ExtractedMedication(**med) for med in extracted_medications]
            medispan_service = MedispanMatchService(
                self.document.tenant_id,
                self.document.medispan_adapter_settings,
                self.medispan_model
            )
            medispan_matched_medications,medispan_matched_drugs = await medispan_service.run(
                self.document.app_id,
                self.document.tenant_id,
                self.document.patient_id,
                self.document.document_id,                
                self.page.page_number,
                self.page.run_id,
                extracted_medications
            )
            await self.storage.write_text(GCS_BUCKET_NAME, 
                            f"{base_path}/medispan_matched/{self.page.run_id}/{self.page.page_number}.json", 
                            json.dumps([x.model_dump() for x in medispan_matched_medications]),
                            content_type="application/json")
            
        except Exception as e:
            LOGGER.error(f"Failed to match medications: {str(traceback.format_exc())}")
            raise e
        # do medispan matching
        
        return medispan_matched_medications,medispan_matched_drugs
    
    async def get_medication_storage_uri(self):
        base_path = await self.storage.get_base_path(self.document)
        return f"gs://{GCS_BUCKET_NAME}/{base_path}/extracted_medications/{self.page.run_id}/{self.page.page_number}.json"
    
    async def get_medispan_matched_storage_uri(self):
        base_path = await self.storage.get_base_path(self.document)
        return f"gs://{GCS_BUCKET_NAME}/{base_path}/medispan_matched/{self.page.run_id}/{self.page.page_number}.json"
    
    async def perform_ocr(self):
        ocr_raw  = await DocumentAIAdapter().process_document(self.page.storage_uri)
        results = json.dumps(ocr_raw[0]).encode('utf-8')
        base_path = await self.storage.get_base_path(self.document)
        #base_path = base_path.replace("medication_extraction","paperglass")
        ocr_storage_uri = await self.storage.write_text(GCS_BUCKET_NAME, 
                                                        f"{base_path}/ocr/{self.page.page_number}/raw.json", 
                                                        results, 
                                                        content_type="application/json")
        return ocr_storage_uri