module "medication_extraction_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medication-extraction"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medication_extraction:${coalesce(var.paperglass_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", "9"
  ]
  env = {
    SERVICE                                                  = "medication_extraction"
    STAGE                                                    = var.env
    VERSION                                                  = var.medication_extraction_version
    DEBUG                                                    = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                                          = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                                           = var.app_project_id
    GCP_LOCATION                                             = split("-", var.region)[0]
    GCP_LOCATION_2                                           = var.region
    GCP_LOCATION_3                                           = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON                       = "nam5"
    GCP_FIRESTORE_DB                                         = "viki-${var.env}"
    GCP_DOCAI_DOC_PROCESSOR_ID                               = split("/", google_document_ai_processor.document_ocr_processor.id)[5] # Extract the processor ID from the resource URI
    GCP_DOCAI_DOC_PROCESSOR_VERSION                          = "pretrained"
    CLOUD_PROVIDER                                           = "google"
    CLOUD_PROVIDER                                           = "google"
    SELF_API_URL                                             = var.medication_extraction_api_2_url
    SELF_API_URL_2                                           = var.medication_extraction_api_url
    DEFAULT_PRIORITY_QUEUE_API_URL                           = var.medication_extraction_default_api_url
    HIGH_PRIORITY_QUEUE_API_URL                              = var.medication_extraction_high_api_url
    QUARANTINE_QUEUE_API_URL                                 = var.medication_extraction_quarantine_api_url
    QUEUE_RESOLVER_VERSION                                   = var.cloudtask_queue_resolver_version
    CLOUDTASK_REGISTERED_APP_IDS                             = join(",", var.registered_app_ids)
    CLOUD_TASK_QUEUE_NAME                                    = google_cloud_tasks_queue.paperglass_classification.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY                           = google_cloud_tasks_queue.paperglass_classification_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE                         = google_cloud_tasks_queue.paperglass_classification_quarantine.name
    CLOUD_TASK_QUEUE_NAME_2                                  = google_cloud_tasks_queue.paperglass_extraction.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2                         = google_cloud_tasks_queue.paperglass_extraction_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2                       = google_cloud_tasks_queue.paperglass_extraction_quarantine.name
    SERVICE_ACCOUNT_EMAIL                                    = module.ai_sa.email
    OKTA_CLIENT_ID                                           = "api.wellsky.viki.paperglass"
    OKTA_VERIFY                                              = "true"
    OKTA_AUDIENCE                                            = var.okta_audience # dev: "viki.prod.wellsky.io", qa: "viki.prod.wellsky.io", stage: "viki.prod.wellsky.io", prod: "viki.dev.wellsky.io"
    OKTA_TOKEN_ISSUER_URL                                    = var.okta_issuer_url
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_SERVICE_NAME                                        = "viki.paperglass.api"
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled
    GCP_PUBSUB_PROJECT_ID                                    = var.app_project_id
    EXTRACTION_PUBSUB_TOPIC_NAME                             = google_pubsub_topic.orchestraction_extraction_topic.name
    NEW_RELIC_LICENSE_KEY                                    = var.newrelic_api_license_key
    NEW_RELIC_APP_NAME                                       = "Viki Medication Extraction (${var.env})"
    NEW_RELIC_MONITOR_MODE                                   = "true"
    NEW_RELIC_LOG                                            = "stdout"
    NEW_RELIC_LOG_LEVEL                                      = "info"
    NEW_RELIC_HIGH_SECURITY                                  = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                    = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED         = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED   = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED            = "false"
    NEW_RELIC_TRACE_ENABLED                                  = var.newrelic_trace_enabled
    MEDICATION_EXTRACTION_V4_TOPIC                           = google_pubsub_topic.medication_extraction_v4_topic.name
    EXTRACTION_CLASSIFY_INTERNAL_TOPIC                       = "NA"
    EXTRACTION_DOCUMENT_STATUS_TOPIC                         = google_pubsub_topic.medication_extraction_doc_status_topic.name
    EXTRACTION_MEDICATION_INTERNAL_TOPIC                     = "NA"
    EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC         = "NA"
    PAPERGLASS_API_URL                                       = module.paperglass_api.url
    PAPERGLASS_INTEGRATION_TOPIC                             = google_pubsub_topic.paperglass_integration_topic.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME               = google_cloud_tasks_queue.v4_extraction_entrypoint.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY      = google_cloud_tasks_queue.v4_extraction_entrypoint_priority.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE    = google_cloud_tasks_queue.v4_extraction_entrypoint_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME             = google_cloud_tasks_queue.v4_status_check.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY    = google_cloud_tasks_queue.v4_status_check_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE  = google_cloud_tasks_queue.v4_status_check_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME            = google_cloud_tasks_queue.v4_paperglass_integration_status_update.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY   = google_cloud_tasks_queue.v4_paperglass_integration_status_update_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE = google_cloud_tasks_queue.v4_paperglass_integration_status_update_quarantine.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME                 = google_cloud_tasks_queue.v4_paperglass_medications_integration.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY        = google_cloud_tasks_queue.v4_paperglass_medications_integration_priority.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE      = google_cloud_tasks_queue.v4_paperglass_medications_integration_quarantine.name
    AUDIT_LOGGER_TOPIC                                           = "prompt_logger_topic" #only used for local dev
    AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME                           = google_cloud_tasks_queue.v4_audit_log_queue.name
    AUDIT_LOGGER_API_URL                                         = module.audit_logger_api.url
    LLM_PROMPT_AUDIT_ENABLED                                     = "true"
    LOADTEST_LLM_EMULATOR_ENABLED                                = "false" # Enables the load testing LLM emulator
    STEP_CLASSIFY_LLM_MODEL                                      = var.step_classify_llm_model
    STEP_EXTRACTMEDICATION_LLM_MODEL                             = var.step_extractmedication_llm_model
    STEP_MEDISPANMATCH_LLM_MODEL                                 = var.step_medispanmatch_llm_model
    MEDISPAN_API_BASE_URL                                        = format("%s/%s/", module.medispan_api.url, "api")
    PGVECTOR_HOST                = var.alloydb_ip_address
    PGVECTOR_PORT                = 5432
    PGVECTOR_USER                = var.alloydb_user_username
    PGVECTOR_PASSWORD            = var.alloydb_user_password
    PGVECTOR_DATABASE            = "postgres"
    PGVECTOR_SSL_MODE            = "require"
    PGVECTOR_CONNECTION_TIMEOUT  = 1
    PGVECTOR_EMBEDDING_DIMENSION = 768
    PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH = "false"
    PGVECTOR_TABLE_MEDISPAN      = var.meddb_table_medispan
    PGVECTOR_TABLE_MERATIVE      = var.meddb_table_merative
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN = var.meddb_search_function_medispan
    PGVECTOR_SEARCH_FUNCTION_MERATIVE = var.meddb_search_function_merative
    FIRESTOREVECTOR_COLLECTION_MEDISPAN = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE = "meddb_merative"

    MEDDB_REPO_STRATEGY          = var.meddb_active_repo

    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT  = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
    FOO="bar" # adding to force a deploy of this container
  }
  secrets = toset([
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
  ])
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 1 : 1
  concurrency         = 300  # This needs to be pulled from tfvars as it is overwritten on promote env
  memory              = 4096 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4   # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 600
  vpc_connector_name  = var.vpc_connector
}


