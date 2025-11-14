locals {
  cloud_run_env = {
    SERVICE                        = "rcmedge"
    STAGE                          = var.env
    VERSION                        = var.rcmedge_version
    DEBUG                          = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCP_PROJECT_ID                 = var.app_project_id
    GCP_LOCATION                   = var.region
    GCS_ARTIFACTS_BUCKET           = module.rcmedge_bucket.name
    FAST_LLM_AGENT_MODEL           = "gemini-2.5-flash"
    PRO_LLM_AGENT_MODEL            = "gemini-2.5-pro"
    RULES_EXECUTOR_AGENT_ENGINE_ID = "7911091714964586496"
    EDI_GENERATOR_AGENT_ENGINE_ID   = "7212470822768738304"
    CLAIM_RULES_EXTRACTOR_AGENT_ENGINE_ID = "3161025561111822336"
    RULES_EVENTS_API_URL           = "https://rcmedge-rules-events-zqftmopgsq-uk.a.run.app"
    MODE                           = "CLOUD"
    GCP_PUBSUB_PROJECT_ID          = var.app_project_id
    CLAIM_RULES_FIRESTORE_COLLECTION = "x12_claim_rules_v2"
  }
}

module "rcmedge_rules_api" {
  source                = "terraform.wellsky.net/wellsky/cloudrun/gcp"
  name                  = "rcmedge-rules-api"
  location              = var.region
  service_account_email = module.rcmedge_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/rcmedge-rules-api:${var.rcmedge_version}"
  command = [
    "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
  ]
  env = local.cloud_run_env

  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory              = 512
  cpus                = 1
  project_id          = var.app_project_id
  timeout             = 600
}


module "rcmedge_rules_events" {
  source                = "terraform.wellsky.net/wellsky/cloudrun/gcp"
  name                  = "rcmedge-rules-events"
  location              = var.region
  service_account_email = module.rcmedge_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/rcmedge-rules-api:${var.rcmedge_version}"
  command = [
    "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
  ]
  env = local.cloud_run_env

  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.allow_public_access
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory              = 512
  cpus                = 1
  project_id          = var.app_project_id
  timeout             = 600
}