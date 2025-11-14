
# GRADER Metrics

resource "google_logging_metric" "orchestration_grader_start_metric" {
  name    = "orchestration_grader_start_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Orchestration grader start\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration grader start"
  }
}

resource "google_logging_metric" "orchestration_grader_complete_metric" {
  name    = "orchestration_grader_complete_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Grading complete for document\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration grader complete"
  }
}

resource "google_logging_metric" "orchestration_medicationextraction_grader_elapsedtime_metric" {
  name    = "orchestration_medicationextraction_grader_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Grading complete for document\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Medication extraction grader elapsed time"
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
}

resource "google_logging_metric" "orchestration_grader_failed_metric" {
  name    = "orchestration_grader_failed_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Grading failed for document\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Orchestration grader failed"
  }
}

resource "google_logging_metric" "medication_medispan_matched_metric" {
  name    = "medication_medispan_matched_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Medication matched to Medispan\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Medication matched to Medispan"
  }
}

resource "google_logging_metric" "medication_medispan_unmatched_metric" {
  name    = "medication_medispan_unmatched_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Medication not matched to Medispan\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Medication not matched to Medispan"
  }
}

resource "google_logging_metric" "orchestration_medication_grader_score_metric" {
  name    = "orchestration_medication_grader_score_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Medication grade medication score\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Medication grader score"
  }
  value_extractor = "EXTRACT(jsonPayload.score)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
}