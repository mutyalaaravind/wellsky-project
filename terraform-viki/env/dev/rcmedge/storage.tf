module "rcmedge_bucket" {
  source        = "terraform.wellsky.net/wellsky/bucket/gcp"
  name          = "rcmedge-${var.env}-${var.app_project_id}"
  location      = var.region
  project_id    = var.app_project_id
  storage_class = "REGIONAL"
  force_destroy = true
  labels        = var.labels
  bucket_admins = [module.rcmedge_sa.iam_email]
  cors = [
    {
      max_age_seconds = 3600
      method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
      origin          = ["*"]
      response_header = ["*"]
    }
  ]
}