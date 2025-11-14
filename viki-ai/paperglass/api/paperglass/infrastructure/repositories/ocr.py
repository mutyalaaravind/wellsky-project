from copy import deepcopy
from typing import Dict, List, Optional
from uuid import uuid4
from google.cloud import firestore
from datetime import datetime

from paperglass.domain.values import PageOcrStatus
from paperglass.settings import FIRESTORE_EMULATOR_HOST, GCP_FIRESTORE_DB
from paperglass.domain.models import ExtractedMedication, Page

class PageOCRRepository:
    def __init__(self,db_name = GCP_FIRESTORE_DB):
        if not FIRESTORE_EMULATOR_HOST:
            self.db = firestore.AsyncClient(database=db_name)
        else:
            self.db = firestore.AsyncClient()
        self.collection = "paperglass_doc_ocr"
        self.ocr_collection = "page_ocr"
        

    async def get_ocr_status(self, document_id: str, page_number: int) -> PageOcrStatus:
        doc_page_ocr = self.db.collection(self.collection).document(document_id).collection(self.ocr_collection).document(str(page_number))
        doc_page_ocr = await doc_page_ocr.get()
        if doc_page_ocr.exists:
            return PageOcrStatus(doc_page_ocr.get("status"))
        else:
            return PageOcrStatus.NOT_STARTED

    async def create_or_update_ocr_status(self, 
                                          document_id: str, 
                                          page_number: int, 
                                          storage_uri:str, 
                                          status: PageOcrStatus):
        doc_page_ocr = self.db.collection(self.collection).document(document_id).collection(self.ocr_collection).document(str(page_number))
        doc_page_ocr = await doc_page_ocr.get()
        
        if doc_page_ocr.exists:
            doc_page_ocr = self.db.collection(self.collection).document(document_id).collection(self.ocr_collection).document(str(page_number))
            await doc_page_ocr.update({"status": status.value, "updated_at": datetime.utcnow()})
        else:
            doc_page_ocr = self.db.collection(self.collection).document(document_id).collection(self.ocr_collection).document(str(page_number))
            await doc_page_ocr.set({
                "storage_uri": storage_uri,
                "document_id": document_id,
                "page_number": page_number,
                "status": status,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
