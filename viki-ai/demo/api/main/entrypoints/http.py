"""
Main HTTP multiplexer.

Handles GraphQL requests.
"""

from textwrap import dedent
from main.settings import DEBUG, STAGE, VERSION
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.requests import Request
from starlette.routing import Mount, Route
from main.interface.adapters.rest import RestAdapter


async def index(request):
    return PlainTextResponse(
        dedent(
            fr'''
            Demo API

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
            allow_headers=['*'],
        ),
    ],
    routes=[
        Route('/', index),
        Mount('/api', RestAdapter()),
    ],
)
