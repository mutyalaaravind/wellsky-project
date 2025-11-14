// Allow Cloud Run Service Agent to pull GAR image from mgmt project
// Ensure that Cloud Run Service Account exists
resource "google_project_service_identity" "cloud_run_identity" {
  provider = google-beta
  project  = var.app_project_id
  service  = google_project_service.run[var.app_project_id].service
}
// Bind Cloud Run Service Account
resource "google_artifact_registry_repository_iam_member" "gar_member" {
  project    = var.mgmt_project_id
  location   = var.region
  repository = "images"
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_project_service_identity.cloud_run_identity.email}"
}

// Ensure that default Cloud Build Service Account exists
resource "google_project_service_identity" "cloud_build_identity" {
  provider = google-beta
  project  = var.mgmt_project_id
  service  = google_project_service.cloudbuild.service
}

// Allow Cloud Run to call iam.serviceAccounts.getAccessToken to get access token for Cloud Run services
resource "google_project_iam_member" "token_creator" {
  project = var.app_project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_project_service_identity.cloud_run_identity.email}"
}

// Allow PubSub to create identity tokens (required for Eventarc):
resource "google_project_service_identity" "pubsub_identity" {
  provider = google-beta
  project  = var.app_project_id
  service  = google_project_service.pubsub[var.app_project_id].service
}
resource "google_project_iam_member" "pubsub_token_creator" {
  project = var.app_project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_project_service_identity.pubsub_identity.email}"
}

resource "google_project_iam_member" "health_cloud_service_account_permissions" {
  project = var.app_project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-healthcare.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "discovery_engine_service_account_permissions" {
  project = var.app_project_id
  role    = "roles/healthcare.fhirStoreAdmin"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-discoveryengine.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "healthcare_service_big_query_account_permissions" {
  project = var.app_project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-healthcare.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "healthcare_service_big_query_job_user_account_permissions" {
  project = var.app_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-healthcare.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "alloydb_sa_gcs_permissions" {
  project = var.app_project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-alloydb.iam.gserviceaccount.com"
}

# resource "google_artifact_registry_repository_iam_member" "prod_tfe_agent_gar_member" {
#   count      = var.env == "dev" ? 1 : 0
#   project    = var.mgmt_project_id
#   location   = var.region
#   repository = google_artifact_registry_repository.images[0].name
#   role       = "roles/artifactregistry.reader"
#   member     = "serviceAccount:tfe-agent@${replace(var.mgmt_project_id, "-dev-", "-prod-")}.iam.gserviceaccount.com"
# }

resource "google_project_iam_member" "artifactRegistry_admin" {
  project = var.mgmt_project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:terraform-agent@${var.mgmt_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "artifactRegistry_writer" {
  project = var.mgmt_project_id
  role    = "roles/writer"
  member  = "serviceAccount:terraform-agent@${var.mgmt_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "terraform_agent_bigquery_admin" {
  project = var.app_project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:terraform-agent@${var.mgmt_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "tfe_agent_bigquery_admin" {
  project = var.app_project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:tfe-agent@${var.mgmt_project_id}.iam.gserviceaccount.com"
}
