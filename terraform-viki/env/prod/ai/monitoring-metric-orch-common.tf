#Document operation instance created
resource "google_logging_metric" "orchestration_documentcreated_metric" {
  name    = "orchestration_documentcreated_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Document operation instance created\" AND jsonPayload.operation_type=\"medication_extraction\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Document created"
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_pagecreated_metric" {
  name    = "orchestration_pagecreated_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Page::Created\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Page created"
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }  
  label_extractors = {
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_splitpages_pagecount_metric" {
  name    = "orchestration_splitpages_pagecount_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Step::DocumentOperationStep.SPLIT_PAGES\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "SplitPages page count"
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.page_count)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
  label_extractors = {
    priority = "EXTRACT(jsonPayload.priority)"
  }
}