"""
Entity Table of Contents (TOC) models for tracking entity extraction counts.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid1
from pydantic import BaseModel, Field

from .models import Aggregate


class EntityTOCEntry(BaseModel):
    """
    Represents a single TOC entry for entity extraction counts.
    Contains: app_id, tenant_id, patient_id, document_id, run_id, category:str, count:int, page_number:int, schema_uri:str
    """
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    run_id: str  # aka document_operation_instance_id
    category: str  # entity category/type
    count: int
    page_number: Optional[int] = None  # Page number where entities were found, None for document-level counts
    schema_uri: Optional[str] = None  # URI reference to the entity schema used for this category


class DocumentEntityTOC(Aggregate):
    """
    Document-level aggregate for entity extraction TOC entries.
    This is stored as a subcollection under document records.
    """
    id: str = Field(default_factory=lambda: str(uuid1()))
    document_id: str
    run_id: str  # aka document_operation_instance_id
    entries: List[EntityTOCEntry] = Field(default_factory=list)
    
    @classmethod
    def create(cls, 
               app_id: str,
               tenant_id: str,
               patient_id: str,
               document_id: str,
               run_id: str,
               entity_counts: Dict[str, int],
               schema_uri_map: Optional[Dict[str, str]] = None) -> 'DocumentEntityTOC':
        """
        Create a DocumentEntityTOC from entity counts.
        
        Args:
            app_id: Application ID
            tenant_id: Tenant ID  
            patient_id: Patient ID
            document_id: Document ID
            run_id: Run ID (document_operation_instance_id)
            entity_counts: Dictionary mapping entity category to count
            schema_uri_map: Optional dictionary mapping entity category to schema URI
            
        Returns:
            DocumentEntityTOC instance
        """
        entries = []
        for category, count in entity_counts.items():
            schema_uri = schema_uri_map.get(category) if schema_uri_map else None
            entry = EntityTOCEntry(
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id,
                document_id=document_id,
                run_id=run_id,
                category=category,
                count=count,
                page_number=None,  # Document-level counts
                schema_uri=schema_uri
            )
            entries.append(entry)
        
        return cls(
            id=uuid1().hex,
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            run_id=run_id,
            entries=entries
        )

    @classmethod
    def create_with_page_counts(cls, 
                               app_id: str,
                               tenant_id: str,
                               patient_id: str,
                               document_id: str,
                               run_id: str,
                               page_entity_counts: Dict[int, Dict[str, int]],
                               schema_uri_map: Optional[Dict[str, str]] = None) -> 'DocumentEntityTOC':
        """
        Create a DocumentEntityTOC from page-level entity counts.
        
        Args:
            app_id: Application ID
            tenant_id: Tenant ID  
            patient_id: Patient ID
            document_id: Document ID
            run_id: Run ID (document_operation_instance_id)
            page_entity_counts: Dictionary mapping page number to entity counts by category
                               e.g., {1: {"medication": 5, "condition": 2}, 2: {"medication": 3}}
            schema_uri_map: Optional dictionary mapping entity category to schema URI
            
        Returns:
            DocumentEntityTOC instance
        """
        entries = []
        for page_number, entity_counts in page_entity_counts.items():
            for category, count in entity_counts.items():
                schema_uri = schema_uri_map.get(category) if schema_uri_map else None
                entry = EntityTOCEntry(
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    document_id=document_id,
                    run_id=run_id,
                    category=category,
                    count=count,
                    page_number=page_number,
                    schema_uri=schema_uri
                )
                entries.append(entry)
        
        return cls(
            id=uuid1().hex,
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            run_id=run_id,
            entries=entries
        )
    
    def get_collection_name(self) -> str:
        """
        Return the Firestore collection name for this aggregate.
        This will be a subcollection under the document.
        """
        return f"documents/{self.document_id}/entity_toc"
    
    def add_entry(self, category: str, count: int, page_number: Optional[int] = None, schema_uri: Optional[str] = None) -> None:
        """Add a new TOC entry."""
        entry = EntityTOCEntry(
            app_id=self.app_id,
            tenant_id=self.tenant_id,
            patient_id=self.patient_id,
            document_id=self.document_id,
            run_id=self.run_id,
            category=category,
            count=count,
            page_number=page_number,
            schema_uri=schema_uri
        )
        self.entries.append(entry)
    
    def add_page_entry(self, page_number: int, category: str, count: int, schema_uri: Optional[str] = None) -> None:
        """Add a new page-level TOC entry."""
        self.add_entry(category, count, page_number, schema_uri)
    
    def update_entry(self, category: str, count: int, page_number: Optional[int] = None) -> None:
        """Update an existing TOC entry or create if it doesn't exist."""
        for entry in self.entries:
            if entry.category == category and entry.page_number == page_number:
                entry.count = count
                return
        # If not found, add new entry
        self.add_entry(category, count, page_number)
    
    def get_entry_by_category(self, category: str, page_number: Optional[int] = None) -> Optional[EntityTOCEntry]:
        """Get TOC entry by category and optionally by page number."""
        for entry in self.entries:
            if entry.category == category and entry.page_number == page_number:
                return entry
        return None
    
    def get_entries_by_page(self, page_number: int) -> List[EntityTOCEntry]:
        """Get all TOC entries for a specific page."""
        return [entry for entry in self.entries if entry.page_number == page_number]
    
    def get_document_level_entries(self) -> List[EntityTOCEntry]:
        """Get all document-level TOC entries (where page_number is None)."""
        return [entry for entry in self.entries if entry.page_number is None]
    
    def get_total_count_by_category(self, category: str) -> int:
        """Get total count for a category across all pages."""
        return sum(entry.count for entry in self.entries if entry.category == category)
    
    def get_page_summary(self) -> Dict[int, Dict[str, int]]:
        """Get a summary of entity counts by page and category."""
        page_summary = {}
        for entry in self.entries:
            if entry.page_number is not None:
                if entry.page_number not in page_summary:
                    page_summary[entry.page_number] = {}
                page_summary[entry.page_number][entry.category] = entry.count
        return page_summary
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "run_id": self.run_id,
            "entries": [entry.dict() for entry in self.entries],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
