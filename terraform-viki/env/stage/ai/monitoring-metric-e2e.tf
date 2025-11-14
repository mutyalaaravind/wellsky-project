
resource "google_logging_metric" "paperglass_e2e_orchestration_success_metric" {
  name    = "paperglass_e2e_orchestration_success_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E orchestration test passed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E orchestration test passed"
  }
}

resource "google_logging_metric" "paperglass_e2e_orchestration_failed_metric" {
  name    = "paperglass_e2e_orchestration_failed_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E orchestration test failed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E orchestration test failed"
  }
}

resource "google_logging_metric" "paperglass_e2e_orchestration_timeout_metric" {
  name    = "paperglass_e2e_orchestration_timeout_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E orchestration test timeout\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E orchestration test timeout"
  }
}