resource "google_healthcare_fhir_store" "ts_default" {
  name    = "viki-fhir-store"
  dataset = google_healthcare_dataset.ts_dataset.id
  version = "R4"


  enable_update_create = true

  labels = var.labels
}

resource "google_healthcare_dataset" "ts_dataset" {
  name     = "viki-dataset"
  location = "us-central1" # preview limitation with search & conversation
  project  = var.app_project_id
}