from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from model_aggregates.documents import DocumentAggregate
from infrastructure.document_ports import DocumentRepositoryPort


class DocumentFirestoreAdapter(DocumentRepositoryPort):
    """Firestore adapter for document repository"""

    def __init__(self, firestore_client: firestore.AsyncClient):
        """
        Initialize the document repository with an AsyncClient.

        Args:
            firestore_client: Firestore AsyncClient instance configured for the appropriate environment
        """
        self._firestore_client = firestore_client

    def _get_subject_collection_ref(self, app_id: str, subject_id: str):
        """Get reference to the subject's documents subcollection"""
        return (
            self._firestore_client
            .collection("admin_demo_subjects")
            .document(app_id)
            .collection("subjects")
            .document(subject_id)
            .collection("documents")
        )

    def _document_to_dict(self, document: DocumentAggregate) -> Dict[str, Any]:
        """Convert document aggregate to Firestore dict"""
        return {
            "id": document.id,
            "app_id": document.app_id,
            "subject_id": document.subject_id,
            "name": document.name,
            "uri": document.uri,
            "metadata": document.metadata,
            "status": document.status,
            "content_type": document.content_type,
            "size": document.size,
            "active": document.active,
            "created_by": document.created_by,
            "modified_by": document.modified_by,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
        }

    def _dict_to_document(self, doc_dict: Dict[str, Any]) -> DocumentAggregate:
        """Convert Firestore dict to document aggregate"""
        return DocumentAggregate(
            id=doc_dict["id"],
            app_id=doc_dict["app_id"],
            subject_id=doc_dict["subject_id"],
            name=doc_dict["name"],
            uri=doc_dict["uri"],
            metadata=doc_dict.get("metadata", {}),
            status=doc_dict.get("status", "new"),
            content_type=doc_dict.get("content_type"),
            size=doc_dict.get("size"),
            active=doc_dict.get("active", True),
            created_by=doc_dict.get("created_by"),
            modified_by=doc_dict.get("modified_by"),
            created_at=doc_dict.get("created_at", datetime.utcnow()),
            updated_at=doc_dict.get("updated_at", datetime.utcnow()),
        )

    async def save(self, document: DocumentAggregate) -> None:
        """Save a document to Firestore"""
        collection_ref = self._get_subject_collection_ref(document.app_id, document.subject_id)
        doc_ref = collection_ref.document(document.id)

        document_data = self._document_to_dict(document)
        await doc_ref.set(document_data)

    async def get_by_id(self, app_id: str, subject_id: str, document_id: str) -> Optional[DocumentAggregate]:
        """Get a document by its ID"""
        collection_ref = self._get_subject_collection_ref(app_id, subject_id)
        doc_ref = collection_ref.document(document_id)

        doc_snapshot = await doc_ref.get()

        if not doc_snapshot.exists:
            return None

        return self._dict_to_document(doc_snapshot.to_dict())

    async def get_by_subject(
        self,
        app_id: str,
        subject_id: str,
        include_deleted: bool = False
    ) -> List[DocumentAggregate]:
        """Get all documents for a subject"""
        collection_ref = self._get_subject_collection_ref(app_id, subject_id)

        if include_deleted:
            # Get all documents
            query = collection_ref.order_by("created_at", direction=firestore.Query.DESCENDING)
        else:
            # Get only active documents
            query = (
                collection_ref
                .where(filter=FieldFilter("active", "==", True))
                .order_by("created_at", direction=firestore.Query.DESCENDING)
            )

        docs = query.stream()
        documents = []

        async for doc in docs:
            documents.append(self._dict_to_document(doc.to_dict()))

        return documents

    async def delete_by_id(self, app_id: str, subject_id: str, document_id: str) -> bool:
        """Hard delete a document from Firestore"""
        collection_ref = self._get_subject_collection_ref(app_id, subject_id)
        doc_ref = collection_ref.document(document_id)

        doc_snapshot = await doc_ref.get()
        if not doc_snapshot.exists:
            return False

        await doc_ref.delete()
        return True

    async def find_by_document_id(self, document_id: str) -> Optional[DocumentAggregate]:
        """Find a document by its ID across all app_ids and subject_ids"""
        # This requires a collection group query since we need to search across
        # all documents subcollections in the entire database

        query = (
            self._firestore_client
            .collection_group("documents")
            .where(filter=FieldFilter("id", "==", document_id))
            .where(filter=FieldFilter("active", "==", True))
            .limit(1)
        )

        docs = []
        async for doc in query.stream():
            docs.append(doc)

        if not docs:
            return None

        return self._dict_to_document(docs[0].to_dict())