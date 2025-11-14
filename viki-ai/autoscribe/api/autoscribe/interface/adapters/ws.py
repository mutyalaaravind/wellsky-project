import os
from pydantic import BaseModel, ValidationError
import pydantic

from okta_jwt_verifier import BaseJWTVerifier
from okta_jwt_verifier.exceptions import JWTValidationException
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.websockets import WebSocket

from autoscribe.infrastructure.ports import ISpeechRecognitionPort
from autoscribe.usecases.streaming import streaming_transcribe
from autoscribe.usecases.types import ErrorEvent


class AuthError(Exception):
    pass


class Metadata(BaseModel):
    token: str
    backend: str
    model: str
    transaction_id: str
    section_id: str


class WebSocketAdapter(Starlette):
    def __init__(self, okta_disable, okta_issuer, okta_audience, okta_scope):
        self.okta_disable = okta_disable
        self.jwt_verifier = BaseJWTVerifier(okta_issuer, audience=okta_audience)
        self.okta_scope = okta_scope
        super().__init__(
            debug=True,
            routes=[
                Mount('/transcribe', self.ws_transcribe),
            ],
        )

    async def _validate_token(self, token) -> None:
        """
        Check if token is valid, raise AuthError otherwise.
        """
        try:
            await self.jwt_verifier.verify_access_token(token)
        except JWTValidationException as err:
            raise AuthError(f'Invalid token: {err}')
        try:
            claims = self.jwt_verifier.parse_token(token)[1]
        except JWSError:
            raise AuthError('Invalid JWT payload')
        if self.okta_scope not in claims.get('scp'):
            raise AuthError(f'Missing required scope {self.okta_scope}')

    async def ws_transcribe(self, scope, receive, send):
        websocket = WebSocket(scope=scope, receive=receive, send=send)
        try:
            await websocket.accept()
            # Receive metadata
            try:
                metadata = Metadata.parse_obj(await websocket.receive_json())
            except ValidationError as err:
                await websocket.send_json(ErrorEvent(message=err.json()).dict())
                return

            # Authorize client
            if not self.okta_disable:
                try:
                    await self._validate_token(metadata.token)
                except AuthError as err:
                    await websocket.send_json(ErrorEvent(message=str(err)).dict())
                    return

            # Start receiving data
            async for result in streaming_transcribe(
                metadata.transaction_id,
                metadata.section_id,
                websocket.iter_bytes(),
                metadata.backend,
                metadata.model,
            ):
                try:
                    await websocket.send_json(result.dict())
                except:
                    pass
        finally:
            try:
                await websocket.close()
            except RuntimeError:
                pass
