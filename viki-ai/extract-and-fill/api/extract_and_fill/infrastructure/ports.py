from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator, List, Optional

from extract_and_fill.domain.models import PromptChunk


class IPromptPort(ABC):
    @abstractmethod
    async def extract(self, content: str, model: str) -> str:
        pass

    @abstractmethod
    async def save_prompt_template(self, transcript_id: str, prompt_template: dict, model: str) -> str:
        pass

    @abstractmethod
    async def get_prompt_template(self, transcript_id: str) -> str:
        pass


class IEmbeddingsAdapter(ABC):
    # @abstractmethod
    # def create_index(self,dimension, metric):
    #     pass

    @abstractmethod
    async def upsert(self, unique_identifier, sentences):
        pass

    @abstractmethod
    async def search(self, qid, uery_strings):
        pass


class ISentencePort(ABC):
    @abstractmethod
    async def save(self, sentences: List[str]) -> List[dict]:
        pass

    @abstractmethod
    async def get(self, id: str) -> dict:
        pass

    @abstractmethod
    async def get_by_group_id(self, id: str) -> List[dict]:
        pass


class ITranscriptPort(ABC):
    @abstractmethod
    async def save(self, transcript_id, transcript: str) -> str:
        pass

    @abstractmethod
    async def save_autoscribe_transcript_id(
        self, autoscribe_transcript_id, autoScribe_transcription_version, transcript_id
    ) -> str:
        pass

    @abstractmethod
    async def get_transcript_id_by_autoscribe_id(self, autoscribe_transcript_id) -> str:
        pass


class IMessageBusAdapter(ABC):
    @abstractmethod
    async def publish(self, topic: str, message: str) -> None:
        pass


class IEmbeddingsMetadataAdapter(ABC):
    @abstractmethod
    async def save(self, sentence_group_id: str, status: str) -> bool:
        pass

    @abstractmethod
    async def get_by_group_id(self, sentence_group_id: str) -> List[dict]:
        pass

    @abstractmethod
    async def update(self, sentence_group_id: str, status: str) -> bool:
        pass


class IPromptChunkRepository(ABC):
    @abstractmethod
    async def save(self, chunk: PromptChunk):
        pass

    @abstractmethod
    async def get(self, chunk_id: str) -> PromptChunk:
        pass

    @abstractmethod
    async def list_by_transcript_id(self, transcript_id: str) -> List[PromptChunk]:
        pass

    @abstractmethod
    async def delete(self, chunk_id: str):
        pass


class IPromptChunkCheckSumRepository(IPromptChunkRepository):
    pass


class ICommandsRepository(ABC):

    @abstractmethod
    async def save(self, command) -> None:
        pass
