module "medispan_api" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medispan-api-default"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medispan-api:${var.medispan_api_version}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
  ]
  env = {
    SERVICE                             = "medispan_api"
    STAGE                               = var.env
    VERSION                             = var.medispan_api_version
    DEBUG                               = true
    CORS_ORIGINS                        = "http://localhost:3000,http://localhost:21000"
    GCP_PROJECT_ID                      = var.app_project_id
    GCP_LOCATION                        = var.region
    GCP_FIRESTORE_DB                    = "viki-${var.env}"
    GCP_EMBEDDING_MODEL                 = "text-embedding-005"
    PGVECTOR_HOST                       = var.alloydb_ip_address
    PGVECTOR_PORT                       = 5432
    PGVECTOR_USER                       = var.alloydb_user_username
    PGVECTOR_PASSWORD                   = var.alloydb_user_password
    PGVECTOR_DATABASE                   = "postgres"
    PGVECTOR_SSL_MODE                   = "require"
    PGVECTOR_CONNECTION_TIMEOUT         = 1
    PGVECTOR_EMBEDDING_DIMENSION        = 768
    PGVECTOR_TABLE_MEDISPAN             = var.meddb_table_medispan           # "medispan_drugs_gcp_768_2"
    PGVECTOR_TABLE_MERATIVE             = var.meddb_table_merative           # "merative_drugs_gcp_768_2"    
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN   = var.meddb_search_function_medispan # "medispan_search_gcp_768_2"
    PGVECTOR_SEARCH_FUNCTION_MERATIVE   = var.meddb_search_function_merative # "merative_search_gcp_768_2"
    FIRESTOREVECTOR_COLLECTION_MEDISPAN = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE = "meddb_merative"
    MEDDB_REPO_STRATEGY                 = var.meddb_active_repo
    CIRCUIT_BREAKER_FAILURE_THRESHOLD   = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT    = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD   = 2
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.medispan_api.allow_public_access
  organization_id     = var.organization_id
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  vpc_connector_name  = var.vpc_connector
  memory              = 2048 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4    # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 180
}

module "medispan_api_high" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medispan-high"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medispan-api:${var.medispan_api_version}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
  ]
  env = {
    SERVICE                             = "medispan_api"
    STAGE                               = var.env
    VERSION                             = var.medispan_api_version
    DEBUG                               = true
    CORS_ORIGINS                        = "http://localhost:3000,http://localhost:21000"
    GCP_PROJECT_ID                      = var.app_project_id
    GCP_LOCATION                        = var.region
    GCP_FIRESTORE_DB                    = "viki-${var.env}"
    GCP_EMBEDDING_MODEL                 = "text-embedding-005"
    PGVECTOR_HOST                       = var.alloydb_ip_address
    PGVECTOR_PORT                       = 5432
    PGVECTOR_USER                       = var.alloydb_user_username
    PGVECTOR_PASSWORD                   = var.alloydb_user_password
    PGVECTOR_DATABASE                   = "postgres"
    PGVECTOR_SSL_MODE                   = "require"
    PGVECTOR_CONNECTION_TIMEOUT         = 1
    PGVECTOR_EMBEDDING_DIMENSION        = 768
    PGVECTOR_TABLE_MEDISPAN             = var.meddb_table_medispan           # "medispan_drugs_gcp_768_2"
    PGVECTOR_TABLE_MERATIVE             = var.meddb_table_merative           # "merative_drugs_gcp_768_2"    
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN   = var.meddb_search_function_medispan # "medispan_search_gcp_768_2"
    PGVECTOR_SEARCH_FUNCTION_MERATIVE   = var.meddb_search_function_merative # "merative_search_gcp_768_2"
    FIRESTOREVECTOR_COLLECTION_MEDISPAN = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE = "meddb_merative"
    MEDDB_REPO_STRATEGY                 = var.meddb_active_repo
    CIRCUIT_BREAKER_FAILURE_THRESHOLD   = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT    = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD   = 2
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.medispan_api.allow_public_access
  organization_id     = var.organization_id
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  vpc_connector_name  = var.vpc_connector
  memory              = 2048 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4    # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 180
}

module "medispan_api_quarantine" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-medispan-api-quarantine"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-medispan-api:${var.medispan_api_version}"
  command = [
    "uv", "run", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8080",
    "--workers", "1"
  ]
  env = {
    SERVICE                             = "medispan_api"
    STAGE                               = var.env
    VERSION                             = var.medispan_api_version
    DEBUG                               = true
    CORS_ORIGINS                        = "http://localhost:3000,http://localhost:21000"
    GCP_PROJECT_ID                      = var.app_project_id
    GCP_LOCATION                        = var.region
    GCP_FIRESTORE_DB                    = "viki-${var.env}"
    GCP_EMBEDDING_MODEL                 = "text-embedding-005"
    PGVECTOR_HOST                       = var.alloydb_ip_address
    PGVECTOR_PORT                       = 5432
    PGVECTOR_USER                       = var.alloydb_user_username
    PGVECTOR_PASSWORD                   = var.alloydb_user_password
    PGVECTOR_DATABASE                   = "postgres"
    PGVECTOR_SSL_MODE                   = "require"
    PGVECTOR_CONNECTION_TIMEOUT         = 1
    PGVECTOR_EMBEDDING_DIMENSION        = 768
    PGVECTOR_TABLE_MEDISPAN             = var.meddb_table_medispan           # "medispan_drugs_gcp_768_2"
    PGVECTOR_TABLE_MERATIVE             = var.meddb_table_merative           # "merative_drugs_gcp_768_2"    
    PGVECTOR_SEARCH_FUNCTION_MEDISPAN   = var.meddb_search_function_medispan # "medispan_search_gcp_768_2"
    PGVECTOR_SEARCH_FUNCTION_MERATIVE   = var.meddb_search_function_merative # "merative_search_gcp_768_2"
    FIRESTOREVECTOR_COLLECTION_MEDISPAN = "meddb_medispan"
    FIRESTOREVECTOR_COLLECTION_MERATIVE = "meddb_merative"
    MEDDB_REPO_STRATEGY                 = var.meddb_active_repo
    CIRCUIT_BREAKER_FAILURE_THRESHOLD   = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT    = 60
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD   = 2
  }
  labels              = var.labels
  ingress             = "all"
  allow_public_access = var.cloud_run_services.medispan_api.allow_public_access
  organization_id     = var.organization_id
  min_instances       = (var.env == "dev" || var.env == "qa") ? 0 : 1
  vpc_connector_name  = var.vpc_connector
  memory              = 2048 # This needs to be pulled from tfvars as it is overwritten on promote env
  cpus                = 4    # This needs to be pulled from tfvars as it is overwritten on promote env
  project_id          = var.app_project_id
  timeout             = 180
}

