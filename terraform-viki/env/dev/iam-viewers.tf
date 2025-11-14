
resource "google_project_iam_member" "monitoring_dashboard_viewer" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/monitoring.dashboardViewer"
  member   = each.value
}

resource "google_project_iam_member" "monitoring_log_viewer" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/logging.viewer"
  member   = each.value
}

resource "google_project_iam_member" "support_users_monitoring_viewer" {
  for_each = var.support_users
  project  = var.app_project_id
  role     = "roles/monitoring.viewer"
  member   = each.value
}

resource "google_project_iam_member" "support_users_logging_viewer" {
  for_each = var.support_users
  project  = var.app_project_id
  role     = "roles/logging.viewer"
  member   = each.value
}

resource "google_project_iam_member" "support_users_bigquery_job_user" {
  for_each = var.support_users
  project  = var.app_project_id
  role     = "roles/bigquery.jobUser"
  member   = each.value
}
