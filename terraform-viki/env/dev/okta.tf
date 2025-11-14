locals {
  auth_server_name = "viki-${var.env}"
  namespace        = "api.wellsky.viki"
  okta_scopes = {
    transcription   = "${local.namespace}.ai.transcription",   # VIKI AI autoscribe APIs
    form-completion = "${local.namespace}.ai.form-completion", # VIKI AI form completion APIs
    nlparse         = "${local.namespace}.ai.nlparse",         # VIKI AI nlparse APIs
    paperglass      = "${local.namespace}.ai.paperglass",      # VIKI AI hhh APIs
    summarization-agents = "${local.namespace}.ai.summarization-agents", # VIKI AI summarization agents APIs
    admin           = "${local.namespace}.ai.admin",           # VIKI AI admin APIs
  }
}

module "okta_auth_server" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server?ref=v1.8.8"

  auth_server_audience = var.okta_audience
  auth_server_desc     = "VIKI Auth Server (${var.env})"
  auth_server_name     = local.auth_server_name
}

module "okta_scopes" {
  for_each = local.okta_scopes

  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-scope?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server.okta_auth_server.name
  scope_name            = each.value
  scope_consent         = "IMPLICIT"

  depends_on = [module.okta_auth_server]
}

module "okta_auth_server_policy_demo" {
  // Policy for developer login into Demo
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server.okta_auth_server.name
  policy_allowed_clients = [
    module.okta_demo_spa.okta_spa_app.client_id,
  ]
  policy_desc = "Allows developers to sign in to Demo"
  policy_name = "AI Developer Policy (${var.env})"

  depends_on = [module.okta_auth_server]
}

module "okta_auth_server_policy_testapp" {
  // Policy for TestApp
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server.okta_auth_server.name
  policy_allowed_clients = [
    module.okta_test_app.okta_service_app.client_id,
  ]
  policy_desc = "Allows TestApp to use AI APIs"
  policy_name = "AI TestApp Policy (${var.env})"

  depends_on = [module.okta_auth_server]
}

module "okta_auth_server_policy_rule_demo" {
  // Allow developer to login into Demo
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["authorization_code"]
  okta_auth_server_name          = module.okta_auth_server.okta_auth_server.name
  policy_id                      = module.okta_auth_server_policy_demo.auth_server_policy.id
  access_token_lifetime_minutes  = 1440
  refresh_token_lifetime_minutes = 86400
  refresh_token_window_minutes   = 86400
  rule_name                      = "AI Demo SPA"
  scope_whitelist                = ["openid", "email", "profile", local.okta_scopes.transcription, local.okta_scopes.form-completion]

  depends_on = [module.okta_auth_server]
}

module "okta_auth_server_policy_rule_testapp" {
  // Allow TestApp to call AI APIs
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["client_credentials"]
  okta_auth_server_name          = module.okta_auth_server.okta_auth_server.name
  policy_id                      = module.okta_auth_server_policy_testapp.auth_server_policy.id
  access_token_lifetime_minutes  = 60
  refresh_token_lifetime_minutes = 3600
  refresh_token_window_minutes   = 3600
  rule_name                      = "Applications that call AI APIs"
  scope_whitelist                = [local.okta_scopes.transcription, local.okta_scopes.form-completion]

  depends_on = [module.okta_auth_server]
}

// Naming convention:
// <ProductName> <MicroserviceName> <TenantName?> Client<BusinessUnit <Env>>
// E. g. for app that is used by ACMEHealth (external product) to call FakeHub APIs (internal product):
// FakeHub ACMEHealth Client(Payer Dev)

module "okta_demo_spa" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-spa-app?ref=v1.9.0"

  app_name                      = "AI Demo Client(VIKI ${title(var.env)})"
  app_client_id                 = "${local.namespace}.${var.env}.demo"
  app_redirect_uris             = var.demo_redirect_uris
  app_post_logout_redirect_uris = var.demo_trusted_origins
  app_grant_types               = ["authorization_code", "refresh_token"]
  app_status                    = "ACTIVE"
  trusted_origin_urls           = var.demo_trusted_origins
  trusted_origin_scopes         = ["CORS", "REDIRECT"]
}

