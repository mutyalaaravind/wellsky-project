from dataclasses import asdict
import os
from typing import List
from pydantic import BaseModel, ValidationError
import pydantic
from json import JSONDecodeError

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from extract_and_fill.usecases.extract import (
    ExtractionError,
    collect_extraction_results,
    extract_sync,
    extract as extract_usecase,
    get_chunk_count,
    get_extraction_results,
    getEmbeddingsStatus,
    initiate_embeddings,
    save_transcript,
    search,
    get_sentences,
    create_embeddings,
    save_extracted_text,
    save_prompt_template,
    get_or_create_transcript_id,
)


class RestAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Route('/extract', self.extract, methods=['POST']),
                Route('/extract/{transcript_id}', self.extraction_status, methods=['GET']),
                Route('/extract/{transcript_id}/collect', self.extraction_result, methods=['GET', 'POST']),
                Route('/search', self.search, methods=['POST']),
                Route('/saveTranscript', self.save_transcript, methods=['POST']),
                Route('/getSentenceByGroupId', self.get_sentences_by_group_id, methods=['POST']),
                Route('/createEmbeddings', self.create_embeddings, methods=['POST']),
                Route('/getEmbeddingsStatus', self.get_embeddings_status, methods=['GET']),
                Route('/extractSync', self.extract_sync, methods=['POST']),
                Route('/savePromptTemplate', self.save_prompt_template, methods=['POST']),
                Route('/getTranscriptId', self.get_or_create_transcript_id, methods=['GET']),
                Route('/getChunkCount', self.get_chunk_count, methods=['GET']),
                Route('/ping', self.ping, methods=['GET']),
            ],
        )

    async def extract(self, request: Request):
        payload = await request.json()
        transcript_id = payload['transcript_id']
        transcript_text = payload['transcript_text']
        json_template = payload['json_template']
        model = payload['model']
        enable_embedding = payload["enable_embedding"]
        transcript_version = payload['transcript_version']
        try:
            response = await extract_usecase(
                transcript_id, transcript_text, json_template, model, enable_embedding, transcript_version
            )
        except ExtractionError as e:
            return JSONResponse({'error': str(e)}, status_code=400)
        return JSONResponse(response)

    async def extract_sync(self, request: Request):
        payload = await request.json()
        transcript_id = payload['transcript_id']
        transcript_text = payload['transcript_text']
        json_template = payload['json_template']
        model = payload['model']
        enable_embedding = payload["enable_embedding"]
        response = await extract_sync(transcript_id, transcript_text, json_template, model, enable_embedding)
        return JSONResponse(response)

    async def extraction_status(self, request: Request):
        transcript_id = request.path_params['transcript_id']
        return JSONResponse([result.dict() for result in await get_extraction_results(transcript_id)])

    async def extraction_result(self, request: Request):
        transcript_id = request.path_params['transcript_id']
        results = await collect_extraction_results(transcript_id)
        if request.method == 'POST':
            try:
                body = await request.json()
            except JSONDecodeError:
                return JSONResponse({'error': 'Invalid JSON'}, status_code=400)
            if 'overrides' not in body:
                return JSONResponse({'error': 'Missing "overrides" key'}, status_code=400)
            overrides = body['overrides']

            # Recursively merge results with overrides
            def merge_results(source, override):
                if isinstance(source, dict) and isinstance(override, dict):
                    for key, value in override.items():
                        if key in source:
                            source[key] = merge_results(source[key], value)
                        else:
                            source[key] = value
                else:
                    return override
                return source

            # hack: please remove below block when we go to prod
            if results:
                extraction_status_results = [result.dict() for result in await get_extraction_results(transcript_id)]
                if extraction_status_results and extraction_status_results[0].get("transcript_text"):
                    if len(extraction_status_results[0].get("transcript_text")) > 100:
                        results = merge_results(results, overrides)
            # hack block end

        return JSONResponse(results)

    async def ping(self, request: Request):
        return JSONResponse({'status': 'ok'})

    async def search(self, request: Request):
        payload = await request.json()
        transcript_id = payload['transcript_id']
        query_strings = payload['query_strings']
        response = await search(transcript_id, query_strings)
        return JSONResponse(response)

    async def save_transcript(self, request: Request):
        payload = await request.json()
        auto_scribe_transcript_id = payload['autoScribeTranscriptId']
        transcript = payload['transcript']
        response = await save_transcript(auto_scribe_transcript_id, transcript)
        return JSONResponse(response)

    async def get_sentences_by_group_id(self, request: Request):
        payload = await request.json()
        sentence_group_id = payload['groupId']
        response = await get_sentences(sentence_group_id) if sentence_group_id else []
        return JSONResponse(response)

    async def create_embeddings(self, request: Request):
        payload = await request.json()
        sentence_group_id = payload['groupId']
        status = await initiate_embeddings(sentence_group_id)
        return JSONResponse({'status': status})

    async def get_embeddings_status(self, request: Request):
        sentence_group_id = request.query_params.get('groupId')
        status = await getEmbeddingsStatus(sentence_group_id)
        return JSONResponse({'status': status})

    async def save_extracted_text(self, request: Request):
        payload = await request.json()
        transaction_id = payload['transactionId']
        formData = payload['formData']
        response = await save_extracted_text(transaction_id, formData)
        return JSONResponse(response)

    async def save_prompt_template(self, request: Request):
        payload = await request.json()
        transcript_id = payload['transcriptId']
        prompt_template = payload['promptTemplate']
        model = payload['model']
        response = await save_prompt_template(transcript_id, prompt_template, model)
        return JSONResponse(response)

    async def get_or_create_transcript_id(self, request: Request):
        auto_scribe_transcript_id = request.query_params.get('autoScribeTranscriptId')
        transcript_text = request.query_params.get('transcriptText')
        response = await get_or_create_transcript_id(auto_scribe_transcript_id, transcript_text)
        return JSONResponse(response)

    async def get_chunk_count(self, request: Request):
        transcript_id = request.query_params.get('transcriptId')
        return JSONResponse(await get_chunk_count(transcript_id))
