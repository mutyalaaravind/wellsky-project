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
    Get environment variable or raise ValueError if not found.
    """
    value = os.getenv(key)
    if value is None:
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

# Service configuration - critical settings use getenv_or_die
VERSION = getenv_or_die('VERSION')
SERVICE = getenv_or_die('SERVICE')
STAGE = getenv_or_die('STAGE')
CLOUD_PROVIDER = getenv_or_die('CLOUD_PROVIDER')
DEBUG = to_bool(os.getenv('DEBUG', 'false'))
LOGGING_CHATTY_LOGGERS = to_list_of_strings(os.getenv('LOGGING_CHATTY_LOGGERS', ''))

# Database configuration - optional with defaults
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
REDIS_DB = to_int(os.getenv('REDIS_DB', '0'))
DJT_REDIS_TTL_DEFAULT = to_int(os.getenv('DJT_REDIS_TTL_DEFAULT', '43200'))  # 12 hours in seconds

# Google Cloud configuration - critical settings use getenv_or_die
GCP_PROJECT_ID = getenv_or_die('GCP_PROJECT_ID')
GCP_LOCATION = getenv_or_die('GCP_LOCATION')
GCP_LOCATION_2 = getenv_or_die('GCP_LOCATION_2')
GCP_LOCATION_3 = getenv_or_die('GCP_LOCATION_3')

# Service URLs - critical
SELF_API_URL = getenv_or_die('SELF_API_URL')
PAPERGLASS_API_URL = getenv_or_die('PAPERGLASS_API_URL')

SERVICE_ACCOUNT_EMAIL = getenv_or_die('SERVICE_ACCOUNT_EMAIL')

# Task queue configuration - optional with defaults
DEFAULT_TASK_QUEUE = os.getenv('DEFAULT_TASK_QUEUE', 'distributed-job-tracking-queue')
CLOUDTASK_EMULATOR_URL = os.getenv('CLOUDTASK_EMULATOR_URL', 'http://localhost:30001')

STATUS_POST_COMPLETE_TTL = to_int(os.getenv('STATUS_POST_COMPLETE_TTL', '3600'))  # 1 hour in seconds   Length of time a completed job status is retained in the system

# Authentication - optional
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
