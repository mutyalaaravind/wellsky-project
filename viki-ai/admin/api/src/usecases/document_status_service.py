from typing import Optional
from usecases.document_commands import UpdateDocumentStatusFromCallbackCommand
from model_aggregates.documents import DocumentAggregate
from infrastructure.document_ports import DocumentRepositoryPort
from viki_shared.utils.exceptions import exceptionToMap
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentNotFoundError(Exception):
    """Raised when a document is not found"""
    pass


class DocumentStatusService:
    """Application service for handling document status updates from callbacks"""

    def __init__(self, document_repository: DocumentRepositoryPort):
        self.document_repository = document_repository

    async def handle_status_update_from_callback(self, command: UpdateDocumentStatusFromCallbackCommand) -> bool:
        """
        Handle document status update command from Paperglass callback.

        Args:
            command: UpdateDocumentStatusFromCallbackCommand containing status update data

        Returns:
            bool: True if update successful

        Raises:
            DocumentNotFoundError: If document not found
        """
        extra = {
            "operation": "update_document_status_from_callback",
            "document_id": command.document_id,
            "status": command.status,
            "operation_type": command.operation_type,
            "callback_timestamp": command.timestamp
        }

        try:
            logger.info("Processing document status update from Paperglass callback", extra=extra)

            # Get document via repository - need to find by document_id across all subjects
            document = await self._find_document_by_id(command.document_id)

            if not document:
                raise DocumentNotFoundError(f"Document {command.document_id} not found")

            # Store previous status for audit
            previous_status = document.status
            extra.update({
                "app_id": document.app_id,
                "subject_id": document.subject_id,
                "previous_status": previous_status
            })

            # Business logic: validate status transition if needed
            if not self._is_valid_status_transition(previous_status, command.status):
                logger.warning("Invalid status transition attempted", extra={
                    **extra,
                    "from_status": previous_status,
                    "to_status": command.status
                })
                # For now, allow all transitions, but log warning

            # Update document status
            document.update_status(command.status, "paperglass_callback")

            # Save updated document
            await self.document_repository.save(document)

            logger.info("Document status updated successfully via callback", extra={
                **extra,
                "new_status": command.status
            })

            return True

        except DocumentNotFoundError:
            raise  # Re-raise as-is
        except Exception as e:
            logger.error("Error updating document status via callback", extra={
                **extra,
                "error": exceptionToMap(e)
            })
            raise

    async def _find_document_by_id(self, document_id: str) -> Optional[DocumentAggregate]:
        """
        Find document by ID across all app_ids and subject_ids.
        This is needed because the callback only provides the document_id.
        """
        # Note: This is a simplified implementation. In a real system, you might:
        # 1. Add an index by document_id in Firestore
        # 2. Store app_id/subject_id in the callback payload
        # 3. Use a different repository method that searches across collections

        # For now, we'll need to implement a search method in the repository
        # This is a placeholder - the actual implementation depends on the repository structure
        return await self.document_repository.find_by_document_id(document_id)

    def _is_valid_status_transition(self, from_status: str, to_status: str) -> bool:
        """Business logic for valid status transitions"""
        # Define valid transitions - this is business logic
        valid_transitions = {
            "NOT_STARTED": ["QUEUED", "IN_PROGRESS", "FAILED"],
            "QUEUED": ["IN_PROGRESS", "FAILED"],
            "IN_PROGRESS": ["COMPLETED", "FAILED"],
            "COMPLETED": [],  # Terminal state
            "FAILED": ["QUEUED", "IN_PROGRESS"],  # Allow retry
            # Legacy status support for backward compatibility with old documents
            "new": ["QUEUED", "IN_PROGRESS", "FAILED"],
            "processing": ["IN_PROGRESS", "COMPLETED", "FAILED"],
            "completed": ["QUEUED", "IN_PROGRESS", "FAILED"],  # Allow restart from completed
            "failed": ["QUEUED", "IN_PROGRESS"]
        }

        return to_status in valid_transitions.get(from_status, [])