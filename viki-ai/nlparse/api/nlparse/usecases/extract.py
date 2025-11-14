from typing import AsyncIterable, List
from json import dumps, loads

from kink import inject

from nlparse.infrastructure.ports import IHealthcareNLPPort
from nlparse.log import getLogger
from nlparse.usecases.types import ExtractResult, Feature

LOGGER = getLogger(__name__)


def find_related_mentions(mentions: List, relationships: List, mention_id: str):
    return [
        mention
        for mention in mentions
        if mention.id in [relationship.object_id for relationship in relationships if relationship.subject_id == mention_id]
    ]


@inject
async def extract(
    content: str,
    healthcare_nlp: IHealthcareNLPPort,
) -> ExtractResult:
    entities, mentions, relationships = await healthcare_nlp.extract(content)
    print('Entities:')
    for entity in entities:
        print('  -', entity)
    print('Mentions:')
    for mention in mentions:
        print('  -', mention)
    print('Relationships:')
    for relationship in relationships:
        print('  -', relationship)

    problems = []
    medicines = []
    procedures = []

    for mention in mentions:
        if mention.type == 'PROBLEM':
            print('Problem:', mention.text.content)
            related_mentions = find_related_mentions(mentions, relationships, mention.id)
            problems.append(Feature(mention=mention, related_mentions=related_mentions))
        if mention.type == 'MEDICINE':
            print('Medicine:', mention.text.content)
            related_mentions = find_related_mentions(mentions, relationships, mention.id)
            medicines.append(Feature(mention=mention, related_mentions=related_mentions))
        if mention.type == 'PROCEDURE':
            print('Procedure:', mention.text.content)
            related_mentions = find_related_mentions(mentions, relationships, mention.id)
            procedures.append(Feature(mention=mention, related_mentions=related_mentions))
        #
        #
        # for relationship in relationships:
        #     if relationship.subject_id == mention.id:
        #         object_mention = next(
        #             (obj for obj in mentions if obj.id == relationship.object_id), None
        #         )
        #         print('  -', object_mention.text.content)

    return ExtractResult(mentions=mentions, problems=problems, medicines=medicines, procedures=procedures)

    # speech_recognition = speech_recognition_factory.get_implementation(ISpeechRecognitionFactory.Backend(backend))
    # LOGGER.debug('streaming_transcribe: listening, backend = %s, model = %s', backend, model)
    # async for event in speech_recognition.recognize_stream(audio_stream, model):
    #     LOGGER.debug('streaming_transcribe: event = %s', event)
    #     yield event
