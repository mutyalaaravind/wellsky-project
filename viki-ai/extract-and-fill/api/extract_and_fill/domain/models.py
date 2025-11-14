from enum import Enum
from typing import List, Literal, Optional, Union
from pydantic import BaseModel


class PromptChunkStatus(str, Enum):  # str is required so that it is convertable to Firestore values
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERRORED = 'errored'


class PromptChunk(BaseModel):
    id: str
    index: int
    transcript_id: str
    transcript_text: str  # This is an aggregate, so it must contain all required data to be self-sufficient. This is why we include the transcript text in each chunk.
    included_paths: List[str]
    chunk_schema: dict  # "schema" is a reserved word in pydantic
    model: str
    transcript_version: Optional[int] = 0
    status: PromptChunkStatus = PromptChunkStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    other: Optional[dict] = None

    @classmethod
    def create(
        cls, index, transcript_id, transcript_text, included_paths, chunk_schema, model, transcript_version, other=None
    ):
        return cls(
            id=f'{transcript_id}.{index}',
            index=index,
            transcript_id=transcript_id,
            transcript_text=transcript_text,
            included_paths=included_paths,
            chunk_schema=chunk_schema,
            model=model,
            transcript_version=transcript_version,
            other=other,
        )

    def set_processing(self):
        self.status = PromptChunkStatus.PROCESSING

    def set_result(self, result: dict):
        self.status = PromptChunkStatus.COMPLETED
        self.result = result

    def set_error(self, error: str):
        self.status = PromptChunkStatus.ERRORED
        self.error = error

    @property
    def is_finished(self):
        return self.status in [PromptChunkStatus.COMPLETED, PromptChunkStatus.ERRORED]


class PromptChunkCheckSum(BaseModel):
    id: str
    total_chunks: int


class Sentence(BaseModel):
    id: int
    text: str


class Section(BaseModel):
    sentences: List[Sentence]
