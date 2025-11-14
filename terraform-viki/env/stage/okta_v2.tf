locals {
  auth_server_name_v2 = "viki-${var.env}-v2"
  namespace_v2        = "api.wellsky.viki"
  okta_scopes_v2 = {
    transcription   = "${local.namespace_v2}.ai.transcription",   # VIKI AI autoscribe APIs
    form-completion = "${local.namespace_v2}.ai.form-completion", # VIKI AI form completion APIs
    nlparse         = "${local.namespace_v2}.ai.nlparse",         # VIKI AI nlparse APIs
    paperglass      = "${local.namespace_v2}.ai.paperglass",      # VIKI AI hhh APIs
  }
}

module "okta_auth_server_v2" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server?ref=v1.8.8"

  auth_server_audience = var.okta_service_audience
  auth_server_desc     = "VIKI Auth Server V2 (${var.env})"
  auth_server_name     = local.auth_server_name_v2
}

module "okta_scopes_v2" {
  for_each = local.okta_scopes_v2

  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-scope?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server_v2.okta_auth_server.name
  scope_name            = each.value
  scope_consent         = "IMPLICIT"

  depends_on = [module.okta_auth_server_v2]
}

# module "okta_auth_server_policy_demo_v2" {
#   // Policy for developer login into Demo
#   source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

#   okta_auth_server_name = module.okta_auth_server_v2.okta_auth_server.name
#   policy_allowed_clients = [
#     module.okta_demo_spa_v2.okta_spa_app.client_id,
#   ]
#   policy_desc = "Allows developers to sign in to Demo"
#   policy_name = "AI Developer Policy (${var.env})"

#   depends_on = [module.okta_auth_server_v2]
# }

# module "okta_auth_server_policy_testapp_v2" {
#   // Policy for TestApp
#   source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

#   okta_auth_server_name = module.okta_auth_server_v2.okta_auth_server.name
#   policy_allowed_clients = [
#     module.okta_test_app_v2.okta_service_app.client_id,
#   ]
#   policy_desc = "Allows TestApp to use AI APIs"
#   policy_name = "AI TestApp Policy (${var.env})"

#   depends_on = [module.okta_auth_server_v2]
# }

# module "okta_auth_server_policy_rule_demo_v2" {
#   // Allow developer to login into Demo
#   source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

#   grant_type_whitelist           = ["authorization_code"]
#   okta_auth_server_name          = module.okta_auth_server_v2.okta_auth_server.name
#   policy_id                      = module.okta_auth_server_policy_demo_v2.auth_server_policy.id
#   access_token_lifetime_minutes  = 1440
#   refresh_token_lifetime_minutes = 86400
#   refresh_token_window_minutes   = 86400
#   rule_name                      = "AI Demo SPA"
#   scope_whitelist                = ["openid", "email", "profile", local.okta_scopes.transcription, local.okta_scopes.form-completion]

#   depends_on = [module.okta_auth_server_v2]
# }

# module "okta_auth_server_policy_rule_testapp_v2" {
#   // Allow TestApp to call AI APIs
#   source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

#   grant_type_whitelist           = ["client_credentials"]
#   okta_auth_server_name          = module.okta_auth_server_v2.okta_auth_server.name
#   policy_id                      = module.okta_auth_server_policy_testapp_v2.auth_server_policy.id
#   access_token_lifetime_minutes  = 60
#   refresh_token_lifetime_minutes = 3600
#   refresh_token_window_minutes   = 3600
#   rule_name                      = "Applications that call AI APIs"
#   scope_whitelist                = [local.okta_scopes.transcription, local.okta_scopes.form-completion]

#   depends_on = [module.okta_auth_server_v2]
# }

// Naming convention:
// <ProductName> <MicroserviceName> <TenantName?> Client<BusinessUnit <Env>>
// E. g. for app that is used by ACMEHealth (external product) to call FakeHub APIs (internal product):
// FakeHub ACMEHealth Client(Payer Dev)

# module "okta_demo_spa_v2" {
#   source = "git@github.com:mediwareinc/terraform-okta//okta-spa-app?ref=v1.9.0"

#   app_name                      = "AI Demo Client V2(VIKI ${title(var.env)})"
#   app_client_id                 = "${local.namespace}.${var.env}.demo-v2"
#   app_redirect_uris             = var.demo_redirect_uris
#   app_post_logout_redirect_uris = var.demo_trusted_origins
#   app_grant_types               = ["authorization_code", "refresh_token"]
#   app_status                    = "ACTIVE"
#   trusted_origin_urls           = var.demo_trusted_origins
#   trusted_origin_scopes         = ["CORS", "REDIRECT"]
# }

