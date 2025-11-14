resource "google_logging_metric" "orchestration_attachment_event_metric" {
  name    = "orchestration_attachmentevent_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Received raw message from eventarc\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_missingmetadatafilter_metric" {
  name    = "orchestration_attachmentevent_missingmetadatafilter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"No attachment metadata found for\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Missing metadata"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_updatefilter_metric" {
  name    = "orchestration_attachmentevent_updatefilter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Skipping since its update/older event\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Update"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_whitelistfilter_metric" {
  name    = "orchestration_attachmentevent_whitelistfilter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"not in allow list.  Skipping\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Tenant whitelist"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_unsupportedtypefilter_metric" {
  name    = "orchestration_attachmentevent_unsupportedtypefilter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Unsupported file type for attachment\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Unsupported type"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_hostfileinactivefilter_metric" {
  name    = "orchestration_attachmentevent_hostfileinactivefilter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Host attachment is not active.  Deleting document\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Host attachment inactive"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_hostfileexistsfilter_metric" {
  name    = "orchestration_attachmentevent_hostfileexistsfilter_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Host attachment already imported.  Skipping\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Host attachment already exists"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_retrievalerror_metric" {
  name    = "orchestration_attachmentevent_retrievalerror_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Exception occurred during retrieval of external attachment\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event filter: Retrieval error"

    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    file_type = "EXTRACT(jsonPayload.file_type)",
  }
}

resource "google_logging_metric" "orchestration_attachment_event_accept_metric" {
  name    = "orchestration_attachmentevent_accept_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::ATTACHMENT::ACCEPTED\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event: Accept"

    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }
  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    file_type = "EXTRACT(jsonPayload.file_type)",
  }  
}

resource "google_logging_metric" "external_hhh_object_metadata" {
  name    = "external_hhh_object_metadata"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::STORAGE_METADATA::RETRIEVED\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH Document Source"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "source"
      value_type  = "STRING"
      description = "Source"
    }
    labels {
      key         = "file_type"
      value_type  = "STRING"
      description = "File Type"
    }    
  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    source = "EXTRACT(jsonPayload.storage_metadata.SOURCE)",
    file_type = "EXTRACT(jsonPayload.file_type)",
  }  
}