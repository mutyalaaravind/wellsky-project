"""
Pub/Sub message handler.
"""

from textwrap import dedent

from extract_and_fill.interface.adapters.eventarc import EventarcAdapter
from extract_and_fill.interface.adapters.pubsub import PubSubAdapter
from extract_and_fill.settings import DEBUG
from starlette.applications import Starlette
from starlette.routing import Mount


app = Starlette(
    debug=DEBUG,
    on_startup=[],
    on_shutdown=[],
    routes=[
        Mount('/eventarc', EventarcAdapter()),
        Mount('/pubsub', PubSubAdapter()),
    ],
)