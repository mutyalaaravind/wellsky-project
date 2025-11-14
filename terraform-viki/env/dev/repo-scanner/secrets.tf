module "repo_scanner_secrets" {
  source = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  for_each = {
    github_token = {
      name        = "github-token",
      secret_data = "changeme"
    }
  }
  labels              = var.labels
  managers            = var.managers
  accessors           = concat(["serviceAccount:${module.code_scanner_sa.email}"], sort(var.managers)) # sort() is necessary to ensure that "managers" is a list (not a set) and is sorted
  name                = "repo-scanner-${var.env}-${each.value.name}"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data         = each.value.secret_data
  skip_secret_data    = false
}
