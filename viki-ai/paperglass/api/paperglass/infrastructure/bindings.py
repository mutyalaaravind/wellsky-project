"""
This module tells injector how to map driven ports to adapters.
"""

from kink import di
from paperglass.infrastructure.adapters.medispan_api_search_filter import MedispanAPISearchFilterAdapter
from paperglass.infrastructure.adapters.medispan_llm_filter import MedispanLLMFilterAdapter
from paperglass.infrastructure.adapters.external_medications import HHHAdapter
from paperglass.infrastructure.adapters.medispan import MedispanAdapter, MedispanCachedAdapter
from paperglass.infrastructure.adapters.medispan_vector_search import MedispanVectorSearchAdapter
from paperglass.infrastructure.adapters.medispan_firestore_vector_search import MedispanFireStoreVectorSearchAdapter
from paperglass.infrastructure.adapters.settings import SettingsAdapter
from paperglass.infrastructure.adapters.fhir_store_adapter import FhirStoreAdapter
from paperglass.infrastructure.adapters.prompt import PromptAdapter
from paperglass.infrastructure.adapters.prompt_dummyload import DummyPromptAdapter
from paperglass.infrastructure.adapters.vertex_ai_vector_search import VertexAIVectorAdapter
from paperglass.infrastructure.adapters.search import SearchAdapter
from paperglass.infrastructure.adapters.search_indexer import SearchIndexer
from paperglass.infrastructure.adapters.search_fhir import SearchFHIRAdapter

from paperglass.settings import MEDISPAN_STRATEGY


from ..settings import (
    STAGE,
    CLOUD_PROVIDER,
    FIRESTORE_EMULATOR_HOST,
    GCP_DOCAI_HCC_PROCESSOR_ID,
    GCP_DOCAI_HCC_PROCESSOR_VERSION,
    GCP_DOCAI_SUMMARIZER_PROCESSOR_ID,
    GCP_DOCAI_SUMMARIZER_PROCESSOR_VERSION,
    GCP_DOCAI_DOC_PROCESSOR_ID,
    GCP_DOCAI_DOC_PROCESSOR_VERSION,
    GCP_PROJECT_ID,
    GCP_PUBSUB_PROJECT_ID,
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID_2,
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT_2,
    GCP_VECTOR_SEARCH_INDEX_NAME_2,
    GCS_BUCKET_NAME,
    GCP_LOCATION,
    GCP_LOCATION_2,
    GCP_LOCATION_3,
    GCP_SEARCH_AND_CONVERSATION_DATA_SOURCE_ID,
    GCP_SEARCH_AND_CONVERSATION_FHIR_DATA_SOURCE_ID,
    GCP_VECTOR_SEARCH_INDEX_GCS_URI,
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT,
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID,
    HHH_ATTACHMENTS_API,
    MEDISPAN_CLIENT_ID,
    MEDISPAN_CLIENT_SECRET,
    MEDISPAN_FILTER_STRATEGY,
    MEDISPAN_STRATEGY,
    VECTOR_SEARCH_PROVIDER,
    GCP_VECTOR_SEARCH_INDEX_NAME,
    FHIR_DATA_STORE,
    FHIR_SERVER_URL,
    FHIR_DATA_SET,
    FHIR_SEARCH_STORE_ID,
    HHH_MEDICATION_PROFILE_BASE_URL,
    GCP_MULTI_REGION_FIRESTORE_LOCATON,
    GCP_FIRESTORE_DB,
    MOCK_PROMPT_ENABLED,
)

from paperglass.domain.values import FilterStrategy, MedispanStrategy

from .adapters.google import (
    ApplicationIntegrationAdapter,
    CloudTaskAdapter,
    FirestoreQueryAdapter,
    FirestoreUnitOfWorkManagerAdapter,
    GoogleStorageAdapter,
)
from .adapters.cloudtask_factory import create_cloud_task_adapter
from .adapters.google_pubsub import GooglePubSubAdapter
from .adapters.docai import DocumentAIAdapter

from .ports import (
    IDocumentAIAdapter,
    IEmbeddings2Adapter,
    IEmbeddingsAdapter,
    IHHHAdapter,
    IFhirStoreAdapter,
    IMedispanPort,
    IPromptAdapter,
    IQueryPort,
    IRelevancyFilterPort,
    ISettingsPort,
    IStoragePort,
    IUnitOfWorkManagerPort,
    IUnitOfWork,
    ISearchAdapter,
    ISearchIndexer,
    ISearchFHIRAdapter,
    ICloudTaskPort,
    IApplicationIntegration,
    IMessagingPort,
)

