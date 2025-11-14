# Configuration for AI2 Autoscribe API Cloud Run service
module "ai2_autoscribe_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai2-autoscribe-api"
  location              = var.region
  service_account_email = module.ai_sa.email

  # TODO: Configure image and version
  image = "us-east4-docker.pkg.dev/viki-dev-mgmt-wsky/images/ai2-autoscribe-api:latest"
  command = [
    "uvicorn", "autoscribe.entrypoints.http:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.autoscribe_api.uvicorn_workers),
  ]
  env = {
    SERVICE                   = "autoscribe"
    STAGE                     = var.env
    VERSION                   = var.autoscribe_version
    DEBUG                     = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME           = module.ai_provisional_bucket.name
    GCP_PROJECT_ID            = var.app_project_id
    GOOGLE_SPEECH_API_VERSION = "v1"
    OKTA_DISABLE              = (var.env == "dev" || var.env == "qa") ? "true" : "false" # TODO
    OKTA_ISSUER               = var.okta_issuer
    OKTA_AUDIENCE             = var.okta_audience
    OKTA_SCOPE                = var.okta_scopes.transcription
    AWS_ROLE_ARN              = var.autoscribe_aws_role_arn
    AWS_DEFAULT_REGION        = var.aws_default_region
    CLOUD_PROVIDER            = "google"
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.autoscribe_api.allow_public_access
  min_instances       = var.cloud_run_services.autoscribe_api.min_instances
  max_instances       = var.cloud_run_services.autoscribe_api.max_instances == "unlimited" ? null : var.cloud_run_services.autoscribe_api.max_instances
  memory              = var.cloud_run_services.autoscribe_api.memory
  cpus                = var.cloud_run_services.autoscribe_api.cpus
  concurrency         = var.cloud_run_services.autoscribe_api.concurrency
  timeout             = var.cloud_run_services.autoscribe_api.timeout  
}

