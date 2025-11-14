resource "google_artifact_registry_repository" "images" {
  # Cloud run images
  count = local.provision_mgmt ? 1 : 0

  project       = var.mgmt_project_id
  location      = var.region
  repository_id = "images"
  description   = "VIKI images"
  format        = "DOCKER"

  depends_on = [google_project_service.artifactregistry]
}

module "static_bucket" {
  count         = local.provision_mgmt ? 1 : 0
  source        = "git@github.com:mediwareinc/terraform-gcp-bucket.git?ref=v0.3.3"
  project_id    = var.mgmt_project_id
  name          = "viki-static-${var.env}"
  location      = var.region
  storage_class = "REGIONAL"
  labels        = var.labels
  force_destroy = true
  bucket_admins = [module.github_builder[0].iam_email]
  /* bucket_viewers = toset() */
}

# // Allow prod TFE agent to pull artifacts from dev TFE (for promotion)
# resource "google_artifact_registry_repository_iam_member" "prod_tfe_agent_gar_member" {
#   for_each   = var.env == "dev" ? toset(concat(var.app_project_ids, var.dmz_project_ids)) : toset([])
#   project    = var.mgmt_project_id
#   location   = var.region
#   repository = "images"
#   role       = "roles/artifactregistry.reader"
#   member     = "serviceAccount:tfe-agent@${replace(var.mgmt_project_id, "-dev-", "-prod-")}.iam.gserviceaccount.com"
# }
