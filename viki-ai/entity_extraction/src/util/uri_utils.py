"""
Utility functions for generating URIs for documents and pages.
"""

from typing import Optional


class DocumentUriGenerator:
    """
    Utility class for generating Google Cloud Storage URIs for documents and pages.
    """
    
    BASE_URI = "gs://viki-ai-provisional-dev/paperglass/documents"
    
    @classmethod
    def generate_document_uri(
        cls,
        app_id: str,
        tenant_id: str,
        patient_id: str,
        document_id: str
    ) -> str:
        """
        Generate a document-level URI.
        
        Args:
            app_id: Application ID
            tenant_id: Tenant ID
            patient_id: Patient ID
            document_id: Document ID
            
        Returns:
            Document-level GS URI in format:
            gs://viki-ai-provisional-dev/paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/document.pdf
        """
        return f"{cls.BASE_URI}/{app_id}/{tenant_id}/{patient_id}/{document_id}/document.pdf"
    
    @classmethod
    def generate_page_uri(
        cls,
        app_id: str,
        tenant_id: str,
        patient_id: str,
        document_id: str,
        page_number: int
    ) -> str:
        """
        Generate a page-level URI.
        
        Args:
            app_id: Application ID
            tenant_id: Tenant ID
            patient_id: Patient ID
            document_id: Document ID
            page_number: Page number
            
        Returns:
            Page-level GS URI in format:
            gs://viki-ai-provisional-dev/paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/pages/{page_number}.pdf
        """
        return f"{cls.BASE_URI}/{app_id}/{tenant_id}/{patient_id}/{document_id}/pages/{page_number}.pdf"
    
    @classmethod
    def generate_subject_uri(
        cls,
        app_id: str,
        tenant_id: str,
        patient_id: str,
        document_id: str,
        page_number: Optional[int] = None
    ) -> str:
        """
        Generate a subject URI based on whether a page number is provided.
        
        Args:
            app_id: Application ID
            tenant_id: Tenant ID
            patient_id: Patient ID
            document_id: Document ID
            page_number: Optional page number. If provided, generates page-level URI, otherwise document-level URI.
            
        Returns:
            Document-level URI if page_number is None, otherwise page-level URI
        """
        if page_number is None:
            return cls.generate_document_uri(app_id, tenant_id, patient_id, document_id)
        else:
            return cls.generate_page_uri(app_id, tenant_id, patient_id, document_id, page_number)
