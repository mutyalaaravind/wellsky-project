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
    GCP_VECTOR_SEARCH_INDEX_NAME        = google_vertex_ai_index.extraction_index.id
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT    = google_vertex_ai_index.extraction_index.deployed_indexes[0].index_endpoint
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID = google_vertex_ai_index.extraction_index.deployed_indexes[0].deployed_index_id
    FIRESTORE_DB                        = "ai-${var.env}"
    PUBSUB_TOPIC                        = "deprecated"
    CLOUD_PROVIDER                      = "google"
  }
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_api.allow_public_access
  organization_id     = var.organization_id
  min_instances = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory        = 512
  cpus          = 1
  project_id    = var.app_project_id
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
    GCP_VECTOR_SEARCH_INDEX_NAME        = google_vertex_ai_index.extraction_index.id
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT    = google_vertex_ai_index.extraction_index.deployed_indexes[0].index_endpoint
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID = google_vertex_ai_index.extraction_index.deployed_indexes[0].deployed_index_id
    FIRESTORE_DB                        = "ai-${var.env}"
    PUBSUB_TOPIC                        = "deprecated"
    CLOUD_PROVIDER                      = "google"
  }
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_events.allow_public_access
  organization_id     = var.organization_id
  min_instances = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory        = 512
  cpus          = 1
  project_id    = var.app_project_id
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
    GCP_VECTOR_SEARCH_INDEX_NAME        = google_vertex_ai_index.extraction_index.id
    GCP_VECTOR_SEARCH_INDEX_ENDPOINT    = google_vertex_ai_index.extraction_index.deployed_indexes[0].index_endpoint
    GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID = google_vertex_ai_index.extraction_index.deployed_indexes[0].deployed_index_id
    FIRESTORE_DB                        = "ai-${var.env}"
    PUBSUB_TOPIC                        = "deprecated"
    CLOUD_PROVIDER                      = "google"
  }
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_events_vertexai.allow_public_access
  organization_id     = var.organization_id
  min_instances = (var.env == "dev" || var.env == "qa") ? 0 : 1
  max_instances = 1 # At most one instance of this service should be running at a time
  concurrency   = 5 # Handle only 5 requests at a time
  memory        = 512
  cpus          = 1
  project_id    = var.app_project_id
}

module "extract_and_fill_widget_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-extract-and-fill-widget-${var.env}-envjson"
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
        secret_name = module.extract_and_fill_widget_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }
  labels        = var.labels
  ingress       = "all"
  allow_public_access = var.cloud_run_services.extract_and_fill_widget.allow_public_access
  organization_id     = var.organization_id
  min_instances = (var.env == "dev" || var.env == "qa") ? 0 : 1
  memory        = 512
  cpus          = 1
  project_id    = var.app_project_id
  depends_on    = [module.extract_and_fill_widget_envjson]
}

