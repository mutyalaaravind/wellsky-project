# End of the pipeline ===================================================================

resource "google_logging_metric" "pipeline_success_metric" {
  name    = "pipeline_success_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STATUS.COMPLETE\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Success"    
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
  }
  label_extractors = {    
    priority = "EXTRACT(jsonPayload.document.priority)",
    status = "EXTRACT(jsonPayload.status)"
  }
}

resource "google_logging_metric" "pipeline_success_elapsedtime_metric" {
  name    = "pipeline_success_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STATUS.COMPLETE\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Success Elapsed Time"    
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
    priority = "EXTRACT(jsonPayload.document.priority)"
  }
}

resource "google_logging_metric" "pipeline_failed_metric" {
  name    = "pipeline_failed_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STATUS.FAILED\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Failed"    
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  label_extractors = {    
    priority = "EXTRACT(jsonPayload.document.priority)",
    status = "EXTRACT(jsonPayload.status)",
    step = "EXTRACT(jsonPayload.step)",
    error = "EXTRACT(jsonPayload.error.type)",
  }
}

resource "google_logging_metric" "pipeline_failed_elapsedtime_metric" {
  name    = "pipeline_failed_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STATUS.FAILED\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Failed Elapsed Time"    
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
    priority = "EXTRACT(jsonPayload.document.priority)"
  }
}