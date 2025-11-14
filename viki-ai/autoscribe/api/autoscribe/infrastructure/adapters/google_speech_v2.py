from hashlib import sha1
from typing import AsyncIterator, Tuple

import aiohttp
from gcloud.aio.storage import Storage
from google.cloud.speech_v2 import (
    RecognitionFeatures,
    RecognizeRequest,
    SpeakerDiarizationConfig,
    SpeechAsyncClient,
    RecognitionConfig,
    StreamingRecognitionConfig,
    StreamingRecognitionFeatures,
    StreamingRecognizeRequest,
    AutoDetectDecodingConfig,
    StreamingRecognizeResponse,
)

from autoscribe.infrastructure.ports import ISpeechRecognitionPort
from autoscribe.log import getLogger
from autoscribe.usecases.types import StreamEvent

LOGGER = getLogger(__name__)


class GoogleSpeechV2Adapter(ISpeechRecognitionPort):
    def __init__(self, gcp_project_id):
        self.gcp_project_id = gcp_project_id
        self.speech_client = SpeechAsyncClient()

    async def recognize_stream(
        self, async_iterable: AsyncIterator[bytes], model: str, format: str = 'ogg'
    ) -> AsyncIterator[StreamEvent]:
        async def request_generator() -> AsyncIterator[RecognizeRequest]:
            try:
                yield StreamingRecognizeRequest(
                    recognizer=f'projects/{self.gcp_project_id}/locations/global/recognizers/_',
                    streaming_config=StreamingRecognitionConfig(
                        config=RecognitionConfig(
                            auto_decoding_config=AutoDetectDecodingConfig(),
                            language_codes=['en-US'],
                            model=model,
                            features=RecognitionFeatures(
                                enable_automatic_punctuation=True,
                                # diarization_config=SpeakerDiarizationConfig(
                                #     # enable_speaker_diarization=True,
                                #     min_speaker_count=2,
                                #     max_speaker_count=2,
                                # ),
                            ),
                        ),
                        streaming_features=StreamingRecognitionFeatures(
                            interim_results=True,
                        ),
                    ),
                )
                async for blob in async_iterable:
                    print(len(blob))
                    if not blob:
                        return
                    yield StreamingRecognizeRequest(
                        audio=blob,
                    )
            except:
                return

        stream = await self.speech_client.streaming_recognize(requests=request_generator())
        resp: StreamingRecognizeResponse
        async for resp in stream:
            print(resp)
            yield resp.results[0].is_final, resp.results[0].alternatives[0].transcript
