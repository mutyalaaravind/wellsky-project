
resource "google_logging_metric" "orchestration_medicationextraction_classification_metric" {
  name    = "orchestration_medicationextraction_classification_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration Page Classification\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration Page Classification StepGroup"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    page_number = "EXTRACT(jsonPayload.page_number)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_classification_elapsedtime_metric" {
  name    = "orchestration_medicationextraction_classification_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration Page Classification\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration Page Classification StepGroup elapsed time"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
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
    page_number = "EXTRACT(jsonPayload.page_number)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_classification_waittime_metric" {
  name    = "orchestration_medicationextraction_classification_waittime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"StepGroup:PageClassification wait time\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration Page Classification StepGroup wait time"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
    }
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
    page_number = "EXTRACT(jsonPayload.page_number)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}


resource "google_logging_metric" "orchestration_medicationextraction_extraction_metric" {
  name    = "orchestration_medicationextraction_extraction_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration Medication Extraction\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration Medication Extraction StepGroup"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    page_number = "EXTRACT(jsonPayload.page_number)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_extraction_elapsedtime_metric" {
  name    = "orchestration_medicationextraction_extraction_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration Medication Extraction\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration Medication Extraction StepGroup elapsed time"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
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
    page_number = "EXTRACT(jsonPayload.page_number)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_extraction_waittime_metric" {
  name    = "orchestration_medicationextraction_extraction_waittime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration Medication Extraction\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration Medication Extraction StepGroup wait time"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
    }
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
    page_number = "EXTRACT(jsonPayload.page_number)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}


resource "google_logging_metric" "orchestration_medicationextraction_success_metric" {
  name    = "orchestration_medicationextraction_success_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration success\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration success"
    labels {
      key         = "operation_type"
      value_type  = "STRING"
      description = "The operation_type"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    operation_type = "EXTRACT(jsonPayload.operation_type)",
    priority       = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_success_elapsedtime_metric" {
  name    = "orchestration_medicationextraction_success_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration success\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration success elapsed time"
    labels {
      key         = "operation_type"
      value_type  = "STRING"
      description = "The operation_type"
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
    operation_type = "EXTRACT(jsonPayload.operation_type)",
    priority       = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_failed_metric" {
  name    = "orchestration_medicationextraction_failed_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration failed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration failed"
    labels {
      key         = "operation_type"
      value_type  = "STRING"
      description = "The operation_type"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    operation_type = "EXTRACT(jsonPayload.operation_type)",
    priority       = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_failed_elapsedtime_metric" {
  name    = "orchestration_medicationextraction_failed_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration failed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Medication extraction orchestration failed elapsed time"
    labels {
      key         = "operation_type"
      value_type  = "STRING"
      description = "The operation_type"
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
    operation_type = "EXTRACT(jsonPayload.operation_type)",
    priority       = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_recover_metric" {
  name    = "orchestration_medicationextraction_recover_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Recovering failed instance log\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration recovery"
    labels {
      key         = "step_group"
      value_type  = "STRING"
      description = "Step group"
    }
    labels {
      key         = "retry_count"
      value_type  = "STRING"
      description = "Retry count"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    step_group  = "EXTRACT(jsonPayload.step_group)",
    retry_count = "EXTRACT(jsonPayload.retry_count)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_medicationsperpage_metric" {
  name    = "orchestration_medicationextraction_medicationsperpage_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Step::DocumentOperationStep.MEDICATIONS_EXTRACTION completed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Medications per page"
    labels {
      key         = "page_number"
      value_type  = "STRING"
      description = "Page Number"
    }
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.medication_count)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
  label_extractors = {
    page_number = "EXTRACT(jsonPayload.page_number)",
    branch      = "EXTRACT(jsonPayload.branch)",
    priority    = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_evidencelinking_metric" {
  name    = "orchestration_medicationextraction_evidencelinking_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"MedicationExtraction::EvidenceLinking\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Evidence linked"
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
  }
  label_extractors = {
    status = "EXTRACT(jsonPayload.status)"
  }
}
