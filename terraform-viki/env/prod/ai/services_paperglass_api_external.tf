module "paperglass_external_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-paperglass-external-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-paperglass-api:${var.paperglass_version}"
  command = [
    "uvicorn", "paperglass.entrypoints.http_api:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.paperglass_api_external.uvicorn_workers),
  ]
  env = merge(local.common_env, {
    # Service-specific overrides
    SERVICE                = "paperglass_external_api"
    VERSION                = var.paperglass_version
    SELF_API               = format("%s/%s", module.paperglass_api.url, "api")
    OTEL_SERVICE_NAME      = "viki.paperglass.api.external"
    NEW_RELIC_APP_NAME     = "Viki Paperglass External API (${var.env})"
  })
  secrets = toset(local.common_secrets)
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  vpc_connector_name  = var.vpc_connector
  min_instances       = var.cloud_run_services.paperglass_api_external.min_instances
  max_instances       = var.cloud_run_services.paperglass_api_external.max_instances == "unlimited" ? null : var.cloud_run_services.paperglass_api_external.max_instances  
  memory              = var.cloud_run_services.paperglass_api_external.memory
  cpus                = var.cloud_run_services.paperglass_api_external.cpus
  project_id          = var.app_project_id
  timeout             = var.cloud_run_services.paperglass_api_external.timeout
}
