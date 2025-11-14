# from __future__ import annotations
from dataclasses import asdict
from typing import List, Dict, Callable, Type, TYPE_CHECKING
import extract_and_fill.domain.commands as commands
import extract_and_fill.domain.events as events
from extract_and_fill.domain.message_bus import MessageBus
from extract_and_fill.log import getLogger
from extract_and_fill.domain.models import PromptChunk, PromptChunkCheckSum
from extract_and_fill.infrastructure.ports import IPromptChunkCheckSumRepository
from kink import inject

LOGGER = getLogger(__name__)
PROGRAM = "oasis_e"


async def create_embeddings(command: commands.CreateEmbeddingCommand):
    from extract_and_fill.usecases.extract import create_embeddings

    LOGGER.debug(f'creating extract domain embeddings for {command.sentence_group_id}')
    await create_embeddings(command.sentence_group_id)


@inject()
async def create_extract_transcript(
    command: commands.CreateTranscriptionCommand, prompt_chunk_checksom_repo: IPromptChunkCheckSumRepository
):
    from extract_and_fill.usecases.extract import (
        save_transcript,
        initiate_embeddings,
        get_prompt_template,
        delete_chunks,
    )

    from extract_and_fill.usecases.extract import create_command

    LOGGER.debug(f'creating extract transcript for {command.autoScribeTranscriptionId}')
    transcript_id = await save_transcript(
        command.autoScribeTranscriptionId, command.transcriptText, command.autoScribeTranscriptionVersion
    )
    LOGGER.debug(f'initiating embeddings for {transcript_id}')
    await initiate_embeddings(transcript_id)
    LOGGER.debug(f'checking for existing prompt template {transcript_id}')
    prompt_template, model = await get_prompt_template(transcript_id)
    if prompt_template:
        LOGGER.debug(
            f'initiating extraction for {command.autoScribeTranscriptionId}:{command.autoScribeTranscriptionVersion}'
        )

        # ToDo: classify transcript in different sections

        # for each section in the prompt template, trigger extraction
        sections = prompt_template.get("items")
        counter = 0

        await delete_chunks(transcript_id)

        for section in sections:
            if section.get("dataType") == "SECTION":
                if section.get("localQuestionCode"):
                    if section.get("localQuestionCode") not in ["C", "N", "B"]:
                        continue
                    # ToDo: need transaction
                    await create_command(
                        commands.ExtractSectionCommand(
                            index=counter,
                            sectionId=section.get("localQuestionCode"),
                            transcriptId=transcript_id,
                            transcriptText=command.transcriptText,  # ToDo: classified transcription needs to be passed
                            transcriptVersion=command.autoScribeTranscriptionVersion,
                            promptTemplate=section,
                            model=model,
                        )
                    )
                    counter = counter + 1
        await prompt_chunk_checksom_repo.save(PromptChunkCheckSum(id=transcript_id, total_chunks=counter))
    else:
        LOGGER.info(f'no prompt template exists for {transcript_id}')


async def extract_section(command: commands.ExtractSectionCommand):
    from extract_and_fill.usecases.prompt_manager import extract_by_qa_strategy_and_store_result

    LOGGER.debug(f"Extracting section for {command.sectionId}")
    await extract_by_qa_strategy_and_store_result(
        index=command.index,
        section_id=command.sectionId,
        transcript_id=command.transcriptId,
        transcript_text=command.transcriptText,
        transcript_version=command.transcriptVersion,
        model=command.model,
        form_schema=command.promptTemplate,
    )


EVENT_HANDLERS = {events.Event: []}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CreateEmbeddingCommand: [create_embeddings],
    commands.CreateTranscriptionCommand: [create_extract_transcript],
    commands.ExtractSectionCommand: [extract_section],
}  # type: Dict[Type[commands.Command], Callable]
