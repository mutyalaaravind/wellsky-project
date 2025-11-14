

resource "google_logging_metric" "orchestration_step_medispanmatch_medicationcount_metric" {
  name    = "orchestration_step_medispanmatch_medicationcount_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Step::DocumentOperationStep.MEDISPAN_MATCHING completed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Orchestration Step Medispan Match medication count"
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Code branch"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.medication_count)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    priority = "EXTRACT(jsonPayload.priority)"
  }

}