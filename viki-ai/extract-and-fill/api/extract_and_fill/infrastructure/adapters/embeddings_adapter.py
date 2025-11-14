import datetime
from typing import List
import uuid
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient

from extract_and_fill.infrastructure.ports import IEmbeddingsMetadataAdapter


class EmbeddingsMetadataFireStoreAdapter(IEmbeddingsMetadataAdapter):
    EMBEDDING_METADATA_COLLECTION = u"extract_embeddings_metadata"

    def __init__(self, project_id, location, db_name) -> None:
        if db_name != "(default)":
            self.db = AsyncFirestoreClient(project=project_id, database=db_name)
        else:
            self.db = AsyncFirestoreClient()

    async def save(self, sentence_group_id, status='started'):
        result = []
        doc_ref = self.db.collection(self.EMBEDDING_METADATA_COLLECTION).document(sentence_group_id)
        data = {
            'embedding_metadata_id': sentence_group_id,
            'sentence_group_id': sentence_group_id,
            'status': status,
            "updatedAt": datetime.datetime.utcnow().isoformat(),
        }
        await doc_ref.set(data)
        return True

    async def get_by_group_id(self, sentence_group_id):
        doc_ref = self.db.collection(self.EMBEDDING_METADATA_COLLECTION).where(
            "sentence_group_id", "==", sentence_group_id
        )
        docs = await doc_ref.get()
        return [doc.to_dict() for doc in docs]

    async def update(self, sentence_group_id, status):
        doc_ref = self.db.collection(self.EMBEDDING_METADATA_COLLECTION).document(sentence_group_id)
        await doc_ref.update({'status': status, "updatedAt": datetime.datetime.utcnow().isoformat()})
        return True
