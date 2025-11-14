module "autoscribe_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-autoscribe-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-autoscribe-api:${coalesce(var.cloud_run_services.autoscribe_api.image_version, var.autoscribe_version)}"
  command = [
    "uvicorn", "autoscribe.entrypoints.http:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.autoscribe_api.uvicorn_workers),
  ]
  env = {
    SERVICE                   = "autoscribe"
    STAGE                     = var.env
    VERSION                   = coalesce(var.cloud_run_services.autoscribe_api.image_version, var.autoscribe_version)
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
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.autoscribe_api.allow_public_access
  organization_id     = var.organization_id
  min_instances       = var.cloud_run_services.autoscribe_api.min_instances
  max_instances       = var.cloud_run_services.autoscribe_api.max_instances == "unlimited" ? null : var.cloud_run_services.autoscribe_api.max_instances
  memory              = var.cloud_run_services.autoscribe_api.memory
  cpus                = var.cloud_run_services.autoscribe_api.cpus
  timeout             = var.cloud_run_services.autoscribe_api.timeout
  project_id          = var.app_project_id
}

module "autoscribe_widget_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-autoscribe-widget-${var.env}-envjson"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    API_URL = module.autoscribe_api.url
    VERSION = var.autoscribe_version
  })
  skip_secret_data = false
}

module "autoscribe_widget" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-autoscribe-widget"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-autoscribe-widget:${coalesce(var.cloud_run_services.autoscribe_widget.image_version, var.autoscribe_version)}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.autoscribe_widget_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.autoscribe_api.allow_public_access
  organization_id     = var.organization_id
  min_instances       = var.cloud_run_services.autoscribe_widget.min_instances
  max_instances       = var.cloud_run_services.autoscribe_widget.max_instances == "unlimited" ? null : var.cloud_run_services.autoscribe_widget.max_instances
  memory              = var.cloud_run_services.autoscribe_widget.memory
  cpus                = var.cloud_run_services.autoscribe_widget.cpus
  timeout             = var.cloud_run_services.autoscribe_widget.timeout
  project_id          = var.app_project_id
  depends_on          = [module.autoscribe_widget_envjson]
}
