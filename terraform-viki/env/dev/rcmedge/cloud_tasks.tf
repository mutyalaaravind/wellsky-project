resource "google_cloud_tasks_queue" "rcmedge_queue" {
  name     = "rcmedge-queue"
  location = var.region
  project  = var.app_project_id

  rate_limits {
    max_concurrent_dispatches = 10
    max_dispatches_per_second = 500
  }

  retry_config {
    max_attempts       = 5
    max_retry_duration = "4s"
    min_backoff        = "1s"
    max_backoff        = "10s"
    max_doublings      = 2
  }

  stackdriver_logging_config {
    sampling_ratio = 0.9
  }
}

# IAM binding for Cloud Tasks queue
resource "google_cloud_tasks_queue_iam_member" "queue_invoker" {
  name     = google_cloud_tasks_queue.rcmedge_queue.name
  location = google_cloud_tasks_queue.rcmedge_queue.location
  project  = var.app_project_id
  role     = "roles/cloudtasks.enqueuer"
  member   = "serviceAccount:${module.rcmedge_sa.email}"
}