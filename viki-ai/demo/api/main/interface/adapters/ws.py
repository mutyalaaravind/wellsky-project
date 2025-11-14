from dataclasses import asdict
import os
from typing import List
from pydantic import BaseModel, ValidationError
import pydantic

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.websockets import WebSocket
from autoscribe.infrastructure.ports import ISpeechRecognitionPort

from autoscribe.usecases.streaming import streaming_transcribe


class WebSocketAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Mount('/transcribe', self.ws_transcribe),
            ],
        )

    async def ws_transcribe(self, scope, receive, send):
        websocket = WebSocket(scope=scope, receive=receive, send=send)
        await websocket.accept()
        async for result in streaming_transcribe(websocket.iter_bytes()):
            try:
                await websocket.send_json(asdict(result))
            except RuntimeError:
                break
        try:
            await websocket.close()
        except RuntimeError:
            pass
