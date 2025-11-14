from typing import AsyncIterable, List
from json import dumps, loads, JSONDecodeError
from textwrap import dedent
import uuid
from extract_and_fill.domain.models import PromptChunkStatus

from kink import inject
from extract_and_fill.domain.services import PromptChunkGenerator, JSONHealer

from extract_and_fill.infrastructure.ports import (
    IEmbeddingsMetadataAdapter,
    IMessageBusAdapter,
    IPromptChunkCheckSumRepository,
    IPromptPort,
    IEmbeddingsAdapter,
    ISentencePort,
    ITranscriptPort,
    IPromptChunkRepository,
    ICommandsRepository,
)
from extract_and_fill.log import getLogger

LOGGER = getLogger(__name__)


class ExtractionError(Exception):
    pass


@inject()
async def save_prompt_template(
    transcript_id: str, prompt_template: str, model: str, prompt_adapter: IPromptPort
) -> str:
    return await prompt_adapter.save_prompt_template(transcript_id, prompt_template, model)


@inject()
async def get_prompt_template(transcript_id: str, prompt_adapter: IPromptPort) -> str:
    prompt_template_record = await prompt_adapter.get_prompt_template(transcript_id)
    prompt_template = prompt_template_record.get("extract_prompt_template") if prompt_template_record else None
    model = prompt_template_record.get("model") if prompt_template_record else None
    return prompt_template, model


@inject()
async def save_transcript(
    autoscribe_transcript_id: str,
    transcript_text: str,
    autoScribe_transcription_version: int,
    transcript_adapter: ITranscriptPort,
    embeddings_adapter: IEmbeddingsAdapter,
    sentence_adapter: ISentencePort,
) -> str:
    transcript_id = None
    if autoscribe_transcript_id:
        LOGGER.debug(f'saving autoscribe transcript:{autoscribe_transcript_id}')
        transcript_id, transcript_version = await transcript_adapter.get_transcript_id_by_autoscribe_id(
            autoscribe_transcript_id
        )
        LOGGER.debug(f'saving autoscribe transcript:{autoscribe_transcript_id}')
        transcript_id = await transcript_adapter.save(transcript_id, transcript_text)
        await transcript_adapter.save_autoscribe_transcript_id(
            autoscribe_transcript_id, autoScribe_transcription_version, transcript_id
        )
        sentences = await sentence_adapter.save(transcript_id, transcript_text.split("\n"))
        return transcript_id
    else:
        LOGGER.debug('saving transcript')
        transcript_id = await transcript_adapter.save(transcript_id, transcript_text)
        LOGGER.debug('getting sentences')
        sentences = await sentence_adapter.save(transcript_id, transcript_text.split("\n"))
    return transcript_id


@inject()
async def get_or_create_transcript_id(
    autoscribe_transcript_id: str,
    transcript_text: str,
    transcript_adapter: ITranscriptPort,
    embeddings_adapter: IEmbeddingsAdapter,
    sentence_adapter: ISentencePort,
) -> str:
    transcript_id = None
    transcript_version = 0
    if autoscribe_transcript_id:
        LOGGER.info('getting transcript id')
        transcript_id, transcript_version = await transcript_adapter.get_transcript_id_by_autoscribe_id(
            autoscribe_transcript_id
        )
        if not transcript_id:
            LOGGER.info('saving autoscribe transcript id')
            transcript_id = await transcript_adapter.save_autoscribe_transcript_id(
                autoscribe_transcript_id, transcript_version, str(uuid.uuid4())
            )
        return {"transcriptId": transcript_id, "transcriptVersion": transcript_version}
    else:
        LOGGER.debug('saving transcript')
        transcript_id = await transcript_adapter.save(transcript_id, transcript_text)
        LOGGER.debug('getting sentences')
        sentences = await sentence_adapter.save(transcript_id, transcript_text.split("\n"))
    return {"transcriptId": transcript_id, "transcriptVersion": transcript_version}


