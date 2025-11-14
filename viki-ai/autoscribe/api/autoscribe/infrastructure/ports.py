from abc import ABC, abstractmethod
from enum import Enum
from typing import AsyncIterator, Optional

from autoscribe.domain.models import Transaction
from autoscribe.usecases.types import StreamEvent


class IPersistencePort(ABC):
    @abstractmethod
    async def put_transaction(self, transaction: Transaction):
        pass

    @abstractmethod
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        pass


class ISpeechRecognitionFactory(ABC):
    class Backend(Enum):
        GOOGLE_V1 = 'google_v1'
        GOOGLE_V2 = 'google_v2'
        AWS_TRANSCRIBE = 'aws_transcribe'

    @abstractmethod
    def get_implementation(self, backend: Backend):
        pass


class ISpeechRecognitionPort(ABC):
    @abstractmethod
    async def recognize_stream(
        self,
        transaction_id: str,
        section_id: str,
        async_iterable: AsyncIterator[bytes],
        model: str,
        format: str = 'ogg',
    ) -> AsyncIterator[StreamEvent]:
        pass

    @abstractmethod
    async def get_audio_signed_url(self, transaction_id: str, section_id: str) -> Optional[str]:
        pass
