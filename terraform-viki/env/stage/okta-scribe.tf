locals {
  # External App Registrations for Scribe
  scribe_app_registrations = {
    "pacf-wssc-suki" = {
      business_unit = "PACF"
      solution      = "WSSC - Suki"
      scopes = [
        "${local.namespace}.ai.transcription",
      ]
      accessors = [
        "user:brian.jerome@wellsky.com",
        "group:CLD-TeamPterodactyl@wellsky.com",
      ]
      create_jwks = true
    }
  }

  jwks = {
    for k, v in local.scribe_app_registrations : k => {
      kty = "RSA"
      kid = k
      e   = jsondecode(data.jwks_from_key.jwks[k].jwks)["e"]
      n   = jsondecode(data.jwks_from_key.jwks[k].jwks)["n"]
    } if v.create_jwks
  }
}

module "scribe_okta_service_apps" {
  source  = "terraform.wellsky.net/wellsky/service-app/okta"
  version = "2.1.2"

  for_each = local.scribe_app_registrations

  app_name = format("Scribe: %s %s - M2M (%s)", each.value.business_unit, each.value.solution, title(var.env))
}

module "scribe_okta_auth_server_policies" {
  source  = "terraform.wellsky.net/wellsky/auth-server-policy/okta"
  version = "2.1.1"

  for_each = local.scribe_app_registrations

  okta_auth_server_name  = module.okta_auth_server_v2.okta_auth_server.name
  policy_name            = format("%s.%s.%s.app.policy", lower(each.value.business_unit), replace(lower(each.value.solution), " ", ""), var.env)
  policy_desc            = format("Scribe %s %s Policy (%s)", each.value.business_unit, each.value.solution, var.env)
  policy_allowed_clients = [module.scribe_okta_service_apps[each.key].okta_service_app.id]
}

module "scribe_okta_auth_server_policy_rules" {
  source  = "terraform.wellsky.net/wellsky/auth-server-policy-rule/okta"
  version = "2.1.1"

  for_each = local.scribe_app_registrations

  grant_type_whitelist  = ["client_credentials"]
  okta_auth_server_name = module.okta_auth_server_v2.okta_auth_server.name
  policy_id             = module.scribe_okta_auth_server_policies[each.key].auth_server_policy.id

  access_token_lifetime_minutes  = 60
  refresh_token_lifetime_minutes = 3600
  refresh_token_window_minutes   = 3600

  rule_name       = format("%s.%s.%s.app.policy.rule", lower(each.value.business_unit), replace(lower(each.value.solution), " ", ""), var.env)
  scope_whitelist = each.value.scopes
  group_whitelist = ["EVERYONE"]
}

module "scribe_okta_services_client_credentials" {
  source  = "terraform.wellsky.net/wellsky/secret/gcp"
  version = "1.1.0"

  for_each = local.scribe_app_registrations

  project_id = var.app_project_id
  labels = merge(var.labels, {
    owner         = "enterprise"
    business-unit = "wsky"
    application   = "scribe"
    service       = "transcription"
  })

  name = format("Scribe_App_ClientCredentials_%s_%s", upper(each.value.business_unit), replace(replace(upper(each.value.solution), " ", ""), "-", "_"))
  secret_data = jsonencode({
    "client_id"     = module.scribe_okta_service_apps[each.key].okta_service_app.client_id
    "client_secret" = module.scribe_okta_service_apps[each.key].okta_service_app.client_secret
  })

  replication_regions = [var.region]

  accessors = each.value.accessors
  managers  = []
}

resource "tls_private_key" "scribe_rsa" {
  for_each = { for k, v in local.scribe_app_registrations : k => v if v.create_jwks == true }

  algorithm = "RSA"
  rsa_bits  = 4096
}

module "scribe_app_rsa_private_keys" {
  source  = "terraform.wellsky.net/wellsky/secret/gcp"
  version = "1.1.0"

  for_each = { for k, v in local.scribe_app_registrations : k => v if v.create_jwks == true }

  project_id = var.app_project_id
  labels = merge(var.labels, {
    owner         = "enterprise"
    business-unit = "wsky"
    application   = "scribe"
    service       = "transcription"
  })

  name        = format("Scribe_App_RSA_Private_Key_%s_%s", upper(each.value.business_unit), replace(replace(upper(each.value.solution), " ", ""), "-", "_"))
  secret_data = tls_private_key.scribe_rsa[each.key].private_key_pem

  replication_regions = [var.region]

  accessors = each.value.accessors
  managers  = []
}

