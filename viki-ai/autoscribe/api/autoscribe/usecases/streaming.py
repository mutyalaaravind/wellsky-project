from typing import AsyncIterable, List
from json import dumps, loads
import datetime
from autoscribe.domain.time import now_utc

from kink import inject

from autoscribe.infrastructure.ports import IPersistencePort, ISpeechRecognitionFactory, ISpeechRecognitionPort
from autoscribe.log import getLogger
from autoscribe.usecases.types import DiarizationEvent, ErrorEvent, StartEvent, StreamEvent, TextSentence

LOGGER = getLogger(__name__)


@inject
async def streaming_transcribe(
    transaction_id: str,
    section_id: str,
    audio_stream: AsyncIterable[bytes],
    backend: str,
    model: str,
    persistence: IPersistencePort,
    speech_recognition_factory: ISpeechRecognitionFactory,
) -> AsyncIterable[StreamEvent]:
    transaction = await persistence.get_transaction(transaction_id)
    if not transaction:
        yield ErrorEvent(message=f'Transaction {transaction_id} not found')
        return
    speech_recognition = speech_recognition_factory.get_implementation(ISpeechRecognitionFactory.Backend(backend))
    LOGGER.debug('streaming_transcribe: listening, backend = %s, model = %s', backend, model)
    sentences = []
    yield StartEvent(transaction_id=transaction.id)
    async for event in speech_recognition.recognize_stream(transaction.id, section_id, audio_stream, model):
        LOGGER.debug('streaming_transcribe: event = %s', event)
        if isinstance(event, DiarizationEvent):
            sentences = event.sentences
        yield event
    transaction.update_section(
        section_id,
        sentences,
        [
            TextSentence(speaker_tag=sentence.speaker_tag, start=sentence.get_start(), text=sentence.get_text())
            for sentence in sentences
        ],
    )
    transaction.set_section_backend(section_id, backend)
    await persistence.put_transaction(transaction)
