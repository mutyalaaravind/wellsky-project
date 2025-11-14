import asyncio
from datetime import timedelta
from json import dumps
from time import time
from typing import AsyncIterator, List, Optional, Tuple

import aiohttp
from gcloud.aio.storage import Storage
import google.auth  # type: ignore
from google.auth.transport import requests  # type: ignore
from google.cloud import storage  # type: ignore
from google.cloud.speech_v1p1beta1 import (
    RecognizeRequest,
    SpeakerDiarizationConfig,
    SpeechAsyncClient,
    LongRunningRecognizeRequest,
    RecognitionConfig,
    RecognitionAudio,
    StreamingRecognitionConfig,
    StreamingRecognizeRequest,
)
from proto.message import MessageToDict

from autoscribe.infrastructure.ports import ISpeechRecognitionPort
from autoscribe.log import getLogger
from autoscribe.usecases.types import DiarizationEvent, ErrorEvent, RecognitionEvent, Sentence, StreamEvent, Word

LOGGER = getLogger(__name__)


class GoogleSpeechAdapter(ISpeechRecognitionPort):
    def __init__(self, gcp_project_id: str, bucket: str, cloud_provider: str):
        self.gcp_project_id = gcp_project_id
        self.bucket = bucket
        self.speech_client = SpeechAsyncClient()
        self.cache = {}
        self.sync_client = storage.Client(project=gcp_project_id)
        self.cloud_provider = cloud_provider

    async def upload(
        self, transaction_id: str, section_id: str, content: bytes, messages: Optional[List] = None, format: str = 'ogg'
    ) -> str:
        LOGGER.info('Saving recording to GCS')
        prefix = f'autoscribe/audio/{transaction_id}/{section_id}'
        path = f'{prefix}/audio.{format}'
        # async with Storage() as storage:
        #     bucket = storage.get_bucket(self.bucket)
        #     if await bucket.blob_exists(path):
        #         LOGGER.info('recognize: %s already exists, overwriting', path)
        #     await bucket.new_blob(path).upload(content)
        #     if messages:
        #         await bucket.new_blob(f'{prefix}/messages.json').upload(dumps(messages, indent=4))
        bucket = self.sync_client.bucket(self.bucket)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(None, blob.upload_from_string, content)
        if messages:
            blob = bucket.blob(f'{prefix}/messages.json')
            await asyncio.get_event_loop().run_in_executor(None, blob.upload_from_string, dumps(messages, indent=4))
        uri = f'gs://{self.bucket}/{path}'
        LOGGER.info('Recording written to %s', uri)
        return uri

    async def _request_generator(self, async_iterable, model):
        try:
            yield StreamingRecognizeRequest(
                streaming_config=StreamingRecognitionConfig(
                    config=RecognitionConfig(
                        language_code='en-US',
                        # audio_channel_count=2,
                        encoding=RecognitionConfig.AudioEncoding.WEBM_OPUS,  # TODO
                        sample_rate_hertz=48000,  # TODO
                        diarization_config=SpeakerDiarizationConfig(
                            enable_speaker_diarization=True,
                            min_speaker_count=2,
                            max_speaker_count=2,
                        ),
                        model=model,
                    ),
                    interim_results=True,
                ),
            )
            async for blob in async_iterable:
                if not blob:
                    return
                LOGGER.debug('Streaming blob of length %d to Google Speech API', len(blob))
                yield StreamingRecognizeRequest(
                    audio_content=blob,
                )
        except:
            LOGGER.exception('recognize_stream: error')

    async def recognize_stream(
        self,
        transaction_id: str,
        section_id: str,
        async_iterable: AsyncIterator[bytes],
        model: str,
        format: str = 'ogg',
    ) -> AsyncIterator[StreamEvent]:
        blobs: List[bytes] = []
        messages: List[dict] = []

        end_of_stream = False

        async def _blob_iterator():
            nonlocal end_of_stream
            async for blob in async_iterable:
                blobs.append(blob)
                yield blob
            end_of_stream = True

        request_generator = self._request_generator(_blob_iterator(), model)

        started = time()

        try:
            stream = await self.speech_client.streaming_recognize(requests=request_generator)
            async for resp in stream:
                if resp.results:
                    messages.append({'time': time() - started, 'message': MessageToDict(resp._pb)})
                    if end_of_stream:
                        # For some reason, Google sometimes duplicates diarization of last sentence when stopping.
                        LOGGER.warn('Discarding streaming recognition event since the audio stream is finished')
                        continue
                    LOGGER.debug(
                        'is_final=%s, transcript=%s',
                        resp.results[0].is_final,
                        resp.results[0].alternatives[0].transcript,
                    )
                    if resp.results[0].is_final:
                        LOGGER.debug('Words: %s', [word.word for word in resp.results[0].alternatives[0].words])
                        sentences = []
                        last_speaker = -1
                        for word in resp.results[0].alternatives[0].words:
                            speaker_tag = int(word.speaker_tag)
                            if speaker_tag != last_speaker:
                                sentences.append(Sentence(speaker_tag=speaker_tag))
                                last_speaker = speaker_tag
                            sentences[-1].words.append(
                                Word(
                                    text=word.word,
                                    start=word.start_time.total_seconds(),
                                    end=word.end_time.total_seconds(),
                                    # speaker_tag=speaker_tag,
                                )
                            )

                        yield DiarizationEvent(sentences=sentences)
                    else:
                        yield RecognitionEvent(transcript=resp.results[0].alternatives[0].transcript)

        except Exception as exc:
            LOGGER.exception('recognize_stream: error')
            yield ErrorEvent(message=str(exc))  # TODO
            return
        asyncio.create_task(self.upload(transaction_id, section_id, b''.join(blobs), messages, format))

    def _get_signed_url(self, bucket_name: str, path: str):
        # https://stackoverflow.com/a/64245028/3455614
        # See paperglass/api/paperglass/infrastructure/adapters/google.py for an extended rant about the suckiness of auth
        if self.cloud_provider == "google":
            # Breaks in local env
            credentials, _ = google.auth.default()
            req = requests.Request()
            credentials.refresh(req)

            client = storage.Client(project=self.gcp_project_id)
            bucket = client.get_bucket(bucket_name)
            blob = bucket.get_blob(path)

            service_account_email = credentials.service_account_email
            return blob.generate_signed_url(
                expiration=timedelta(minutes=60),
                service_account_email=service_account_email,
                access_token=credentials.token,
            )
        else:
            # Breaks in Cloud Run:
            # >  AttributeError: you need a private key to sign credentials.the credentials you are currently using <class 'google.auth.compute_engine.credentials.Credentials'> just contains a token
            blob = self.sync_client.bucket(bucket_name).blob(path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=48),
                method="GET",
            )
            return url

    async def get_audio_signed_url(self, transaction_id: str, section_id: str, format='ogg') -> Optional[str]:
        prefix = f'autoscribe/audio/{transaction_id}/{section_id}'
        path = f'{prefix}/audio.{format}'
        # Does not work with service accounts for some reason:
        # > Blob signing is only suported for tokens with explicit client_email and private_key data; please check your token points to a JSON service account file
        # async with Storage() as storage:
        #     bucket = storage.get_bucket(self.bucket)
        #     blob = await bucket.get_blob(path)
        #     blob.genera
        #     return await blob.get_signed_url(3600)
        # return None

        # Good old synchronous kludge...
        return await asyncio.get_event_loop().run_in_executor(None, self._get_signed_url, self.bucket, path)
