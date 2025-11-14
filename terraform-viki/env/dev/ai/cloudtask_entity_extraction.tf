

resource "google_cloud_tasks_queue" "entity_extraction_launch_queue" {
  name     = "entity-extraction-launch-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}