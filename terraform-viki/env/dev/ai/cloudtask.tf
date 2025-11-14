resource "google_cloud_tasks_queue" "paperglass_classification" {
  name     = "paperglass-classification-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_priority" {
  name     = "paperglass-classification-priority-queue"
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

resource "google_cloud_tasks_queue" "paperglass_classification_quarantine" {
  name     = "paperglass-classification-quarantine-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction" {
  name     = "paperglass-extraction-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_priority" {
  name     = "paperglass-extraction-priority-queue"
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

resource "google_cloud_tasks_queue" "paperglass_extraction_quarantine" {
  name     = "paperglass-extraction-quarantine-queue"
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

resource "google_cloud_tasks_queue" "paperglass_command" {
  name     = "paperglass-command-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = 2000
    max_dispatches_per_second = var.cloudtask_paperglass_command_schedule_max_dispatches_per_second
  }
  retry_config {
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 2
  }
}

resource "google_cloud_tasks_queue" "paperglass_command_schedule" {
  name     = "paperglass-command-schedule-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = 12
    max_dispatches_per_second = 2
  }
  retry_config {
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 2
  }
}


resource "google_cloud_tasks_queue" "paperglass-command-external-create-document-queue" {
  name     = "paperglass-command-external-create-document-queue"
  location = var.region
  project  = var.app_project_id
  rate_limits {
    max_concurrent_dispatches = 12
    max_dispatches_per_second = 2
  }
  retry_config {
    max_retry_duration = "4s"
    max_backoff        = "3s"
    min_backoff        = "2s"
    max_doublings      = 2
  }
}


resource "google_cloud_tasks_queue" "v4_extraction_entrypoint" {
  name     = "v4-extraction-entrypoint-default-queue"
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

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_priority" {
  name     = "v4-extraction-entrypoint-priority-queue"
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

resource "google_cloud_tasks_queue" "v4_extraction_entrypoint_quarantine" {
  name     = "v4-extraction-entrypoint-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check" {
  name     = "v4-status-check-default-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_priority" {
  name     = "v4-status-check-priority-queue"
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

resource "google_cloud_tasks_queue" "v4_status_check_quarantine" {
  name     = "v4-status-check-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update" {
  name     = "v4-paperglass-integration-status-update-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_priority" {
  name     = "v4-paperglass-integration-status-update-priority-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_integration_status_update_quarantine" {
  name     = "v4-paperglass-integration-status-update-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration" {
  name     = "v4-paperglass-medications-integration-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_priority" {
  name     = "v4-paperglass-medications-integration-priority-queue"
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

resource "google_cloud_tasks_queue" "v4_paperglass_medications_integration_quarantine" {
  name     = "v4-paperglass-medications-integration-quarantine-queue"
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

resource "google_cloud_tasks_queue" "v4_audit_log_queue" {
  name     = "v4-audit-log-queue"
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

resource "google_cloud_tasks_queue" "entity_extraction_intra_default_default_queue" {
  name     = "entity-extraction-intra-default-default-queue"
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

resource "google_cloud_tasks_queue" "entity_extraction_intra_default_high_queue" {
  name     = "entity-extraction-intra-default-high-queue"
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

resource "google_cloud_tasks_queue" "paperglass_host_publish_callback" {
  name     = "paperglass-host-publish-callback-queue"
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