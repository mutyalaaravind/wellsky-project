
resource "google_logging_metric" "pipeline_group_classify_metric" {
  name    = "pipeline_group_classify_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::GROUP.CLASSIFY\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Group Classify"    
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "Priority"
    }
    labels {
      key         = "retry_attempt"
      value_type  = "STRING"
      description = "Retry Attempt"
    }

  }
  label_extractors = {    
    priority = "EXTRACT(jsonPayload.request.document.priority)",
    retry_attempt = "EXTRACT(jsonPayload.request.retry_attempt)"
  }
}

resource "google_logging_metric" "pipeline_group_classify_elapsedtime_metric" {
  name    = "pipeline_group_classify_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::GROUP.CLASSIFY\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Group Classify Elapsed Time"    
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
    priority = "EXTRACT(jsonPayload.request.document.priority)"
  }
}

resource "google_logging_metric" "pipeline_group_classify_waittime_metric" {
  name    = "pipeline_group_classify_waittime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::GROUP.CLASSIFY\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Group Classify Wait Time"    
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.wait_time)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
  label_extractors = {    
    priority = "EXTRACT(jsonPayload.request.document.priority)"
  }
}


resource "google_logging_metric" "pipeline_group_medications_metric" {
  name    = "pipeline_group_medications_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::GROUP.MEDICATIONS\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Group Medications"    
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "Priority"
    }
    labels {
      key         = "retry_attempt"
      value_type  = "STRING"
      description = "Retry attempt"
    }
  }
  label_extractors = {    
    priority = "EXTRACT(jsonPayload.request.document.priority)",
    retry_attempt = "EXTRACT(jsonPayload.request.retry_attempt)"
  }
}

resource "google_logging_metric" "pipeline_group_medications_elapsedtime_metric" {
  name    = "pipeline_group_medications_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::GROUP.MEDICATIONS\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Group Medications Elapsed Time"    
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
    priority = "EXTRACT(jsonPayload.request.document.priority)"
  }
}

resource "google_logging_metric" "pipeline_group_medications_waittime_metric" {
  name    = "pipeline_group_medications_waittime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::GROUP.MEDICATIONS\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Group Medications Wait Time"    
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.wait_time)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
  label_extractors = {    
    priority = "EXTRACT(jsonPayload.request.document.priority)"
  }
}
