module "skysense-scribe-api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "skysense-scribe-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/skysense-scribe-api:${var.skysense_scribe_api_version}"
  command = [
    "uv", "run", "uvicorn", "api.main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.skysense_scribe_api.uvicorn_workers),
  ]

  env = {
    SERVICE                   = "skysense-scribe-api"
    STAGE                     = var.env
    VERSION                   = var.skysense_scribe_api_version
    DEBUG                     = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME           = module.ai_provisional_bucket.name
    GCP_PROJECT_ID            = var.app_project_id
    GCP_LOCATION              = "us-central1"
    APPLY_DIARIZATION_FIX     = "true"
    GOOGLE_SPEECH_API_VERSION = "v1"
    OKTA_DISABLE              = (var.env == "dev" || var.env == "qa") ? "true" : "false" # TODO
    OKTA_TOKEN_ISSUER_URL     = var.okta_service_issuer_url
    OKTA_AUDIENCE             = var.okta_service_audience
    OKTA_SCOPE                = var.okta_scopes.transcription
    AWS_DEFAULT_REGION        = var.aws_default_region
    CLOUD_PROVIDER            = "google"
    DEEPGRAM_API_URL          = "http://34.117.227.129/"
    DEEPGRAM_WS_URL           = "ws://34.117.227.129/"
    DEEPGRAM_API_KEY          = "DEEPGRAM_API_KEY"
    TRANSCRIBE_MODEL          = "nova-3"
    GEMINI_MODEL              = "gemini-2.5-flash-lite"
    GEMINI_LITE_MODEL         = "gemini-2.5-flash-lite"
    GOOGLE_CLOUD_PROJECT      = var.app_project_id
    GCS_TEMP_BUCKET_NAME      = "ltc-scribe-temp-bucket-qa"
    GCS_SCRIBE_BUCKET_NAME    = "ltc-scribe-bucket-qa"
    GCS_ISSUE_LOGS_BUCKET     = module.scribe_issue_log_bucket.name
    GEMINI_API_KEY            = "GEMINI_API_KEY"
    GOOGLE_API_KEY            = "GOOGLE_API_KEY"
    SUPPORT_TOOL_APP_ID       = "cmehaa54f00013b6oc3ijh6u1"
    SUPER_USER_PWD            = var.scribe_superuser_password
    JWT_SECRET_KEY            = var.scribe_jwt_secret
    LOG_LEVEL                 = "DEBUG"
    QUESTION_BATCH_SIZE       = 5
  }
  project_id          = var.app_project_id
  vpc_connector_name  = var.vpc_connector
  labels = merge(
    var.labels,
    {
      service     = "skysense-scribe-api"
      application = "scribe"
    }
  )
  ingress             = "all"
  allow_public_access = var.cloud_run_services.skysense_scribe_api.allow_public_access
  min_instances       = var.cloud_run_services.skysense_scribe_api.min_instances
  max_instances       = var.cloud_run_services.skysense_scribe_api.max_instances == "unlimited" ? null : var.cloud_run_services.skysense_scribe_api.max_instances
  memory              = var.cloud_run_services.skysense_scribe_api.memory
  cpus                = var.cloud_run_services.skysense_scribe_api.cpus
  concurrency         = var.cloud_run_services.skysense_scribe_api.concurrency
  timeout             = var.cloud_run_services.skysense_scribe_api.timeout
}

