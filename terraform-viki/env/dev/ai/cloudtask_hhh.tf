resource "google_cloud_tasks_queue" "paperglass_classification_hhh_default" {
  name     = "paperglass-classification-hhh-default-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_hhh_high" {
  name     = "paperglass-classification-hhh-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_hhh_quarantine" {
  name     = "paperglass-classification-hhh-quarantine-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_hhh_default" {
  name     = "paperglass-extraction-hhh-default-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_hhh_high" {
  name     = "paperglass-extraction-hhh-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_hhh_quarantine" {
  name     = "paperglass-extraction-hhh-quarantine-queue"
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
resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_hhh_default" {
  name     = "v4-extraction-entrypoint-hhh-default-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_hhh_high" {
  name     = "v4-extraction-entrypoint-hhh-high-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_hhh_quarantine" {
  name     = "v4-extraction-entrypoint-hhh-quarantine-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_quarantine_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_status_check_hhh_default" {
  name     = "v4-status-check-hhh-default-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_hhh_high" {
  name     = "v4-status-check-hhh-high-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_hhh_quarantine" {
  name     = "v4-status-check-hhh-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_hhh_default" {
  name     = "v4-paperglass-integration-status-update-hhh-default-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_hhh_high" {
  name     = "v4-paperglass-integration-status-update-hhh-high-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_hhh_quarantine" {
  name     = "v4-paperglass-integration-status-update-hhh-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_hhh_default" {
  name     = "v4-paperglass-medications-integration-hhh-default-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_hhh_high" {
  name     = "v4-paperglass-medications-integration-hhh-high-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_hhh_quarantine" {
  name     = "v4-paperglass-medications-integration-hhh-quarantine-queue"
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