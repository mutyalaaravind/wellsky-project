locals {
  # Service account email construction for cross-project access
  terraform_agent_email = "terraform-agent@${var.mgmt_project_id}.iam.gserviceaccount.com"
  tfe_agent_email      = "tfe-agent@${var.mgmt_project_id}.iam.gserviceaccount.com"
}