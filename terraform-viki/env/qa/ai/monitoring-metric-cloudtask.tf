
resource "google_logging_metric" "orchestration_stepgroup_cloudtask_enqueue_metric" {
  name    = "orchestration_stepgroup_cloudtask_enqueue_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Submit CloudTask\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration StepGroup CloudTask submit"
    labels {
      key         = "category"
      value_type  = "STRING"
      description = "StepGroup category"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "Priority"
    }
    labels {
      key         = "queueName"
      value_type  = "STRING"
      description = "Queue Name"
    }
  }
  label_extractors = {
    category  = "EXTRACT(jsonPayload.category)",
    priority  = "EXTRACT(jsonPayload.priority)",
    queueName = "EXTRACT(jsonPayload.queueName)"

  }
}