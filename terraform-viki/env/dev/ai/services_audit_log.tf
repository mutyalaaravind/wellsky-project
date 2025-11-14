# module "audit_logger_api" {
#   source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
#   name                  = "ai-prompt-logger"
#   location              = var.region
#   service_account_email = module.ai_sa.email
#   image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-prompt_logger:${var.paperglass_version}"
#   command = [
#     "uv", "run", "uvicorn", "main:app",
#     "--host", "0.0.0.0",
#     "--port", "8080",
#   ]
#   env = {
#     SERVICE             = "audit_logger"
#     STAGE               = var.env
#     VERSION             = var.medication_extraction_version
#     DEBUG               = (var.env == "dev" || var.env == "qa") ? "true" : "false"
#     GCP_PROJECT_ID      = var.app_project_id
#     GCP_LOCATION        = "us-central1"
#     BIGQUERY_DATASET_ID = google_bigquery_dataset.audit_log_dataset.dataset_id
#     BIGQUERY_TABLE_ID   = google_bigquery_table.audit_log_table.table_id
#     # TASKS_QUEUE_NAME                                         = google_cloud_tasks_queue.v4_audit_log_queue.name
#     # TASKS_SERVICE_URL                                        = var.audit_logger_api_url
#     # TASKS_SERVICE_ACCOUNT                                    = module.ai_sa.email
#   }
#   secrets = toset([
#     {
#       key     = "MEDISPAN_CLIENT_ID",
#       name    = module.secret["medispan_client_id"].name,
#       version = "latest",
#     },
#     {
#       key     = "MEDISPAN_CLIENT_SECRET",
#       name    = module.secret["medispan_client_secret"].name,
#       version = "latest",
#     },
#     {
#       key     = "OKTA_CLIENT_SECRET",
#       name    = module.secret["okta_client_secret"].name,
#       version = "latest",
#     },
#     {
#       key     = "HHH_ATTACHMENTS_CLIENT_SECRET",
#       name    = module.secret["hhh_attachments_client_secret"].name,
#       version = "latest",
#     },
#     {
#       key     = "SHAREPOINT_CLIENT_ID",
#       name    = module.secret["sharepoint_client_id"].name,
#       version = "latest",
#     },
#     {
#       key     = "SHAREPOINT_CLIENT_SECRET",
#       name    = module.secret["sharepoint_client_secret"].name,
#       version = "latest",
#     }
#   ])
#   labels              = var.labels
#   ingress             = "all"
#   min_instances       = (var.env == "dev" || var.env == "qa") ? 1 : 1
#   memory              = 2048 # This needs to be pulled from tfvars as it is overwritten on promote env
#   cpus                = 4   # This needs to be pulled from tfvars as it is overwritten on promote env
#   project_id          = var.app_project_id
#   timeout             = 180
# }