module "medication_extraction_api_2" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medication-extraction-2"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medication_extraction:${coalesce(var.paperglass_version, var.apps_version)}"
  command = [
    "uv", "run","uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", "9"
  ]
  env = {
    SERVICE                                                  = "medication_extraction"
    STAGE                                                    = var.env
    VERSION                                                  = var.medication_extraction_version
    DEBUG                                                    = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                                          = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                                           = var.app_project_id
    GCP_LOCATION                                             = split("-", var.region)[0]
    GCP_LOCATION_2                                           = var.region
    GCP_LOCATION_3                                           = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON                       = "nam5"
    GCP_FIRESTORE_DB                                         = "viki-${var.env}"
    GCP_DOCAI_DOC_PROCESSOR_ID                               = split("/", google_document_ai_processor.document_ocr_processor.id)[5] # Extract the processor ID from the resource URI
    GCP_DOCAI_DOC_PROCESSOR_VERSION                          = "pretrained"
    CLOUD_PROVIDER                                           = "google"
    CLOUD_PROVIDER                                           = "google"
    SELF_API_URL                                             = var.medication_extraction_api_2_url
    SELF_API_URL_2                                           = var.medication_extraction_api_url
    DEFAULT_PRIORITY_QUEUE_API_URL                           = var.medication_extraction_default_api_url
    HIGH_PRIORITY_QUEUE_API_URL                              = var.medication_extraction_high_api_url
    QUARANTINE_QUEUE_API_URL                                 = var.medication_extraction_quarantine_api_url
    QUEUE_RESOLVER_VERSION                                   = var.cloudtask_queue_resolver_version
    CLOUDTASK_REGISTERED_APP_IDS                             = join(",", var.registered_app_ids)
    CLOUD_TASK_QUEUE_NAME                                    = google_cloud_tasks_queue.paperglass_classification.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY                           = google_cloud_tasks_queue.paperglass_classification_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE                         = google_cloud_tasks_queue.paperglass_classification_quarantine.name
    CLOUD_TASK_QUEUE_NAME_2                                  = google_cloud_tasks_queue.paperglass_extraction.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2                         = google_cloud_tasks_queue.paperglass_extraction_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2                       = google_cloud_tasks_queue.paperglass_extraction_quarantine.name
    SERVICE_ACCOUNT_EMAIL                                    = module.ai_sa.email
    OKTA_CLIENT_ID                                           = "api.wellsky.viki.paperglass"
    OKTA_VERIFY                                              = "true"
    OKTA_AUDIENCE                                            = var.okta_audience # dev: "viki.prod.wellsky.io", qa: "viki.prod.wellsky.io", stage: "viki.prod.wellsky.io", prod: "viki.dev.wellsky.io"
    OKTA_TOKEN_ISSUER_URL                                    = var.okta_issuer_url
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_SERVICE_NAME                                        = "viki.paperglass.api"
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled
    GCP_PUBSUB_PROJECT_ID                                    = var.app_project_id
    EXTRACTION_PUBSUB_TOPIC_NAME                             = google_pubsub_topic.orchestraction_extraction_topic.name
    NEW_RELIC_LICENSE_KEY                                    = var.newrelic_api_license_key
    NEW_RELIC_APP_NAME                                       = "Viki Medication Extraction (${var.env})"
    NEW_RELIC_MONITOR_MODE                                   = "true"
    NEW_RELIC_LOG                                            = "stdout"
    NEW_RELIC_LOG_LEVEL                                      = "info"
    NEW_RELIC_HIGH_SECURITY                                  = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                    = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED         = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED   = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED            = "false"
    NEW_RELIC_TRACE_ENABLED                                  = var.newrelic_trace_enabled
    MEDICATION_EXTRACTION_V4_TOPIC                           = google_pubsub_topic.medication_extraction_v4_topic.name
    EXTRACTION_CLASSIFY_INTERNAL_TOPIC                       = "NA"
    EXTRACTION_DOCUMENT_STATUS_TOPIC                         = google_pubsub_topic.medication_extraction_doc_status_topic.name
    EXTRACTION_MEDICATION_INTERNAL_TOPIC                     = "NA"
    EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC         = "NA"
    PAPERGLASS_API_URL                                       = module.paperglass_api.url
    PAPERGLASS_INTEGRATION_TOPIC                             = google_pubsub_topic.paperglass_integration_topic.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME               = google_cloud_tasks_queue.v4_extraction_entrypoint.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY      = google_cloud_tasks_queue.v4_extraction_entrypoint_priority.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE    = google_cloud_tasks_queue.v4_extraction_entrypoint_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME             = google_cloud_tasks_queue.v4_status_check.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY    = google_cloud_tasks_queue.v4_status_check_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE  = google_cloud_tasks_queue.v4_status_check_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME            = google_cloud_tasks_queue.v4_paperglass_integration_status_update.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY   = google_cloud_tasks_queue.v4_paperglass_integration_status_update_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE = google_cloud_tasks_queue.v4_paperglass_integration_status_update_quarantine.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME                 = google_cloud_tasks_queue.v4_paperglass_medications_integration.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY        = google_cloud_tasks_queue.v4_paperglass_medications_integration_priority.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE      = google_cloud_tasks_queue.v4_paperglass_medications_integration_quarantine.name
    AUDIT_LOGGER_TOPIC                                           = "prompt_logger_topic" #only used for local dev
    AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME                           = google_cloud_tasks_queue.v4_audit_log_queue.name
    AUDIT_LOGGER_API_URL                                         = module.audit_logger_api.url
    LLM_PROMPT_AUDIT_ENABLED                                     = "true"
    LOADTEST_LLM_EMULATOR_ENABLED                                = "false" # Enables the load testing LLM emulator 
    STEP_CLASSIFY_LLM_MODEL                                      = var.step_classify_llm_model
    STEP_EXTRACTMEDICATION_LLM_MODEL                             = var.step_extractmedication_llm_model
    STEP_MEDISPANMATCH_LLM_MODEL                                 = var.step_medispanmatch_llm_model
    MEDISPAN_API_BASE_URL                                        = format("%s/%s/", module.medispan_api.url, "api")
    PGVECTOR_HOST                = var.alloydb_ip_address
    PGVECTOR_PORT                = 5432
    PGVECTOR_USER                = var.alloydb_user_username
    PGVECTOR_PASSWORD            = var.alloydb_user_password
    PGVECTOR_DATABASE            = "postgres"
    PGVECTOR_SSL_MODE            = "require"
    PGVECTOR_CONNECTION_TIMEOUT  = 1
    PGVECTOR_EMBEDDING_DIMENSION = 768
    PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH = "false"
    PGVECTOR_TABLE_MEDISPAN      = var.meddb_table_medispan
    PGVECTOR_TABLE_MERATIVE      = var.meddb_table_merative
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN = var.meddb_search_function_medispan
    PGVECTOR_SEARCH_FUNCTION_MERATIVE = var.meddb_search_function_merative
    FIRESTOREVECTOR_COLLECTION_MEDISPAN = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE = "meddb_merative"

    MEDDB_REPO_STRATEGY          = var.meddb_active_repo

    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT  = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
  }
  secrets = toset([
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
  ])
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 1 : 1
  concurrency         = 300  # This needs to be pulled from tfvars as it is overwritten on promote env
  memory              = 4096 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4   # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 600
  vpc_connector_name  = var.vpc_connector
}

