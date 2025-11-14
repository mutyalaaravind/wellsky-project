resource "google_logging_metric" "orchestration_attachment_event_metric" {
  name    = "orchestration_attachmentevent_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Received raw message from eventarc\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event"
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
  }
}

resource "google_logging_metric" "orchestration_attachment_event_accept_metric" {
  name    = "orchestration_attachmentevent_accept_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"Creating new HostAttachmentAggregate\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Attachment event: Accept"
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
  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    source = "EXTRACT(jsonPayload.storage_metadata.SOURCE)",
  }
}