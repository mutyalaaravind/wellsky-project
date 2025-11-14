module "ai_provisional_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v0.3.3"
  project_id    = var.app_project_id
  name          = "viki-ai-provisional-${var.env}"
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

module "scribe_temp_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v1.0.0"
  project_id    = var.app_project_id
  name          = "ltc-scribe-temp-${var.env}"
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

module "scribe_data_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v1.0.0"
  project_id    = var.app_project_id
  name          = "ltc-scribe-data-${var.env}"
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

module "scribe_issue_log_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v1.0.0"
  project_id    = var.app_project_id
  name          = "ltc-scribe-issue-logs-${var.env}"
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
module "meddb_bucket" {
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v1.0.0"
  project_id    = var.app_project_id
  name          = "meddb-${var.env}"
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


locals {
  subdomain         = "viki-${var.env}"
  dns_name_resolved = "${local.subdomain}.${data.google_dns_managed_zone.dns_zone.dns_name}"
  dns_zone          = "viki-${var.env}-dmz-pub"
}

data "google_dns_managed_zone" "dns_zone" {
  project = var.dmz_project_id
  name    = local.dns_zone
}

module "viki_service_frontend" {
  source               = "git@github.com:mediwareinc/terraform-gcp-website-bucket?ref=v0.1.3"
  bucket_location      = "US"
  bucket_objectadmins  = var.managers
  bucket_project_id    = var.dmz_project_id
  bucket_storageadmins = var.managers
  dns_name             = local.dns_name_resolved
  dns_project_id       = var.dmz_project_id
  dns_zone             = local.dns_zone
  name                 = "viki-service-frontend-${var.env}"
  labels               = var.labels
  enable_cdn           = true
  /* main_page = "index.html" */
  /* not_found_page = "404.html" */
}


