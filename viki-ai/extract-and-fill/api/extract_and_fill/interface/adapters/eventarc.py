import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from extract_and_fill.domain.commands import FireStoreTriggerToCommandConvertor
from extract_and_fill.domain.message_bus import MessageBus
from extract_and_fill.usecases.handlers import COMMAND_HANDLERS, EVENT_HANDLERS
from extract_and_fill.usecases.extract import process_chunk

from google.cloud import firestore
from google.events.cloud.firestore import DocumentEventData
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from extract_and_fill.log import getLogger

LOGGER = getLogger(__name__)


class DecoderThatHandlesStupidGoogleTypes:
    """
    Reason:
        - https://issuetracker.google.com/issues/128852268
        - https://groups.google.com/g/google-appengine/c/5UIcqGFtezE

    Source: https://stackoverflow.com/a/62983902/3455614
    """

    def __init__(self, client) -> None:
        self.client = client
        self._action_dict = {
            'geo_point_value': (lambda x: dict(x)),
            'string_value': (lambda x: str(x)),
            'array_value': (lambda x: [self._parse_value(value_dict) for value_dict in x.get("values", [])]),
            'boolean_value': (lambda x: bool(x)),
            'null_value': (lambda x: None),
            'timestamp_value': (lambda x: self._parse_timestamp(x)),
            'reference_value': (lambda x: self._parse_doc_ref(x)),
            'map_value': (lambda x: {key: self._parse_value(value) for key, value in x["fields"].items()}),
            'integer_value': (lambda x: int(x)),
            'double_value': (lambda x: float(x)),
        }

    def convert(self, data_dict: dict) -> dict:
        result_dict = {}
        for key, value_dict in data_dict.items():
            result_dict[key] = self._parse_value(value_dict)
        return result_dict

    def _parse_value(self, value_dict: dict) -> Any:
        data_type, value = value_dict.popitem()

        return self._action_dict[data_type](value)

    def _parse_timestamp(self, timestamp: str):
        try:
            return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError as e:
            return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

    def _parse_doc_ref(self, doc_ref: str) -> firestore.DocumentReference:
        path_parts = doc_ref.split('/documents/')[1].split('/')
        collection_path = path_parts[0]
        document_path = '/'.join(path_parts[1:])

        doc_ref = self.client.collection(collection_path).document(document_path)
        return doc_ref


class EventarcAdapter(Starlette):
    async def process_message(
        self, collection_name: str, document_id: str, before: Optional[dict], after: Optional[dict]
    ):
        try:
            LOGGER.info(
                'Collection = %s, doc = %s, before = %s, after = %s',
                collection_name,
                document_id,
                json.dumps(before)[:256],
                json.dumps(after)[:256],
            )
        except:
            LOGGER.error('Failed to log message', exc_info=True)
        # Returning 4xx will cause Eventarc to retry the message.
        if collection_name == 'extract_schema_chunks':
            # TODO - we'll need to decide whether to directly call usecases or to send a command.
            if not before and after:
                print(f'New chunk inserted, id={document_id}, we need to start processing it now')
                #await process_chunk(document_id)
            return Response(status_code=200)
        commands = FireStoreTriggerToCommandConvertor().convert(collection_name, document_id, before, after)
        LOGGER.info('Command=%s', commands)
        [await MessageBus(command_handlers=COMMAND_HANDLERS, event_handlers=EVENT_HANDLERS).handle(command) for command in commands]
        return Response(status_code=200)

    async def on_eventarc_firestore(self, request: Request):
        """
        This endpoint is called by real Eventarc (in GCP) when a Firestore document is created, updated or deleted.
        """
        body = await request.body()
        proto: DocumentEventData = DocumentEventData.deserialize(body)
        data: dict = DocumentEventData.to_dict(proto)
        LOGGER.info('Received message from eventarc: %s', data)

        full_path = (proto.value or proto.old_value).name
        path_parts = full_path.split('/documents/')[1].split('/')  # e. g. ["fide_events", "foobar"]
        collection_name, document_id = path_parts

        before = (
            DecoderThatHandlesStupidGoogleTypes(firestore.Client()).convert(data['old_value']['fields'])
            if proto.old_value
            else None
        )
        after = (
            DecoderThatHandlesStupidGoogleTypes(firestore.Client()).convert(data['value']['fields'])
            if proto.value
            else None
        )
        return await self.process_message(collection_name, document_id, before, after)

    async def on_eventarc_firestore_json(self, request: Request):
        """
        This endpoint is called by JS function in local Firebase emulator to simulate actual Pub/Sub push subscription.
        """
        data = await request.json()
        return await self.process_message(
            data['collection_name'],
            data['document_id'],
            data.get('before'),
            data.get('after'),
        )

    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Route('/firestore', self.on_eventarc_firestore, methods=['POST']),
                Route('/firestore/json', self.on_eventarc_firestore_json, methods=['POST']),
            ],
        )
