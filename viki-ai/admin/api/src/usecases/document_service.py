import os
from typing import List, Optional
from fastapi import UploadFile
from kink import inject
from viki_shared.utils.logger import getLogger

from model_aggregates.documents import DocumentAggregate
from usecases.document_commands import (
    CreateDocumentCommand,
    UpdateDocumentCommand,
    DeleteDocumentCommand,
    UpdateDocumentStatusCommand,
    GetDocumentsQuery,
    GetDocumentQuery,
    UploadDocumentCommand
)
from infrastructure.document_ports import DocumentRepositoryPort, FileStoragePort
from adapters.paperglass_adapter import PaperglassAdapter
from settings import Settings

logger = getLogger(__name__)


class DocumentService:
    """Service for managing documents"""

    @inject
    def __init__(
        self,
        document_repository: DocumentRepositoryPort,
        file_storage: FileStoragePort,
        paperglass_adapter: PaperglassAdapter,
        settings: Settings
    ):
        self._document_repository = document_repository
        self._file_storage = file_storage
        self._paperglass_adapter = paperglass_adapter
        self._settings = settings

    async def handle_create_document(self, command: CreateDocumentCommand) -> DocumentAggregate:
        """Handle document creation"""
        document = DocumentAggregate.create(
            app_id=command.app_id,
            subject_id=command.subject_id,
            name=command.name,
            uri=command.uri,
            metadata=command.metadata,
            content_type=command.content_type,
            size=command.size,
            created_by=command.created_by
        )
        
        await self._document_repository.save(document)
        return document

    async def handle_upload_document(
        self, 
        command: UploadDocumentCommand, 
        file: UploadFile
    ) -> DocumentAggregate:
        """Handle document upload to GCS and Firestore"""
        # Create document record first to get the document ID
        document = DocumentAggregate.create(
            app_id=command.app_id,
            subject_id=command.subject_id,
            name=command.filename,
            uri="",  # Will be updated after upload
            metadata=command.metadata,
            content_type=command.content_type,
            size=command.size,
            created_by=command.uploaded_by
        )
        
        # Determine environment for bucket naming
        env = os.getenv('ENVIRONMENT', 'dev')
        bucket_name = f"viki-admin-{env}"
        
        # Generate GCS path with document ID: /demo/{app_id}/subjects/{subject_id}/{document_id}/{document_name}
        object_path = f"demo/{command.app_id}/subjects/{command.subject_id}/{document.id}/{command.filename}"
        
        # Upload file to GCS
        gcs_uri = await self._file_storage.upload_file(
            bucket_name=bucket_name,
            object_path=object_path,
            file=file,
            metadata=command.metadata
        )
        
        # Update document with GCS URI
        document.uri = gcs_uri
        
        # Save to Firestore
        await self._document_repository.save(document)
        
        # Automatically submit to PaperGlass for processing
        await self._submit_to_paperglass(document, command.subject_id)
        
        return document

    async def handle_update_document(self, command: UpdateDocumentCommand) -> Optional[DocumentAggregate]:
        """Handle document update"""
        document = await self._document_repository.get_by_id(
            command.app_id, 
            command.subject_id, 
            command.document_id
        )
        
        if not document or not document.active:
            return None

        if command.name:
            document.name = command.name
        if command.metadata is not None:
            document.update_metadata(command.metadata, command.modified_by)
        if command.status:
            document.update_status(command.status, command.modified_by)

        await self._document_repository.save(document)
        return document

    async def handle_delete_document(self, command: DeleteDocumentCommand) -> bool:
        """Handle document soft deletion"""
        document = await self._document_repository.get_by_id(
            command.app_id, 
            command.subject_id, 
            command.document_id
        )
        
        if not document or not document.active:
            return False

        document.soft_delete(command.deleted_by)
        await self._document_repository.save(document)
        return True

    async def handle_update_document_status(self, command: UpdateDocumentStatusCommand) -> Optional[DocumentAggregate]:
        """Handle document status update"""
        document = await self._document_repository.get_by_id(
            command.app_id, 
            command.subject_id, 
            command.document_id
        )
        
        if not document or not document.active:
            return None

        document.update_status(command.status, command.modified_by)
        await self._document_repository.save(document)
        return document

    async def get_documents(self, query: GetDocumentsQuery) -> List[DocumentAggregate]:
        """Get all documents for a subject"""
        return await self._document_repository.get_by_subject(
            query.app_id, 
            query.subject_id, 
            include_deleted=query.include_deleted
        )

    async def get_document(self, query: GetDocumentQuery) -> Optional[DocumentAggregate]:
        """Get a specific document"""
        return await self._document_repository.get_by_id(
            query.app_id, 
            query.subject_id, 
            query.document_id
        )

    async def _submit_to_paperglass(self, document: DocumentAggregate, subject_id: str):
        """
        Automatically submit document to PaperGlass for processing with integration override.
        
        Args:
            document: The document aggregate that was just uploaded
            subject_id: Subject ID (patient_id in PaperGlass context)
        """
        extra = {
            "operation": "submit_to_paperglass",
            "app_id": document.app_id,
            "subject_id": subject_id,
            "document_id": document.id,
            "document_uri": document.uri
        }
        
        try:
            logger.info("Automatically submitting document to PaperGlass for processing", extra=extra)
            
            # Start with user-provided metadata from document
            combined_metadata = document.metadata.copy() if document.metadata else {}

            # Add system integration metadata (always override user integration config for security)
            integration_config = {
                "base_url": self._settings.ADMIN_DEMO_BASE_URL,
                "callback": {
                    "enabled": True,
                    "endpoint": f"{{base_url}}{self._settings.ADMIN_DEMO_ENTITY_CALLBACK_ENDPOINT}",
                    "status_callback": f"{self._settings.SELF_API_URL}/api/v1/demo/documents/{document.id}/status-callback",
                    "embed_entities_enabled": True,
                    "cloudtask_enabled": False,
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
            }
            combined_metadata["integration"] = integration_config

            extra.update({
                "user_metadata_keys": list(document.metadata.keys()) if document.metadata else [],
                "combined_metadata_keys": list(combined_metadata.keys()),
                "has_user_metadata": bool(document.metadata)
            })

            logger.info("Sending combined metadata to PaperGlass", extra=extra)

            # Submit to PaperGlass
            response = await self._paperglass_adapter.submit_external_document(
                gs_uri=document.uri,
                app_id=document.app_id,
                tenant_id="admin-experiment",  # Use admin-experiment as tenant_id for admin UI experiments
                patient_id=subject_id,
                host_file_id=document.id,
                file_name=document.name,
                file_type=document.content_type or "application/pdf",
                metadata=combined_metadata
            )
            
            extra.update({
                "paperglass_submission": "success",
                "paperglass_response_status": response.get("status", "unknown")
            })
            
            logger.info("Successfully submitted document to PaperGlass", extra=extra)
            
        except Exception as e:
            from viki_shared.utils.exceptions import exceptionToMap
            extra.update({
                "paperglass_submission": "failed",
                "error": exceptionToMap(e)
            })
            logger.error(f"Failed to submit document to PaperGlass: {str(e)}", extra=extra)
            # Don't re-raise the exception to avoid breaking the document upload flow
            # The document was already saved successfully, so this is a non-critical failure