module "skysense-scribe-ws" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "skysense-scribe-ws"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/skysense-scribe-api:${var.skysense_scribe_api_version}"
  command = [
    "uv", "run", "uvicorn", "api.main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.skysense_scribe_ws.uvicorn_workers),
  ]

  env = {
    SERVICE                   = "skysense-scribe-ws"
    STAGE                     = var.env
    VERSION                   = var.skysense_scribe_api_version
    DEBUG                     = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME           = module.ai_provisional_bucket.name
    GCP_PROJECT_ID            = var.app_project_id
    GCP_LOCATION              = "us-central1"
    GOOGLE_SPEECH_API_VERSION = "v1"
    OKTA_DISABLE              = (var.env == "dev" || var.env == "qa") ? "true" : "false" # TODO
    OKTA_TOKEN_ISSUER_URL     = var.okta_service_issuer_url
    OKTA_AUDIENCE             = var.okta_service_audience
    OKTA_SCOPE                = var.okta_scopes.transcription
    AWS_DEFAULT_REGION        = var.aws_default_region
    CLOUD_PROVIDER            = "google"
    DEEPGRAM_API_URL          = "http://34.117.227.129/"
    DEEPGRAM_WS_URL           = "ws://34.117.227.129/"
    DEEPGRAM_API_KEY          = "DEEPGRAM_API_KEY"
    TRANSCRIBE_MODEL          = "nova-3"
    GEMINI_MODEL              = "gemini-2.5-flash-lite"
    GEMINI_LITE_MODEL         = "gemini-2.5-flash-lite"
    GOOGLE_CLOUD_PROJECT      = var.app_project_id
    GCS_TEMP_BUCKET_NAME      = "tc-scribe-temp-bucket-qa"
    GCS_SCRIBE_BUCKET_NAME    = "ltc-scribe-bucket-qa"
    GEMINI_API_KEY            = "GEMINI_API_KEY"
    GOOGLE_API_KEY            = "GOOGLE_API_KEY"
    JWT_SECRET_KEY            = var.scribe_jwt_secret
    LOG_LEVEL                 = "DEBUG"
  }
  project_id          = var.app_project_id
  labels = merge(
    var.labels,
    {
      service     = "skysense-scribe-ws"
      application = "scribe"
    }
  )
  ingress             = "all"
  allow_public_access = var.cloud_run_services.skysense_scribe_ws.allow_public_access
  min_instances       = var.cloud_run_services.skysense_scribe_ws.min_instances
  max_instances       = var.cloud_run_services.skysense_scribe_ws.max_instances == "unlimited" ? null : var.cloud_run_services.skysense_scribe_ws.max_instances
  memory              = var.cloud_run_services.skysense_scribe_ws.memory
  cpus                = var.cloud_run_services.skysense_scribe_ws.cpus
  concurrency         = var.cloud_run_services.skysense_scribe_ws.concurrency
  timeout             = var.cloud_run_services.skysense_scribe_ws.timeout
}



module "skysense_scribe_events" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "skysense-scribe-events"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/skysense-scribe-api:${var.skysense_scribe_api_version}"
  command = [
    "uv", "run", "uvicorn", "api.event:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.skysense_scribe_events.uvicorn_workers),
  ]

  env = {
    SERVICE                   = "skysense-scribe-events"
    STAGE                     = var.env
    VERSION                   = var.skysense_scribe_api_version
    DEBUG                     = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME           = module.ai_provisional_bucket.name
    GCP_PROJECT_ID            = var.app_project_id
    GCP_LOCATION              = "us-central1"
    GOOGLE_SPEECH_API_VERSION = "v1"
    OKTA_DISABLE              = (var.env == "dev" || var.env == "qa") ? "true" : "false" # TODO
    OKTA_TOKEN_ISSUER_URL     = var.okta_service_issuer_url
    OKTA_AUDIENCE             = var.okta_service_audience
    OKTA_SCOPE                = var.okta_scopes.transcription
    AWS_DEFAULT_REGION        = var.aws_default_region
    CLOUD_PROVIDER            = "google"
    DEEPGRAM_API_URL          = "http://34.117.227.129/"
    DEEPGRAM_API_KEY          = "DEEPGRAM_API_KEY"
    TRANSCRIBE_MODEL          = "nova-3"
    GEMINI_MODEL              = "gemini-2.5-flash-lite"
    GEMINI_LITE_MODEL         = "gemini-2.5-flash-lite"
    GOOGLE_CLOUD_PROJECT      = var.app_project_id
    GCS_TEMP_BUCKET_NAME      = "tc-scribe-temp-bucket-qa"
    GCS_SCRIBE_BUCKET_NAME    = "ltc-scribe-bucket-qa"
    GEMINI_API_KEY            = "GEMINI_API_KEY"
    GOOGLE_API_KEY            = "GOOGLE_API_KEY"
    LOG_LEVEL                 = "DEBUG"
    QUESTION_BATCH_SIZE       = 5
  }
  project_id          = var.app_project_id
  vpc_connector_name  = var.vpc_connector
  labels = merge(
    var.labels,
    {
      service     = "skysense-scribe-events"
      application = "scribe"
    }
  )
  ingress             = "all"
  allow_public_access = var.cloud_run_services.skysense_scribe_events.allow_public_access
  min_instances       = var.cloud_run_services.skysense_scribe_events.min_instances
  max_instances       = var.cloud_run_services.skysense_scribe_events.max_instances == "unlimited" ? null : var.cloud_run_services.skysense_scribe_events.max_instances
  memory              = var.cloud_run_services.skysense_scribe_events.memory
  cpus                = var.cloud_run_services.skysense_scribe_events.cpus
  concurrency         = var.cloud_run_services.skysense_scribe_events.concurrency
  timeout             = var.cloud_run_services.skysense_scribe_events.timeout  
}
