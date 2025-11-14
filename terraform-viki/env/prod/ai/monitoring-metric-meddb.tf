resource "google_logging_metric" "extraction_meddb_adapter_metric" {
  name    = "extraction_meddb_adapter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"EXTRACTION::MEDDB::SEARCH::ADAPTER\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "MedDB Adapter"
    labels {
      key         = "app_id"
      value_type  = "STRING"
      description = "AppID"
    }
    labels {
      key         = "catalog"
      value_type  = "STRING"
      description = "Catalog"
    }    
    labels {
      key         = "adapter"
      value_type  = "STRING"
      description = "Adapter"
    }
  }
  label_extractors = {
    app_id = "EXTRACT(jsonPayload.app_id)",
    catalog    = "EXTRACT(jsonPayload.catalog)",    
    adapter    = "EXTRACT(jsonPayload.adapter)"
  }
}

resource "google_logging_metric" "extraction_meddb_circuitbreaker_metric" {
  name    = "extraction_meddb_circuitbreaker_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"EXTRACTION::MEDDB::SEARCH::CIRCUITBREAKER\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "MedDB Circuit Breaker"
    labels {
      key         = "app_id"
      value_type  = "STRING"
      description = "AppID"
    }
    labels {
      key         = "catalog"
      value_type  = "STRING"
      description = "Catalog"
    }
    labels {
      key         = "circuit_state"
      value_type  = "STRING"
      description = "Circuit State"
    }
    labels {
      key         = "adapter"
      value_type  = "STRING"
      description = "Adapter"
    }
  }
  label_extractors = {
    app_id = "EXTRACT(jsonPayload.app_id)",
    catalog    = "EXTRACT(jsonPayload.catalog)",
    circuit_state  = "EXTRACT(jsonPayload.circuit_state)",
    adapter    = "EXTRACT(jsonPayload.adapter)"
  }
}


resource "google_logging_metric" "extraction_meddb_adapter_elapsedtime_metric" {
  name    = "extraction_meddb_adapter_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"EXTRACTION::MEDDB::ELAPSEDTIME\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Extraction MedDB Adapter Elapsed Time"
    labels {
      key         = "adapter"
      value_type  = "STRING"
      description = "Adapter"
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
    adapter = "EXTRACT(jsonPayload.adapter)"    
  }
}