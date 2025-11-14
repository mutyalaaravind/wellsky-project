"""
Main HTTP multiplexer.

Handles GraphQL requests.
"""

from textwrap import dedent

from autoscribe.interface.adapters.ws import WebSocketAdapter
from autoscribe.interface.adapters.rest import RestAdapter
from autoscribe.settings import DEBUG, OKTA_AUDIENCE, OKTA_DISABLE, OKTA_ISSUER, OKTA_SCOPE, STAGE, VERSION
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route


async def index(request):
    return PlainTextResponse(
        dedent(
            fr'''
            AutoScribe

            Recognizes speech in real time.

            Version: {VERSION}
            Stage: {STAGE}
            '''
        ).strip('\n')
    )


app = Starlette(
    debug=DEBUG,
    on_startup=[],
    on_shutdown=[],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_methods=("GET", "POST", "OPTIONS"),
            allow_headers=[
                'access-control-allow-origin',
                'authorization',
                'content-type',
                'x-api-key',
                'graphql-submit-form',
                'httponly',
                'secure',
                'strict-transport-security',
                'x-content-type-options',
                'x-frame-options',
                'sentry-trace',
            ],
        ),
    ],
    routes=[
        Route('/', index),
        Mount('/api', RestAdapter()),
        Mount('/ws', WebSocketAdapter(OKTA_DISABLE, OKTA_ISSUER, OKTA_AUDIENCE, OKTA_SCOPE)),
    ],
)