module "medication_extraction_default_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medication-extraction-default"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medication_extraction:${coalesce(var.paperglass_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", "9"
  ]
  env = {
    SERVICE                                                  = "medication_extraction"
    STAGE                                                    = var.env
    VERSION                                                  = var.medication_extraction_version
    DEBUG                                                    = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                                          = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                                           = var.app_project_id
    GCP_LOCATION                                             = split("-", var.region)[0]
    GCP_LOCATION_2                                           = var.region
    GCP_LOCATION_3                                           = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON                       = "nam5"
    GCP_FIRESTORE_DB                                         = "viki-${var.env}"
    GCP_DOCAI_DOC_PROCESSOR_ID                               = split("/", google_document_ai_processor.document_ocr_processor.id)[5] # Extract the processor ID from the resource URI
    GCP_DOCAI_DOC_PROCESSOR_VERSION                          = "pretrained"
    CLOUD_PROVIDER                                           = "google"
    SELF_API_URL                                             = var.medication_extraction_api_url
    SELF_API_URL_2                                           = var.medication_extraction_api_url
    DEFAULT_PRIORITY_QUEUE_API_URL                           = var.medication_extraction_default_api_url
    HIGH_PRIORITY_QUEUE_API_URL                              = var.medication_extraction_high_api_url
    QUARANTINE_QUEUE_API_URL                                 = var.medication_extraction_quarantine_api_url
    QUEUE_RESOLVER_VERSION                                   = var.cloudtask_queue_resolver_version
    CLOUDTASK_REGISTERED_APP_IDS                             = join(",", var.registered_app_ids)
    CLOUD_TASK_QUEUE_NAME                                    = google_cloud_tasks_queue.paperglass_classification.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY                           = google_cloud_tasks_queue.paperglass_classification_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE                         = google_cloud_tasks_queue.paperglass_classification_quarantine.name
    CLOUD_TASK_QUEUE_NAME_2                                  = google_cloud_tasks_queue.paperglass_extraction.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2                         = google_cloud_tasks_queue.paperglass_extraction_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2                       = google_cloud_tasks_queue.paperglass_extraction_quarantine.name
    SERVICE_ACCOUNT_EMAIL                                    = module.ai_sa.email
    OKTA_CLIENT_ID                                           = "api.wellsky.viki.paperglass"
    OKTA_VERIFY                                              = "true"
    OKTA_AUDIENCE                                            = var.okta_audience # dev: "viki.prod.wellsky.io", qa: "viki.prod.wellsky.io", stage: "viki.prod.wellsky.io", prod: "viki.dev.wellsky.io"
    OKTA_TOKEN_ISSUER_URL                                    = var.okta_issuer_url
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_SERVICE_NAME                                        = "viki.paperglass.api"
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled
    GCP_PUBSUB_PROJECT_ID                                    = var.app_project_id
    EXTRACTION_PUBSUB_TOPIC_NAME                             = google_pubsub_topic.orchestraction_extraction_topic.name
    NEW_RELIC_LICENSE_KEY                                    = var.newrelic_api_license_key
    NEW_RELIC_APP_NAME                                       = "Viki Medication Extraction (${var.env})"
    NEW_RELIC_MONITOR_MODE                                   = "true"
    NEW_RELIC_LOG                                            = "stdout"
    NEW_RELIC_LOG_LEVEL                                      = "info"
    NEW_RELIC_HIGH_SECURITY                                  = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                    = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED         = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED   = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED            = "false"
    NEW_RELIC_TRACE_ENABLED                                  = var.newrelic_trace_enabled
    MEDICATION_EXTRACTION_V4_TOPIC                           = google_pubsub_topic.medication_extraction_v4_topic.name
    EXTRACTION_CLASSIFY_INTERNAL_TOPIC                       = "NA"
    EXTRACTION_DOCUMENT_STATUS_TOPIC                         = google_pubsub_topic.medication_extraction_doc_status_topic.name
    EXTRACTION_MEDICATION_INTERNAL_TOPIC                     = "NA"
    EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC         = "NA"
    PAPERGLASS_API_URL                                       = module.paperglass_api.url
    PAPERGLASS_INTEGRATION_TOPIC                             = google_pubsub_topic.paperglass_integration_topic.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME               = google_cloud_tasks_queue.v4_extraction_entrypoint.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY      = google_cloud_tasks_queue.v4_extraction_entrypoint_priority.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE    = google_cloud_tasks_queue.v4_extraction_entrypoint_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME             = google_cloud_tasks_queue.v4_status_check.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY    = google_cloud_tasks_queue.v4_status_check_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE  = google_cloud_tasks_queue.v4_status_check_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME            = google_cloud_tasks_queue.v4_paperglass_integration_status_update.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY   = google_cloud_tasks_queue.v4_paperglass_integration_status_update_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE = google_cloud_tasks_queue.v4_paperglass_integration_status_update_quarantine.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME                 = google_cloud_tasks_queue.v4_paperglass_medications_integration.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY        = google_cloud_tasks_queue.v4_paperglass_medications_integration_priority.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE      = google_cloud_tasks_queue.v4_paperglass_medications_integration_quarantine.name
    AUDIT_LOGGER_TOPIC                                           = "prompt_logger_topic" #only used for local dev
    AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME                           = google_cloud_tasks_queue.v4_audit_log_queue.name
    AUDIT_LOGGER_API_URL                                         = module.audit_logger_api.url
    LLM_PROMPT_AUDIT_ENABLED                                     = "true"
    LOADTEST_LLM_EMULATOR_ENABLED                                = "false"
    STEP_CLASSIFY_LLM_MODEL                                      = var.step_classify_llm_model
    STEP_EXTRACTMEDICATION_LLM_MODEL                             = var.step_extractmedication_llm_model
    STEP_MEDISPANMATCH_LLM_MODEL                                 = var.step_medispanmatch_llm_model
    MEDISPAN_API_BASE_URL                                        = format("%s/%s/", module.medispan_api.url, "api")
    PGVECTOR_HOST                                           = var.alloydb_ip_address
    PGVECTOR_PORT                                           = 5432
    PGVECTOR_USER                                           = var.alloydb_user_username
    PGVECTOR_PASSWORD                                       = var.alloydb_user_password
    PGVECTOR_DATABASE                                       = "postgres"
    PGVECTOR_SSL_MODE                                       = "require"
    PGVECTOR_CONNECTION_TIMEOUT                             = 1
    PGVECTOR_EMBEDDING_DIMENSION                            = 768
    PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH                    = "false"
    PGVECTOR_TABLE_MEDISPAN                                 = var.meddb_table_medispan
    PGVECTOR_TABLE_MERATIVE                                 = var.meddb_table_merative
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN                       = var.meddb_search_function_medispan
    PGVECTOR_SEARCH_FUNCTION_MERATIVE                       = var.meddb_search_function_merative
    FIRESTOREVECTOR_COLLECTION_MEDISPAN                     = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE                     = "meddb_merative"

    MEDDB_REPO_STRATEGY          = var.meddb_active_repo

    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT  = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
  }
  secrets = toset([
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
  ])
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 1 : 1
  concurrency         = 300
  memory              = 8192 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4    # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 600
  vpc_connector_name  = var.vpc_connector
}

