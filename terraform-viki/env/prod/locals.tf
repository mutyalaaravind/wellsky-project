locals {
  name_prefix        = "${var.env}-viki"
  provision_mgmt     = var.env == "dev" || var.env == "prod"
  cloud_run_base_url = "${var.app_project_id}.${var.region}.run.app"

  # # If we are in 'dev' or 'prod', get the email from the module that creates it.
  # # Otherwise, get the email from the data source that looks it up.
  # ado_deployer_sa_email = local.provision_mgmt ? module.ado_workload_identity_federation[0].service_account_email : data.google_service_account.ado_deployer_from_mgmt[0].email
}
