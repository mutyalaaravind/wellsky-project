// Create identity pool that can be used in GHA to push images to GAR in VIKI projects
// Adapted from https://github.com/mediwareinc/terraform-core-svcs/blob/294a5ffabb5ac21a7a2ee9b99e61ad4428bd4d3f/gcp/projects/development/_github.tf
//
// Docs & usage:
// https://registry.terraform.io/modules/terraform-google-modules/github-actions-runners/google/latest/submodules/gh-oidc

locals {
  github_sa_name  = "github-builder"
  github_sa_email = "${local.github_sa_name}@${var.mgmt_project_id}.iam.gserviceaccount.com"

  // List of GH repos in which GHA can use workload identity pool to authenticate in GCP (to push to VIKI GAR & static bucket)
  repos = [
    "mediwareinc/viki-ai",
    "mediwareinc/medispan-api",
    "mediwareinc/autoscribe",
  ]
}

module "github_builder" {
  count   = local.provision_mgmt ? 1 : 0
  source  = "terraform.wellsky.net/wellsky/service-account/gcp"
  version = "0.4.11"

  project_id   = var.mgmt_project_id
  account_id   = local.github_sa_name
  description  = "Service Account for use with GitHub"
  display_name = "GitHub Build Service Account"
  labels       = var.labels
  roles = [
    "roles/artifactregistry.writer",
    "roles/storage.objectUser",
  ]
}

module "github_oidc" {
  count   = local.provision_mgmt ? 1 : 0
  source  = "terraform-google-modules/github-actions-runners/google//modules/gh-oidc"
  version = "4.0.0"

  project_id  = var.mgmt_project_id
  pool_id     = "ci-cd"
  provider_id = "wellsky-github"

  sa_mapping = {
    # Grant access to repos.
    # We cannot define more than 1 here, so we define first only and then define the rest separately below.
    (module.github_builder[0].account_id) = {
      sa_name   = module.github_builder[0].id
      attribute = "attribute.repository/${slice(local.repos, 0, 1)[0]}"
    }
  }
}

resource "google_service_account_iam_member" "wif_sa_member" {
  for_each           = local.provision_mgmt ? toset(slice(local.repos, 1, length(local.repos))) : toset([])
  service_account_id = module.github_builder[0].id
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${module.github_oidc[0].pool_name}/attribute.repository/${each.value}"
}

// Do we need this?
module "github_builder_sa_grp_members" {
  count   = local.provision_mgmt ? 1 : 0
  source  = "terraform.wellsky.net/wellsky/service-account-grp-member/gcp"
  version = "0.2.1"

  service_accounts = [
    local.github_sa_email
  ]

  depends_on = [module.github_builder]
}
