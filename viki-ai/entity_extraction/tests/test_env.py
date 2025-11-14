"""
Test environment configuration for unit tests.
Sets up required environment variables before importing any modules that depend on settings.
"""
import os

# Set up test environment variables
TEST_ENV_VARS = {
    "VERSION": "dev",
    "SERVICE": "entity-extraction",
    "STAGE": "dev",
    "DEBUG": "true",
    "CLOUD_PROVIDER": "gcp",
    "GCP_PROJECT_ID": "viki-dev-app-wsky",
    "GCP_PUBSUB_PROJECT_ID": "viki-dev-app-wsky",
    "GCS_BUCKET_NAME": "viki-ai-provisional-dev",
    "GCP_LOCATION": "us",
    "GCP_LOCATION_2": "us-east4",
    "GCP_LOCATION_3": "us-central1",
    "GCP_MULTI_REGION_FIRESTORE_LOCATON": "nam5",
    "GCP_FIRESTORE_DB": "viki-dev",
    "SERVICE_ACCOUNT_EMAIL": "viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com",
    "SELF_API_URL": "http://entity-extraction-api:16000",
    "SELF_API_URL_2": "http://entity-extraction-api:16000",
    "PAPERGLASS_API_URL": "http://paperglass-api:15000",
    "PAPERGLASS_INTEGRATION_TOPIC": "extract_v4_paperglass_medications_topic",
    "DJT_API_URL": "http://djt-api:17000",
    "MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME": "medication-extraction-v4-status-check-queue",
    "CLOUDTASK_EMULATOR_URL": "http://cloudtask-emulator:8080",
    "CLOUDTASK_EMULATOR_HOST": "cloudtask-emulator:8080",
    "CLOUDTASK_EMULATOR_ENABLED": "false",
    "INTRA_TASK_INVOCATION_DEFAULT_QUEUE": "entity-extraction-intra-default-default-queue",
    "ENTITY_EXTRACTION_INTRA_TASK_INVOCATION_DEFAULT_QUEUE": "entity-extraction-intra-default-default-queue",
    "LLM_PROMPT_AUDIT_ENABLED": "true",
}

def setup_test_env():
    """Set up test environment variables."""
    for key, value in TEST_ENV_VARS.items():
        os.environ[key] = value

# Automatically set up environment when this module is imported
setup_test_env()
