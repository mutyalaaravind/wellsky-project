import os
from typing import Optional

import aiocache


def getenv_or_die(key: str) -> str:
    """
    Get environment variable or raise ValueError if not found.
    Critical for production environments where missing config should fail fast.
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


# Service configuration
VERSION: str = getenv_or_die('VERSION')
SERVICE: str = getenv_or_die('SERVICE')
STAGE: str = getenv_or_die('STAGE')
DEBUG: bool = to_bool(os.getenv('DEBUG'))

# Cloud provider configuration
CLOUD_PROVIDER: str = os.getenv("CLOUD_PROVIDER", "google")

# GCP configuration
GCP_PROJECT_ID: str = getenv_or_die('GCP_PROJECT_ID')
GCP_PUBSUB_PROJECT_ID: str = getenv_or_die('GCP_PUBSUB_PROJECT_ID')
GCS_BUCKET_NAME: str = getenv_or_die('GCS_BUCKET_NAME')
GCP_LOCATION: str = getenv_or_die('GCP_LOCATION')
GCP_LOCATION_2: str = getenv_or_die('GCP_LOCATION_2')
GCP_LOCATION_3: str = getenv_or_die('GCP_LOCATION_3')
GCP_MULTI_REGION_FIRESTORE_LOCATON: str = getenv_or_die('GCP_MULTI_REGION_FIRESTORE_LOCATON')
GCP_FIRESTORE_DB: str = getenv_or_die('GCP_FIRESTORE_DB')
SERVICE_ACCOUNT_EMAIL: str = getenv_or_die('SERVICE_ACCOUNT_EMAIL')
FIRESTORE_EMULATOR_HOST: Optional[str] = os.getenv('FIRESTORE_EMULATOR_HOST')

# API URLs
SELF_API_URL: str = getenv_or_die("SELF_API_URL")
DJT_API_URL: str = getenv_or_die("DJT_API_URL")
PAPERGLASS_API_URL: str = getenv_or_die("PAPERGLASS_API_URL")
ENTITY_EXTRACTION_API_URL: str = getenv_or_die("ENTITY_EXTRACTION_API_URL")

# Admin Demo Integration Settings
ADMIN_DEMO_BASE_URL: str = getenv_or_die("ADMIN_DEMO_BASE_URL")
ADMIN_DEMO_ENTITY_CALLBACK_ENDPOINT: str = getenv_or_die("ADMIN_DEMO_ENTITY_CALLBACK_ENDPOINT")
PAPERGLASS_INTERNAL_DOCUMENT_CREATE_ENDPOINT: str = getenv_or_die("PAPERGLASS_INTERNAL_DOCUMENT_CREATE_ENDPOINT")

# Okta Authentication
OKTA_ISSUER: str = getenv_or_die("OKTA_ISSUER")
OKTA_AUDIENCE: str = getenv_or_die("OKTA_AUDIENCE")
OKTA_CLIENT_ID: str = getenv_or_die("OKTA_CLIENT_ID")
OKTA_DISABLE: bool = to_bool(os.getenv('OKTA_DISABLE', 'false'))
OKTA_DISABLE_MOCK_USER: Optional[str] = os.getenv('OKTA_DISABLE_MOCK_USER')

# Okta API Integration
OKTA_API_TOKEN: str = getenv_or_die("OKTA_API_TOKEN")
OKTA_APP_ID: str = getenv_or_die("OKTA_APP_ID")
OKTA_DOMAIN: str = getenv_or_die("OKTA_DOMAIN")
OKTA_AUTO_ASSIGN_ENABLED: bool = to_bool(os.getenv('OKTA_AUTO_ASSIGN_ENABLED', 'false'))
OKTA_USER_VALIDATION_ENABLED: bool = to_bool(os.getenv('OKTA_USER_VALIDATION_ENABLED', 'true'))
OKTA_ADMIN_GROUP_ID: str = os.getenv('OKTA_ADMIN_GROUP_ID', '')
OKTA_REGULAR_USERS_GROUP_ID: str = os.getenv('OKTA_REGULAR_USERS_GROUP_ID', '')
OKTA_FAIL_ON_USER_NOT_FOUND: bool = to_bool(os.getenv('OKTA_FAIL_ON_USER_NOT_FOUND', 'true'))


class Settings:
    """Settings container for backward compatibility with existing code."""
    def __init__(self):
        # Service configuration
        self.VERSION = VERSION
        self.SERVICE = SERVICE
        self.STAGE = STAGE
        self.DEBUG = DEBUG

        # Cloud provider configuration
        self.CLOUD_PROVIDER = CLOUD_PROVIDER

        # GCP configuration
        self.GCP_PROJECT_ID = GCP_PROJECT_ID
        self.GCP_PUBSUB_PROJECT_ID = GCP_PUBSUB_PROJECT_ID
        self.GCS_BUCKET_NAME = GCS_BUCKET_NAME
        self.GCP_LOCATION = GCP_LOCATION
        self.GCP_LOCATION_2 = GCP_LOCATION_2
        self.GCP_LOCATION_3 = GCP_LOCATION_3
        self.GCP_MULTI_REGION_FIRESTORE_LOCATON = GCP_MULTI_REGION_FIRESTORE_LOCATON
        self.GCP_FIRESTORE_DB = GCP_FIRESTORE_DB
        self.SERVICE_ACCOUNT_EMAIL = SERVICE_ACCOUNT_EMAIL
        self.FIRESTORE_EMULATOR_HOST = FIRESTORE_EMULATOR_HOST

        # API URLs
        self.SELF_API_URL = SELF_API_URL
        self.DJT_API_URL = DJT_API_URL
        self.PAPERGLASS_API_URL = PAPERGLASS_API_URL
        self.ENTITY_EXTRACTION_API_URL = ENTITY_EXTRACTION_API_URL

        # Admin Demo Integration Settings
        self.ADMIN_DEMO_BASE_URL = ADMIN_DEMO_BASE_URL
        self.ADMIN_DEMO_ENTITY_CALLBACK_ENDPOINT = ADMIN_DEMO_ENTITY_CALLBACK_ENDPOINT
        self.PAPERGLASS_INTERNAL_DOCUMENT_CREATE_ENDPOINT = PAPERGLASS_INTERNAL_DOCUMENT_CREATE_ENDPOINT

        # Okta Authentication
        self.OKTA_ISSUER = OKTA_ISSUER
        self.OKTA_AUDIENCE = OKTA_AUDIENCE
        self.OKTA_CLIENT_ID = OKTA_CLIENT_ID
        self.OKTA_DISABLE = OKTA_DISABLE
        self.OKTA_DISABLE_MOCK_USER = OKTA_DISABLE_MOCK_USER

        # Okta API Integration
        self.OKTA_API_TOKEN = OKTA_API_TOKEN
        self.OKTA_APP_ID = OKTA_APP_ID
        self.OKTA_DOMAIN = OKTA_DOMAIN
        self.OKTA_AUTO_ASSIGN_ENABLED = OKTA_AUTO_ASSIGN_ENABLED
        self.OKTA_USER_VALIDATION_ENABLED = OKTA_USER_VALIDATION_ENABLED
        self.OKTA_ADMIN_GROUP_ID = OKTA_ADMIN_GROUP_ID
        self.OKTA_REGULAR_USERS_GROUP_ID = OKTA_REGULAR_USERS_GROUP_ID
        self.OKTA_FAIL_ON_USER_NOT_FOUND = OKTA_FAIL_ON_USER_NOT_FOUND


@aiocache.cached()
async def get_settings() -> Settings:
    return Settings()