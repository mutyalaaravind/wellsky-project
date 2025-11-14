from dataclasses import asdict
import os
from typing import List
from pydantic import BaseModel, ValidationError
import pydantic

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from autoscribe.usecases.transactions import TransactionUsecaseError, ensure_transaction, get_audio_signed_url, finalize
from autoscribe.usecases.types import TextSentence


class FinalizeRequest(BaseModel):
    transaction_id: str
    section_id: str
    text_sentences: List[TextSentence]


class RestAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Route('/transactions/{transaction_id}/sections/{section_id}', self.get_section, methods=['GET']),
                Route(
                    '/transactions/{transaction_id}/sections/{section_id}/audio-url',
                    self.get_audio_url,
                    methods=['GET'],
                ),
                Route('/finalize', self.finalize, methods=['POST']),
            ],
        )

    async def get_section(self, request: Request):
        transaction = await ensure_transaction(request.path_params['transaction_id'])
        section = transaction.sections.get(request.path_params['section_id'])
        if section:
            return JSONResponse(section.dict())
        return JSONResponse(None)

    async def get_audio_url(self, request: Request):
        try:
            return JSONResponse(
                {'url': await get_audio_signed_url(request.path_params['transaction_id'], request.path_params['section_id'])}
            )
        except TransactionUsecaseError as err:
            return JSONResponse({'error': str(err)}, 400)

    async def finalize(self, request: Request):
        try:
            finalize_request = FinalizeRequest(**await request.json())
        except ValidationError as err:
            return JSONResponse({'status': 'error', 'error': err.errors()}, 400)
        section = await finalize(
            finalize_request.transaction_id, finalize_request.section_id, finalize_request.text_sentences
        )
        return JSONResponse({'status': 'ok', 'version': section.version})
