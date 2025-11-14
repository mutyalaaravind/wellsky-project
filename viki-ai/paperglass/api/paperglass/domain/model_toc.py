from datetime import datetime, timezone
from difflib import SequenceMatcher
from enum import Enum
import json
from typing import Dict, List, Literal, Optional, Union
from uuid import uuid1

from pydantic import BaseModel, Extra, Field

from .models import Aggregate, PageModel, CustomPromptResult

class ProfileType(Enum):
    MEDICATION = "medication"

class ProfileItem(BaseModel):
    name: str

class PageTOC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid1()))
    document_id: str
    page_number: int
    page: PageModel
    toc: CustomPromptResult
    
class PageTOCMedication(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    route: Optional[str] = None
    form: Optional[str] = None

class PageTOCSection(BaseModel):
    name: str    
    meds: List[PageTOCMedication]

class PageTOCDocument(BaseModel):
    name: Optional[str] = None
    documentType: Optional[str] = None
    internalPageNumber: Optional[str]
    internalPageCount: Optional[str]
    sections: List[PageTOCSection] = []

class PageTOCContainer(BaseModel):
    doc: PageTOCDocument

class PageTOCProfile(BaseModel):
    type: ProfileType = ProfileType.MEDICATION
    hasItems: bool = False
    numberOfItems: int = 0
    items: List[ProfileItem] = []

class DocumentTOCSectionMedication(PageTOCMedication):
    pageNumber: int

class TOCPageRange(BaseModel):
    start: int
    end: int

class DocumentTOCSection(BaseModel):
    name: str    
    meds: List[DocumentTOCSectionMedication] = []
    pageRange: TOCPageRange

class DocumentTOCEmbeddedDocument(BaseModel):
    name: Optional[str] = None
    documentType: Optional[str] = None
    pageRange: TOCPageRange
    sections: List[DocumentTOCSection] = []


class DocumentPageProfileFilter(BaseModel):
    pages: Optional[List[int]] = [] # If None or empty list, all pages are included  If items in the list, then filter will only show items (medications) on pages that are on this list.  Page will be 1 based.

class DocumentItemFilter(BaseModel):    
    profileFilter: Dict[ProfileType, DocumentPageProfileFilter]
    

class DocumentTOC(Aggregate):
    id: str = Field(default_factory=lambda: str(uuid1()))   
    document_id: str 
    page_count: Optional[int] = 0
    documents: List[DocumentTOCEmbeddedDocument] = []
    pageProfiles: Optional[Dict[str, List[PageTOCProfile]]] = {}  # Key is page number, value is list of PageTOCProfile

    @classmethod
    def create(cls, app_id:str,
                tenant_id:str,
                patient_id:str, 
                document_id: str,
                document_operation_instance_id:str,
                documents: List[DocumentTOCEmbeddedDocument],
                page_count: Optional[int] = 0,
                pageProfiles: Optional[Dict[str, PageTOCProfile]] = {}
                ) -> 'DocumentTOC':
        id = uuid1().hex
        return cls(id=id, 
                   app_id=app_id,
                   tenant_id=tenant_id,
                    patient_id=patient_id, 
                    document_id=document_id,                     
                    document_operation_instance_id=document_operation_instance_id,
                    documents = documents,
                    page_count = page_count,
                    pageProfiles = pageProfiles
                   )
    
    
    execution_id: Optional[str] = None
    document_operation_instance_id: Optional[str] = None

    events: List = Field(default_factory=list)

"""
E.g.:
{
    "b4ad3bda254911ef9f853e3297f4bd06": {
        "profileFilter": {
            "medication": {
                0: {
                    pageIndex: 0,
                    isSelected: true
                },
                1: {
                    pageIndex: 1,
                    isSelected: false
                }
            }
        }
    }
}
"""
class DocumentPageFilterState(BaseModel):
    pageIndex: int
    isSelected: bool

class DocumentProfileFilter(BaseModel):
    profileFilter: Dict[ProfileType, Dict[str, Dict[str, DocumentPageFilterState]]]

class DocumentFilterState(Aggregate):
    id: str = Field(default_factory=lambda: str(uuid1()))    
    state: Dict[str, Dict[str, Dict[str, Dict[str, DocumentPageFilterState]]]]

    @classmethod
    def create(cls, app_id:str, 
               tenant_id:str, 
               patient_id:str, 
               state: any,
               created_by: Optional[str] = None,
               ) -> 'DocumentFilterState':
        id = uuid1().hex
        return cls(id=id, 
                app_id=app_id, 
                tenant_id=tenant_id, 
                patient_id=patient_id, 
                state=state,
                created_by=created_by
                )
