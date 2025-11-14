resource "google_logging_metric" "aiplatform_predict_metric" {
  name    = "aiplatform_predict_metric"
  project = var.app_project_id
  filter  = "resource.type=\"aiplatform.googleapis.com/Predict\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "aiplatform_gemini_pro_success" {
  name    = "gemini_1_5_pro_success_calls"
  project = var.app_project_id
  filter  = "resource.type=\"aiplatform.googleapis.com/Predict\" AND jsonPayload.model=\"Gemini 1.5 Pro\" AND jsonPayload.status=\"SUCCESS\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "The model name"
    }
  }
  label_extractors = {
    model = "EXTRACT(jsonPayload.model)"
  }
}

resource "google_logging_metric" "aiplatform_gemini_flash_success" {
  name    = "gemini_1_5_flash_success_calls"
  project = var.app_project_id
  filter  = "resource.type=\"aiplatform.googleapis.com/Predict\" AND jsonPayload.model=\"Gemini 1.5 Flash\" AND jsonPayload.status=\"SUCCESS\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "The model name"
    }
  }
  label_extractors = {
    model = "EXTRACT(jsonPayload.model)"
  }
}

resource "google_logging_metric" "aiplatform_gemini_pro_error" {
  name    = "gemini_1_5_pro_error_calls"
  project = var.app_project_id
  filter  = "resource.type=\"aiplatform.googleapis.com/Predict\" AND jsonPayload.model: \"Gemini 1.5 Pro\" AND jsonPayload.status=\"ERROR\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "The model name"
    }
  }
  label_extractors = {
    model = "EXTRACT(jsonPayload.model)"
  }
}
resource "google_logging_metric" "aiplatform_gemini_flash_error" {
  name    = "gemini_1_5_flash_error_calls"
  project = var.app_project_id
  filter  = "resource.type=\"aiplatform.googleapis.com/Predict\" AND jsonPayload.model: \"Gemini 1.5 Flash\" AND jsonPayload.status=\"ERROR\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "The model name"
    }
  }
  label_extractors = {
    model = "EXTRACT(jsonPayload.model)"
  }
}

resource "google_logging_metric" "gemini_quota_metric" {
  name    = "gemini_1_5_quota_usage"
  project = var.app_project_id
  filter  = "resource.type=\"global\" AND jsonPayload.model: \"Gemini 1.5\" AND resource.labels.method=\"google.cloud.aiplatform.v1.PredictionService.GenerateContent\" AND severity=\"ERROR\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "paperglass_api_error_logs_metric" {
  name    = "error_logs_ai_paperglass_api"
  project = var.app_project_id
  filter  = "resource.labels.service_name=\"ai-paperglass-api\" AND severity=\"ERROR\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "paperglass_events_error_logs_metric" {
  name    = "error_logs_ai_paperglass_event"
  project = var.app_project_id
  filter  = "resource.labels.service_name=\"ai-paperglass-events\" AND severity=\"ERROR\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}