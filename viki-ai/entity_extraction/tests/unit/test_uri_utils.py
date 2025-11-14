"""
Unit tests for URI utility functions.
"""

import unittest
from src.util.uri_utils import DocumentUriGenerator


class TestDocumentUriGenerator(unittest.TestCase):
    """Test cases for DocumentUriGenerator class."""

    def test_generate_document_uri(self):
        """Test document URI generation."""
        result = DocumentUriGenerator.generate_document_uri(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc"
        )
        
        expected = "gs://viki-ai-provisional-dev/paperglass/documents/test_app/test_tenant/test_patient/test_doc/document.pdf"
        assert result == expected

    def test_generate_page_uri(self):
        """Test page URI generation."""
        result = DocumentUriGenerator.generate_page_uri(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            page_number=5
        )
        
        expected = "gs://viki-ai-provisional-dev/paperglass/documents/test_app/test_tenant/test_patient/test_doc/pages/5.pdf"
        assert result == expected

    def test_generate_subject_uri_without_page_number(self):
        """Test subject URI generation without page number (document-level)."""
        result = DocumentUriGenerator.generate_subject_uri(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            page_number=None
        )
        
        expected = "gs://viki-ai-provisional-dev/paperglass/documents/test_app/test_tenant/test_patient/test_doc/document.pdf"
        assert result == expected

    def test_generate_subject_uri_with_page_number(self):
        """Test subject URI generation with page number (page-level)."""
        result = DocumentUriGenerator.generate_subject_uri(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            page_number=3
        )
        
        expected = "gs://viki-ai-provisional-dev/paperglass/documents/test_app/test_tenant/test_patient/test_doc/pages/3.pdf"
        assert result == expected

    def test_generate_subject_uri_without_explicit_none(self):
        """Test subject URI generation without passing page_number parameter."""
        result = DocumentUriGenerator.generate_subject_uri(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc"
        )
        
        expected = "gs://viki-ai-provisional-dev/paperglass/documents/test_app/test_tenant/test_patient/test_doc/document.pdf"
        assert result == expected

    def test_base_uri_constant(self):
        """Test BASE_URI constant."""
        assert DocumentUriGenerator.BASE_URI == "gs://viki-ai-provisional-dev/paperglass/documents"

    def test_uri_format_consistency(self):
        """Test that all URIs follow consistent format."""
        app_id = "myapp"
        tenant_id = "tenant123"
        patient_id = "patient456"
        document_id = "doc789"
        
        doc_uri = DocumentUriGenerator.generate_document_uri(app_id, tenant_id, patient_id, document_id)
        page_uri = DocumentUriGenerator.generate_page_uri(app_id, tenant_id, patient_id, document_id, 1)
        subject_doc_uri = DocumentUriGenerator.generate_subject_uri(app_id, tenant_id, patient_id, document_id)
        subject_page_uri = DocumentUriGenerator.generate_subject_uri(app_id, tenant_id, patient_id, document_id, 1)
        
        # All URIs should start with the base URI
        assert doc_uri.startswith(DocumentUriGenerator.BASE_URI)
        assert page_uri.startswith(DocumentUriGenerator.BASE_URI)
        assert subject_doc_uri.startswith(DocumentUriGenerator.BASE_URI)
        assert subject_page_uri.startswith(DocumentUriGenerator.BASE_URI)
        
        # Document URIs should be the same
        assert doc_uri == subject_doc_uri
        
        # Page URIs should be the same
        assert page_uri == subject_page_uri

    def test_different_page_numbers(self):
        """Test page URI generation with different page numbers."""
        app_id = "test_app"
        tenant_id = "test_tenant"
        patient_id = "test_patient"
        document_id = "test_doc"
        
        # Test various page numbers
        for page_num in [1, 10, 100, 999]:
            result = DocumentUriGenerator.generate_page_uri(
                app_id, tenant_id, patient_id, document_id, page_num
            )
            expected = f"gs://viki-ai-provisional-dev/paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/pages/{page_num}.pdf"
            assert result == expected