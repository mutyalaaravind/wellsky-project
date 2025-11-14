locals {
  artifact_reader_map = merge(
    # Create map entries for the readers from your variables.
    { for reader in var.artifact_registry_additional_service_account_readers : reader => reader },

    # Create a map entry for the hardcoded Cloud Run agent.
    { "cloud_run_agent" = "service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com" },

    # Conditionally create a map entry for the ADO deployer.
    # The key "ado_deployer_sa" is static. The value can be resolved at apply time.
    local.provision_mgmt ? { "ado_deployer_sa" = module.ado_workload_identity_federation[0].service_account_email } : {}
  )

  # Adding "-new" suffix here to bypass an issue where ado_workload_identity_federation was recreated, but creation failed because of soft deletes
  ado_name_prefix = "${local.name_prefix}-new"
  pool_id         = "${local.ado_name_prefix}-ado-mediwareis"
  sa_email        = "${local.pool_id}@${var.mgmt_project_id}.iam.gserviceaccount.com"
  sa_id           = "projects/${var.mgmt_project_id}/serviceAccounts/${local.sa_email}"
  ado_subject     = "sc://mediwareis/VIKI/${var.mgmt_project_id}"
}

# set up and defined the workload identity federation for Azure DevOps
module "ado_workload_identity_federation" {
  count  = local.provision_mgmt ? 1 : 0
  source = "git@github.com:mediwareinc/terraform-epe-modules.git//ado-workload-identity-federation?ref=1.1.2"

  project_id = var.mgmt_project_id

  name_prefix = local.ado_name_prefix

  ado = {
    service_connection_name = var.mgmt_project_id
  }

  labels = var.labels
}

resource "google_service_account_iam_member" "ado_workload_identity_user" {
  count = local.provision_mgmt ? 1 : 0

  service_account_id = local.sa_id
  role               = "roles/iam.workloadIdentityUser"
  member             = "principal://iam.googleapis.com/projects/${data.google_project.mgmt-project.number}/locations/global/workloadIdentityPools/${local.pool_id}/subject/${local.ado_subject}"

  depends_on = [
    module.ado_workload_identity_federation
  ]
}

data "google_service_account" "ado_deployer_from_mgmt" {
  count = !local.provision_mgmt && var.ado_source_sa_account_id != "" ? 1 : 0

  account_id = var.ado_source_sa_account_id
  project    = var.mgmt_project_id
}

resource "google_project_iam_member" "ado_deployer_viewer" {
  provider = google.app
  project  = var.app_project_id

  role   = "roles/viewer"
  member = "serviceAccount:${local.ado_deployer_sa_email}"
}

# grant ADO Cloud Run Developer role
resource "google_project_iam_member" "ado_cloud_run_developer" {
  count   = local.provision_mgmt ? 1 : 0
  project = var.mgmt_project_id

  role   = "roles/run.developer"
  member = "serviceAccount:${local.ado_deployer_sa_email}"
}

resource "google_project_iam_member" "ado_service_account_user" {
  count   = local.provision_mgmt ? 1 : 0
  project = var.mgmt_project_id

  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${local.ado_deployer_sa_email}"
}

resource "google_project_iam_member" "storage_objectCreator" {
  count   = local.provision_mgmt ? 1 : 0
  project = var.mgmt_project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${local.ado_deployer_sa_email}"
}

# resource "google_artifact_registry_repository_iam_member" "ado_docker_artifact_registry_writers" {
#   count = local.provision_mgmt ? 1 : 0

#   repository = google_artifact_registry_repository.images[0].name
#   location   = google_artifact_registry_repository.images[0].location
#   project    = var.mgmt_project_id

#   role       = "roles/artifactregistry.writer"
#   member     = "serviceAccount:${local.ado_deployer_sa_email}"

#   depends_on = [google_project_iam_member.artifactRegistry_admin]
# }

# resource "google_artifact_registry_repository_iam_member" "ado_docker_artifact_registry_readers" {
#   for_each = local.artifact_reader_map

#   repository = google_artifact_registry_repository.images[0].name
#   location   = google_artifact_registry_repository.images[0].location
#   project    = var.mgmt_project_id
#   role       = "roles/artifactregistry.reader"
#   member     = "serviceAccount:${each.value}"
#   depends_on = [google_project_iam_member.artifactRegistry_admin]
# }
