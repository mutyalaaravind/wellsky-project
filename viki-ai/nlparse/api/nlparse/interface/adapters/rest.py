from dataclasses import asdict
import os
from typing import List
from pydantic import BaseModel, ValidationError
import pydantic

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from nlparse.usecases.extract import extract


class ExtractRequest(BaseModel):
    content: str


class RestAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Route('/extract', self.extract, methods=['POST']),
            ],
        )

    async def extract(self, request: Request):
        try:
            payload = ExtractRequest(**await request.json())
        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()})
        return JSONResponse((await extract(payload.content)).dict())
        # return JSONResponse({'success': True})
        # payload = await request.json()
        # transcript_id = payload['transcript_id']
        # transcript_text = payload['transcript_text']
        # json_template = payload['json_template']
        # model = payload['model']
        # response = await extract_usecase(transcript_id, transcript_text, json_template, model)
        # return JSONResponse(response)
