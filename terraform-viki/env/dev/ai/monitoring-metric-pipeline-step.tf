
resource "google_logging_metric" "pipeline_step_metric" {
  name    = "pipeline_step_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STEP.\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Step"
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "Priority"
    }
  }
  label_extractors = {
    step     = "EXTRACT(jsonPayload.step_id)",
    priority = "EXTRACT(jsonPayload.document.priority)"
  }
}

resource "google_logging_metric" "pipeline_step_elapsedtime_metric" {
  name    = "pipeline_step_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STEP.\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Step Elapsed Time"
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "Priority"
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
    step     = "EXTRACT(jsonPayload.step_id)",
    priority = "EXTRACT(jsonPayload.document.priority)"
  }
}