@inject()
async def create_embeddings(
    sentence_group_id: str,
    embeddings_adapter: IEmbeddingsAdapter,
    sentence_adapter: ISentencePort,
    embeddings_metadata_adapter: IEmbeddingsMetadataAdapter,
) -> str:
    # message_bus_adapter.publish(PUBSUB_TOPIC, dumps({"sentence_group_id":sentence_group_id}))
    metadata = await embeddings_metadata_adapter.get_by_group_id(sentence_group_id)

    if metadata and metadata[0].get("status") not in ["in_progress", "completed"]:
        # ToDo: To avoid race conditions
        await embeddings_metadata_adapter.update(sentence_group_id, 'in_progress')
        LOGGER.debug('getting sentences')
        sentences = await sentence_adapter.get_by_group_id(sentence_group_id)
        LOGGER.debug(f'creating embeddings for {sentence_group_id}')
        await embeddings_adapter.upsert(
            sentence_group_id,
            sentences,
        )
        await embeddings_metadata_adapter.save(sentence_group_id, 'completed')
        return True
    LOGGER.info(f'embeddings for {sentence_group_id} already in progress')
    return False


@inject()
async def initiate_embeddings(
    sentence_group_id: str,
    embeddings_metadata_adapter: IEmbeddingsMetadataAdapter,
    message_bus_adapter: IMessageBusAdapter,
) -> str:
    # metadata = await embeddings_metadata_adapter.get_by_group_id(sentence_group_id)
    await embeddings_metadata_adapter.save(sentence_group_id, 'started')

    return False


@inject()
async def getEmbeddingsStatus(sentence_group_id: str, embeddings_metadata_adapter: IEmbeddingsMetadataAdapter) -> str:
    metadata = await embeddings_metadata_adapter.get_by_group_id(sentence_group_id)
    if not metadata:
        return False
    isCompleted = [x for x in metadata if x.get("status") == "completed"]
    if isCompleted:
        return True
    else:
        return False


@inject()
async def extract_sync(
    transcript_id: str,
    transcript_text: str,
    json_template: str,
    model: str,
    enable_embedding: bool,
    extract_adapter: IPromptPort,
    embeddings_adapter: IEmbeddingsAdapter,
    sentence_adapter: ISentencePort,
) -> str:
    return await extract_adapter.extract(transcript_text, model)


@inject()
async def extract(
    transcript_id: str,
    transcript_text: str,
    json_template: str,
    model: str,
    enable_embedding: bool,
    transcript_version: int,
    prompt_chunk_repository: IPromptChunkRepository,
    embeddings_adapter: IEmbeddingsAdapter,
    sentence_adapter: ISentencePort,
) -> str:
    # if enable_embedding:
    #     LOGGER.debug('getting sentences')
    #     sentences = sentence_adapter.save(transcript_id,transcript_text.split("\n"))
    #     LOGGER.debug('creating embeddings')
    #     embeddings_adapter.upsert(
    #                 transcript_id,
    #                 sentences,
    #             )
    # LOGGER.debug('extracting: json_template=%s', json_template)

    # Remove previous chunks if all of them have been processed
    # TODO: we should probably introduce a separate chunk-tracking aggregate
    chunks = []
    async for chunk in prompt_chunk_repository.list_by_transcript_id(transcript_id):
        if not chunk.is_finished:
            raise ExtractionError('Chunks are still being processed. Please try again later.')
        chunks.append(chunk)
    for chunk in chunks:
        await prompt_chunk_repository.delete(chunk.id)

    for chunk in PromptChunkGenerator().make_chunks(
        transcript_id, transcript_text, json_template, model, transcript_version
    ):
        LOGGER.debug('saving chunk=%s', chunk)
        await prompt_chunk_repository.save(chunk)
    return None
    # return await extract_adapter.extract(
    #     transcript_id,
    #     transcript_text,
    #     json_template,
    #     model
    # )


