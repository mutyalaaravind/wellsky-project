module "summarization-hope-mcp-server" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "summarization-hope-mcp-server"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/hope-mcp-server:latest"
  command               = ["python", "server_http.py", "--host", "0.0.0.0", "--port", "8080"]

  env = {
    SERVICE              = "summarization-hope-mcp-server"
    STAGE                = var.env
    VERSION              = "latest"
    DEBUG                = "false"
    GCS_BUCKET_NAME      = module.ai_provisional_bucket.name
    GCP_PROJECT_ID       = var.app_project_id
    CLOUD_PROVIDER       = "google"
    GOOGLE_CLOUD_PROJECT = var.app_project_id
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = true
  min_instances       = 3
  memory              = 2048
  cpus                = 1
  project_id          = var.app_project_id
}

# Grant service account Cloud Run Invoker role in viki-prod-app-wsky project
resource "google_project_iam_member" "service_account_run_invoker" {
  project = "viki-prod-app-wsky"
  role    = "roles/run.invoker"
  member  = "serviceAccount:sandbox-rcm-edge-svc-account@temp-nm2oqamj-wsky.iam.gserviceaccount.com"
}

# Dedicated service account for summarization agents
module "summarization_agents_sa" {
  source       = "git@github.com:mediwareinc/terraform-gcp-service-account.git?ref=v0.4.11"
  account_id   = "summarization-agents-${var.env}-sa"
  display_name = "Summarization Agents service account ${var.env}"
  project_id   = var.app_project_id
  labels       = var.labels
}

# Storage bucket for summarization agents
module "summarization_agents_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v1.0.0"
  project_id    = var.app_project_id
  name          = "summarization-agents-storage-${var.env}"
  location      = var.region
  storage_class = "REGIONAL"
  labels        = var.labels
  force_destroy = false
  bucket_admins = [module.summarization_agents_sa.iam_email]
  cors = [
    {
      max_age_seconds = 3600
      method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
      origin          = ["*"]
      response_header = ["*"]
    }
  ]
}