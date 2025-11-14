# module "newrelic-gcp-cloud-integrations" {
#   source = "github.com/newrelic/terraform-provider-newrelic//examples/modules/cloud-integrations/gcp"

#   account_id     = var.newrelic_account_id
#   name                    = "viki-${var.env}"
#   gcp_service_account_id      = var.newrelic_service_account_id
#   gcp_project_id              = var.app_project_id
#   api_key                     = var.newrelic_api_key
# }

# resource "newrelic_cloud_gcp_link_account" "gcp_account" {
#   account_id = var.newrelic_account_id
#   project_id = var.app_project_id
#   name       = "${var.env}-newrelic"
# }