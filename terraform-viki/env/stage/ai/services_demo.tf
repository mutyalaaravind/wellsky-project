module "demo_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-demo-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-demo-api:${var.demo_version}"
  command = [
    "uvicorn", "main.entrypoints.http:app",
    "--host", "0.0.0.0",
    "--port", "8080",
  ]
  env = {
    SERVICE                            = "demo_api"
    STAGE                              = var.env
    VERSION                            = var.demo_version
    DEBUG                              = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                    = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                     = var.app_project_id
    GCP_PROJECT_LOCATION               = var.region
    FIRESTORE_DB                       = "ai-${var.env}"
    GCP_MULTI_REGION_FIRESTORE_LOCATON = "nam5"
    GCP_FIRESTORE_DB                   = "viki-${var.env}"
    OKTA_PAPERGLASS_CLIENT_ID          = "api.wellsky.viki.paperglass.${var.env}"
    OKTA_PAPERGLASS_SCOPE              = "api.wellsky.viki.ai.paperglass"
    OKTA_PAPERGLASS_TOKEN_ISSUER_URL   = var.okta_issuer_url
  }
  secrets = toset([
    {
      key     = "OKTA_PAPERGLASS_CLIENT_SECRET",
      name    = module.secret["okta_client_secret"].name,
      version = "latest",
    }
  ])
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.demo_api.allow_public_access
  #organization_id     = var.organization_id
  min_instances = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory              = 512
  cpus                = 1
  project_id          = var.app_project_id
}

module "demo_dashboard_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-demo-dashboard-${var.env}-envjson"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    AUTOSCRIBE_WIDGET_HOST = var.autoscribe_widget_url
    EXTRACT_WIDGET_HOST    = module.extract_and_fill_widget.url
    PAPERGLASS_WIDGET_HOST = var.paperglass_widget_url
    AUTOSCRIBE_WIDGET_API  = var.autoscribe_api_url
    DEMO_API               = "${var.demo_api_url}/api"
    FORMS_WIDGETS_HOST     = var.forms_widgets_host
    FORMS_API              = var.forms_api
    FORMS_API_KEY          = var.forms_api_key
    VERSION                = var.demo_version
    OKTA_ISSUER            = var.okta_issuer
    OKTA_CLIENT_ID         = var.okta_demo_client_id
    OKTA_SCOPES = [
      var.okta_scopes["transcription"],
      var.okta_scopes["form-completion"],
    ]
    OKTA_DISABLE    = var.okta_disable
    MED_WIDGET_HOST = "https://${local.cdn_dns_name}/medwidget/${var.frontends_version}",
  })
  skip_secret_data = false
}

module "demo_dashboard" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-demo-dashboard"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-demo-dashboard:${var.demo_version}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.demo_dashboard_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.demo_api.allow_public_access
  #organization_id     = var.organization_id
  min_instances = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory              = 512
  cpus                = 1
  project_id          = var.app_project_id
  depends_on          = [module.demo_dashboard_envjson]
}