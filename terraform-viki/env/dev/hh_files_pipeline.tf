locals {
  service_account_email = ""
  external_pubsub_topic = "projects/viki-${var.env}-app-wsky/topics/external-files-topic"
}

resource "google_storage_bucket" "hh_files_bucket" {
  name                        = "hh-files"
  location                    = var.region
  project                     = var.app_project_id
  uniform_bucket_level_access = true
  default_event_based_hold    = true
  labels                      = var.labels
}

data "google_storage_project_service_account" "gcs_account" {
  project = var.app_project_id
}

resource "google_pubsub_topic_iam_binding" "binding" {
  project = var.app_project_id
  topic   = local.external_pubsub_topic
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"]
}

resource "google_storage_notification" "on_file_arrived_notification" {
  bucket         = google_storage_bucket.hh_files_bucket.name # replace with the existing bucket
  topic          = local.external_pubsub_topic
  payload_format = "JSON_API_V1"
  event_types    = ["OBJECT_FINALIZE", "OBJECT_METADATA_UPDATE"]
  # custom_attributes = {
  #     appId = "12345"
  # }
  depends_on = [google_pubsub_topic_iam_binding.binding]
}