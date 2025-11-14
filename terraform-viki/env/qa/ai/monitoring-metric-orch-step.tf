
resource "google_logging_metric" "orchestration_step_metric" {
  name    = "orchestration_step_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Step::DocumentOperationStep.\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration Step"
    labels {
      key         = "step_id"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    step_id  = "EXTRACT(jsonPayload.step_id)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_step_elapsedtime_metric" {
  name    = "orchestration_step_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Step::DocumentOperationStep.\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration Step Elapsed Time"
    labels {
      key         = "step_id"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
  label_extractors = {
    step_id  = "EXTRACT(jsonPayload.step_id)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}