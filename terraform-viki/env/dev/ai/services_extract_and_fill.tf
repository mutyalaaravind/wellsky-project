module "extract_and_fill_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-extract-and-fill-api"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-extract-and-fill-api:${var.extract_and_fill_version}"
  command = [
    "uvicorn", "extract_and_fill.entrypoints.http1:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.extract_and_fill_api.uvicorn_workers),
  ]
  env = {
    SERVICE                             = "extract_and_fill"
    STAGE                               = var.env
    VERSION                             = var.extract_and_fill_version
    DEBUG                               = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                     = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                      = var.app_project_id
    GCP_PROJECT_LOCATION                = var.region
    GCP_PROJECT_LOCATION_2              = "us-central1"
    PINECONE_API_KEY                    = ""
    PINECONE_ENV                        = "gcp-starter"
    PINECONE_VECTOR_SEARCH_INDEX_NAME   = "extractor-vector-index"
    GCP_VECTOR_SEARCH_INDEX_GCS_URI     = "${google_storage_bucket.bucket.name}/contents"
    GCP_VECTOR_SEARCH_INDEX_NAME        = "" #google_vertex_ai_index.extraction_index.id
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT    = "" #google_vertex_ai_index.extraction_index.deployed_indexes[0].index_endpoint
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID = "" #google_vertex_ai_index.extraction_index.deployed_indexes[0].deployed_index_id
    FIRESTORE_DB                        = "ai-${var.env}"
    PUBSUB_TOPIC                        = "deprecated"
    CLOUD_PROVIDER                      = "google"
  }
  project_id    = var.app_project_id  
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_api.allow_public_access
  min_instances = var.cloud_run_services.extract_and_fill_api.min_instances
  max_instances = var.cloud_run_services.extract_and_fill_api.max_instances == "unlimited" ? null : var.cloud_run_services.extract_and_fill_api.max_instances
  memory        = var.cloud_run_services.extract_and_fill_api.memory
  cpus          = var.cloud_run_services.extract_and_fill_api.cpus
  concurrency   = var.cloud_run_services.extract_and_fill_api.concurrency
  timeout       = var.cloud_run_services.extract_and_fill_api.timeout  
}

module "extract_and_fill_events" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-extract-and-fill-events"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-extract-and-fill-api:${var.extract_and_fill_version}"
  command = [
    "uvicorn", "extract_and_fill.entrypoints.events:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.extract_and_fill_events.uvicorn_workers),
  ]
  env = {
    SERVICE                             = "extract_and_fill_events"
    STAGE                               = var.env
    VERSION                             = var.extract_and_fill_version
    DEBUG                               = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                     = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                      = var.app_project_id
    GCP_PROJECT_LOCATION                = var.region
    GCP_PROJECT_LOCATION_2              = "us-central1"
    PINECONE_API_KEY                    = ""
    PINECONE_ENV                        = "gcp-starter"
    PINECONE_VECTOR_SEARCH_INDEX_NAME   = "extractor-vector-index"
    GCP_VECTOR_SEARCH_INDEX_GCS_URI     = "${google_storage_bucket.bucket.name}/contents"
    GCP_VECTOR_SEARCH_INDEX_NAME        = "" #google_vertex_ai_index.extraction_index.id
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT    = "" #google_vertex_ai_index.extraction_index.deployed_indexes[0].index_endpoint
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID = "" #google_vertex_ai_index.extraction_index.deployed_indexes[0].deployed_index_id
    FIRESTORE_DB                        = "ai-${var.env}"
    PUBSUB_TOPIC                        = "deprecated"
    CLOUD_PROVIDER                      = "google"
  }
  project_id    = var.app_project_id
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_events.allow_public_access
  min_instances = var.cloud_run_services.extract_and_fill_events.min_instances
  max_instances = var.cloud_run_services.extract_and_fill_events.max_instances == "unlimited" ? null : var.cloud_run_services.extract_and_fill_events.max_instances
  memory        = var.cloud_run_services.extract_and_fill_events.memory
  cpus          = var.cloud_run_services.extract_and_fill_events.cpus
  concurrency   = var.cloud_run_services.extract_and_fill_events.concurrency
  timeout       = var.cloud_run_services.extract_and_fill_events.timeout  
}

