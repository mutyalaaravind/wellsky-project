
locals {
  # List all SQL files in the dedup_sql directory
  sql_files = fileset("${path.module}/dedup_sql", "*_dedup.sql")
}

# Create a service account for the scheduled queries
resource "google_service_account" "bq_scheduled_query" {
  account_id   = "bq-${var.env}-scheduled-query"
  display_name = "BigQuery Scheduled Query Service Account"
  project      = var.app_project_id
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "bq_scheduled_query_roles" {
  for_each = toset([
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser"
  ])

  project = var.app_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.bq_scheduled_query.email}"
}

#Create scheduled queries for each SQL file
resource "google_bigquery_data_transfer_config" "scheduled_query" {
  for_each = local.sql_files

  project        = data.google_project.app_project.project_id
  display_name   = "Scheduled Dedup - ${replace(each.value, "_dedup.sql", "")}"
  location       = "us-central1"
  data_source_id = "scheduled_query"
  schedule       = "every 1 hours"
  #destination_dataset_id = "firestore_sync"
  #name = "projects/${var.app_project_id}/locations/us-central1/transferConfigs/${replace(each.value, "_dedup.sql", "")}"


  params = {
    query = file("${path.module}/dedup_sql/${each.value}")
  }

  service_account_name = google_service_account.bq_scheduled_query.email
}

output "scheduled_queries" {
  description = "Created scheduled queries"
  value = {
    for k, v in google_bigquery_data_transfer_config.scheduled_query : k => {
      name     = v.display_name
      schedule = v.schedule
    }
  }
}
