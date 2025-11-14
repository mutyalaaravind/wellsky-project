data "google_project" "project" {
  project_id = var.app_project_id
}

data "google_project" "mgmt-project" {
  project_id = var.mgmt_project_id
}

data "google_project" "app-project" {
  project_id = var.app_project_id
}
