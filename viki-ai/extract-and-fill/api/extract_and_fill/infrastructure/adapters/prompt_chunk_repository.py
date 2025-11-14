from datetime import datetime
import json
from typing import List, Optional, Any, Iterator, Tuple

from google.cloud.firestore import AsyncClient
from extract_and_fill.domain.models import PromptChunk, PromptChunkCheckSum

from extract_and_fill.infrastructure.ports import IPromptChunkCheckSumRepository, IPromptChunkRepository
from extract_and_fill.log import getLogger

LOGGER = getLogger(__name__)


class PromptChunkRepositoryAdapter(IPromptChunkRepository):
    def __init__(self, db_name):
        # TODO: Location
        self.client = AsyncClient(database=db_name)
        self.schema_chunks_ref = self.client.collection('extract_schema_chunks')

    async def save(self, chunk):
        doc = self.schema_chunks_ref.document(chunk.id)
        chunk_dict = chunk.dict()
        # not sure but I think this is needed for firestore to know that
        # this is new data and not just overwriting the same data
        # updatedAt will ensure firestore triggers are fired otherwise
        # just overwriting the same data will not trigger the triggers
        chunk_dict.update({"updatedAt": datetime.now().isoformat()})
        await doc.set(chunk_dict)

    async def get(self, chunk_id: str) -> dict:
        doc = self.schema_chunks_ref.document(chunk_id)
        chunk = (await doc.get()).to_dict()
        # chunk['schema'] = chunk.get('schema')
        return PromptChunk.parse_obj(chunk)

    async def list_by_transcript_id(self, transcript_id: str) -> List[PromptChunk]:
        async for doc in self.schema_chunks_ref.where('transcript_id', '==', transcript_id).stream():
            yield PromptChunk.parse_obj(doc.to_dict())

    async def delete(self, chunk_id: str):
        doc = self.schema_chunks_ref.document(chunk_id)
        await doc.delete()


class PromptChunkCheckSumRepositoryAdapter(IPromptChunkCheckSumRepository):
    def __init__(self, db_name):
        # TODO: Location
        self.client = AsyncClient(database=db_name)
        self.schema_chunks_ref = self.client.collection('extract_schema_chunks_checksum')

    async def save(self, chunk: PromptChunkCheckSum):
        doc = self.schema_chunks_ref.document(chunk.id)
        chunk_dict = chunk.dict()
        # not sure but I think this is needed for firestore to know that
        # this is new data and not just overwriting the same data
        # updatedAt will ensure firestore triggers are fired otherwise
        # just overwriting the same data will not trigger the triggers
        chunk_dict.update({"updatedAt": datetime.now().isoformat()})
        await doc.set(chunk_dict)

    async def get(self, chunk_id: str) -> dict:
        doc = self.schema_chunks_ref.document(chunk_id)
        chunk = (await doc.get()).to_dict()
        # chunk['schema'] = chunk.get('schema')
        return PromptChunk.parse_obj(chunk)

    async def list_by_transcript_id(self, transcript_id: str) -> List[PromptChunkCheckSum]:
        async for doc in self.schema_chunks_ref.where('id', '==', transcript_id).stream():
            yield PromptChunkCheckSum.parse_obj(doc.to_dict())

    async def delete(self, chunk_id: str):
        doc = self.schema_chunks_ref.document(chunk_id)
        await doc.delete()
