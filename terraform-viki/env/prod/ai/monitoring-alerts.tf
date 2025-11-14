
module "gcp_alert_notification_channel_email" {
  source         = "git@github.com:mediwareinc/terraform-gcp-alert.git//modules/notification_channel/email?ref=v0.12.0"
  project_id     = var.app_project_id
  contact_emails = var.alert_notification_channel_emails
  labels = var.labels
}

# resource "google_monitoring_alert_policy" "pipeline_pt_exceeded_alert" {
#   display_name = "Vertex AI: Character Throughput PT Quota Exceeded"
#   combiner     = "OR"
#   notification_channels = ["projects/viki-prod-app-wsky/notificationChannels/5997950230120564708"]

#   conditions {
#     display_name = "Vertex AI: Character Throughput PT Quota Exceeded"
#     condition_threshold {
#       filter          = "resource.type = \"aiplatform.googleapis.com/PublisherModel\" AND resource.labels.model_user_id = \"gemini-1.5-flash-002\" AND metric.type = \"aiplatform.googleapis.com/publisher/online_serving/consumed_throughput\""
#       comparison      = "COMPARISON_GT"
#       threshold_value = 215000
#       duration        = "0s"      

#       aggregations {
#         alignment_period     = "60s"
#         cross_series_reducer = "REDUCE_SUM"
#         per_series_aligner   = "ALIGN_RATE"
#         group_by_fields = [
#               "metric.label.request_type",
#               "resource.label.model_user_id"]        
#       }
#     }
#   }

#   documentation {    
#     content  = "## Viki Vertex AI PT quota exceeded\n\nViki PT quota of 215kchar/s exceeded.  Overflow will be absorbed by Vertex AI shared which can handle ~100kchar/s"
#     mime_type = "text/markdown"
#   }

#   user_labels = var.labels

#   alert_strategy {
#     auto_close = "1800s"    
#     # notification_rate_limit {
#     #   period = "60s"
#     # }
#   }  
# }