module "medication_extraction_high_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medication-extraction-high"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medication_extraction:${coalesce(var.paperglass_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", "9"
  ]
  env = {
    SERVICE                                                  = "medication_extraction"
    STAGE                                                    = var.env
    VERSION                                                  = var.medication_extraction_version
    DEBUG                                                    = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                                          = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                                           = var.app_project_id
    GCP_LOCATION                                             = split("-", var.region)[0]
    GCP_LOCATION_2                                           = var.region
    GCP_LOCATION_3                                           = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON                       = "nam5"
    GCP_FIRESTORE_DB                                         = "viki-${var.env}"
    GCP_DOCAI_DOC_PROCESSOR_ID                               = split("/", google_document_ai_processor.document_ocr_processor.id)[5] # Extract the processor ID from the resource URI
    GCP_DOCAI_DOC_PROCESSOR_VERSION                          = "pretrained"
    CLOUD_PROVIDER                                           = "google"
    CLOUD_PROVIDER                                           = "google"
    SELF_API_URL                                             = var.medication_extraction_api_url
    SELF_API_URL_2                                           = var.medication_extraction_api_url
    DEFAULT_PRIORITY_QUEUE_API_URL                           = var.medication_extraction_default_api_url
    HIGH_PRIORITY_QUEUE_API_URL                              = var.medication_extraction_high_api_url
    QUARANTINE_QUEUE_API_URL                                 = var.medication_extraction_quarantine_api_url
    QUEUE_RESOLVER_VERSION                                   = var.cloudtask_queue_resolver_version
    CLOUDTASK_REGISTERED_APP_IDS                             = join(",", var.registered_app_ids)
    CLOUD_TASK_QUEUE_NAME                                    = google_cloud_tasks_queue.paperglass_classification.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY                           = google_cloud_tasks_queue.paperglass_classification_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE                         = google_cloud_tasks_queue.paperglass_classification_quarantine.name
    CLOUD_TASK_QUEUE_NAME_2                                  = google_cloud_tasks_queue.paperglass_extraction.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2                         = google_cloud_tasks_queue.paperglass_extraction_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2                       = google_cloud_tasks_queue.paperglass_extraction_quarantine.name
    SERVICE_ACCOUNT_EMAIL                                    = module.ai_sa.email
    OKTA_CLIENT_ID                                           = "api.wellsky.viki.paperglass"
    OKTA_VERIFY                                              = "true"
    OKTA_AUDIENCE                                            = var.okta_audience # dev: "viki.prod.wellsky.io", qa: "viki.prod.wellsky.io", stage: "viki.prod.wellsky.io", prod: "viki.dev.wellsky.io"
    OKTA_TOKEN_ISSUER_URL                                    = var.okta_issuer_url
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_SERVICE_NAME                                        = "viki.paperglass.api"
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled
    GCP_PUBSUB_PROJECT_ID                                    = var.app_project_id
    EXTRACTION_PUBSUB_TOPIC_NAME                             = google_pubsub_topic.orchestraction_extraction_topic.name
    NEW_RELIC_LICENSE_KEY                                    = var.newrelic_api_license_key
    NEW_RELIC_APP_NAME                                       = "Viki Medication Extraction (${var.env})"
    NEW_RELIC_MONITOR_MODE                                   = "true"
    NEW_RELIC_LOG                                            = "stdout"
    NEW_RELIC_LOG_LEVEL                                      = "info"
    NEW_RELIC_HIGH_SECURITY                                  = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                    = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED         = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED   = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED            = "false"
    NEW_RELIC_TRACE_ENABLED                                  = var.newrelic_trace_enabled
    MEDICATION_EXTRACTION_V4_TOPIC                           = google_pubsub_topic.medication_extraction_v4_topic.name
    EXTRACTION_CLASSIFY_INTERNAL_TOPIC                       = "NA"
    EXTRACTION_DOCUMENT_STATUS_TOPIC                         = google_pubsub_topic.medication_extraction_doc_status_topic.name
    EXTRACTION_MEDICATION_INTERNAL_TOPIC                     = "NA"
    EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC         = "NA"
    PAPERGLASS_API_URL                                       = module.paperglass_api.url
    PAPERGLASS_INTEGRATION_TOPIC                             = google_pubsub_topic.paperglass_integration_topic.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME               = google_cloud_tasks_queue.v4_extraction_entrypoint.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY      = google_cloud_tasks_queue.v4_extraction_entrypoint_priority.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE    = google_cloud_tasks_queue.v4_extraction_entrypoint_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME             = google_cloud_tasks_queue.v4_status_check.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY    = google_cloud_tasks_queue.v4_status_check_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE  = google_cloud_tasks_queue.v4_status_check_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME            = google_cloud_tasks_queue.v4_paperglass_integration_status_update.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY   = google_cloud_tasks_queue.v4_paperglass_integration_status_update_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE = google_cloud_tasks_queue.v4_paperglass_integration_status_update_quarantine.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME                 = google_cloud_tasks_queue.v4_paperglass_medications_integration.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY        = google_cloud_tasks_queue.v4_paperglass_medications_integration_priority.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE      = google_cloud_tasks_queue.v4_paperglass_medications_integration_quarantine.name
    CALLBACK_PAPERGLASS_ENABLED                                  = "true" # Used to turn off callback to paperglass for quarantine parallel testing
    AUDIT_LOGGER_TOPIC                                           = "prompt_logger_topic" #only used for local dev
    AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME                           = google_cloud_tasks_queue.v4_audit_log_queue.name
    AUDIT_LOGGER_API_URL                                         = module.audit_logger_api.url
    LLM_PROMPT_AUDIT_ENABLED                                     = "true"
    LOADTEST_LLM_EMULATOR_ENABLED                                = "false"
    STEP_CLASSIFY_LLM_MODEL                                      = var.step_classify_llm_model
    STEP_EXTRACTMEDICATION_LLM_MODEL                             = var.step_extractmedication_llm_model
    STEP_MEDISPANMATCH_LLM_MODEL                                 = var.step_medispanmatch_llm_model
    MEDISPAN_API_BASE_URL                                        = format("%s/%s/", module.medispan_api_high.url, "api")
    PGVECTOR_HOST                = var.alloydb_ip_address
    PGVECTOR_PORT                = 5432
    PGVECTOR_USER                = var.alloydb_user_username
    PGVECTOR_PASSWORD            = var.alloydb_user_password
    PGVECTOR_DATABASE            = "postgres"
    PGVECTOR_SSL_MODE            = "require"
    PGVECTOR_CONNECTION_TIMEOUT  = 1
    PGVECTOR_EMBEDDING_DIMENSION = 768
    PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH = "false"
    PGVECTOR_TABLE_MEDISPAN      = var.meddb_table_medispan
    PGVECTOR_TABLE_MERATIVE      = var.meddb_table_merative    
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN = var.meddb_search_function_medispan
    PGVECTOR_SEARCH_FUNCTION_MERATIVE = var.meddb_search_function_merative
    FIRESTOREVECTOR_COLLECTION_MEDISPAN = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE = "meddb_merative"

    MEDDB_REPO_STRATEGY          = var.meddb_active_repo

    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT  = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
  }
  secrets = toset([
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
  ])
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 1 : 1
  concurrency         = 300
  memory              = 8192 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4    # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 600
  vpc_connector_name  = var.vpc_connector
}