di[IStoragePort] = lambda _: GoogleStorageAdapter(GCP_PROJECT_ID, GCS_BUCKET_NAME, CLOUD_PROVIDER)
di[IUnitOfWorkManagerPort] = lambda _: FirestoreUnitOfWorkManagerAdapter()
di[IQueryPort] = lambda _: FirestoreQueryAdapter(GCP_FIRESTORE_DB)
di[IDocumentAIAdapter] = lambda _: DocumentAIAdapter(
    GCP_PROJECT_ID,
    GCP_LOCATION,
    GCP_DOCAI_HCC_PROCESSOR_ID,
    GCP_DOCAI_HCC_PROCESSOR_VERSION,
    GCP_DOCAI_SUMMARIZER_PROCESSOR_ID,
    GCP_DOCAI_SUMMARIZER_PROCESSOR_VERSION,
    GCP_DOCAI_DOC_PROCESSOR_ID,
    GCP_DOCAI_DOC_PROCESSOR_VERSION
)
di[ISearchAdapter] = lambda _: SearchAdapter(GCP_PROJECT_ID, "us", GCP_SEARCH_AND_CONVERSATION_DATA_SOURCE_ID)
di[ISearchIndexer] = lambda _: SearchIndexer(
    GCP_PROJECT_ID,
    "us",
    GCP_LOCATION_3,
    GCP_SEARCH_AND_CONVERSATION_DATA_SOURCE_ID,
    fhir_datastore_id=FHIR_DATA_STORE,
    fhir_dataset=FHIR_DATA_SET,
    fhir_search_store_id=FHIR_SEARCH_STORE_ID,
)
di[ISearchFHIRAdapter] = lambda _: SearchFHIRAdapter(
    GCP_PROJECT_ID, "us", GCP_SEARCH_AND_CONVERSATION_FHIR_DATA_SOURCE_ID
)
di[IEmbeddingsAdapter] = lambda _: VertexAIVectorAdapter(
    project_id=GCP_PROJECT_ID,
    location=GCP_LOCATION_2,
    api_key="",
    env="",
    gcs_uri=GCP_VECTOR_SEARCH_INDEX_GCS_URI,
    index_name=GCP_VECTOR_SEARCH_INDEX_NAME,
    index_endpoint=GCP_VECTOR_SEARCH_INDEX_ENDPOINT,
    deployed_index_id=GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID,
)
di[IEmbeddings2Adapter] = lambda _: VertexAIVectorAdapter(
    project_id=GCP_PROJECT_ID,
    location=GCP_LOCATION_2,
    api_key="",
    env="",
    gcs_uri=GCP_VECTOR_SEARCH_INDEX_GCS_URI,
    index_name=GCP_VECTOR_SEARCH_INDEX_NAME_2,
    index_endpoint=GCP_VECTOR_SEARCH_INDEX_ENDPOINT_2,
    deployed_index_id=GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID_2,
)

# NEVER USE MOCK PROMPT IN PRODUCTION!
if STAGE == "prod" or not MOCK_PROMPT_ENABLED:
    di[IPromptAdapter] = lambda _: PromptAdapter(GCP_PROJECT_ID, GCP_LOCATION_3, GCP_FIRESTORE_DB)
else:
    di[IPromptAdapter] = lambda _: DummyPromptAdapter(GCP_PROJECT_ID, GCP_LOCATION_3, GCP_FIRESTORE_DB)

di[IFhirStoreAdapter] = lambda _: FhirStoreAdapter(FHIR_SERVER_URL, FHIR_DATA_STORE)
di[ISettingsPort] = lambda _: SettingsAdapter(GCP_FIRESTORE_DB)
di[ICloudTaskPort] = lambda _: create_cloud_task_adapter()
if MEDISPAN_STRATEGY == MedispanStrategy.VECTOR_SEARCH.value:
    di[IMedispanPort] = lambda _: MedispanVectorSearchAdapter(MEDISPAN_CLIENT_ID, MEDISPAN_CLIENT_SECRET)

if MEDISPAN_STRATEGY == MedispanStrategy.FIRE_STORE.value:
    di[IMedispanPort] = lambda _: MedispanFireStoreVectorSearchAdapter(GCP_PROJECT_ID, GCP_FIRESTORE_DB)

elif MEDISPAN_STRATEGY == MedispanStrategy.MEDISPAN_CACHED.value:
    di[IMedispanPort] = lambda _: MedispanCachedAdapter(MEDISPAN_CLIENT_ID, MEDISPAN_CLIENT_SECRET)
else:
    di[IMedispanPort] = lambda _: MedispanAdapter(MEDISPAN_CLIENT_ID, MEDISPAN_CLIENT_SECRET)

if MEDISPAN_FILTER_STRATEGY == FilterStrategy.LLM:
    di[IRelevancyFilterPort] = lambda di: MedispanLLMFilterAdapter()
elif MEDISPAN_FILTER_STRATEGY == FilterStrategy.LOGIC:
    di[IRelevancyFilterPort] = lambda di: MedispanAPISearchFilterAdapter()

di[IApplicationIntegration] = lambda _: ApplicationIntegrationAdapter(GCP_PROJECT_ID,GCP_LOCATION_3)
di[IHHHAdapter] = lambda _: HHHAdapter(HHH_MEDICATION_PROFILE_BASE_URL, HHH_ATTACHMENTS_API)

di[IMessagingPort] = lambda _: GooglePubSubAdapter(GCP_PUBSUB_PROJECT_ID)
