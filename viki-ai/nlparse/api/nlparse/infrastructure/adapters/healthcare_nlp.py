import asyncio
from typing import AsyncIterator, List, Optional, Tuple
from functools import partial

import aioboto3
from aiocache.decorators import inspect
import aiofiles
from aiohttp import ClientSession
from amazon_transcribe.auth import CredentialResolver, StaticCredentialResolver
from aiocache import cached
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.model import AudioStream, TranscriptEvent, TranscriptResultStream
# from google.auth._default_async import default_async
# from google.auth._credentials_async import Credentials
# from google.auth.transport import _aiohttp_requests
from google.auth import default
from google.auth.transport.requests import AuthorizedSession

from nlparse.infrastructure.ports import IHealthcareNLPPort
from nlparse.log import getLogger
from nlparse.settings import SERVICE, STAGE
from nlparse.usecases.types import Entity, Mention, Relationship, Text, Value

LOGGER = getLogger(__name__)


async def before_request(self, request, method, url, headers):
    if not self.valid:
        if inspect.iscoroutinefunction(self.refresh):
            await self.refresh(request)
        else:
            self.refresh(request)
    self.apply(headers)


class HealthcareNLPAdapter(IHealthcareNLPPort):
    def __init__(self, project_id, location):
        self.project_id = project_id
        self.location = location
        # self.creds, self.project = default_async()
        # ***
        # Monkey-patch workaround
        # https://github.com/googleapis/google-auth-library-python/issues/1417
        # ***
        # self.creds.before_request = partial(Credentials.before_request, self.creds)

    def get_operation_url(self, operation: str):
        return f'https://healthcare.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/services/nlp:{operation}'

    async def extract(self, text: str) -> Tuple[List[Entity], List[Mention], List[Relationship]]:
        return await asyncio.get_event_loop().run_in_executor(None, partial(self.extract_sync, text))

    def extract_sync(self, text: str) -> Tuple[List[Entity], List[Mention], List[Relationship]]:
        creds, _ = default()

        with AuthorizedSession(creds) as authed_session:
            response = authed_session.request(
                'POST', self.get_operation_url('analyzeEntities'), json={'documentContent': text}
            )
            data = response.json()
            LOGGER.info('NLP result: status=%d, body=%s', response.status_code, data)
            return (
                [
                    Entity(
                        id=entity['entityId'],
                        preferred_term=entity['preferredTerm'],
                        vocabulary_codes=entity['vocabularyCodes'],
                    )
                    for entity in data.get('entities', [])
                ],
                [
                    Mention(
                        id=mention['mentionId'],
                        type=mention['type'],
                        text=Text(content=mention['text']['content'], begin_offset=mention['text']['beginOffset']),
                        linked_entities=[obj['entityId'] for obj in mention['linkedEntities']] if mention.get('linkedEntities') else [],
                        temporal_assessment=Value.parse_obj(mention['temporalAssessment'])
                        if mention.get('temporalAssessment')
                        else None,
                        certainty_assessment=Value.parse_obj(mention['certaintyAssessment'])
                        if mention.get('certaintyAssessment')
                        else None,
                        subject=mention['subject'] if mention.get('subject') else None,
                        confidence=mention['confidence'],
                    )
                    for mention in data.get('entityMentions', [])
                ],
                [
                    Relationship(
                        subject_id=relationship['subjectId'],
                        object_id=relationship['objectId'],
                        confidence=relationship['confidence'],
                    )
                    for relationship in data.get('relationships', [])
                ],
            )
