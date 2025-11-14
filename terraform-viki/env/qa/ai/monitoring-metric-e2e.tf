
resource "google_logging_metric" "paperglass_e2e_orchestration_success_metric" {
  name    = "paperglass_e2e_orchestration_success_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E orchestration test passed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E orchestration test passed"
  }
}

resource "google_logging_metric" "paperglass_e2e_orchestration_failed_metric" {
  name    = "paperglass_e2e_orchestration_failed_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E orchestration test failed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E orchestration test failed"
  }
}

resource "google_logging_metric" "paperglass_e2e_orchestration_timeout_metric" {
  name    = "paperglass_e2e_orchestration_timeout_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E orchestration test timeout\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E orchestration test timeout"
  }
}

# Test Harness Metrics

resource "google_logging_metric" "paperglass_e2e_testharness_start_metric" {
  name    = "paperglass_e2e_testharness_start_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::E2E::TestHarness::start\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E Test Start"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
  }
  label_extractors = {
    mode = "EXTRACT(jsonPayload.mode)"
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_complete_metric" {
  name    = "paperglass_e2e_testharness_complete_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::E2E::TestHarness:complete\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E Test Complete"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
    labels {
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  label_extractors = {
    mode  = "EXTRACT(jsonPayload.mode)",
    error = "EXTRACT(jsonPayload.error.type)"
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_complete_total_f1_metric" {
  name    = "paperglass_e2e_testharness_complete_total_f1_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::E2E::TestHarness:complete\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "E2E Test Complete Total F1"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
  }

  value_extractor = "EXTRACT(jsonPayload.summary.f1)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }

  label_extractors = {
    mode = "EXTRACT(jsonPayload.mode)",
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_complete_testcase_count_metric" {
  name    = "paperglass_e2e_testharness_complete_testcase_count_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E::TestHarness::run_testcase::assessment\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E Test Complete Testcase Count"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
  }
  label_extractors = {
    mode = "EXTRACT(jsonPayload.mode)",
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_complete_testcase_accuracy_metric" {
  name    = "paperglass_e2e_testharness_complete_testcase_accuracy_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E::TestHarness::run_testcase::assessment\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "E2E Test Complete Testcase Accuracy"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
  }

  value_extractor = "EXTRACT(jsonPayload.assessment.accuracy)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }

  label_extractors = {
    mode = "EXTRACT(jsonPayload.mode)",
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_complete_testcase_recall_metric" {
  name    = "paperglass_e2e_testharness_complete_testcase_recall_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E::TestHarness::run_testcase::assessment\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "E2E Test Complete Testcase Recall"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
  }

  value_extractor = "EXTRACT(jsonPayload.assessment.recall)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }

  label_extractors = {
    mode = "EXTRACT(jsonPayload.mode)",
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_complete_testcase_f1_metric" {
  name    = "paperglass_e2e_testharness_complete_testcase_f1_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"E2E::TestHarness::run_testcase::assessment\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "E2E Test Complete Testcase F1"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
  }

  value_extractor = "EXTRACT(jsonPayload.assessment.f1)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }

  label_extractors = {
    mode = "EXTRACT(jsonPayload.mode)",
  }
}

resource "google_logging_metric" "paperglass_e2e_testharness_failed_metric" {
  name    = "paperglass_e2e_testharness_failed_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::E2E::TestHarness::failed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "E2E Test Failed"
    labels {
      key         = "mode"
      value_type  = "STRING"
      description = "Mode"
    }
    labels {
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  label_extractors = {
    mode  = "EXTRACT(jsonPayload.mode)",
    error = "EXTRACT(jsonPayload.error.type)"
  }
}