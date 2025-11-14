resource "google_firebase_project" "firebase" {
  provider = google-beta
  project  = var.app_project_id

  depends_on = [google_project_service.firebase]
}

resource "google_project_service" "component_firebase_hosting_api" {
  for_each = toset([var.app_project_id, var.mgmt_project_id])
  project  = each.value
  service  = "firebasehosting.googleapis.com"

  disable_on_destroy         = false
  disable_dependent_services = true

  depends_on = [google_project_service.firebase]
}

resource "google_firebase_hosting_site" "web_components_site" {
  provider = google-beta.app # note aliased app provider
  project  = var.app_project_id
  site_id  = var.web_components_site_id

  depends_on = [
    google_project_service.component_firebase_hosting_api,
    google_firebase_project.firebase
  ]
}

resource "google_project_iam_member" "builder_firebase_viewer" {
  count   = local.provision_mgmt ? 1 : 0
  project = var.app_project_id

  role   = "roles/firebase.viewer"
  member = "serviceAccount:${module.github_builder[0].email}"

  depends_on = [
    google_project_service.firebase,
    google_firebase_project.firebase
  ]
}

# resource "google_project_iam_member" "ado_deployer_firebase_admin" {
#   provider = google.app
#   project  = var.app_project_id
#   role     = "roles/firebasehosting.admin"
#   member   = "serviceAccount:${local.ado_deployer_sa_email}"
# }
