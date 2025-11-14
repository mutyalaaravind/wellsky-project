# Common Environment Variables for AI Services
# This file provides a centralized way to manage environment variables
# that are shared across multiple AI services, with the ability to override
# specific variables per service.

locals {
  # File hash that changes when this file is modified
  env_config_version = filesha256("${path.module}/services_common_env.tf")

  # Base environment variables that are common across all AI services
  common_env = {
    # Core service configuration
    STAGE              = var.env
    DEBUG              = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    CLOUD_PROVIDER     = "google"
    ENV_CONFIG_VERSION = local.env_config_version

    # GCP configuration
    GCP_PROJECT_ID                     = var.app_project_id
    GCP_PUBSUB_PROJECT_ID              = var.app_project_id
    GCS_BUCKET_NAME                    = module.ai_provisional_bucket.name
    GCP_LOCATION                       = split("-", var.region)[0]
    GCP_LOCATION_2                     = var.region
    GCP_LOCATION_3                     = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON = "nam5"
    GCP_FIRESTORE_DB                   = "viki-${var.env}"

    # Document AI configuration
    GCP_DOCAI_HCC_PROCESSOR_ID             = "7359477870825dbb"
    GCP_DOCAI_HCC_PROCESSOR_VERSION        = "pretrained"
    GCP_DOCAI_SUMMARIZER_PROCESSOR_ID      = "fcaac0296ec91273"
    GCP_DOCAI_SUMMARIZER_PROCESSOR_VERSION = "pretrained-foundation-model-v1.0-2023-08-22"
    GCP_DOCAI_DOC_PROCESSOR_ID             = split("/", google_document_ai_processor.document_ocr_processor.id)[5]
    GCP_DOCAI_DOC_PROCESSOR_VERSION        = "pretrained"

    # Search and Conversation configuration
    GCP_SEARCH_AND_CONVERSATION_DATA_SOURCE_ID      = "patient-charts-3_1709317732426"
    GCP_SEARCH_AND_CONVERSATION_FHIR_DATA_SOURCE_ID = "fhir-store-search"

    # Vector Search configuration
    GCP_VECTOR_SEARCH_INDEX_GCS_URI       = "gs://viki-ai-provisional-dev/icd10-search-balki/"
    GCP_VECTOR_SEARCH_INDEX_NAME          = "projects/145042810266/locations/us-east4/indexes/7823403463626194944"
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT      = "projects/145042810266/locations/us-east4/indexEndpoints/957208434862718976"
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID   = "extraction_index_deployed__1699595619091"
    GCP_VECTOR_SEARCH_INDEX_NAME_2        = "projects/145042810266/locations/us-east4/indexes/2213712730899087360"
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT_2    = "projects/145042810266/locations/us-east4/indexEndpoints/8337579081239363584"
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID_2 = "deploy_endpoint_1714065441017"

    # FHIR configuration
    FHIR_SERVER_URL      = var.fhir_server_url
    FHIR_DATA_STORE      = var.fhir_data_store
    FHIR_DATA_SET        = var.fhir_data_set
    FHIR_SEARCH_STORE_ID = var.fhir_search_store_id

    # Integration configuration
    INTEGRATION_PROJECT_NAME           = "MedicationExtractionPipeline"
    APPLICATION_INTEGRATION_TRIGGER_ID = "api_trigger/MedicationExtractionPipeline_API_2"

    # Queue configuration
    QUEUE_RESOLVER_VERSION       = var.cloudtask_queue_resolver_version
    CLOUDTASK_REGISTERED_APP_IDS = join(",", var.registered_app_ids)

    # Service Account
    SERVICE_ACCOUNT_EMAIL = module.ai_sa.email

    # HHH configuration
    HHH_MEDICATION_PROFILE_BASE_URL = "${var.proxy_url}/"
    HHH_ATTACHMENTS_API             = "https://api.qa-wsh.hhh-dev-app.prj.gcp.wellsky.io/"
    HHH_ATTACHMENTS_AUTH_SERVER     = "https://auth.stable.wellsky.io/connect/token"
    HHH_ATTACHMENTS_CLIENT_ID       = "client.hhh.medication.genai.qa"

    # Okta configuration
    OKTA_CLIENT_ID          = "api.wellsky.viki.paperglass"
    OKTA_VERIFY             = "true"
    OKTA_AUDIENCE           = var.okta_audience
    OKTA_TOKEN_ISSUER_URL   = var.okta_issuer_url
    OKTA_SERVICE_ISSUER_URL = var.okta_service_issuer_url
    OKTA_SERVICE_AUDIENCE   = var.okta_service_audience

    # OpenTelemetry configuration
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled

    # API timeout configuration
    EXTERNAL_API_CONNECT_TIMEOUT_SECONDS        = "60"
    EXTERNAL_API_SOCKET_CONNECT_TIMEOUT_SECONDS = "60"
    EXTERNAL_API_SOCKET_READ_TIMEOUT_SECONDS    = "60"

    # Medispan configuration
    MEDISPAN_API_URL                     = var.medispan_api_url
    MEDISPAN_PAGE_SIZE                   = var.medispan_page_size
    MEDISPAN_FILTER_ENABLED              = true
    MEDISPAN_LLM_SCORING_ENABLED         = true
    MEDISPAN_VECTOR_SEARCH_PROJECT_ID    = "viki-qa-app-wsky"
    MEDISPAN_VECTOR_SEARCH_REGION        = "us-central1"
    MEDISPAN_VECTOR_SEARCH_DEPLOYMENT_ID = "medsearch_1723187204068"
    MEDISPAN_VECTOR_SEARCH_ENDPOINT_ID   = "7990947045466701824"
    MEDISPAN_STRATEGY                    = "firestore"
    MEDISPAN_API_BASE_URL                = format("%s/%s/", module.medispan_api.url, "api")

    # Medication configuration
    MEDICATION_MATCHING_BATCH_SIZE = "20"
    MULTIMODAL_TEMPERATURE         = var.multimodal_temperature
    MEDICAL_SUMMARIZATION_API_URL  = "https://healthcare.googleapis.com/v1alpha2/projects/viki-${var.env}-app-wsky/locations/us-central1/services/medlm:summarizeClinicalRecords"

    # Orchestration configuration
    ORCHESTRATION_GRADER_SCHEDULE_WINDOW_ENABLED = var.orchestration_grader_schedule_window_enabled
    EXTRACTION_PUBSUB_TOPIC_NAME                 = google_pubsub_topic.orchestraction_extraction_topic.name

    # New Relic configuration
    NEW_RELIC_LICENSE_KEY                                  = var.newrelic_api_license_key
    NEW_RELIC_MONITOR_MODE                                 = "true"
    NEW_RELIC_LOG                                          = "stdout"
    NEW_RELIC_LOG_LEVEL                                    = "info"
    NEW_RELIC_HIGH_SECURITY                                = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                  = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED       = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED          = "false"
    NEW_RELIC_TRACE_ENABLED                                = var.newrelic_trace_enabled

    # Medication Extraction V4 configuration
    MEDICATION_EXTRACTION_V4_TOPIC                            = google_pubsub_topic.medication_extraction_v4_topic.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME            = google_cloud_tasks_queue.v4_extraction_entrypoint.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY   = google_cloud_tasks_queue.v4_extraction_entrypoint_priority.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE = google_cloud_tasks_queue.v4_extraction_entrypoint_quarantine.name
    MEDICATION_EXTRACTION_V4_API_URL                          = var.medication_extraction_api_url
    MEDICATION_EXTRACTION_V4_API_DEFAULT_URL                  = var.medication_extraction_default_api_url
    MEDICATION_EXTRACTION_V4_API_HIGH_URL                     = var.medication_extraction_high_api_url
    MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL               = var.medication_extraction_quarantine_api_url

    MEDICATION_EXTRACTION_RESPAWN_INFLIGHT_ENABLED = "false"

    MOCK_PROMPT_ENABLED = var.mock_prompt_enabled

    # Entity Extraction configuration
    ENTITY_EXTRACTION_API_URL           = var.entity_extraction_api_url
    ENTITY_EXTRACTION_LAUNCH_QUEUE_NAME = google_cloud_tasks_queue.entity_extraction_launch_queue.name

    # Cloud Task Queue configuration
    CLOUD_TASK_QUEUE_NAME                                       = google_cloud_tasks_queue.paperglass_classification.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY                              = google_cloud_tasks_queue.paperglass_classification_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE                            = google_cloud_tasks_queue.paperglass_classification_quarantine.name
    CLOUD_TASK_QUEUE_NAME_2                                     = google_cloud_tasks_queue.paperglass_extraction.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2                            = google_cloud_tasks_queue.paperglass_extraction_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2                          = google_cloud_tasks_queue.paperglass_extraction_quarantine.name
    CLOUD_TASK_COMMAND_QUEUE_NAME                               = google_cloud_tasks_queue.paperglass_command.name
    CLOUD_TASK_COMMAND_SCHEDULE_QUEUE_NAME                      = google_cloud_tasks_queue.paperglass_command_schedule.name
    CLOUD_TASK_COMMAND_EXTERNAL_CREATE_DOCUMENT_TASK_QUEUE_NAME = google_cloud_tasks_queue.paperglass-command-external-create-document-queue.name
    CLOUD_TASK_PUBLISH_CALLBACK_QUEUE_NAME                      = google_cloud_tasks_queue.paperglass_host_publish_callback.name

    # Feature flags
    E2E_TEST_ENABLE                                 = "true"
    FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED = var.command_outofband_cloudtask_enabled

    # Other configuration
    PAGE_OCR_TOPIC = "NA"
  }
}

# Common secrets configuration that can be reused across services
locals {
  common_secrets = [
    {
      key     = "MEDISPAN_CLIENT_ID",
      name    = module.secret["medispan_client_id"].name,
      version = "latest",
    },
    {
      key     = "MEDISPAN_CLIENT_SECRET",
      name    = module.secret["medispan_client_secret"].name,
      version = "latest",
    },
    {
      key     = "OKTA_CLIENT_SECRET",
      name    = module.secret["okta_client_secret"].name,
      version = "latest",
    },
    {
      key     = "HHH_ATTACHMENTS_CLIENT_SECRET",
      name    = module.secret["hhh_attachments_client_secret"].name,
      version = "latest",
    },
    {
      key     = "SHAREPOINT_CLIENT_ID",
      name    = module.secret["sharepoint_client_id"].name,
      version = "latest",
    },
    {
      key     = "SHAREPOINT_CLIENT_SECRET",
      name    = module.secret["sharepoint_client_secret"].name,
      version = "latest",
    }
  ]
}
