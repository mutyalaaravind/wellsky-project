from copy import deepcopy
from typing import Dict, List, Optional
from uuid import uuid4
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

from paperglass.settings import FIRESTORE_EMULATOR_HOST, GCP_FIRESTORE_DB
from paperglass.domain.models import ExtractedMedication
from paperglass.domain.time import now_utc
from paperglass.domain.util_json import DateTimeEncoder

from paperglass.log import CustomLogger

LOGGER = CustomLogger(__name__)

class MedicationsRepository:
    def __init__(self,db_name = GCP_FIRESTORE_DB):
        if not FIRESTORE_EMULATOR_HOST:
            self.db = firestore.AsyncClient(database=db_name)
        else:
            self.db = firestore.AsyncClient()
        self.collection = "paperglass_doc_medications"
        self.runs_collection = "runs"
        self.medications_collection = "medications"


    def get_medications(self, document_id:str, run_id: str) -> List[Dict]:
        """Retrieves all medications for a specific run."""
        medications_ref = self.db.collection(self.collection).document(document_id)\
            .collection(self.medications_collection)
        #medications = medications_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        medications = medications_ref.where("document_operation_instance_id", "==", run_id)
        return [ExtractedMedication(**medication.to_dict()) for medication in medications]
        return [{'id': medication.id, **medication.to_dict()} for medication in medications]
    
    async def list_medications(self, document_id:str, page_number: int) -> List[ExtractedMedication]:
        """Retrieves all medications for a given document and page"""
        document_ref = self.db.collection(self.collection).document(document_id)
        medications_ref = document_ref.collection(self.medications_collection)
        medications = await medications_ref.where(filter=FieldFilter("page_number", "==", page_number))\
                                           .where(filter=FieldFilter("document_operation_instance_id", "==", "latest"))\
                                           .get()

        results = [ExtractedMedication(**medication.to_dict()) for medication in medications]

        return results
    
    async def get_latest_doc_operation_instance_id(self, document_id:str):
        doc_operation_instance_id = None
        extracted_medications = await self.db.collection_group(self.medications_collection) \
            .where("document_id","==",document_id) \
            .where("document_operation_instance_id", "==", "latest").get()
        if extracted_medications:
            extracted_medication_sample = await self.db.collection(self.collection).document(document_id)\
                .collection(self.medications_collection).document(ExtractedMedication(**extracted_medications[0].to_dict()).id).get()
            if extracted_medication_sample.exists:
                doc_operation_instance_id = ExtractedMedication(**extracted_medication_sample.to_dict()).document_operation_instance_id
        return doc_operation_instance_id
    
    async def get_medications_by_document_ids(self, document_ids:List[str], run_id: str) -> List[Dict]:
        medications = await self.db.collection_group(self.medications_collection) \
            .where("document_id", "in", document_ids) \
            .where("document_operation_instance_id", "==", run_id).get()
        
        extracted_medications = [ExtractedMedication(**medication.to_dict()) for medication in medications]
        return extracted_medications

    async def get_medication(self, document_id: str, medication_id: str) -> Optional[Dict]:
        """Retrieves a specific medication by its ID."""
        medication_ref = self.db.collection(self.collection).document(document_id)\
            .collection(self.medications_collection).document(medication_id)
        medication = await medication_ref.get()
        return ExtractedMedication(**medication.to_dict()) if medication.exists else None

    async def batch_create_medications(self, document_id: str, page_number:int,run_id: str, medications_data: List[ExtractedMedication]) -> List[str]:
        """Creates multiple medications in a batch operation."""
        batch = self.db.batch()
        delete_batch = self.db.batch()
        document_ref = self.db.collection(self.collection).document(document_id)
        medications_ref = document_ref.collection(self.medications_collection)
        medication_refs = []
        
        existing_latest_meds = await medications_ref.where("document_operation_instance_id", "==", "latest")\
                                .where("page_number", "==", page_number).get()
        
        for med in existing_latest_meds:
            batch.delete(med.reference)
            
        #await delete_batch.commit()
        
        doc = await document_ref.get()
        
        if doc.exists:
            page_number_mapping = doc.to_dict().get("page_medicatons_count", {})
        else:
            page_number_mapping = {}
            
        total_medications = len([ med for med in medications_data if med.page_number == page_number])
        
        page_number_mapping[str(page_number)] = total_medications
        
        now = now_utc()
        now_str = now.isoformat()

        batch.set(document_ref, {'document_id': document_id, "page_medicatons_count":page_number_mapping, "created_at": now_str})
        
        
        for data in medications_data:
            new_ref = medications_ref.document(data.id)
            # data['created_at'] = datetime.utcnow()
            batch.set(new_ref, data.dict())
            medication_refs.append(new_ref)
            
        latest_medications_data = deepcopy(medications_data)
        
        for data in latest_medications_data:
            new_ref = medications_ref.document(f"{data.id}-latest")
            data.document_operation_instance_id = "latest"
            # data['created_at'] = datetime.utcnow()
            batch.set(new_ref, data.dict())
            medication_refs.append(new_ref)

        await batch.commit()
        return [ref.id for ref in medication_refs]
