import asyncio
from typing import AsyncIterator, Optional

import aioboto3
import aiofiles
from amazon_transcribe.auth import CredentialResolver, StaticCredentialResolver
from aiocache import cached
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.model import AudioStream, TranscriptEvent, TranscriptResultStream
import google.auth.transport._aiohttp_requests
import google.oauth2._id_token_async

from autoscribe.infrastructure.ports import ISpeechRecognitionPort
from autoscribe.log import getLogger
from autoscribe.settings import SERVICE, STAGE
from autoscribe.usecases.types import DiarizationEvent, ErrorEvent, RecognitionEvent, Sentence, StreamEvent, Word

LOGGER = getLogger(__name__)


class AWSTranscribeAdapter(ISpeechRecognitionPort):
    def __init__(self, aws_role_arn: Optional[str], aws_region: Optional[str]) -> None:
        self.client = None
        self.aws_role_arn = aws_role_arn
        self.aws_region = aws_region

    @cached(ttl=1800)
    async def _assume_role_with_web_identity(self, aws_role_arn) -> CredentialResolver:
        """
        Authenticates in AWS with Web Identity using GCP SA to access AWS services.
        """
        request = google.auth.transport._aiohttp_requests.Request()

        id_token = await google.oauth2._id_token_async.fetch_id_token(request, None)

        async with aioboto3.Session().client('sts') as sts:
            response = await sts.assume_role_with_web_identity(
                RoleArn=aws_role_arn,
                RoleSessionName=f'viki-{SERVICE}-{STAGE}',
                WebIdentityToken=id_token,
                DurationSeconds=3600,
            )

        creds = response['Credentials']
        return StaticCredentialResolver(
            access_key_id=creds['AccessKeyId'],
            secret_access_key=creds['SecretAccessKey'],
            session_token=creds['SessionToken'],
        )

    async def _blob_writer(self, source_stream: AsyncIterator[bytes], target_stream: AudioStream):
        async for blob in source_stream:
            LOGGER.debug('Streaming blob of length %d to AWS Transcribe API', len(blob))
            await target_stream.send_audio_event(audio_chunk=blob)
        await target_stream.end_stream()

    async def _event_reader(self, source_stream: TranscriptResultStream) -> AsyncIterator[TranscriptEvent]:
        async for event in source_stream:
            if isinstance(event, TranscriptEvent):
                yield event

    async def recognize_stream(
        self, transaction_id: str, section_id: str, async_iterable: AsyncIterator[bytes], model: str, format: str = 'ogg'
    ) -> AsyncIterator[StreamEvent]:
        try:
            if self.aws_role_arn:
                # GCP mode: assume role with web identity using AWS_ROLE_ARN
                # TODO: Cache this
                aws_session_creds = await self._assume_role_with_web_identity(self.aws_role_arn)
            else:
                # Local operation: use predefined credentials (env vars, ~/.aws/config, etc)
                aws_session_creds = None

            self.client = TranscribeStreamingClient(region=self.aws_region, credential_resolver=aws_session_creds)

            stream = await self.client.start_stream_transcription(
                language_code='en-US',
                media_sample_rate_hz=48000,
                media_encoding='ogg-opus',
                show_speaker_label=True,
            )
            writer = self._blob_writer(async_iterable, stream.input_stream)
            writer_task = asyncio.create_task(writer)

            sentences = []

            async for event in self._event_reader(stream.output_stream):
                if event.transcript.results:
                    result = event.transcript.results[0]
                    alternative = result.alternatives[0]
                    if result.is_partial:
                        yield RecognitionEvent(transcript=alternative.transcript)
                    else:
                        last_speaker = -1
                        for item in alternative.items:
                            if item.speaker is not None:
                                speaker_tag = int(item.speaker) + 1
                            else:
                                speaker_tag = 0
                            if item.item_type == 'punctuation' and sentences:
                                # Punctuation does not have speaker value, so let's assume it's for the active speaker
                                sentences[-1].words.append(Word(text=item.content, start=item.start_time, end=item.end_time))
                                continue
                            elif speaker_tag != last_speaker:
                                sentences.append(Sentence(speaker_tag=speaker_tag))
                                last_speaker = speaker_tag
                            sentences[-1].words.append(Word(text=item.content, start=item.start_time, end=item.end_time))
                        yield DiarizationEvent(sentences=sentences)
                    yield result
            await writer_task
        except Exception as exc:
            LOGGER.exception('recognize_stream: error')
            yield ErrorEvent(message=str(exc))  # TODO
            return
