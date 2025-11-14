module "admin_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-admin-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-admin-api:${coalesce(var.cloud_run_services.admin_api.image_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.admin_api.uvicorn_workers),
  ]
  env = {
    SERVICE                            = "admin_api"
    STAGE                              = var.env
    VERSION                            = coalesce(var.cloud_run_services.admin_api.image_version, var.apps_version)
    DEBUG                              = (var.env == "dev" || var.env == "qa") ? "true" : "false"

    CLOUD_PROVIDER                     = "google"
    GCP_PROJECT_ID                     = var.app_project_id
    GCP_PUBSUB_PROJECT_ID              = var.app_project_id
    GCS_BUCKET_NAME                    = module.ai_provisional_bucket.name
    GCP_LOCATION                       = split("-", var.region)[0]
    GCP_LOCATION_2                     = var.region
    GCP_LOCATION_3                     = "us-central1"
    SERVICE_ACCOUNT_EMAIL              = module.ai_sa.email
    
    GCP_FIRESTORE_DB                   = "viki-${var.env}"
    GCP_MULTI_REGION_FIRESTORE_LOCATON = "nam5"

    OKTA_PAPERGLASS_CLIENT_ID          = "api.wellsky.viki.paperglass"
    OKTA_PAPERGLASS_SCOPE              = "api.wellsky.viki.ai.paperglass"
    OKTA_PAPERGLASS_TOKEN_ISSUER_URL   = var.okta_issuer_url
    SELF_API_URL                       = var.admin_api_url
    DJT_API_URL                        = var.djt_api_url
    PAPERGLASS_API_URL                 = var.paperglass_api_url
    ENTITY_EXTRACTION_API_URL          = var.entity_extraction_api_url
    ADMIN_DEMO_BASE_URL                = var.admin_api_url
    ADMIN_DEMO_ENTITY_CALLBACK_ENDPOINT = "/api/v1/entities/callback"
    PAPERGLASS_INTERNAL_DOCUMENT_CREATE_ENDPOINT = "/api/document/internal/create"
  }
  secrets = toset([
    {
      key     = "OKTA_PAPERGLASS_CLIENT_SECRET",
      name    = module.secret["okta_client_secret"].name,
      version = "latest",
    }
  ])
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.admin_api.allow_public_access
  organization_id     = var.organization_id
  min_instances       = var.cloud_run_services.admin_api.min_instances
  max_instances       = var.cloud_run_services.admin_api.max_instances == "unlimited" ? null : var.cloud_run_services.admin_api.max_instances
  memory              = var.cloud_run_services.admin_api.memory
  cpus                = var.cloud_run_services.admin_api.cpus
  project_id          = var.app_project_id
  timeout             = var.cloud_run_services.admin_api.timeout
}

module "admin_ui_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-admin-ui-${var.env}-envjson"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    ADMIN_API          = var.admin_api_url
    VERSION            = coalesce(var.cloud_run_services.admin_api.image_version, var.apps_version)
    OKTA_ISSUER        = var.okta_issuer
    OKTA_CLIENT_ID     = var.okta_admin_client_id
    OKTA_SCOPES = [
      var.okta_scopes["admin"],
    ]
    OKTA_DISABLE = var.okta_disable
  })
  skip_secret_data = false
}

module "admin_ui" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-admin-ui"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-admin-ui:${coalesce(var.cloud_run_services.admin_ui.image_version, var.apps_version)}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.admin_ui_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.admin_ui.allow_public_access
  organization_id     = var.organization_id
  min_instances       = var.cloud_run_services.admin_ui.min_instances
  max_instances       = var.cloud_run_services.admin_ui.max_instances == "unlimited" ? null : var.cloud_run_services.admin_ui.max_instances
  memory              = var.cloud_run_services.admin_ui.memory
  cpus                = var.cloud_run_services.admin_ui.cpus
  project_id          = var.app_project_id
  depends_on          = [module.admin_ui_envjson]
}