module "okta_test_app" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-service-app?ref=v1.8.8"

  app_name      = "AI TestApp Client(VIKI ${title(var.env)})"
  app_client_id = "${local.namespace}.${var.env}.test-app"
  app_status    = "ACTIVE"
}

module "okta_demo_group" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-group?ref=v1.9.0"

  group_name = "Demo Users (VIKI ${title(var.env)})"
  group_desc = "Users who can sign into AI Demo SPA"
}

module "okta_demo_group_assignment" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-assign-app-to-group?ref=v1.9.0"

  app_id   = module.okta_demo_spa.okta_spa_app.id
  group_id = module.okta_demo_group.group.id
}

module "okta_admin_spa" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-spa-app?ref=v1.9.0"

  app_name                      = "AI Admin Client(VIKI ${title(var.env)})"
  app_client_id                 = "${local.namespace}.${var.env}.admin"
  app_redirect_uris             = var.admin_redirect_uris
  app_post_logout_redirect_uris = var.admin_trusted_origins
  app_grant_types               = ["authorization_code", "refresh_token"]
  app_status                    = "ACTIVE"
  trusted_origin_urls           = var.admin_trusted_origins
  trusted_origin_scopes         = ["CORS", "REDIRECT"]
}

module "okta_admin_group" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-group?ref=v1.9.0"

  group_name = "Admin Users (VIKI ${title(var.env)})"
  group_desc = "Users who can sign into AI Admin SPA"
}

module "okta_admin_group_assignment" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-assign-app-to-group?ref=v1.9.0"

  app_id   = module.okta_admin_spa.okta_spa_app.id
  group_id = module.okta_admin_group.group.id
}

# Regular Users Group (membership managed by Admin UI)
module "okta_regular_users_group" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-group?ref=v1.9.0"

  group_name = "Regular Users (VIKI ${title(var.env)})"
  group_desc = "Regular users who can sign into AI Admin SPA (managed by Admin UI)"
}

# Assign Regular Users Group to Admin UI App
module "okta_regular_users_group_assignment" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-assign-app-to-group?ref=v1.9.0"

  app_id   = module.okta_admin_spa.okta_spa_app.id
  group_id = module.okta_regular_users_group.group.id
}

# IMPORTANT: Do NOT add okta_group_memberships resource for this group
# The Admin UI will manage membership via Okta API

# Custom claim for group-roles to identify superusers (access tokens)
module "okta_auth_server_claim_group_roles" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-claim?ref=v1.8.8"

  okta_auth_server_name   = module.okta_auth_server.okta_auth_server.name
  name                    = "group-roles"
  value                   = "isMemberOfGroupName(\"${module.okta_admin_group.group.name}\") ? \"superuser\" : null"
  value_type              = "EXPRESSION"
  claim_type              = "RESOURCE"  # For access tokens
  always_include_in_token = true
  scopes                  = ["openid", "email", "profile", local.okta_scopes.admin]

  depends_on = [module.okta_auth_server, module.okta_admin_group]
}

# Custom claim for group-roles to identify superusers (ID tokens)
module "okta_auth_server_claim_group_roles_id" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-claim?ref=v1.8.8"

  okta_auth_server_name   = module.okta_auth_server.okta_auth_server.name
  name                    = "group-roles"
  value                   = "isMemberOfGroupName(\"${module.okta_admin_group.group.name}\") ? \"superuser\" : null"
  value_type              = "EXPRESSION"
  claim_type              = "IDENTITY"  # For ID tokens
  always_include_in_token = true
  scopes                  = ["openid", "profile"]

  depends_on = [module.okta_auth_server, module.okta_admin_group]
}

module "okta_auth_server_policy_admin" {
  // Policy for admin login into Admin UI
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server.okta_auth_server.name
  policy_allowed_clients = [
    module.okta_admin_spa.okta_spa_app.client_id,
  ]
  policy_desc = "Allows administrators to sign in to Admin UI"
  policy_name = "AI Admin Policy (${var.env})"