module "medication_extraction_quarantine_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medication-extraction-quarantine"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medication_extraction:${coalesce(var.paperglass_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", "9"
  ]
  env = {
    SERVICE                                                  = "medication_extraction"
    STAGE                                                    = var.env
    VERSION                                                  = var.medication_extraction_version
    DEBUG                                                    = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                                          = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                                           = var.app_project_id
    GCP_LOCATION                                             = split("-", var.region)[0]
    GCP_LOCATION_2                                           = var.region
    GCP_LOCATION_3                                           = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON                       = "nam5"
    GCP_FIRESTORE_DB                                         = "viki-${var.env}"
    GCP_DOCAI_DOC_PROCESSOR_ID                               = split("/", google_document_ai_processor.document_ocr_processor.id)[5] # Extract the processor ID from the resource URI
    GCP_DOCAI_DOC_PROCESSOR_VERSION                          = "pretrained"
    CLOUD_PROVIDER                                           = "google"
    SELF_API_URL                                             = var.medication_extraction_api_url
    SELF_API_URL_2                                           = var.medication_extraction_api_url
    DEFAULT_PRIORITY_QUEUE_API_URL                           = var.medication_extraction_default_api_url
    HIGH_PRIORITY_QUEUE_API_URL                              = var.medication_extraction_high_api_url
    QUARANTINE_QUEUE_API_URL                                 = var.medication_extraction_quarantine_api_url
    QUEUE_RESOLVER_VERSION                                   = var.cloudtask_queue_resolver_version
    CLOUDTASK_REGISTERED_APP_IDS                             = join(",", var.registered_app_ids)
    CLOUD_TASK_QUEUE_NAME                                    = google_cloud_tasks_queue.paperglass_classification.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY                           = google_cloud_tasks_queue.paperglass_classification_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE                         = google_cloud_tasks_queue.paperglass_classification_quarantine.name
    CLOUD_TASK_QUEUE_NAME_2                                  = google_cloud_tasks_queue.paperglass_extraction.name
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2                         = google_cloud_tasks_queue.paperglass_extraction_priority.name
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2                       = google_cloud_tasks_queue.paperglass_extraction_quarantine.name
    SERVICE_ACCOUNT_EMAIL                                    = module.ai_sa.email
    OKTA_CLIENT_ID                                           = "api.wellsky.viki.paperglass"
    OKTA_VERIFY                                              = "true"
    OKTA_AUDIENCE                                            = var.okta_audience # dev: "viki.prod.wellsky.io", qa: "viki.prod.wellsky.io", stage: "viki.prod.wellsky.io", prod: "viki.dev.wellsky.io"
    OKTA_TOKEN_ISSUER_URL                                    = var.okta_issuer_url
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_SERVICE_NAME                                        = "viki.paperglass.api"
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled
    GCP_PUBSUB_PROJECT_ID                                    = var.app_project_id
    EXTRACTION_PUBSUB_TOPIC_NAME                             = google_pubsub_topic.orchestraction_extraction_topic.name
    NEW_RELIC_LICENSE_KEY                                    = var.newrelic_api_license_key
    NEW_RELIC_APP_NAME                                       = "Viki Medication Extraction (${var.env})"
    NEW_RELIC_MONITOR_MODE                                   = "true"
    NEW_RELIC_LOG                                            = "stdout"
    NEW_RELIC_LOG_LEVEL                                      = "info"
    NEW_RELIC_HIGH_SECURITY                                  = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                    = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED         = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED   = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED            = "false"
    NEW_RELIC_TRACE_ENABLED                                  = var.newrelic_trace_enabled
    MEDICATION_EXTRACTION_V4_TOPIC                           = google_pubsub_topic.medication_extraction_v4_topic.name
    EXTRACTION_CLASSIFY_INTERNAL_TOPIC                       = "NA"
    EXTRACTION_DOCUMENT_STATUS_TOPIC                         = google_pubsub_topic.medication_extraction_doc_status_topic.name
    EXTRACTION_MEDICATION_INTERNAL_TOPIC                     = "NA"
    EXTRACTION_STANDARDIZE_MEDICATION_INTERNAL_TOPIC         = "NA"
    PAPERGLASS_API_URL                                       = module.paperglass_api.url
    PAPERGLASS_INTEGRATION_TOPIC                             = google_pubsub_topic.paperglass_integration_topic.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME               = google_cloud_tasks_queue.v4_extraction_entrypoint.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY      = google_cloud_tasks_queue.v4_extraction_entrypoint_priority.name
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE    = google_cloud_tasks_queue.v4_extraction_entrypoint_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME             = google_cloud_tasks_queue.v4_status_check.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_PRIORITY    = google_cloud_tasks_queue.v4_status_check_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME_QUARANTINE  = google_cloud_tasks_queue.v4_status_check_quarantine.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME            = google_cloud_tasks_queue.v4_paperglass_integration_status_update.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_PRIORITY   = google_cloud_tasks_queue.v4_paperglass_integration_status_update_priority.name
    MEDICATION_EXTRACTION_V4_STATUS_UPDATE_QUEUE_NAME_QUARANTINE = google_cloud_tasks_queue.v4_paperglass_integration_status_update_quarantine.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME                 = google_cloud_tasks_queue.v4_paperglass_medications_integration.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_PRIORITY        = google_cloud_tasks_queue.v4_paperglass_medications_integration_priority.name
    PAPERGLASS_INTEGRATION_CLOUD_TASK_QUEUE_NAME_QUARANTINE      = google_cloud_tasks_queue.v4_paperglass_medications_integration_quarantine.name
    CALLBACK_PAPERGLASS_ENABLED                                  = "false" # Used to turn off callback to paperglass for quarantine parallel testing
    AUDIT_LOGGER_TOPIC                                           = "prompt_logger_topic" #only used for local dev
    AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME                           = google_cloud_tasks_queue.v4_audit_log_queue.name
    AUDIT_LOGGER_API_URL                                         = module.audit_logger_api.url
    LLM_PROMPT_AUDIT_ENABLED                                     = "true"
    LOADTEST_LLM_EMULATOR_ENABLED                                = "false"
    STEP_CLASSIFY_LLM_MODEL                                      = "gemini-2.5-flash-lite"
    STEP_EXTRACTMEDICATION_LLM_MODEL                             = "gemini-2.5-flash-lite"
    STEP_MEDISPANMATCH_LLM_MODEL                                 = "gemini-2.5-flash-lite"
    MEDISPAN_API_BASE_URL                                        = format("%s/%s/", module.medispan_api_quarantine.url, "api")
    PGVECTOR_HOST                                           = var.alloydb_ip_address
    PGVECTOR_PORT                                           = 5432
    PGVECTOR_USER                                           = var.alloydb_user_username
    PGVECTOR_PASSWORD                                       = var.alloydb_user_password
    PGVECTOR_DATABASE                                       = "postgres"
    PGVECTOR_SSL_MODE                                       = "require"
    PGVECTOR_CONNECTION_TIMEOUT                             = 1
    PGVECTOR_EMBEDDING_DIMENSION                            = 768
    PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH                    = "false"
    PGVECTOR_TABLE_MEDISPAN                                 = var.meddb_table_medispan
    PGVECTOR_TABLE_MERATIVE                                 = var.meddb_table_merative
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN                       = var.meddb_search_function_medispan
    PGVECTOR_SEARCH_FUNCTION_MERATIVE                       = var.meddb_search_function_merative
    FIRESTOREVECTOR_COLLECTION_MEDISPAN                     = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE                     = "meddb_merative"

    MEDDB_REPO_STRATEGY                                     = var.meddb_active_repo

    CIRCUIT_BREAKER_FAILURE_THRESHOLD                       = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT                        = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD                       = 2
  }
  secrets = toset([
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
  ])
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 0
  concurrency         = 300
  memory              = 8192 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4    # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 600
  vpc_connector_name  = var.vpc_connector
}
