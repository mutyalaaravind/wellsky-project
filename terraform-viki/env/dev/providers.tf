provider "google" {
  project = var.mgmt_project_id
}

provider "google-beta" {
  project = var.mgmt_project_id
}

provider "okta" {
  org_name  = var.okta_org_name
  base_url  = var.okta_base_url
  api_token = var.okta_api_token
}

provider "newrelic" {
  account_id = var.newrelic_account_id
  api_key    = var.newrelic_api_key
  region     = "US"
}

# Aliased providers for the app project
provider "google" {
  project = var.app_project_id
  alias   = "app" # app vs mgmt default from above
}

provider "google-beta" {
  project = var.app_project_id
  alias   = "app" # app vs mgmt default from above
}