import datetime
from typing import List
import uuid
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient


class SentenceFireStoreAdapter(object):
    SENTENCE_COLLECTION = u"extract_sentences"

    def __init__(self, project_id, location, db_name) -> None:
        if db_name != "(default)":
            self.db = AsyncFirestoreClient(project=project_id, database=db_name)
        else:
            self.db = AsyncFirestoreClient()

    async def save(self, sentence_group_id, sentences: List[str]) -> List[dict]:
        result = []
        index = 0
        docs = self.db.collection(self.SENTENCE_COLLECTION).where("sentence_group_id", "==", sentence_group_id).stream()
        async for doc in docs:
            await doc.reference.delete()

        for sentence in sentences:
            if not sentence:
                continue
            sentence_id = f"{sentence_group_id}#{index}"
            doc_ref = self.db.collection(self.SENTENCE_COLLECTION).document(sentence_id)
            await doc_ref.set(
                {
                    'sentence_id': sentence_id,
                    'sentence': sentence,
                    'sentence_group_id': sentence_group_id,
                    "updatedAt": datetime.datetime.utcnow().isoformat(),
                }
            )
            result.append(
                {
                    "id": sentence_id,
                    "sentence": sentence,
                    "sentence_group_id": sentence_group_id,
                    "updatedAt": datetime.datetime.utcnow().isoformat(),
                }
            )
            index += 1
        return result

    async def get(self, sentence_id):
        doc_ref = self.db.collection(self.SENTENCE_COLLECTION).document(sentence_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None

    async def get_by_group_id(self, sentence_group_id):
        doc_ref = self.db.collection(self.SENTENCE_COLLECTION).where("sentence_group_id", "==", sentence_group_id)
        docs = await doc_ref.get()
        return [doc.to_dict() for doc in docs]
