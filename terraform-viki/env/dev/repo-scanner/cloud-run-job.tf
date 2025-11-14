locals {
  env_job = {
    REPO_URL="https://github.com/mediwareinc/viki-ai.git"
    GCS_OUTPUT_URL="gs://rcmedge-dev-viki-dev-app-wsky/repo-scanner"
    GCP_PROJECT_ID="viki-dev-app-wsky"
    GITHUB_USERNAME="vipin-wellsky"
    GCP_REGION="us-central1"
    REPO_BRANCH="main"
    ANALYSIS_TIMEOUT=300
    PROMPT_TEMPLATE="third_party_libraries.md"
  }
  env_secret = toset([
    {
      key     = "GITHUB_TOKEN",
      name    = module.repo_scanner_secrets["github_token"].name,
      version = "latest",
    },
  ])
}

module "repo-scanner-job" {
  source = "git@github.com:mediwareinc/terraform-gcp-cloudrun-jobv2.git?ref=v3.0.0"

  name         = "repo-scanner-job"
  image        = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/repo-scanner:${var.image_version}"
  args         = ["./scan_repo_v2.sh"]
  cpu_limit    = 4
  memory_limit = "12Gi"
  parallelism  = 1
  env_secrets = { for item in local.env_secret : item.key => item.name }
  envs     = local.env_job
  labels   = var.labels
  invokers = var.managers
  #   direct_vpc_subnetwork = var.subnet_internal
  #   direct_vpc_egress_setting = "ALL_TRAFFIC" # egress: ALL_TRAFFIC, PRIVATE_RANGES_ONLY
  vpc_access_connector = { "id" : var.vpc_connector, "egress" : "PRIVATE_RANGES_ONLY" } # egress: ALL_TRAFFIC, PRIVATE_RANGES_ONLY
  project_id           = var.app_project_id
  region               = var.region
  service_account      = module.code_scanner_sa.email
  timeout              = "43200s" # 12 hours
  deletion_protection  = false
  network_tags         = var.network_tags
  #depends_on      = [null_resource.build_cf_file_sync]
}