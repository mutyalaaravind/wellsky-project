resource "google_logging_project_sink" "prompt_log_sink" {
  name = "prompt_log-sink"

  project = var.app_project_id

  # Can export to pubsub, cloud storage, bigquery, log bucket, or another project
  destination = "bigquery.googleapis.com/projects/${var.app_project_id}/datasets/${google_bigquery_dataset.audit_log_dataset.dataset_id}"

  # Log all WARN or higher severity messages relating to instances
  filter = "PROMPT_AUDIT_LOG"

  bigquery_options {
    use_partitioned_tables = true
  }

  unique_writer_identity = true

  #   # Use a unique writer (creates a unique service account used for writing)
  #   unique_writer_identity = true
}

resource "google_logging_project_sink" "step_log_sink" {
  name = "step_log_sink"

  project = var.app_project_id

  # Can export to pubsub, cloud storage, bigquery, log bucket, or another project
  destination = "bigquery.googleapis.com/projects/${var.app_project_id}/datasets/${google_bigquery_dataset.audit_log_dataset.dataset_id}"

  # Log all WARN or higher severity messages relating to instances
  filter = "STEP_LOGGER"

  bigquery_options {
    use_partitioned_tables = true
  }

  unique_writer_identity = true

  #   # Use a unique writer (creates a unique service account used for writing)
  #   unique_writer_identity = true
}