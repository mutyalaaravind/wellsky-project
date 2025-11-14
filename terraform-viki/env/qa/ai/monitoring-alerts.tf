
module "gcp_alert_notification_channel_email" {
  source         = "git@github.com:mediwareinc/terraform-gcp-alert.git//modules/notification_channel/email?ref=v0.12.0"
  project_id     = var.app_project_id
  contact_emails = var.alert_notification_channel_emails
  labels         = var.labels
}