module "rcmedge_sa" {
  source       = "terraform.wellsky.net/wellsky/service-account/gcp"
  account_id   = "rcmedge-sa"
  display_name = "RCM Edge Service Account"
  project_id   = var.app_project_id
  labels       = var.labels
  roles = [
    "roles/run.invoker",
    "roles/storage.objectViewer",
    "roles/storage.objectAdmin",
    "roles/cloudtasks.enqueuer",
    "roles/cloudtasks.viewer",
    "roles/aiplatform.admin",
    "roles/cloudtrace.agent",
    "roles/logging.logWriter",
    "roles/datastore.user",
    "roles/pubsub.publisher",
    "roles/eventarc.eventReceiver",
    "roles/iam.serviceAccountTokenCreator",
    "roles/documentai.admin"
  ]
}

#service-282645842516@gcp-sa-aiplatform-re.iam.gserviceaccount.com

data "google_project" "gcp_project" {
  project_id = var.app_project_id
} 


resource "google_project_iam_member" "rcmedge_reasoning_engine_datastore_user" {
  project = var.app_project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:service-${data.google_project.gcp_project.number}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
}