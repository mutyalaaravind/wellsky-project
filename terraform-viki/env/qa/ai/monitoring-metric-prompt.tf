
resource "google_logging_metric" "prompt_metric" {
  name    = "prompt_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Prompt by Model"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model.name)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_step_metric" {
  name    = "prompt_step_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Prompt by Step"
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  label_extractors = {
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_step_elapsedtime_metric" {
  name    = "prompt_step_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt elapsed time by step"
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
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
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}


resource "google_logging_metric" "prompt_elapsedtime_metric" {
  name    = "prompt_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt elapsed time"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
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
    model    = "EXTRACT(jsonPayload.model.name)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_input_length_metric" {
  name    = "prompt_input_length_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt input length"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.prompt_length)"
  bucket_options {
    explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model.name)",
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_input_billable_length_metric" {
  name    = "prompt_input_billable_length_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt input billable length"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.billing_total_billable_characters)"
  bucket_options {
    explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model.name)",
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_input_tokens_metric" {
  name    = "prompt_input_tokens_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt input token count"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.prompt_tokens)"
  bucket_options {
    explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model)",
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_output_length_metric" {
  name    = "prompt_output_length_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt output length"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.response_length)"
  bucket_options {
    explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model.name)",
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_output_tokens_metric" {
  name    = "prompt_output_tokens_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt output token count"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.response_tokens)"
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 10
      growth_factor      = 2
      scale              = 1
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model.name)",
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_gemini_1_5_flash_metric" {
  name    = "prompt_gemini_1_5_flash_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\" AND jsonPayload.model.name: \"gemini-1.5-flash\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Gemini 1.5 Flash prompt"
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

resource "google_logging_metric" "prompt_gemini_1_5_flash_elapsedtime_metric" {
  name    = "prompt_gemini_1_5_flash_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\" AND jsonPayload.model.name: \"gemini-1.5-flash\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Gemini 1.5 Flash prompt elapsed time"
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
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_gemini_1_5_pro_metric" {
  name    = "prompt_gemini_1_5_pro_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\" AND jsonPayload.model.name: \"gemini-1.5-pro\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Gemini 1.5 Pro prompt"
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

resource "google_logging_metric" "prompt_gemini_1_5_pro_elapsedtime_metric" {
  name    = "prompt_gemini_1_5_pro_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\" AND jsonPayload.model.name: \"gemini-1.5-pro\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Gemini 1.5 Pro prompt elapsed time"
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
    priority = "EXTRACT(jsonPayload.priority)"
  }
}

resource "google_logging_metric" "prompt_burndown_metric" {
  name    = "prompt_burndown_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Prompt::multi_modal_predict\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Prompt burndown rate"
    labels {
      key         = "model"
      value_type  = "STRING"
      description = "Model"
    }
    labels {
      key         = "step"
      value_type  = "STRING"
      description = "Step"
    }
    labels {
      key         = "priority"
      value_type  = "STRING"
      description = "The priority"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.burndown_rate)"
  bucket_options {
    explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    model    = "EXTRACT(jsonPayload.model.name)",
    step     = "EXTRACT(jsonPayload.step)",
    priority = "EXTRACT(jsonPayload.priority)"
  }
}