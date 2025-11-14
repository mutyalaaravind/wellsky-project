from kink import di
from extract_and_fill.infrastructure.adapters.prompt_chunk_repository import (
    PromptChunkCheckSumRepositoryAdapter,
    PromptChunkRepositoryAdapter,
)

from extract_and_fill.infrastructure.ports import (
    IEmbeddingsMetadataAdapter,
    IMessageBusAdapter,
    IPromptChunkCheckSumRepository,
    IPromptChunkRepository,
    IPromptPort,
    IEmbeddingsAdapter,
    ISentencePort,
    ITranscriptPort,
    ICommandsRepository,
)
from extract_and_fill.infrastructure.adapters.prompt import PromptAdapter
from extract_and_fill.infrastructure.adapters.pinecone import PineconeAdapter
from extract_and_fill.infrastructure.adapters.vertex_ai_vector_search import VertexAIVectorAdapter
from extract_and_fill.infrastructure.adapters.sentence_adapter import SentenceFireStoreAdapter
from extract_and_fill.infrastructure.adapters.transcript_adapter import TranscriptFireStoreAdapter
from extract_and_fill.infrastructure.adapters.pubsub_adapter import PubSubAdapter
from extract_and_fill.infrastructure.adapters.embeddings_adapter import EmbeddingsMetadataFireStoreAdapter
from extract_and_fill.infrastructure.adapters.commands_repository import CommandsRepository
from extract_and_fill.settings import (
    GCP_PROJECT_ID,
    GCP_PROJECT_LOCATION,
    GCP_PROJECT_LOCATION_2,
    PINECONE_API_KEY,
    PINECONE_ENV,
    PINECONE_VECTOR_SEARCH_INDEX_NAME,
    GCP_VECTOR_SEARCH_INDEX_GCS_URI,
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT,
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID,
    VECTOR_SEARCH_PROVIDER,
    GCP_VECTOR_SEARCH_INDEX_NAME,
    FIRESTORE_DB,
)


di[IPromptPort] = lambda _: PromptAdapter(
    project_id=GCP_PROJECT_ID, location=GCP_PROJECT_LOCATION_2, db_name=FIRESTORE_DB
)
di[IMessageBusAdapter] = lambda _: PubSubAdapter(project_id=GCP_PROJECT_ID)
di[IEmbeddingsMetadataAdapter] = lambda _: EmbeddingsMetadataFireStoreAdapter(
    project_id=GCP_PROJECT_ID, location=GCP_PROJECT_LOCATION, db_name=FIRESTORE_DB
)
di[ISentencePort] = lambda _: SentenceFireStoreAdapter(
    project_id=GCP_PROJECT_ID, location=GCP_PROJECT_LOCATION, db_name=FIRESTORE_DB
)
di[ITranscriptPort] = lambda _: TranscriptFireStoreAdapter(
    project_id=GCP_PROJECT_ID, location=GCP_PROJECT_LOCATION, db_name=FIRESTORE_DB
)
di[IPromptChunkRepository] = lambda _: PromptChunkRepositoryAdapter(db_name=FIRESTORE_DB)
di[IPromptChunkCheckSumRepository] = lambda _: PromptChunkCheckSumRepositoryAdapter(db_name=FIRESTORE_DB)
di[ICommandsRepository] = lambda _: CommandsRepository(project_id=GCP_PROJECT_ID, db_name=FIRESTORE_DB)
if VECTOR_SEARCH_PROVIDER == 'pinecone':
    di[IEmbeddingsAdapter] = lambda _: PineconeAdapter(
        project_id=GCP_PROJECT_ID,
        location=GCP_PROJECT_LOCATION,
        api_key=PINECONE_API_KEY,
        env=PINECONE_ENV,
        index_name=PINECONE_VECTOR_SEARCH_INDEX_NAME,
    )
if VECTOR_SEARCH_PROVIDER == 'vertexai':
    di[IEmbeddingsAdapter] = lambda _: VertexAIVectorAdapter(
        project_id=GCP_PROJECT_ID,
        location=GCP_PROJECT_LOCATION,
        api_key=PINECONE_API_KEY,
        env=PINECONE_ENV,
        gcs_uri=GCP_VECTOR_SEARCH_INDEX_GCS_URI,
        index_name=GCP_VECTOR_SEARCH_INDEX_NAME,
        index_endpoint=GCP_VECTOR_SEARCH_INDEX_ENDPOINT,
        deployed_index_id=GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID,
    )
