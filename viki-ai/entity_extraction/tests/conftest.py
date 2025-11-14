import os
import pytest
from unittest.mock import patch, MagicMock
from google.oauth2 import service_account

# Set up test environment variables before anything else
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

for key, value in TEST_ENV_VARS.items():
    os.environ[key] = value

@pytest.fixture(autouse=True)
def mock_google_auth():
    """Auto-used fixture to mock all Google Cloud authentication and clients during tests."""
    mock_credentials = MagicMock(spec=service_account.Credentials)
    mock_credentials.token = "mock-token"
    mock_credentials.service_account_email = "mock@example.com"
    mock_credentials.refresh.return_value = None
    mock_signer = MagicMock()
    mock_signer.key_id = "mock-key-id"
    mock_credentials.signer = mock_signer

    with patch('google.auth') as mock_google_auth_module, \
         patch('opentelemetry.exporter.cloud_trace.CloudTraceSpanExporter', autospec=True) as mock_trace_exporter, \
         patch('google.cloud.firestore.Client', autospec=True) as mock_firestore_client, \
         patch('google.cloud.storage.Client', autospec=True) as mock_storage_client, \
         patch('google.cloud.logging.Client', autospec=True) as mock_logging_client:
        
        mock_google_auth_module.default.return_value = (mock_credentials, "test-project")
        mock_google_auth_module.impersonated_credentials.Credentials.return_value = mock_credentials
        
        # Configure mock instances if needed
        mock_firestore_client.return_value.project = "test-project"
        mock_storage_client.return_value.project = "test-project"
        mock_logging_client.return_value.project = "test-project"
        
        yield {
            "auth": mock_google_auth_module,
            "trace": mock_trace_exporter,
            "firestore": mock_firestore_client,
            "storage": mock_storage_client,
            "logging": mock_logging_client
        }