@inject()
async def process_chunk(chunk_id: str, extract_adapter: IPromptPort, prompt_chunk_repository: IPromptChunkRepository):
    chunk = await prompt_chunk_repository.get(chunk_id)
    chunk.chunk_schema = loads(dumps(chunk.chunk_schema).replace("answers", "select from following"))
    query = dedent(
        f"""
        you are medical nurse filling OASIS start of care Version E assessment.
        Your job is extract relevant content from the CONTEXT based on the JSON_SCHEMA provided and return final result json response with answers.
        some additional instructions:
        1. Only select answers from the _meta field where _meta exists for a given field
        2. please add verbatim_source key to the json to show source of the extracted text
        3. Please use mm/dd/yyyy format for date fields
        4. Please keep the json schema keys of the output same as the provided json_schema keys with hierarchy intact.
        5. please do not omit any keys from the json_schema.
        6. please do not add any additional keys to the json_schema than mentioned above
        7. please do not include _meta in final result
        8. please give only final result json
        9. please return a valid json 
        
        Examples:
        example CONTEXT: patient name is john wicks.\n he is 45 years old.\n Are you alert and oriented to person, place, and time?.\n yes.\n he is discharged on october 11, 2023
        example JSON_SCHEMA: {dumps({'Patient Name':{'(First)':''},'Discharge Date':'','Orientation':{'Person':'','_meta':{'Person':{'select from following':['Oriented','Disoriented']}}}})}
        example final result: {dumps({'Patient Name':{'(First)':{'value':'john','verbatim_source':'patient name is john wicks.'}},'Discharge Date':{'value':'10/11/2023','verbatim_source':'he is discharged on october 11, 2023'},'Orientation':{'Person':{'value':'Oriented','verbatim_source':'Are you alert and oriented to person, place, and time?.'}}})}

        CONTEXT: {chunk.transcript_text}
        JSON_SCHEMA: {dumps(chunk.chunk_schema)}
        
        
    """
    ).strip()
    LOGGER.info('Starting processing for chunk, id=%s', chunk_id)
    chunk.set_processing()
    await prompt_chunk_repository.save(chunk)
    try:
        result = await extract_adapter.extract(
            query,
            chunk.model,
        )
        try:
            result = result.replace("```json", "").replace("```", "")  # dirty hack but later need to do better job
            result = result.replace("finalresult:", "")
            result = result[result.index("{") :]
            healer = JSONHealer()
            if healer.is_invalid(result):
                LOGGER.warning('Attempting to heal JSON: %s', result)
                result = healer.heal(result)
            result = loads(result) if type(result) == str else result
        except JSONDecodeError:
            raise ValueError(f'Invalid JSON returned from extract_adapter: {result}')
        chunk.set_result(result)
        LOGGER.info('Finished processing for chunk, id=%s', chunk_id)
    except Exception as exc:
        LOGGER.error('Error processing chunk, id=%s, error=%s', chunk_id, exc)
        chunk.set_error(str(exc))
    await prompt_chunk_repository.save(chunk)
    return None


@inject()
async def get_extraction_results(
    transcript_id: str, prompt_chunk_repository: IPromptChunkRepository
) -> AsyncIterable[dict]:
    chunks = []
    async for chunk in prompt_chunk_repository.list_by_transcript_id(transcript_id):
        chunks.append(chunk)
    return chunks


@inject()
async def collect_extraction_results(transcript_id: str, prompt_chunk_repository: IPromptChunkRepository) -> dict:
    # return PromptChunkGenerator().merge_chunks(
    #     [chunk async for chunk in prompt_chunk_repository.list_by_transcript_id(transcript_id) if chunk.result]
    # )
    import json

    return [
        json.loads(chunk.result)
        async for chunk in prompt_chunk_repository.list_by_transcript_id(transcript_id)
        if chunk.result
    ]


@inject()
async def search(
    transcript_id: str,
    query_strings: List[str],
    embeddings_adapter: IEmbeddingsAdapter,
    sentence_adapter: ISentencePort,
) -> str:
    LOGGER.debug('search via embedding')
    results = await embeddings_adapter.search(transcript_id, query_strings)
    sentences = [{"sentence": await sentence_adapter.get(x.get("id")), "distance": x.get("distance")} for x in results]
    return sentences if sentences else None


@inject()
async def get_sentences(transcript_id: str, sentence_adapter: ISentencePort) -> List[dict]:
    return await sentence_adapter.get_by_group_id(transcript_id)


@inject()
async def save_extracted_text(transaction_id, formData):
    pass


@inject()
async def get_extracted_text(transaction_id, formData):
    pass


@inject()
async def create_command(command, commands_repo: ICommandsRepository):
    await commands_repo.save(command)


@inject()
async def delete_chunks(transcript_id: str, prompt_chunk_repository: IPromptChunkRepository):
    chunks = []
    async for chunk in prompt_chunk_repository.list_by_transcript_id(transcript_id):
        if not chunk.is_finished:
            raise ExtractionError('Chunks are still being processed. Please try again later.')
        chunks.append(chunk)
    for chunk in chunks:
        await prompt_chunk_repository.delete(chunk.id)


@inject()
async def get_chunk_count(transcript_id: str, prompt_chunk_check_sum_repository: IPromptChunkCheckSumRepository):
    chunks = []
    async for chunk_check_sum in prompt_chunk_check_sum_repository.list_by_transcript_id(transcript_id):
        return chunk_check_sum.total_chunks if chunk_check_sum else 0
