from copy import deepcopy
import os, json
import aiofiles
from extract_and_fill.infrastructure.ports import IPromptPort, IPromptChunkRepository
from extract_and_fill.domain.models import PromptChunk
from extract_and_fill.domain.services import (
    PromptTemplateWithVerbatimSourceExtractionManager,
    PromptTemplateWithSingleStepExtractionManager,
)
from kink import inject


@inject()
async def extract_by_qa_strategy_and_store_result(
    index,
    section_id,
    transcript_id,
    transcript_text,
    transcript_version,
    model,
    form_schema,
    prompt_chunk_repo: IPromptChunkRepository,
):
    # chunks = prompt_chunk_repo.list_by_transcript_id(transcript_id)

    # async for chunk in chunks:
    #     await prompt_chunk_repo.delete(chunk.id)

    # prompt_manager = PromptTemplateWithVerbatimSourceExtractionManager(section_id=section_id)
    prompt_manager = PromptTemplateWithSingleStepExtractionManager(section_id=section_id)
    # ToDo: chunk for size
    result = await prompt_manager.get_answers_extracted(section_id, transcript_text, model, execute_prompt)

    form_merged_result = {}
    # form_merged_result = prompt_manager.merge_results_with_form_schema(result, form_schema)
    # form_merged_result = prompt_manager.results_with_hierarchy(result, form_schema, hierarchy_results={})
    form_merged_result = {section_id: result}
    chunk = PromptChunk.create(
        index,
        transcript_id,
        transcript_text,
        [],
        form_schema,
        model,
        transcript_version,
        other={"interim_result": result},
    )

    if "error" in result:
        chunk.set_error(result.get("error"))
    else:
        chunk.set_result(json.dumps(form_merged_result))
    await prompt_chunk_repo.save(chunk)


@inject()
async def execute_prompt(prompt_text, model, prompt_adapter: IPromptPort):
    result = await prompt_adapter.extract(prompt_text, model)
    return result