module "extract_and_fill_events_vertexai" {
  // This is a rate-limited version of the above service, which is used for Vertex AI to prevent more than 5 requests at a time.
  // Unfortunately, Pub/Sub does not support rate-limiting, so we have to do it here.
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-extract-and-fill-events-vertexai"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-extract-and-fill-api:${var.extract_and_fill_version}"
  command = [
    "uvicorn", "extract_and_fill.entrypoints.events:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", tostring(var.cloud_run_services.extract_and_fill_events_vertexai.uvicorn_workers),
  ]
  env = {
    SERVICE                             = "extract_and_fill_events"
    STAGE                               = var.env
    VERSION                             = var.extract_and_fill_version
    DEBUG                               = (var.env == "dev" || var.env == "qa") ? "true" : "false"
    GCS_BUCKET_NAME                     = module.ai_provisional_bucket.name
    GCP_PROJECT_ID                      = var.app_project_id
    GCP_PROJECT_LOCATION                = var.region
    GCP_PROJECT_LOCATION_2              = "us-central1"
    PINECONE_API_KEY                    = ""
    PINECONE_ENV                        = "gcp-starter"
    PINECONE_VECTOR_SEARCH_INDEX_NAME   = "extractor-vector-index"
    GCP_VECTOR_SEARCH_INDEX_GCS_URI     = "${google_storage_bucket.bucket.name}/contents"
    GCP_VECTOR_SEARCH_INDEX_NAME        = "" #google_vertex_ai_index.extraction_index.id
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT    = "" #google_vertex_ai_index.extraction_index.deployed_indexes[0].index_endpoint
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID = "" #google_vertex_ai_index.extraction_index.deployed_indexes[0].deployed_index_id
    FIRESTORE_DB                        = "ai-${var.env}"
    PUBSUB_TOPIC                        = "deprecated"
    CLOUD_PROVIDER                      = "google"
  }
  project_id    = var.app_project_id
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_events_vertexai.allow_public_access
  min_instances = var.cloud_run_services.extract_and_fill_events_vertexai.min_instances
  max_instances = var.cloud_run_services.extract_and_fill_events_vertexai.max_instances == "unlimited" ? null : var.cloud_run_services.extract_and_fill_events_vertexai.max_instances  
  memory        = var.cloud_run_services.extract_and_fill_events_vertexai.memory
  cpus          = var.cloud_run_services.extract_and_fill_events_vertexai.cpus
  concurrency   = var.cloud_run_services.extract_and_fill_events_vertexai.concurrency
  timeout       = var.cloud_run_services.extract_and_fill_events_vertexai.timeout
}

module "extract_and_fill_widget_envjson_config" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-extract-and-fill-widget-${var.env}-envjson-config"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    API_URL = module.extract_and_fill_api.url
    VERSION = var.extract_and_fill_version
    #NLPARSE_WIDGET_HOST    = module.nlparse_widget.url
    #AUTOSCRIBE_WIDGET_HOST = module.autoscribe_widget.url
    FORMS_WIDGETS_HOST = var.forms_widgets_host
    FORMS_API          = var.forms_api
    FORMS_API_KEY      = var.forms_api_key
  })
  skip_secret_data = false
}

module "extract_and_fill_widget" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-extract-and-fill-widget"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-extract-and-fill-widget:${var.extract_and_fill_version}"
  port                  = 80
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.extract_and_fill_widget_envjson_config.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  project_id    = var.app_project_id
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_widget.allow_public_access
  min_instances = var.cloud_run_services.extract_and_fill_widget.min_instances
  max_instances = var.cloud_run_services.extract_and_fill_widget.max_instances == "unlimited" ? null : var.cloud_run_services.extract_and_fill_widget.max_instances
  memory        = var.cloud_run_services.extract_and_fill_widget.memory
  cpus          = var.cloud_run_services.extract_and_fill_widget.cpus
  concurrency   = var.cloud_run_services.extract_and_fill_widget.concurrency
  timeout       = var.cloud_run_services.extract_and_fill_widget.timeout  
  depends_on    = [module.extract_and_fill_widget_envjson_config]
}
