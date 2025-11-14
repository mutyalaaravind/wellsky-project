import os
from pathlib import Path
from dotenv import load_dotenv
 
# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_module_root():
    return os.path.dirname(os.path.abspath(__file__))

def getenv_or_die(key: str) -> str:
    """
    >>> getenv_or_die('DEBUG')
    'false'
    >>> import pytest
    >>> with pytest.raises(ValueError):
    ...     getenv_or_die('SOME_UNKNOWN_ENV_VARIABLE')
    """
    value = os.getenv(key)
    if value is None:  # pragma: no cover
        raise ValueError(f'{key} is missing in environment')

    return value


def to_bool(value: str) -> bool:
    return value is not None and value.lower() in ('1', 'y', 'yes', 't', 'true', 'on')

def to_int(value: str) -> int:
    return int(value)

def to_double(value: str) -> float:
    return float(value)

def to_list_of_strings(value: str) -> list:
    return value.split(',')

VERSION = getenv_or_die('VERSION')
SERVICE = getenv_or_die('SERVICE')
STAGE = getenv_or_die('STAGE')
DEBUG = to_bool(os.getenv('DEBUG'))
CLOUD_PROVIDER = getenv_or_die('CLOUD_PROVIDER')
GCP_PROJECT_ID = getenv_or_die('GCP_PROJECT_ID')
GCP_PUBSUB_PROJECT_ID = getenv_or_die('GCP_PUBSUB_PROJECT_ID')
GCS_BUCKET_NAME = getenv_or_die('GCS_BUCKET_NAME')
GCP_LOCATION = getenv_or_die('GCP_LOCATION')
GCP_LOCATION_2 = getenv_or_die('GCP_LOCATION_2')
GCP_LOCATION_3 = getenv_or_die('GCP_LOCATION_3')
GCP_MULTI_REGION_FIRESTORE_LOCATON = getenv_or_die('GCP_MULTI_REGION_FIRESTORE_LOCATON')
GCP_FIRESTORE_DB= getenv_or_die('GCP_FIRESTORE_DB')
EXTRACTION_CLASSIFY_INTERNAL_TOPIC= getenv_or_die('EXTRACTION_CLASSIFY_INTERNAL_TOPIC')
EXTRACTION_MEDICATION_INTERNAL_TOPIC= getenv_or_die('EXTRACTION_MEDICATION_INTERNAL_TOPIC')
EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC= getenv_or_die('EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC')
EXTRACTION_DOCUMENT_STATUS_TOPIC= getenv_or_die('EXTRACTION_DOCUMENT_STATUS_TOPIC')
PAPERGLASS_API_URL= getenv_or_die('PAPERGLASS_API_URL')
PAPERGLASS_INTEGRATION_TOPIC = getenv_or_die('PAPERGLASS_INTEGRATION_TOPIC')
GCP_DOCAI_DOC_PROCESSOR_ID = getenv_or_die('GCP_DOCAI_DOC_PROCESSOR_ID')
GCP_DOCAI_DOC_PROCESSOR_VERSION = getenv_or_die('GCP_DOCAI_DOC_PROCESSOR_VERSION')
MEDICATION_EXTRACTION_V4_TOPIC = getenv_or_die('MEDICATION_EXTRACTION_V4_TOPIC')
SERVICE_ACCOUNT_EMAIL = getenv_or_die('SERVICE_ACCOUNT_EMAIL')
SELF_API_URL = getenv_or_die('SELF_API_URL')
SELF_API_URL_2 = getenv_or_die('SELF_API_URL_2')
DEFAULT_PRIORITY_QUEUE_API_URL = getenv_or_die('DEFAULT_PRIORITY_QUEUE_API_URL')
HIGH_PRIORITY_QUEUE_API_URL = getenv_or_die('HIGH_PRIORITY_QUEUE_API_URL')
QUARANTINE_QUEUE_API_URL = getenv_or_die('QUARANTINE_QUEUE_API_URL')
QUEUE_RESOLVER_VERSION = os.getenv('QUEUE_RESOLVER_VERSION', 'v1')
CLOUDTASK_REGISTERED_APP_IDS = to_list_of_strings(os.getenv("CLOUDTASK_REGISTERED_APP_IDS", "ltc,hhh,007"))
CLOUD_TASK_QUEUE_NAME = getenv_or_die('CLOUD_TASK_QUEUE_NAME')
CLOUD_TASK_QUEUE_NAME_2 = getenv_or_die('CLOUD_TASK_QUEUE_NAME_2')
CLOUD_TASK_QUEUE_NAME_QUARANTINE = getenv_or_die('CLOUD_TASK_QUEUE_NAME_QUARANTINE')
CLOUD_TASK_QUEUE_NAME_QUARANTINE_2 = getenv_or_die('CLOUD_TASK_QUEUE_NAME_QUARANTINE_2')
CLOUD_TASK_QUEUE_NAME_PRIORITY = getenv_or_die('CLOUD_TASK_QUEUE_NAME_PRIORITY')
CLOUD_TASK_QUEUE_NAME_PRIORITY_2 = getenv_or_die('CLOUD_TASK_QUEUE_NAME_PRIORITY_2')
MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME = getenv_or_die('MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME')
MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY= getenv_or_die('MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY')
MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE= getenv_or_die('MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE')
MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME= getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME')
MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY= getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY')
MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE= getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE')
MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME= getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME')
MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY= getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY')
MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE= getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE')
PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME = getenv_or_die('PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME')
PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY= getenv_or_die('PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY')
PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE= getenv_or_die('PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE')
CALLBACK_PAPERGLASS_ENABLED = to_bool(os.getenv('CALLBACK_PAPERGLASS_ENABLED', 'true'))  # We turn this off for tests using quarantine queue if we are using for parallel testing.

