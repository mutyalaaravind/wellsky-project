
module "entityextraction_context_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v1.0.0"
  project_id    = var.app_project_id
  name          = "entityextraction-context-${var.env}"
  location      = var.region
  storage_class = "REGIONAL"
  labels        = var.labels
  force_destroy = true
  bucket_admins = [module.ai_sa.iam_email]
  cors = [
    {
      max_age_seconds = 3600
      method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
      origin          = ["*"]
      response_header = ["*"]
    }
  ]
  /* bucket_viewers = toset() */
}