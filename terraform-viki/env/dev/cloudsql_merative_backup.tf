# SQL Server Cloud SQL Database Instance for Merative .bak file restoration
module "cloudsql_merative" {
  source  = "terraform.wellsky.net/wellsky/cloudsql/gcp//modules/mssql"
  version = "5.2.6"

  availability_type = "ZONAL"

  backup_configuration = {
    binary_log_enabled             = false
    enabled                        = true
    point_in_time_recovery_enabled = false
    start_time                     = "03:00" # 3 AM backup time
    backup_retention_settings = {
      retained_backups = 7
      retention_unit   = "COUNT"
    }
  }

  # SQL Server specific database flags
  database_flags = [
    {
      name  = "user connections"
      value = "100"
    }
  ]

  deletion_protection = false

  database_version = "SQLSERVER_2022_STANDARD"
  db_collation     = "SQL_Latin1_General_CP1_CI_AS" # SQL Server default collation
  db_charset       = "UTF8"
  disk_type        = "PD_SSD"
  disk_size        = 100

  ip_configuration = {
    authorized_networks = []
    ipv4_enabled        = false
    private_network     = "projects/${var.network_project_id}/global/networks/${var.network}"
    require_ssl         = false # encryption not required on a private network
  }

  insights_config = {
    enabled                 = true
    query_plans_per_minute  = 5
    query_string_length     = 1024
    record_application_tags = false
    record_client_address   = false
  }

  labels = merge(var.labels, {
    database-type = "sqlserver"
    purpose       = "merative-backup-restore"
  })

  maintenance_window = {
    day          = 7        # Sunday
    hour         = 3        # 3:00 AM
    update_track = "stable" # Receive updates later (stable)
  }

  name                   = "viki-sqlserver-merative-${var.env}"
  project_id             = var.app_project_id
  random_password_length = 16
  region                 = var.region
  tier                   = "db-custom-2-7680" # 2 vCPUs, 7.5GB RAM
  zone                   = var.zone

  create_timeout = "60m"
}

# Save the root password into secret manager for later access
module "cloudsql_merative_root_password" {
  source  = "terraform.wellsky.net/wellsky/secret/gcp"
  version = "0.4.2"

  labels              = var.labels
  name                = "merative-sqlserver-root-password"
  accessors           = var.managers
  managers            = var.managers
  project_id          = var.app_project_id
  secret_data         = module.cloudsql_merative.root_password
  replication_regions = [var.region]
}

# Data source to get the Cloud SQL instance details (including service account)
data "google_sql_database_instance" "merative_backup" {
  name    = module.cloudsql_merative.instance_name
  project = var.app_project_id

  depends_on = [module.cloudsql_merative]
}

# Grant Cloud SQL service account access to meddb-dev GCS bucket for .bak file import
resource "google_storage_bucket_iam_member" "merative_cloudsql_gcs_access" {
  bucket = "meddb-dev"
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${data.google_sql_database_instance.merative_backup.service_account_email_address}"
}

# Outputs
output "merative_instance_name" {
  description = "The name of the Cloud SQL instance for Merative backup restoration"
  value       = module.cloudsql_merative.instance_name
}

output "merative_connection_name" {
  description = "The connection name of the instance (for Cloud SQL Proxy)"
  value       = module.cloudsql_merative.instance_connection_name
}

output "merative_private_ip" {
  description = "The private IP address of the instance"
  value       = data.google_sql_database_instance.merative_backup.private_ip_address
}

output "merative_service_account" {
  description = "The service account used by the instance (has access to meddb-dev bucket)"
  value       = data.google_sql_database_instance.merative_backup.service_account_email_address
}

# Instructions for importing .bak files from gs://meddb-dev/merative/landing/:
#
# 1. Create target database (if needed):
#    gcloud sql databases create YOUR_DATABASE_NAME \
#      --instance=viki-sqlserver-merative-dev \
#      --project=viki-dev-app-wsky
#
# 2. Import .bak file:
#    gcloud sql import bak viki-sqlserver-merative-dev \
#      gs://meddb-dev/merative/landing/your-file.bak \
#      --database=YOUR_DATABASE_NAME \
#      --project=viki-dev-app-wsky
#
# Note: GCS bucket access is automatically configured by Terraform
# Root password is stored in Secret Manager: merative-sqlserver-root-password