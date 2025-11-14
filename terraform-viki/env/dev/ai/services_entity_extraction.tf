module "entity_extraction_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-entity-extraction"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-entity_extraction:${coalesce(var.cloud_run_services.entity_extraction.image_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.entity_extraction.uvicorn_workers),
  ]
  env = {
    # Core service configuration
    SERVICE        = "entity_extraction"
    STAGE          = var.env
    VERSION        = var.medication_extraction_version
    DEBUG          = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    CLOUD_PROVIDER = "google"

    # GCP configuration
    GCP_PROJECT_ID                     = var.app_project_id
    GCP_PUBSUB_PROJECT_ID              = var.app_project_id
    GCS_BUCKET_NAME                    = module.ai_provisional_bucket.name
    GCP_LOCATION                       = split("-", var.region)[0]
    GCP_LOCATION_2                     = var.region
    GCP_LOCATION_3                     = "us-central1"
    GCP_MULTI_REGION_FIRESTORE_LOCATON = "nam5"
    GCP_FIRESTORE_DB                   = "viki-${var.env}"

    # Service URLs
    SERVICE_ACCOUNT_EMAIL                            = module.ai_sa.email
    SELF_API_URL                                     = var.entity_extraction_api_url
    SELF_API_URL_2                                   = var.entity_extraction_api_url
    PAPERGLASS_API_URL                               = module.paperglass_api.url
    PAPERGLASS_INTEGRATION_TOPIC                     = google_pubsub_topic.paperglass_integration_topic.name
    MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME = google_cloud_tasks_queue.v4_status_check.name

    # Distributed Job Tracking
    DJT_API_URL = var.djt_api_url

    # LLM configuration
    LLM_PROMPT_AUDIT_ENABLED = "true"
  }
  project_id          = var.app_project_id
  vpc_connector_name  = var.vpc_connector
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.entity_extraction.allow_public_access
  min_instances       = var.cloud_run_services.entity_extraction.min_instances
  max_instances       = var.cloud_run_services.entity_extraction.max_instances == "unlimited" ? null : var.cloud_run_services.entity_extraction.max_instances
  memory              = var.cloud_run_services.entity_extraction.memory
  cpus                = var.cloud_run_services.entity_extraction.cpus
  concurrency         = var.cloud_run_services.entity_extraction.concurrency
  timeout             = var.cloud_run_services.entity_extraction.timeout  
}
