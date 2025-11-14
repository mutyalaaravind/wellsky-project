resource "google_project_service" "artifactregistry" {
  project = var.mgmt_project_id
  service = "artifactregistry.googleapis.com"
}
resource "google_project_service" "artifactregistry_app" {
  // Required for most Firebase extensions
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "artifactregistry.googleapis.com"
}

resource "google_project_service" "cloudbuild" {
  project = var.mgmt_project_id
  service = "cloudbuild.googleapis.com"
}

// https://cloud.google.com/iam/docs/service-accounts#locations
// > When a service account is in one project, and it accesses a resource in another project,
// > you usually must enable the API for that resource in both projects.
// > For example, if you have a service account in the project my-service-accounts
// > and a Cloud SQL instance in the project my-application,
// > you must enable the Cloud SQL API in both my-service-accounts and my-application.
resource "google_project_service" "appengine" {
  for_each           = toset([var.app_project_id])
  project            = each.value
  service            = "appengine.googleapis.com"
  disable_on_destroy = false
  disable_dependent_services = true
}

# This resource ONLY manages the core Firebase API for the management project.
# It ONLY runs when local.provision_mgmt is true.
resource "google_project_service" "firebase" {
  count = local.provision_mgmt ? 1 : 0

  project            = var.mgmt_project_id
  service            = "firebase.googleapis.com"
  disable_on_destroy = false
  disable_dependent_services = true
}

resource "google_project_service" "firebase_app" {
  count = local.provision_mgmt ? 1 : 0

  project            = var.app_project_id
  service            = "firebase.googleapis.com"
  disable_on_destroy = false
  disable_dependent_services = true
}

resource "google_project_service" "firebaseextensions" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "firebaseextensions.googleapis.com"

  disable_on_destroy         = false
  disable_dependent_services = true
}

resource "google_project_service" "firestore" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "firestore.googleapis.com"
}

resource "google_project_service" "pubsub" {
  for_each = toset([var.app_project_id, var.mgmt_project_id])
  project  = each.value
  service  = "pubsub.googleapis.com"
}

resource "google_project_service" "bigquery" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "bigquerystorage.googleapis.com"
}

resource "google_project_service" "apigateway" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "apigateway.googleapis.com"
}

resource "google_project_service" "translation" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "translate.googleapis.com"
}

resource "google_project_service" "run" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "run.googleapis.com"
}

resource "google_project_service" "cloud_scheduler_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "cloudscheduler.googleapis.com"
}

resource "google_project_service" "healthcare_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "healthcare.googleapis.com"
}

resource "google_project_service" "eventarc_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "eventarc.googleapis.com"
}

resource "google_project_service" "firestore_key_visualizer_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "firestorekeyvisualizer.googleapis.com"
}

resource "google_project_service" "cloud_billing_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "cloudbilling.googleapis.com"
}

resource "google_project_service" "storage_transfer_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "storagetransfer.googleapis.com"
}

resource "google_project_service" "dataflow_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "dataflow.googleapis.com"
}

resource "google_project_service" "datapipelines_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "datapipelines.googleapis.com"
}

resource "google_project_service" "ai_service" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "aiplatform.googleapis.com"
}

resource "google_project_service" "notebooks_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "notebooks.googleapis.com"
}

resource "google_project_service" "filestore_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "file.googleapis.com"
}

resource "google_project_service" "vision_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "vision.googleapis.com"
}

resource "google_project_service" "speech_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "speech.googleapis.com"
}

resource "google_project_service" "document_ai_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "documentai.googleapis.com"
}

resource "google_project_service" "worstations" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "workstations.googleapis.com"
}

resource "google_project_service" "cloud_tasks" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "cloudtasks.googleapis.com"
}

resource "google_project_service" "redis" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "redis.googleapis.com"
}

# Enable BigQuery Data Transfer API in both management and app projects
resource "google_project_service" "bigquery_data_transfer_api" {
  for_each = toset([var.mgmt_project_id, var.app_project_id])
  project  = each.value
  service  = "bigquerydatatransfer.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "alloydb_api" {
  for_each = toset([var.app_project_id])
  project  = each.value
  service  = "alloydb.googleapis.com"
}