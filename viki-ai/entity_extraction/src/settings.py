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
FIRESTORE_EMULATOR_HOST = os.getenv('FIRESTORE_EMULATOR_HOST')

SERVICE_ACCOUNT_EMAIL = getenv_or_die('SERVICE_ACCOUNT_EMAIL')
SELF_API_URL = getenv_or_die('SELF_API_URL')
SELF_API_URL_2 = getenv_or_die('SELF_API_URL_2')

PAPERGLASS_API_URL= getenv_or_die('PAPERGLASS_API_URL')
PAPERGLASS_INTEGRATION_TOPIC = getenv_or_die('PAPERGLASS_INTEGRATION_TOPIC')

INTRA_TASK_INVOCATION_DEFAULT_QUEUE = os.getenv("ENTITY_EXTRACTION_INTRA_TASK_INVOCATION_DEFAULT_QUEUE", "entity-extraction-intra-default-default-queue")

ENTITYEXTRACTION_CONTEXT_GCS_BUCKET = os.getenv('ENTITYEXTRACTION_CONTEXT_GCS_BUCKET', f"entityextraction-context-{STAGE}")
ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED = to_bool(os.getenv("ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED", "true"))

# Distributed Job Tracking API URL
DJT_API_URL = getenv_or_die('DJT_API_URL')
DJT_API_TIMEOUT = to_double(os.getenv('DJT_API_TIMEOUT', '60.0'))

# Use Docker service name when running in Docker, localhost otherwise
CLOUDTASK_EMULATOR_ENABLED = to_bool(os.getenv("CLOUDTASK_EMULATOR_ENABLED", "false"))
CLOUDTASK_EMULATOR_URL = os.getenv("CLOUDTASK_EMULATOR_URL", "http://localhost:30001")

# Cloud Tasks Configuration
DEFAULT_TASK_QUEUE = os.getenv("DEFAULT_TASK_QUEUE", "default-queue")
MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME = getenv_or_die('MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME')

# JSON utilities configuration
JSON_CLEANERS = [
    {"type": "regex", "match": "(\\\\)", "replace": "\\\\\\\\"}
]
USE_JSON_SAFE_LOADS = to_bool(os.getenv("USE_JSON_SAFE_LOADS", "true"))

# Task Retry Configuration
TASK_RETRY_COUNT_DEFAULT = to_int(os.getenv('TASK_RETRY_COUNT_DEFAULT', '3'))
TASK_RETRY_FACTOR_DEFAULT = to_int(os.getenv('TASK_RETRY_FACTOR_DEFAULT', '5'))

# Google AI Configuration
LLM_VERTEXAI_ENABLED = to_bool(os.getenv('LLM_VERTEXAI_ENABLED', 'true'))
LLM_API_VERSION = os.getenv('LLM_API_VERSION', 'v1')  # v1 or v1alpha
LLM_MODEL_DEFAULT = os.getenv('DEFAULT_LLM_MODEL', 'gemini-1.5-flash-002')
LLM_MAX_OUTPUT_TOKENS_DEFAULT = to_int(os.getenv('LLM_MAX_OUTPUT_TOKENS', '8192'))
LLM_TEMPERATURE_DEFAULT = to_double(os.getenv('LLM_TEMPERATURE', '0.0'))
LLM_TOP_P_DEFAULT = to_double(os.getenv('LLM_TOP_P', '0.95'))
LLM_PROMPT_AUDIT_ENABLED = to_bool(os.getenv('LLM_PROMPT_AUDIT_ENABLED', 'true'))

# OpenTelemetry Tracing Configuration
ENABLE_GCP_TRACE_EXPORTER = to_bool(os.getenv('ENABLE_GCP_TRACE_EXPORTER', 'true'))
ENABLE_CONSOLE_TRACE_EXPORTER = to_bool(os.getenv('ENABLE_CONSOLE_TRACE_EXPORTER', 'false'))
ENABLE_JAEGER_TRACE_EXPORTER = to_bool(os.getenv('ENABLE_JAEGER_TRACE_EXPORTER', 'false'))
JAEGER_ENDPOINT = os.getenv('JAEGER_ENDPOINT', 'http://jaeger:4318/v1/traces')

# Logging Configuration
LOGGING_USE_CUSTOM_LOGGER = to_bool(os.getenv('LOGGING_USE_CUSTOM_LOGGER', 'true'))
LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED = to_bool(os.getenv('LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED', 'true'))
LOGGING_CHATTY_LOGGERS = to_list_of_strings(os.getenv('LOGGING_CHATTY_LOGGERS', 'acachecontrol.cache,aiocache.base,urllib3.connectionpool,httpcore'))
