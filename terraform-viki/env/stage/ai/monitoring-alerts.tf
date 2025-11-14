
module "gcp_alert_notification_channel_email" {
  source         = "git@github.com:mediwareinc/terraform-gcp-alert.git//modules/notification_channel/email?ref=v0.12.0"
  project_id     = var.app_project_id
  contact_emails = var.alert_notification_channel_emails
  labels         = var.labels
}

# resource "google_monitoring_alert_policy" "pipeline_success_elapsedtime_metric_alert" {
#   display_name = "Pipeline Success Elapsed Time Alert"
#   combiner     = "OR"
#   notification_channels = [module.gcp_alert_notification_channel_email.notification_channel_id]

#   conditions {
#     display_name = "Pipeline Success Elapsed Time Condition"
#     condition_threshold {
#       filter          = "metric.type=\"logging.googleapis.com/user/pipeline_success_elapsedtime_metric\""
#       comparison      = "COMPARISON_GT"
#       threshold_value = 500
#       duration        = "0s"

#       aggregations {
#         alignment_period     = "60s"
#         per_series_aligner   = "ALIGN_MEAN"
#       }
#     }
#   }

#   documentation {
#     content = "Alert if the pipeline success elapsed time exceeds 3000."
#     mime_type = "text/markdown"
#   }

#   user_labels = var.labels

#   alert_strategy {
#     notification_rate_limit {
#       period = "300s"
#     }
#   }
# }