  depends_on = [module.okta_auth_server]
}

module "okta_auth_server_policy_rule_admin" {
  // Allow admin to login into Admin UI
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["authorization_code"]
  okta_auth_server_name          = module.okta_auth_server.okta_auth_server.name
  policy_id                      = module.okta_auth_server_policy_admin.auth_server_policy.id
  access_token_lifetime_minutes  = 1440
  refresh_token_lifetime_minutes = 86400
  refresh_token_window_minutes   = 86400
  rule_name                      = "AI Admin SPA"
  scope_whitelist                = ["openid", "email", "profile", local.okta_scopes.admin, local.okta_scopes.transcription, local.okta_scopes.form-completion]

  depends_on = [module.okta_auth_server]
}

// This block doesn't work since Okta TF provider attempts to fetch roles in addition to primary user info, which fails due to insufficient permissions.
# data "okta_user" "demo_user" {
#   for_each = var.okta_demo_users
#   search {
#     expression = "profile.email eq \"${each.value}\""
#   }
# }
// ...because of this, we use a shell script to find user ID:
data "external" "okta_demo_user" {
  for_each = var.okta_demo_users
  program  = ["sh", "${path.module}/find_okta_user.sh"]
  query = {
    okta_api_token = var.okta_api_token
    email          = each.value
  }
}

resource "okta_group_memberships" "demo_users_members" {
  group_id = module.okta_demo_group.group.id
  users    = [for okta_demo_user in data.external.okta_demo_user : okta_demo_user.result.user_id]
}

data "external" "okta_admin_user" {
  for_each = var.okta_admin_users
  program  = ["sh", "${path.module}/find_okta_user.sh"]
  query = {
    okta_api_token = var.okta_api_token
    email          = each.value
  }
}

resource "okta_group_memberships" "admin_users_members" {
  group_id = module.okta_admin_group.group.id
  users    = [for okta_admin_user in data.external.okta_admin_user : okta_admin_user.result.user_id]
}

module "okta_hhh_app" {
  // app for HHH to call AI APIs
  // future: new client means adding new app similar to this one
  source = "git@github.com:mediwareinc/terraform-okta//okta-service-app?ref=v1.9.4"

  app_name      = "HHH Medication Extraction AI Client(${title(var.env)})"
  app_client_id = "${local.namespace}.paperglass" # DO NOT CHANGE - This is in use by HHH.  Changeing will force the creation of a new client ID/Secret which will need to be coordinated with HHH
  app_status    = "ACTIVE"
}

module "okta_ltc_app" {
  // app for LTC to call AI APIs  
  source = "git@github.com:mediwareinc/terraform-okta//okta-service-app?ref=v1.9.4"

  app_name      = "LTC SkySense Extract AI Client-old(${title(var.env)})"
  app_client_id = "${local.namespace}.paperglass.${var.env}.ltc.old"
  app_status    = "ACTIVE"
}

module "okta_auth_server_policy_paperglass" {
  // Policy for SCC
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server.okta_auth_server.name
  policy_allowed_clients = [
    module.okta_hhh_app.okta_service_app.client_id,
    module.okta_ltc_app.okta_service_app.client_id, # in future, new clients will be added here
  ]
  policy_desc = "Policy for PaperGlass clients"
  policy_name = "Policy for PaperGlass clients (${var.env})"

  depends_on = [module.okta_auth_server]
}

module "okta_auth_server_policy_rule_paperglass" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["client_credentials"]
  okta_auth_server_name          = module.okta_auth_server.okta_auth_server.name
  policy_id                      = module.okta_auth_server_policy_paperglass.auth_server_policy.id
  access_token_lifetime_minutes  = 60
  refresh_token_lifetime_minutes = 3600
  refresh_token_window_minutes   = 3600
  rule_name                      = "Paperglass-specific policy to call APIs"
  scope_whitelist                = [local.okta_scopes.paperglass]

  depends_on = [module.okta_auth_server]
}











