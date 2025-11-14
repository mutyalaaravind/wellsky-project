from base64 import b64decode
from datetime import timedelta
from functools import wraps
from logging import getLogger
import json

import pydantic  # type: ignore
from aiohttp_client_cache import CacheBackend, CachedSession  # In-memory cache
from google.auth.transport import _aiohttp_requests  # type: ignore
from google.oauth2 import _id_token_async  # type: ignore
from kink import inject
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from extract_and_fill.settings import DEBUG


LOGGER = getLogger(__name__)


def pubsub_handler(func):
    @wraps(func)
    async def wrapper(self, request: Request, *args, **kwargs):
        """
        Sample event:

        {
            'message': {
                'attributes': {
                    'bucketId': 'fide-andrewsenv-datasource',
                    'eventTime': '2022-10-12T14:25:58.059113Z',
                    'eventType': 'OBJECT_FINALIZE',
                    'notificationConfig': 'projects/_/buckets/fide-andrewsenv-datasource/notificationConfigs/1',
                    'objectGeneration': '1665584757972951',
                    'objectId': 'sample.csv',
                    'payloadFormat': 'JSON_API_V1',
                },
                'data': 'REDACTED (base64)',
                'messageId': '5899758286126148',
                'message_id': '5899758286126148',
                'publishTime': '2022-10-12T14:25:58.349Z',
                'publish_time': '2022-10-12T14:25:58.349Z',
            },
            'subscription': 'projects/fide-365022/subscriptions/fide-datasource-events',
        }

        Sample JWT claims:

        {
            'aud': 'https://fide-app-4gnyu3wmkq-wl.a.run.app/pubsub/events',
            'azp': '115326588369689891196',
            'email': 'fide-sandbox-service-account@wscc-sandbox-app-wsky.iam.gserviceaccount.com',
            'email_verified': True,
            'exp': 1666697894,
            'iat': 1666694294,
            'iss': 'https://accounts.google.com',
            'sub': '115326588369689891196'
        }
        """

        envelope = await request.json()

        LOGGER.info('Received pubsub, headers=%s, envelope=%s', request.headers, envelope)

        # if not DISABLE_PUBSUB_AUTH:
        #     # Validate Pub/Sub token
        #     # https://developers.google.com/identity/sign-in/web/backend-auth#using-a-google-api-client-library
        #     _, _, id_token = request.headers.get('Authorization', '').partition(' ')
        #     try:
        #         # Google JWT validation transport with public key caching
        #         async with CachedSession(
        #             auto_decompress=False, cache=CacheBackend(expire_after=timedelta(seconds=60))
        #         ) as session:
        #             # get_valid_kwargs in aiohttp_client_cache is broken
        #             session._auto_decompress = False  # pylint: disable=protected-access
        #             auth_request = _aiohttp_requests.Request(session)
        #             claims = await _id_token_async.verify_token(id_token, auth_request)  # TODO: Verify audience
        #     except Exception:
        #         LOGGER.exception('Failed to validate JWT token')
        #         return JSONResponse(dict(error='Invalid token'), 400)
        #     if claims['iss'] != 'https://accounts.google.com':
        #         LOGGER.error('Disallowed issuer: %s', claims['iss'])
        #         return JSONResponse(dict(error='Disallowed token issuer.'), 400)
        #     if claims['email'] != PUBSUB_JWT_SA_EMAIL:
        #         LOGGER.error('Disallowed token email: %s, expected %s', claims['email'], PUBSUB_JWT_SA_EMAIL)
        #         return JSONResponse(dict(error='Disallowed token email.'), 400)

        # Decode message
        if not envelope:
            LOGGER.error('Missing envelope')
            return JSONResponse(dict(error='Missing envelope'), 400)
        if not isinstance(envelope, dict) or 'message' not in envelope:
            LOGGER.error('Invalid envelope')
            return JSONResponse(dict(error='Invalid envelope'), 400)
        message = envelope['message']
        encoded_data = message['data']
        data = b64decode(encoded_data).decode('utf-8')

        return await func(self, request, message, data, *args, **kwargs)

    return wrapper


class PubSubAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=DEBUG,
            routes=[
                Route('/events', self.events_handler, methods=['POST']),
                Route('/commands', self.commands_handler, methods=['POST']),
                # Route('/datasource-events', self.datasource_events_handler, methods=['POST']),
            ],
        )

    @pubsub_handler
    @inject()
    async def events_handler(
        self, request: Request, message: dict, data: str
    ):
        event: Event = pydantic.parse_raw_as(Event, data)  # type: ignore
        
        return Response(status_code=204)

    @pubsub_handler
    @inject()
    async def commands_handler(
        self,
        request: Request,
        message: dict,
        data: str
    ):
        print(f"commands pubsub {data},{message}")
        #command: Command = pydantic.parse_raw_as(Command, data)  # type: ignore
        from extract_and_fill.usecases.extract import create_embeddings
        await create_embeddings(json.loads(data).get("sentence_group_id"))
        return Response(status_code=204)
