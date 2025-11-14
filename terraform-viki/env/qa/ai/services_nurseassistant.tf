module "nurse_assistant" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-nurse-assistant"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-nurse-assistant:${var.nurse_assistant_version}"
  command = [
    "./entrypoint.sh", "streamlit",
    "--host", "0.0.0.0",
    "--port", "8080",
  ]

  env = {
    SERVICE                   = "nurse_assistant"
    STAGE                     = var.env
    VERSION                   = var.nurse_assistant_version
    DEBUG                     = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME           = module.ai_provisional_bucket.name
    GCP_PROJECT_ID            = var.app_project_id
    GOOGLE_SPEECH_API_VERSION = "v1"
    OKTA_DISABLE              = (var.env == "dev" || var.env == "qa") ? "true" : "false" # TODO
    OKTA_ISSUER               = var.okta_issuer
    OKTA_AUDIENCE             = var.okta_audience
    OKTA_SCOPE                = var.okta_scopes.transcription
    AWS_DEFAULT_REGION        = var.aws_default_region
    CLOUD_PROVIDER            = "google"
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.nurse_assistant.allow_public_access
  min_instances       = var.cloud_run_services.nurse_assistant.min_instances
  max_instances       = var.cloud_run_services.nurse_assistant.max_instances == "unlimited" ? null : var.cloud_run_services.nurse_assistant.max_instances
  memory              = var.cloud_run_services.nurse_assistant.memory  
  cpus                = var.cloud_run_services.nurse_assistant.cpus
  concurrency         = var.cloud_run_services.nurse_assistant.concurrency
  timeout             = var.cloud_run_services.nurse_assistant.timeout  
}
