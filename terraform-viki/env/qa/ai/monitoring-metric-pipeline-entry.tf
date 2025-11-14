resource "google_logging_metric" "pipeline_start_metric" {
  name    = "pipeline_start_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::START\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Start"
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "Priority"
    }
  }
  label_extractors = {
    priority = "EXTRACT(jsonPayload.document.priority)"
  }
}

resource "google_logging_metric" "pipeline_pagecreated_metric" {
  name    = "pipeline_pagecreated_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::DOCUMENTPAGE::CREATED\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Pipeline Page Created"
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    priority = "EXTRACT(jsonPayload.request.document.priority)"
  }
}

resource "google_logging_metric" "pipeline_splitpages_metric" {
  name    = "pipeline_splitpages_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::PIPELINE::MEDICATIONEXTRACTION::STEP.SPLIT_PAGES\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Pipeline Split Pages"
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.result_count)"
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
