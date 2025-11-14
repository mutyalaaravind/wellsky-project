
resource "google_logging_metric" "pipeline_cloudtask_metric" {
  name    = "pipeline_cloudtask_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::CLOUDTASK::*\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Cloud Task"
    labels {
      key         = "category"
      value_type  = "STRING"
      description = "Category"
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