# module "okta_test_app_v2" {
#   source = "git@github.com:mediwareinc/terraform-okta//okta-service-app?ref=v1.8.8"

#   app_name      = "AI TestApp Client V2(VIKI ${title(var.env)})"
#   app_client_id = "${local.namespace}.${var.env}.test-app-v2"
#   app_status    = "ACTIVE"
# }

# module "okta_demo_group_v2" {
#   source = "git@github.com:mediwareinc/terraform-okta//okta-group?ref=v1.9.0"

#   group_name = "Demo Users V2 (VIKI ${title(var.env)})"
#   group_desc = "Users who can sign into AI Demo SPA"
# }

# module "okta_demo_group_assignment_v2" {
#   source = "git@github.com:mediwareinc/terraform-okta//okta-assign-app-to-group?ref=v1.9.0"

#   app_id   = module.okta_demo_spa_v2.okta_spa_app.id
#   group_id = module.okta_demo_group_v2.group.id
# }

module "okta_hhh_app_v2" {
  // app for HHH to call AI APIs
  // future: new client means adding new app similar to this one
  source = "git@github.com:mediwareinc/terraform-okta//okta-service-app?ref=v1.9.4"

  app_name      = "HHH SkySense Extract AI Client(${title(var.env)})"
  app_client_id = "${local.namespace_v2}.paperglass.${var.env}.hhh"
  app_status    = "ACTIVE"
}

module "okta_ltc_app_v2" {
  // app for LTC to call AI APIs  
  source = "git@github.com:mediwareinc/terraform-okta//okta-service-app?ref=v1.9.4"

  app_name      = "LTC Skysense Extract AI Client(${title(var.env)})"
  app_client_id = "${local.namespace_v2}.paperglass.${var.env}.ltc"
  app_status    = "ACTIVE"
}

resource "okta_app_oauth" "okta-service-app_ltc" {
  label                      = "LTC Skysense Extract AI Client - priv/pub keys(${title(var.env)})"
  client_id                  = "${local.namespace}.paperglass.${var.env}.pk.ltc"
  type                       = "service"
  status                     = "ACTIVE"
  token_endpoint_auth_method = "private_key_jwt"
  auto_key_rotation          = true
  grant_types                = ["client_credentials"]
  response_types             = ["token"]
  omit_secret                = true
  profile                    = null

  # Public key configuration
  jwks {
    kty = "RSA"
    kid = "3e4977fc3e1d4f5b8123c4a7200be321"
    n   = "splNNkuhPlBBfumvwhOQmlse-69RfXc78SvwSWLgtuTy_ox-tzIoBShHfjCwgsAk-yYNIv4kmYtZ4rqHEciiqlYSncG_hV_2-NEdpqYFCsSyZgv5dfcye8IaD5OKA0uvrWM5FRCGxD16R-BQGk79RYbXPKMtTpDfkS81N1Qa4HcspKoWxk6kKPyrQc_YLGYX1YN7BHslUDcfeUQ_wJhIkMCuusiDDbr2-BLckniK6dppP0JXndF5JX7gdKXLez8E4b7X-bzyqkDUx5SYna4Gcyz4vZUs7ORS2PIiQqSqfk1XjGxhnLsNJLzt7Hh9z-9S-JaQIXM2x9YTM8kKTojmFw"
    e   = "AQAB"
  }
}


module "okta_auth_server_policy_paperglass_v2" {
  // Policy for SCC
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server_v2.okta_auth_server.name
  policy_allowed_clients = [
    module.okta_hhh_app_v2.okta_service_app.client_id, # in future, new clients will be added here
    module.okta_ltc_app_v2.okta_service_app.client_id,
  ]
  policy_desc = "Policy for PaperGlass clients"
  policy_name = "Policy for PaperGlass clients (${var.env})"

  depends_on = [module.okta_auth_server_v2]
}

module "okta_auth_server_policy_rule_paperglass_v2" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["client_credentials"]
  okta_auth_server_name          = module.okta_auth_server_v2.okta_auth_server.name
  policy_id                      = module.okta_auth_server_policy_paperglass_v2.auth_server_policy.id
  access_token_lifetime_minutes  = 60
  refresh_token_lifetime_minutes = 3600
  refresh_token_window_minutes   = 3600
  rule_name                      = "Paperglass-specific policy to call APIs"
  scope_whitelist                = [local.okta_scopes_v2.paperglass]

  depends_on = [module.okta_auth_server_v2]
}
