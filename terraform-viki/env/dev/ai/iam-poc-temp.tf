# THIS is temporary to allow Swathi's cloud function process access to the storage bucket
# DO NOT PROMOTE THIS TO QA!!!!

#gcf-v2-sources-145042810266-us-central1
resource "google_storage_bucket_iam_member" "swathi_temp_storage_admin" {
  bucket = "gcf-v2-sources-145042810266-us-central1"
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:145042810266-compute@developer.gserviceaccount.com"
}