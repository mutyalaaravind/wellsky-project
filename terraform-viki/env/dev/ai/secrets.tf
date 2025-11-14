module "secret" {
  source = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  for_each = {
    medispan_client_id = {
      name        = "medispan-client-id",
      secret_data = "changeme",
    },
    medispan_client_secret = {
      name        = "medispan-client-secret",
      secret_data = "changeme",
    },
    okta_client_secret = {
      name        = "okta-client-secret",
      secret_data = "changeme",
    },
    okta_api_token = {
      name        = "okta-api-token",
      secret_data = "changeme",
    },
    hhh_attachments_client_secret = {
      name        = "hhh-attachments-client-secret",
      secret_data = "changeme",
    },
    sharepoint_client_id = {
      name        = "sharepoint_client_id",
      secret_data = "changeme"
    },
    sharepoint_client_secret = {
      name        = "sharepoint_client_secret",
      secret_data = "changeme"
    }
  }
  labels              = var.labels
  managers            = var.managers
  accessors           = concat(["serviceAccount:${local.ai_sa_email}"], sort(var.managers)) # sort() is necessary to ensure that "managers" is a list (not a set) and is sorted
  name                = "viki-${var.env}-${each.value.name}"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data         = each.value.secret_data
  skip_secret_data    = false
}
