# Support App - React UI for Scribe Session Support

module "skysense_scribe_support_tool_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "skysense-scribe-support-tool-${var.env}-envjson"
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
    VERSION          = coalesce(var.skysense_scribe_support_tool_app_version, var.cloud_run_services.skysense_scribe_support_tool.image_version, var.apps_version)

    # OAuth/Authentication settings (if needed in future)
    OKTA_ISSUER      = var.okta_issuer
    OKTA_CLIENT_ID   = var.okta_admin_client_id
    OKTA_DISABLE     = var.okta_disable
  })
  skip_secret_data = false
}

module "skysense_scribe_support_tool" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "skysense-scribe-support-tool"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-support-ui:${coalesce(var.skysense_scribe_support_tool_app_version, var.cloud_run_services.skysense_scribe_support_tool.image_version, var.apps_version)}"
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
        secret_name = module.skysense_scribe_support_tool_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  project_id          = var.app_project_id
  labels = merge(
    var.labels,
    {
      service     = "skysense-scribe-support-tool"
      application = "scribe"
    }
  )
  ingress             = "all"
  allow_public_access = var.cloud_run_services.skysense_scribe_support_tool.allow_public_access
  min_instances       = var.cloud_run_services.skysense_scribe_support_tool.min_instances
  max_instances       = var.cloud_run_services.skysense_scribe_support_tool.max_instances == "unlimited" ? null : var.cloud_run_services.skysense_scribe_support_tool.max_instances
  memory              = var.cloud_run_services.skysense_scribe_support_tool.memory
  cpus                = var.cloud_run_services.skysense_scribe_support_tool.cpus
  timeout             = var.cloud_run_services.skysense_scribe_support_tool.timeout
  depends_on          = [module.skysense_scribe_support_tool_envjson]
}

# Output the service URL
output "skysense_scribe_support_tool_url" {
  value = module.skysense_scribe_support_tool.url
  description = "URL of the Support UI Cloud Run service"
}

