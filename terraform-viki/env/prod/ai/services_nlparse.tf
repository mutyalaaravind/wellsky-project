module "nlparse_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-nlparse-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-nlparse-api:${var.nlparse_version}"
  command = [
    "uvicorn", "nlparse.entrypoints.http:app",
    "--host", "0.0.0.0",
    "--port", "8080",
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
  labels              = var.labels
  ingress             = "all"
  allow_public_access = true
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory              = 512
  cpus                = 1
  project_id          = var.app_project_id
}

module "nlparse_widget_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-nlparse-widget-${var.env}-envjson"
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
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-nlparse-widget:${var.nlparse_version}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.nlparse_widget_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = true
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory              = 512
  cpus                = 1
  project_id          = var.app_project_id
  depends_on          = [module.nlparse_widget_envjson]
}
