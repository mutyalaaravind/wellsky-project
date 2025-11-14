# Support App - React UI for Scribe Session Support

module "support_ui_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-support-ui-${var.env}-envjson"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    # API URLs for the support app
    API_URLS = {
      LOCAL = "http://127.0.0.1:8000"
      DEV   = "https://skysense-scribe-api-zqftmopgsq-uk.a.run.app"
      QA    = "https://skysense-scribe-api-p32qledfyq-uk.a.run.app"
      STAGE = "https://skysense-scribe-api-zzygbs3ypa-uk.a.run.app"
      PROD  = "https://skysense-scribe-api-cocynqqo6a-uk.a.run.app"
    }
    # Current environment
    ENVIRONMENT      = upper(var.env)
    VERSION          = coalesce(var.support_ui_app_version, var.cloud_run_services.support_ui.image_version, var.apps_version)

    # OAuth/Authentication settings (if needed in future)
    OKTA_ISSUER      = var.okta_issuer
    OKTA_CLIENT_ID   = var.okta_admin_client_id
    OKTA_DISABLE     = var.okta_disable
  })
  skip_secret_data = false
}

module "support_ui" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-support-ui"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-support-ui:${coalesce(var.support_ui_app_version, var.cloud_run_services.support_ui.image_version, var.apps_version)}"
  port                  = 80

  # Mount the env.json configuration
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.support_ui_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }

  labels              = var.labels
  ingress             = "all"
  min_instances       = var.cloud_run_services.support_ui.min_instances
  max_instances       = var.cloud_run_services.support_ui.max_instances == "unlimited" ? null : var.cloud_run_services.support_ui.max_instances
  memory              = var.cloud_run_services.support_ui.memory
  cpus                = var.cloud_run_services.support_ui.cpus
  project_id          = var.app_project_id
  timeout             = var.cloud_run_services.support_ui.timeout
  depends_on          = [module.support_ui_envjson]
}

# Output the service URL
output "support_ui_url" {
  value = module.support_ui.url
  description = "URL of the Support UI Cloud Run service"
}
