module "nlparse_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-nlparse-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-nlparse-api:${coalesce(var.cloud_run_services.nlparse_api.image_version, var.nlparse_version)}"
  command = [
    "uvicorn", "nlparse.entrypoints.http:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.nlparse_api.uvicorn_workers),
  ]
  env = {
    SERVICE        = "nlparse"
    STAGE          = var.env
    VERSION        = var.nlparse_version
    DEBUG          = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCP_PROJECT_ID = var.app_project_id
    GCP_REGION     = var.nlparse_region
    # OKTA_DISABLE              = (var.env == "dev" || var.env == "qa") ? "true" : "false" # TODO
    # OKTA_ISSUER               = var.okta_issuer
    # OKTA_AUDIENCE             = var.okta_audience
    # OKTA_SCOPE                = var.okta_scopes.transcription
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.nlparse_api.allow_public_access
  min_instances       = var.cloud_run_services.nlparse_api.min_instances
  max_instances       = var.cloud_run_services.nlparse_api.max_instances == "unlimited" ? null : var.cloud_run_services.nlparse_api.max_instances
  memory              = var.cloud_run_services.nlparse_api.memory
  cpus                = var.cloud_run_services.nlparse_api.cpus
  concurrency         = var.cloud_run_services.nlparse_api.concurrency
  timeout             = var.cloud_run_services.nlparse_api.timeout  
}

module "nlparse_widget_envjson_config" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-nlparse-widget-${var.env}-envjson-config"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    API_URL = module.nlparse_api.url
    VERSION = var.nlparse_version
  })
  skip_secret_data = false
}

module "nlparse_widget" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-nlparse-widget"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-nlparse-widget:${coalesce(var.cloud_run_services.nlparse_widget.image_version, var.nlparse_version)}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.nlparse_widget_envjson_config.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.nlparse_widget.allow_public_access
  min_instances       = var.cloud_run_services.nlparse_widget.min_instances
  max_instances       = var.cloud_run_services.nlparse_widget.max_instances == "unlimited" ? null : var.cloud_run_services.nlparse_widget.max_instances
  memory              = var.cloud_run_services.nlparse_widget.memory
  cpus                = var.cloud_run_services.nlparse_widget.cpus
  concurrency         = var.cloud_run_services.nlparse_widget.concurrency
  timeout             = var.cloud_run_services.nlparse_widget.timeout  
  depends_on          = [module.nlparse_widget_envjson_config]
}
