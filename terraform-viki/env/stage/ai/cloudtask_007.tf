resource "google_cloud_tasks_queue" "paperglass_classification_007_default" {
  name     = "paperglass-classification-007-default-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_007_high" {
  name     = "paperglass-classification-007-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_007_quarantine" {
  name     = "paperglass-classification-007-quarantine-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_quarantine_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_quarantine_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "paperglass_extraction_007_default" {
  name     = "paperglass-extraction-007-default-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_007_high" {
  name     = "paperglass-extraction-007-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_007_quarantine" {
  name     = "paperglass-extraction-007-quarantine-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_quarantine_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_quarantine_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

# This is the main entrypoint for the v4 extraction process------------------------------------------------------

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_007_default" {
  name     = "v4-extraction-entrypoint-007-default-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_007_high" {
  name     = "v4-extraction-entrypoint-007-high-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_007_quarantine" {
  name     = "v4-extraction-entrypoint-007-quarantine-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_status_check_007_default" {
  name     = "v4-status-check-007-default-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_007_high" {
  name     = "v4-status-check-007-high-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_007_quarantine" {
  name     = "v4-status-check-007-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_007_default" {
  name     = "v4-paperglass-integration-status-update-007-default-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_007_high" {
  name     = "v4-paperglass-integration-status-update-007-high-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_007_quarantine" {
  name     = "v4-paperglass-integration-status-update-007-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_007_default" {
  name     = "v4-paperglass-medications-integration-007-default-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_007_high" {
  name     = "v4-paperglass-medications-integration-007-high-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_007_quarantine" {
  name     = "v4-paperglass-medications-integration-007-quarantine-queue"
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