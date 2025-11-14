resource "google_cloud_tasks_queue" "paperglass_classification_ltc_default" {
  name     = "paperglass-classification-ltc-default-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_ltc_high" {
  name     = "paperglass-classification-ltc-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_ltc_quarantine" {
  name     = "paperglass-classification-ltc-quarantine-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_ltc_default" {
  name     = "paperglass-extraction-ltc-default-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_ltc_high" {
  name     = "paperglass-extraction-ltc-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_ltc_quarantine" {
  name     = "paperglass-extraction-ltc-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_ltc_default" {
  name     = "v4-extraction-entrypoint-ltc-default-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_ltc_high" {
  name     = "v4-extraction-entrypoint-ltc-high-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_ltc_quarantine" {
  name     = "v4-extraction-entrypoint-ltc-quarantine-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = var.cloudtask_max_concurrent_dispatches
    max_dispatches_per_second = var.cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second
  }
  retry_config {
    max_attempts       = 3
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 1
  }
}

resource "google_cloud_tasks_queue" "v4_status_check_ltc_default" {
  name     = "v4-status-check-ltc-default-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_ltc_high" {
  name     = "v4-status-check-ltc-high-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_ltc_quarantine" {
  name     = "v4-status-check-ltc-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_ltc_default" {
  name     = "v4-paperglass-integration-status-update-ltc-default-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_ltc_high" {
  name     = "v4-paperglass-integration-status-update-ltc-high-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_ltc_quarantine" {
  name     = "v4-paperglass-integration-status-update-ltc-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_ltc_default" {
  name     = "v4-paperglass-medications-integration-ltc-default-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_ltc_high" {
  name     = "v4-paperglass-medications-integration-ltc-high-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_ltc_quarantine" {
  name     = "v4-paperglass-medications-integration-ltc-quarantine-queue"
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