module "scribe_app_rsa_public_keys" {
  source  = "terraform.wellsky.net/wellsky/secret/gcp"
  version = "1.1.0"

  for_each = { for k, v in local.scribe_app_registrations : k => v if v.create_jwks == true }

  project_id = var.app_project_id
  labels = merge(var.labels, {
    owner         = "enterprise"
    business-unit = "wsky"
    application   = "scribe"
    service       = "transcription"
  })

  name        = format("Scribe_App_RSA_Public_Key_%s_%s", upper(each.value.business_unit), replace(replace(upper(each.value.solution), " ", ""), "-", "_"))
  secret_data = tls_private_key.scribe_rsa[each.key].public_key_pem

  replication_regions = [var.region]

  accessors = each.value.accessors
  managers  = []
}

data "jwks_from_key" "jwks" {
  for_each = { for k, v in local.scribe_app_registrations : k => v if v.create_jwks == true }

  key = tls_private_key.scribe_rsa[each.key].private_key_pem
  kid = each.key
}

resource "okta_app_oauth" "scribe_oauth_apps" {
  for_each = { for k, v in local.scribe_app_registrations : k => v if v.create_jwks == true }

  label                      = "Skysense Scribe App - Oauth JWKS (${title(var.env)})"
  client_id                  = module.scribe_okta_service_apps[each.key].okta_service_app.client_id
  type                       = "service"
  status                     = "ACTIVE"
  token_endpoint_auth_method = "private_key_jwt"
  auto_key_rotation          = false
  grant_types                = ["client_credentials"]
  response_types             = ["token"]
  omit_secret                = true
  profile                    = null

  jwks {
    kty = local.jwks[each.key].kty
    kid = local.jwks[each.key].kid
    e   = local.jwks[each.key].e
    n   = local.jwks[each.key].n
  }
}

module "scribe_okta_oauth_app_jwks" {
  source  = "terraform.wellsky.net/wellsky/secret/gcp"
  version = "1.1.0"

  for_each = { for k, v in local.scribe_app_registrations : k => v if v.create_jwks == true }

  project_id = var.app_project_id
  labels = merge(var.labels, {
    owner         = "enterprise"
    business-unit = "wsky"
    application   = "scribe"
    service       = "transcription"
  })

  name        = format("Scribe_App_JWKS_%s_%s", upper(each.value.business_unit), replace(replace(upper(each.value.solution), " ", ""), "-", "_"))
  secret_data = data.jwks_from_key.jwks[each.key].jwks

  replication_regions = [var.region]

  accessors = each.value.accessors
  managers  = []
}


# HS Test Client for Scribe
module "scribe-hs-test-client" {
  source = "git@github.com:mediwareinc/terraform-okta-service-app.git?ref=v2.1.2"

  app_name = "Scribe: HS Test Client - M2M (${title(var.env)})"
}

module "scribe-scope-policy" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name  = module.okta_auth_server_v2.okta_auth_server.name
  policy_allowed_clients = [module.scribe-hs-test-client.okta_service_app.id]
  policy_desc            = "Scribe Scope Policy"
  policy_name            = "Scribe Scope Policy (${var.env})"

  depends_on = [module.okta_auth_server_v2]
}

module "scribe-scope-policy-rule" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["client_credentials"]
  okta_auth_server_name          = module.okta_auth_server_v2.okta_auth_server.name
  policy_id                      = module.scribe-scope-policy.auth_server_policy.id
  access_token_lifetime_minutes  = 60
  refresh_token_lifetime_minutes = 3600
  refresh_token_window_minutes   = 3600
  rule_name                      = "Scribe scope"
  scope_whitelist                = ["${local.namespace}.ai.transcription"]
  group_whitelist                = ["EVERYONE"]

  depends_on = [module.okta_auth_server_v2]
}

module "scribe-hs-test-client-secret" {
  source  = "terraform.wellsky.net/wellsky/secret/gcp"
  version = "1.1.0"

  project_id          = var.app_project_id
  name                = "scribe-human-services-app-credentials"
  replication_regions = [var.region]

  accessors = [
    "user:scott.carter@wellsky.com"
  ]
  managers = [
    "user:scott.carter@wellsky.com"
  ]

  secret_data = jsonencode({
    client_id     = module.scribe-hs-test-client.okta_service_app.client_id
    client_secret = module.scribe-hs-test-client.okta_service_app.client_secret
  })

  labels = merge(var.labels, {
    owner : "enterprise"
    business-unit : "wsky"
    environment : var.env

    application : "scribe"
    service : "transcription"
  })
}
