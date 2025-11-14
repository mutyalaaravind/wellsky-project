module "paperglass_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-paperglass-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-paperglass-api:${var.paperglass_version}"
  command = [
    "uvicorn", "paperglass.entrypoints.http1:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.paperglass_api.uvicorn_workers),
  ]
  env = merge(local.common_env, {
    # Service-specific overrides
    SERVICE            = "paperglass"
    VERSION            = var.paperglass_version
    OTEL_SERVICE_NAME  = "viki.paperglass.api"
    NEW_RELIC_APP_NAME = "Viki Paperglass API (${var.env})"
    SELF_API           = format("https://ai-paperglass-api-%s.%s.run.app/api", data.google_project.app_project.number, var.region)
  })
  secrets             = toset(local.common_secrets)
  project_id          = var.app_project_id
  vpc_connector_name  = var.vpc_connector
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.paperglass_api.allow_public_access
  min_instances       = var.cloud_run_services.paperglass_api.min_instances
  max_instances       = var.cloud_run_services.paperglass_api.max_instances == "unlimited" ? null : var.cloud_run_services.paperglass_api.max_instances
  memory              = var.cloud_run_services.paperglass_api.memory
  cpus                = var.cloud_run_services.paperglass_api.cpus
  concurrency         = var.cloud_run_services.paperglass_api.concurrency
  timeout             = var.cloud_run_services.paperglass_api.timeout
}

module "paperglass_api_secondary" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-paperglass-api-secondary"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-paperglass-api:${var.paperglass_version}"
  command = [
    "uvicorn", "paperglass.entrypoints.http1:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.paperglass_api.uvicorn_workers),
  ]
  env = merge(local.common_env, {
    # Service-specific overrides
    SERVICE            = "paperglass"
    VERSION            = var.paperglass_version
    OTEL_SERVICE_NAME  = "viki.paperglass.api.beffe"
    NEW_RELIC_APP_NAME = "Viki Paperglass API BEFFE (${var.env})"
    SELF_API           = "${var.paperglass_api_url}/api"
  })
  secrets             = toset(local.common_secrets)
  project_id          = var.app_project_id
  vpc_connector_name  = var.vpc_connector
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.paperglass_api_secondary.allow_public_access
  min_instances       = var.cloud_run_services.paperglass_api.min_instances
  max_instances       = var.cloud_run_services.paperglass_api.max_instances == "unlimited" ? null : var.cloud_run_services.paperglass_api.max_instances
  memory              = var.cloud_run_services.paperglass_api.memory
  cpus                = var.cloud_run_services.paperglass_api.cpus
  concurrency         = var.cloud_run_services.paperglass_api.concurrency
  timeout             = var.cloud_run_services.paperglass_api.timeout
}

module "paperglass_events" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-paperglass-events"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-paperglass-api:${var.paperglass_version}"
  command = [
    "uvicorn", "paperglass.entrypoints.events:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.paperglass_events.uvicorn_workers),
  ]
  env = merge(local.common_env, {
    # Service-specific overrides
    SERVICE            = "paperglass_events"
    VERSION            = var.paperglass_version
    OTEL_SERVICE_NAME  = "viki.paperglass.events"
    NEW_RELIC_APP_NAME = "Viki Paperglass Events (${var.env})"
    SELF_API           = format("%s/%s", module.paperglass_api.url, "api")
  })
  secrets             = toset(local.common_secrets)
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.paperglass_events.allow_public_access
  min_instances       = var.cloud_run_services.paperglass_events.min_instances
  max_instances       = var.cloud_run_services.paperglass_events.max_instances == "unlimited" ? null : var.cloud_run_services.paperglass_events.max_instances  
  memory              = var.cloud_run_services.paperglass_events.memory
  cpus                = var.cloud_run_services.paperglass_events.cpus
  concurrency         = var.cloud_run_services.paperglass_events.concurrency
  timeout             = var.cloud_run_services.paperglass_events.timeout
}

module "paperglass_external_events" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-paperglass-external-events"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-paperglass-api:${var.paperglass_version}"
  command = [
    "uvicorn", "paperglass.entrypoints.events:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.paperglass_external_events.uvicorn_workers),
  ]
  env = merge(local.common_env, {
    # Service-specific overrides
    SERVICE            = "paperglass_events_external"
    VERSION            = var.paperglass_version
    OTEL_SERVICE_NAME  = "viki.paperglass.events.external"
    NEW_RELIC_APP_NAME = "Viki Paperglass Events External (${var.env})"
    SELF_API           = format("%s/%s", module.paperglass_api.url, "api")
  })
  secrets             = toset(local.common_secrets)
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.paperglass_external_events.allow_public_access
  min_instances       = var.cloud_run_services.paperglass_external_events.min_instances
  max_instances       = var.cloud_run_services.paperglass_external_events.max_instances == "unlimited" ? null : var.cloud_run_services.paperglass_external_events.max_instances
  memory              = var.cloud_run_services.paperglass_external_events.memory
  cpus                = var.cloud_run_services.paperglass_external_events.cpus
  concurrency         = var.cloud_run_services.paperglass_external_events.concurrency
  timeout             = var.cloud_run_services.paperglass_external_events.timeout
}

module "paperglass_widget_envjson_config" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-paperglass-widget-${var.env}-envjson-config"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    API_URL            = var.paperglass_api_secondary_url
    VERSION            = var.paperglass_version
    FORMS_WIDGETS_HOST = var.forms_widgets_host
    FORMS_API          = var.forms_api
    FORMS_API_KEY      = var.forms_api_key
  })
  skip_secret_data = false
}

module "paperglass_widget" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-paperglass-widget"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-paperglass-widget:${var.paperglass_version}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.paperglass_widget_envjson_config.name
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
  min_instances       = var.cloud_run_services.paperglass_widget.min_instances
  max_instances       = var.cloud_run_services.paperglass_widget.max_instances == "unlimited" ? null : var.cloud_run_services.paperglass_widget.max_instances
  memory              = var.cloud_run_services.paperglass_widget.memory
  cpus                = var.cloud_run_services.paperglass_widget.cpus
  concurrency         = var.cloud_run_services.paperglass_widget.concurrency
  timeout             = var.cloud_run_services.paperglass_widget.timeout
  depends_on          = [module.paperglass_widget_envjson_config]
}
