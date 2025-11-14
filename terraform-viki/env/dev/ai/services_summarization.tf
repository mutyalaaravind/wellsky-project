module "summarization-hope-mcp-server" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "summarization-demo-mcp-server"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/demo-mcp-server:latest"
  command               = [
    "python", "server_http.py", 
    "--host", "0.0.0.0", 
    "--port", "8080",    
  ]

  env = {
    SERVICE              = "summarization-demo-mcp-server"
    STAGE                = var.env
    VERSION              = "latest"
    DEBUG                = "true"
    GCS_BUCKET_NAME      = module.ai_provisional_bucket.name
    GCP_PROJECT_ID       = var.app_project_id
    CLOUD_PROVIDER       = "google"
    GOOGLE_CLOUD_PROJECT = var.app_project_id
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.summarization_hope_mcp_server.allow_public_access
  min_instances       = var.cloud_run_services.summarization_hope_mcp_server.min_instances
  max_instances       = var.cloud_run_services.summarization_hope_mcp_server.max_instances == "unlimited" ? null : var.cloud_run_services.summarization_hope_mcp_server.max_instances
  memory              = var.cloud_run_services.summarization_hope_mcp_server.memory
  cpus                = var.cloud_run_services.summarization_hope_mcp_server.cpus
  concurrency         = var.cloud_run_services.summarization_hope_mcp_server.concurrency
  timeout             = var.cloud_run_services.summarization_hope_mcp_server.timeout  
}

# Grant service account Cloud Run Invoker role in viki-dev-app-wsky project
resource "google_project_iam_member" "service_account_run_invoker" {
  project = "viki-dev-app-wsky"
  role    = "roles/run.invoker"
  member  = "serviceAccount:summarization-agents-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "ai_platform_re_run_invoker" {
  project = "viki-dev-app-wsky"
  role    = "roles/run.invoker"
  member  = "serviceAccount:service-145042810266@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
}

module "summarization-agent-ui-server" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "summarization-agent-ui-server"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/summarization-agent-ui-server:latest"
  command               = ["uv", "run", "python", "backend/start_server.py"]

  env = {
    SERVICE              = "summarization-agent-ui-server"
    STAGE                = var.env
    VERSION              = "latest"
    DEBUG                = "true"
    GCS_BUCKET_NAME      = module.ai_provisional_bucket.name
    GCP_PROJECT_ID       = var.app_project_id
    CLOUD_PROVIDER       = "google"
    GOOGLE_CLOUD_PROJECT = var.app_project_id

    # Required missing variables for start_server.py
    GCP_REGION         = var.region
    OKTA_CLIENT_ID     = "0oasyyb5qvqGPgZJu1d6"
    OKTA_CLIENT_SECRET = "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"
    OKTA_AUTHORITY     = "https://wellsky-ciam.oktapreview.com/oauth2/aussyy6p7tqLFjziZ1d6"
    REDIRECT_URL       = "http://localhost:8080/api/auth/okta/callback"

    # Additional configuration
    OKTA_ORG_NAME               = "wellsky-ciam"
    OKTA_BASE_URL               = "oktapreview.com"
    OKTA_SERVER_NAME            = "STABLE CIAM-Preview"
    OKTA_JWKS_URI               = "https://wellsky-ciam.oktapreview.com/oauth2/aussyy6p7tqLFjziZ1d6/v1/keys"
    OKTA_AUDIENCE               = "WellSky.Stable.Auth.Server"
    OKTA_SCOPES                 = "api.wellsky.edof.read,api.wellsky.edof.write"
    OKTA_SCOPE_WHITELIST        = "openid,profile,email,api.wellsky.edof.read,api.wellsky.edof.write"
    OKTA_TOKEN_LIFETIME         = "60"
    OKTA_REFRESH_TOKEN_LIFETIME = "60"

    # MCP Server Configuration
    MCP_SERVER_URL = "https://summarization-hope-mcp-server-145042810266.us-east4.run.app/mcp/"

    # Storage configuration
    GCS_DEFAULT_STORAGE_CLASS = "STANDARD"
    GCS_DEFAULT_LOCATION      = "US"
    GCS_DEFAULT_CONTENT_TYPE  = "application/pdf"
  }
  project_id          = var.app_project_id
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.summarization_agent_ui_server.allow_public_access
  min_instances       = var.cloud_run_services.summarization_agent_ui_server.min_instances
  max_instances       = var.cloud_run_services.summarization_agent_ui_server.max_instances == "unlimited" ? null : var.cloud_run_services.summarization_agent_ui_server.max_instances
  memory              = var.cloud_run_services.summarization_agent_ui_server.memory
  cpus                = var.cloud_run_services.summarization_agent_ui_server.cpus
  concurrency         = var.cloud_run_services.summarization_agent_ui_server.concurrency
  timeout             = var.cloud_run_services.summarization_agent_ui_server.timeout  
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
  force_destroy = true
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
