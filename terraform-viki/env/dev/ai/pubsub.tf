resource "google_pubsub_topic" "external_files_topic" {
  name    = "external-files-topic"
  project = var.app_project_id
  labels  = var.labels
}

resource "google_pubsub_topic" "orchestraction_extraction_topic" {
  name    = "orchestraction-extraction-topic"
  project = var.app_project_id
  labels  = var.labels
}

resource "google_pubsub_subscription" "orchestration_extraction_topic_subscription" {
  name    = "orchestraction-extraction-topic-subscription"
  topic   = google_pubsub_topic.orchestraction_extraction_topic.id
  project = var.app_project_id

  ack_deadline_seconds = 600

  labels = var.labels

  push_config {
    push_endpoint = format("%s/%s", module.paperglass_events.url, "eventarc/pubsub/json")

    # attributes = {
    #   x-goog-version = "v1"
    # }
  }
  enable_message_ordering = true
}

resource "google_pubsub_topic" "medication_extraction_v4_topic" {
  name                       = "medication-extraction-v4-topic-${var.env}"
  project                    = var.app_project_id
  labels                     = var.labels
  message_retention_duration = "604800s" # Retain messages for 7 days (7 * 24 * 60 * 60 seconds)
}

resource "google_pubsub_subscription" "medication_extraction_v4_topic_subscription" {
  name    = "medication-extraction-v4-topic-subscription"
  topic   = google_pubsub_topic.medication_extraction_v4_topic.id
  project = var.app_project_id

  ack_deadline_seconds = 600

  labels = var.labels

  push_config {
    push_endpoint = format("%s/%s", module.medication_extraction_api.url, "run_extraction_pubsub")

    # attributes = {
    #   x-goog-version = "v1"
    # }
  }
  enable_message_ordering = true
}

resource "google_pubsub_topic" "paperglass_integration_topic" {
  name                       = "paperglass-integration-topic-${var.env}"
  project                    = var.app_project_id
  labels                     = var.labels
  message_retention_duration = "604800s" # Retain messages for 7 days (7 * 24 * 60 * 60 seconds)
}

resource "google_pubsub_subscription" "paperglass_integration_topic_subscription" {
  name    = "paperglass-integration-topic-subscription"
  topic   = google_pubsub_topic.paperglass_integration_topic.id
  project = var.app_project_id

  ack_deadline_seconds = 600

  labels = var.labels

  push_config {
    push_endpoint = format("%s/%s", module.paperglass_events.url, "eventarc/medications")

    # attributes = {
    #   x-goog-version = "v1"
    # }
  }
  enable_message_ordering = true
}

resource "google_pubsub_topic" "medication_extraction_doc_status_topic" {
  name                       = "medication-extraction-doc-status-topic-${var.env}"
  project                    = var.app_project_id
  labels                     = var.labels
  message_retention_duration = "604800s" # Retain messages for 7 days (7 * 24 * 60 * 60 seconds)
}

resource "google_pubsub_subscription" "medication_extraction_doc_status_topic_subscription" {
  name    = "medication-extraction-doc-status-topic-subscription"
  topic   = google_pubsub_topic.medication_extraction_doc_status_topic.id
  project = var.app_project_id

  ack_deadline_seconds = 600

  labels = var.labels

  push_config {
    push_endpoint = format("%s/%s", module.medication_extraction_api.url, "update_status_pubsub")

    # attributes = {
    #   x-goog-version = "v1"
    # }
  }
  enable_message_ordering = true
}

resource "google_pubsub_topic_iam_binding" "binding" {
  project = var.app_project_id
  topic   = google_pubsub_topic.external_files_topic.id
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:${var.hhh_gcs_sa_email}"]
}

resource "google_pubsub_topic" "event_orchestration_complete_topic" {
  name                       = "event-orchestration-complete-topic-${var.env}"
  project                    = var.app_project_id
  labels                     = var.labels
  message_retention_duration = "604800s" # Retain messages for 7 days (7 * 24 * 60 * 60 seconds)
}

resource "google_pubsub_topic" "event_medication_publish_topic" {
  name                       = "event-medication-publish-topic-${var.env}"
  project                    = var.app_project_id
  labels                     = var.labels
  message_retention_duration = "604800s" # Retain messages for 7 days (7 * 24 * 60 * 60 seconds)
}

resource "google_pubsub_topic" "command_scheduledwindow_1_topic" {
  name                       = "command-scheduledwindow-1-topic-${var.env}"
  project                    = var.app_project_id
  labels                     = var.labels
  message_retention_duration = "604800s" # Retain messages for 7 days (7 * 24 * 60 * 60 seconds)
}

output "external_files_topic_id" {
  value = google_pubsub_topic.external_files_topic.id
}
output "event_orchestration_complete_topic_id" {
  value = google_pubsub_topic.event_orchestration_complete_topic.id
}