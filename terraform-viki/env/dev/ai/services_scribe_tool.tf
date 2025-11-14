module "skysense-scribe-tool" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "skysense-scribe-tool"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/skysense-scribe-api:${var.skysense_scribe_api_version}"
  command = [
    "./entrypoint.sh", "streamlit",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.skysense_scribe_tool.uvicorn_workers),
  ]

  env = {
    SERVICE                   = "skysense-scribe-tool"
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
    GOOGLE_CLOUD_PROJECT      = var.app_project_id
    GCS_TEMP_BUCKET_NAME      = "ltc-scribe-temp-bucket"
    GCS_SCRIBE_BUCKET_NAME    = "ltc-scribe-bucket"
    GEMINI_API_KEY            = "GEMINI_API_KEY"
    GOOGLE_API_KEY            = "GOOGLE_API_KEY"
    GCS_BUCKET_NAME_TOOL      = "poc-scribe-temp"
    LOG_LEVEL                 = "DEBUG"
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.skysense_scribe_tool.allow_public_access
  min_instances       = var.cloud_run_services.skysense_scribe_tool.min_instances
  max_instances       = var.cloud_run_services.skysense_scribe_tool.max_instances == "unlimited" ? null : var.cloud_run_services.skysense_scribe_tool.max_instances
  memory              = var.cloud_run_services.skysense_scribe_tool.memory
  cpus                = var.cloud_run_services.skysense_scribe_tool.cpus
  concurrency         = var.cloud_run_services.skysense_scribe_tool.concurrency
  timeout             = var.cloud_run_services.skysense_scribe_tool.timeout
}
