# Distributed Job Tracking Service Configuration

# Cloud Tasks Queue for distributed job tracking
resource "google_cloud_tasks_queue" "distributed_job_tracking_queue" {
  name     = "distributed-job-tracking-queue"
  location = var.region
  project  = var.app_project_id

  rate_limits {
    max_concurrent_dispatches = 10
    max_dispatches_per_second = 5
  }

  retry_config {
    max_attempts       = 3
    max_retry_duration = "300s"
    max_backoff        = "60s"
    min_backoff        = "1s"
    max_doublings      = 3
  }
}

# Main Distributed Job Tracking API Service
module "distributed_job_tracking_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-distributed-job-tracking"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-distributed_job_tracking:${coalesce(var.cloud_run_services.distributed_job_tracking.image_version, var.apps_version)}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.distributed_job_tracking.uvicorn_workers),
  ]
  env = {
    # Critical settings using getenv_or_die
    VERSION                = coalesce(var.cloud_run_services.distributed_job_tracking.image_version, var.apps_version)
    SERVICE                = "distributed-job-tracking"
    STAGE                  = var.env
    DEBUG                  = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    CLOUD_PROVIDER         = "google"
    GCP_PROJECT_ID         = var.app_project_id
    GCP_LOCATION           = split("-", var.region)[0]
    GCP_LOCATION_2         = var.region
    GCP_LOCATION_3         = "us-central1"
    GCP_FIRESTORE_DB       = "viki-${var.env}"
    GCS_BUCKET_NAME        = module.ai_provisional_bucket.name
    SELF_API_URL           = "https://ai-distributed-job-tracking-${var.app_project_id}.${var.region}.run.app/api"
    PAPERGLASS_API_URL     = module.paperglass_api.url
    SERVICE_ACCOUNT_EMAIL  = module.ai_sa.email
    CLOUDTASK_EMULATOR_URL = ""

    # Optional settings with defaults
    REDIS_URL             = "redis://${var.redis_host}:${var.redis_port}"
    REDIS_DB              = "0"
    DJT_REDIS_TTL_DEFAULT = "43200" # 12 hours in seconds

    DEFAULT_TASK_QUEUE = google_cloud_tasks_queue.distributed_job_tracking_queue.name

    # Logging configuration
    LOGGING_CHATTY_LOGGERS = ""

    # New Relic monitoring
    NEW_RELIC_LICENSE_KEY                                  = var.newrelic_api_license_key
    NEW_RELIC_APP_NAME                                     = "Viki Distributed Job Tracking (${var.env})"
    NEW_RELIC_MONITOR_MODE                                 = "true"
    NEW_RELIC_LOG                                          = "stdout"
    NEW_RELIC_LOG_LEVEL                                    = "info"
    NEW_RELIC_HIGH_SECURITY                                = "false"
    NEW_RELIC_APPLICATION_LOGGING_ENABLED                  = "true"
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED       = "true"
    NEW_RELIC_APPLICATION_LOGGING_LOCAL_DECORATING_ENABLED = "true"
    NEW_RELIC_APPLICATION_LOGGING_METRICS_ENABLED          = "false"
    NEW_RELIC_TRACE_ENABLED                                = var.newrelic_trace_enabled

    # OpenTelemetry configuration
    OTEL_SDK_DISABLED                                        = var.opentelemetry_disabled
    OTEL_SERVICE_NAME                                        = "viki.distributed-job-tracking.api"
    OTEL_TRACES_EXPORTER                                     = "otlp"
    OTEL_EXPORTER_OTLP_ENDPOINT                              = var.opentelemetry_otlp_endpoint
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = ".*"
    GCP_TRACE_ENABLED                                        = var.gcp_trace_enabled

  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.distributed_job_tracking.allow_public_access
  organization_id     = var.organization_id
  vpc_connector_name  = var.vpc_connector
  min_instances       = var.cloud_run_services.distributed_job_tracking.min_instances
  max_instances       = var.cloud_run_services.distributed_job_tracking.max_instances == "unlimited" ? null : var.cloud_run_services.distributed_job_tracking.max_instances
  memory              = var.cloud_run_services.distributed_job_tracking.memory
  cpus                = var.cloud_run_services.distributed_job_tracking.cpus
  project_id          = var.app_project_id
  timeout             = var.cloud_run_services.distributed_job_tracking.timeout
}