AUDIT_LOGGER_TOPIC = getenv_or_die('AUDIT_LOGGER_TOPIC')
AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME = getenv_or_die('AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME')
AUDIT_LOGGER_API_URL = getenv_or_die('AUDIT_LOGGER_API_URL')
LOADTEST_LLM_EMULATOR_ENABLED = to_bool(os.getenv('LOADTEST_LLM_EMULATOR_ENABLED', 'false')) # Swaps out the LLM adapter for a dummy adapter
LLM_PROMPT_AUDIT_ENABLED = to_bool(os.getenv('LLM_PROMPT_AUDIT_ENABLED', 'true')) # Logs the prompt to GCS
CLASSIFY_ENABLED = to_bool(os.getenv('CLASSIFY_ENABLED', 'false')) # Enables the classify pipeline
PIPELINE_RETRY_COUNT = to_int(os.getenv('PIPELINE_RETRY_COUNT', '3')) # Number of times to retry a pipeline

LLM_MODEL_DEFAULT = os.getenv('LLM_MODEL_DEFAULT', 'gemini-2.5-flash-lite')

STEP_CLASSIFY_LLM_MODEL = os.getenv('STEP_CLASSIFY_LLM_MODEL', LLM_MODEL_DEFAULT)
STEP_EXTRACTMEDICATION_LLM_MODEL = os.getenv('STEP_EXTRACTMEDICATION_LLM_MODEL', LLM_MODEL_DEFAULT)
STEP_MEDISPANMATCH_LLM_MODEL = os.getenv('STEP_MEDISPANMATCH_LLM_MODEL', LLM_MODEL_DEFAULT)

MEDDB_SIMILARIY_THRESHOLD = float(os.getenv('MEDDB_SIMILARIY_THRESHOLD', '0.7')) # Similarity threshold for MedDB semantic search
MEDDB_TOP_K = int(os.getenv('MEDDB_TOP_K', '20')) # Number of top results to return from MedDB semantic search
MEDDB_MAX_RESULTS = int(os.getenv('MEDDB_MAX_RESULTS', '5')) # Maximum number of results to return from MedDB semantic search
MEDDB_RERANK_STRENGTH_ENABLED = to_bool(os.getenv('MEDDB_RERANK_STRENGTH_ENABLED', 'false')) # Enables reranking of results based on strength
MEDDB_RERANK_ELIGIBLE_FORMS = to_list_of_strings(os.getenv('MEDDB_RERANK_ELIGIBLE_FORMS', 'tablet,capsule,powder')) # Forms that are eligible for reranking based on strength

LOGGING_CHATTY_LOGGERS = to_list_of_strings(os.getenv('LOGGING_CHATTY_LOGGERS', 'acachecontrol.cache,aiocache.base,urllib3.connectionpool')) #List of loggers that should be set to DEBUG level

MEDISPAN_API_BASE_URL = getenv_or_die('MEDISPAN_API_BASE_URL')

PGVECTOR_HOST: str = os.getenv("PGVECTOR_HOST", "localhost")
PGVECTOR_PORT: int = int(os.getenv("PGVECTOR_PORT", "5433"))
PGVECTOR_USER: str = os.getenv("PGVECTOR_USER", "postgres")
PGVECTOR_PASSWORD: str = os.getenv("PGVECTOR_PASSWORD", "DummyPasswordForTesting@2025")
PGVECTOR_DATABASE: str = os.getenv("PGVECTOR_DATABASE", "postgres")
PGVECTOR_SSL_MODE: str = os.getenv("PGVECTOR_SSL_MODE", "require")
PGVECTOR_TABLE_MEDISPAN: str = os.getenv("PGVECTOR_TABLE_MEDISPAN", "medispan_drugs_gcp_768_2")
PGVECTOR_TABLE_MERATIVE: str = os.getenv("PGVECTOR_TABLE_MERATIVE", "merative_drugs_gcp_768_2")
PGVECTOR_EMBEDDING_DIMENSION: int = int(os.getenv("PGVECTOR_EMBEDDING_DIMENSION", "768"))
PGVECTOR_SEARCH_FUNCTION_MEDISPAN: str = os.getenv("PGVECTOR_SEARCH_FUNCTION_MEDISPAN", "medispan_search_gcp_768_2")
PGVECTOR_SEARCH_FUNCTION_MERATIVE: str = os.getenv("PGVECTOR_SEARCH_FUNCTION_MERATIVE", "merative_search_gcp_768_2")
PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH: bool = to_bool(os.getenv("PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH", "true"))

PGVECTOR_CONNECTION_TIMEOUT: int = int(os.getenv("PGVECTOR_CONNECTION_TIMEOUT", "2"))

FIRESTOREVECTOR_COLLECTION_MEDISPAN: str = os.getenv("FIRESTOREVECTOR_COLLECTION_MEDISPAN", "meddb_medispan")
FIRESTOREVECTOR_COLLECTION_MERATIVE: str = os.getenv("FIRESTOREVECTOR_COLLECTION_MERATIVE", "meddb_merative")

GCP_EMBEDDING_MODEL: str = os.getenv("GCP_EMBEDDING_MODEL", "text-embedding-005")

LLM_RESPONSE_INTERPRET_NOTJSON_ENABLED = to_bool(os.getenv('LLM_RESPONSE_INTERPRET_NOTJSON_ENABLED', 'true'))