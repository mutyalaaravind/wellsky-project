# Grant AI Platform service account access to the admin bucket
resource "google_storage_bucket_iam_member" "admin_bucket_vertex_ai_access" {
  bucket = module.admin_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:service-${data.google_project.app_project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}