resource "google_pubsub_topic" "log_export_topic" {
  name    = "log-export-topic"
  project = var.app_project_id

  labels = var.labels
}

resource "google_logging_project_sink" "log_export_sink" {
  name    = "log-export-sink"
  project = var.app_project_id

  destination = "pubsub.googleapis.com/projects/${var.app_project_id}/topics/${google_pubsub_topic.log_export_topic.name}"
  filter      = "resource.type!=\"audited_resource\" AND severity>=INFO"

  # Ensure the sink has the necessary permissions to write to the Pub/Sub topic
  unique_writer_identity = true

  depends_on = [google_pubsub_topic.log_export_topic]
}

resource "google_pubsub_topic_iam_binding" "log_export_topic_writer" {
  project = var.app_project_id
  topic   = google_pubsub_topic.log_export_topic.name
  role    = "roles/pubsub.publisher"
  members = [
    google_logging_project_sink.log_export_sink.writer_identity
  ]

  depends_on = [
    google_pubsub_topic.log_export_topic,
    google_logging_project_sink.log_export_sink
  ]
}

# resource "google_pubsub_subscription" "log_export_subscription" {
#   name  = "log-export-subscription"
#   topic = google_pubsub_topic.log_export_topic.id
#   project = var.app_project_id  

#   ack_deadline_seconds = 600

#   push_config {
#     push_endpoint = "https://log-api.newrelic.com/log/v1?Api-Key=${var.newrelic_api_key}&format=gcp"
#   }

#   labels = var.labels

#   depends_on = [
#     google_pubsub_topic.log_export_topic,
#     google_logging_project_sink.log_export_sink
#   ]
# }
