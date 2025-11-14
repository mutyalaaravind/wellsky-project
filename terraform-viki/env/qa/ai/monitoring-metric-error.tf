resource "google_logging_metric" "error_type_metric" {
  name    = "error_type_metric"
  project = var.app_project_id
  filter  = "severity: \"ERROR\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Error Type"
    labels {
      key         = "service_name"
      value_type  = "STRING"
      description = "Service"
    }
    labels {
      key         = "error_type"
      value_type  = "STRING"
      description = "Error type"
    }
  }
  label_extractors = {
    service_name = "EXTRACT(jsonPayload.resource.labels.service_name)",
    error_type   = "EXTRACT(jsonPayload.error.type)"
  }
}