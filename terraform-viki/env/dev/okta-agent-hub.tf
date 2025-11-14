# ============================================
# Okta Configuration for WellSky Agent Hub
# ============================================

locals {
  agent_hub_namespace = "api.wellsky.viki.agent-hub"

  # Redirect URIs for different environments
  agent_hub_redirect_uris_dev = [
    "http://localhost:3000/login/callback",
    "http://127.0.0.1:3000/login/callback",
    "http://localhost:8080/login/callback",  # Docker container
    "http://127.0.0.1:8080/login/callback",  # Docker container
    "https://skysense-agent-hub-145042810266.us-central1.run.app/login/callback",  # Cloud Run (dev)
  ]

  agent_hub_logout_uris_dev = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Docker container
    "http://127.0.0.1:8080",  # Docker container
    "https://skysense-agent-hub-145042810266.us-central1.run.app",  # Cloud Run (dev)
  ]

  agent_hub_trusted_origins_dev = [
    # Note: Trusted origins are global in Okta and already exist from other apps.
    # Redirect URIs above are app-specific and sufficient for authentication.
    # No trusted origins needed here - they're already configured globally.
  ]
}

# Agent Hub SPA Application
# Note: This app allows ALL authenticated Okta users (no group restriction)
module "okta_agent_hub_spa_dev" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-spa-app?ref=v1.9.0"

  app_name                      = "WellSky Agent Hub SPA (${title(var.env)})"
  app_client_id                 = "${local.agent_hub_namespace}.${var.env}"
  app_redirect_uris             = local.agent_hub_redirect_uris_dev
  app_post_logout_redirect_uris = local.agent_hub_logout_uris_dev
  app_grant_types               = ["authorization_code", "refresh_token"]
  app_status                    = "ACTIVE"
  trusted_origin_urls           = local.agent_hub_trusted_origins_dev
  trusted_origin_scopes         = ["CORS", "REDIRECT"]
}

# Policy to allow users to access Agent Hub
# NOTE: Using OLD authorization server (viki-dev) to match existing frontend/backend config
module "okta_auth_server_policy_agent_hub" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy?ref=v1.8.8"

  okta_auth_server_name = module.okta_auth_server.okta_auth_server.name
  policy_allowed_clients = [
    module.okta_agent_hub_spa_dev.okta_spa_app.client_id,
  ]
  policy_desc = "Allows users to sign in to WellSky Agent Hub"
  policy_name = "Agent Hub Policy (${var.env})"

  depends_on = [module.okta_auth_server]
}

# Policy rule for Agent Hub access
# NOTE: Using OLD authorization server (viki-dev) and OLD scopes
module "okta_auth_server_policy_rule_agent_hub" {
  source = "git@github.com:mediwareinc/terraform-okta.git//okta-auth-server-policy-rule?ref=v1.8.8"

  grant_type_whitelist           = ["authorization_code"]
  okta_auth_server_name          = module.okta_auth_server.okta_auth_server.name
  policy_id                      = module.okta_auth_server_policy_agent_hub.auth_server_policy.id
  access_token_lifetime_minutes  = 1440  # 24 hours
  refresh_token_lifetime_minutes = 86400 # 60 days
  refresh_token_window_minutes   = 86400 # 60 days
  rule_name                      = "Agent Hub SPA"
  group_whitelist                = [module.okta_agent_hub_group.group.id]  # Allow Agent Hub Users group
  scope_whitelist = [
    "openid",
    "email",
    "profile",
    local.okta_scopes.transcription,
    local.okta_scopes.form-completion
  ]

  depends_on = [module.okta_auth_server_policy_agent_hub, module.okta_agent_hub_group]
}

# User group for Agent Hub access
module "okta_agent_hub_group" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-group?ref=v1.9.0"

  group_name = "Agent Hub Users (${title(var.env)})"
  group_desc = "Users who can access WellSky Agent Hub"
}

# Assign app to group
module "okta_agent_hub_group_assignment" {
  source = "git@github.com:mediwareinc/terraform-okta//okta-assign-app-to-group?ref=v1.9.0"

  app_id   = module.okta_agent_hub_spa_dev.okta_spa_app.id
  group_id = module.okta_agent_hub_group.group.id

  depends_on = [
    module.okta_agent_hub_spa_dev,
    module.okta_agent_hub_group
  ]
}

# Find Okta users by email
data "external" "okta_agent_hub_user" {
  for_each = var.okta_agent_hub_users
  program  = ["sh", "${path.module}/find_okta_user.sh"]
  query = {
    okta_api_token = var.okta_api_token
    email          = each.value
  }
}

# Add users to Agent Hub group
resource "okta_group_memberships" "agent_hub_users_members" {
  group_id = module.okta_agent_hub_group.group.id
  users    = [for okta_agent_hub_user in data.external.okta_agent_hub_user : okta_agent_hub_user.result.user_id]
}

# Output the client ID for use in frontend config
output "agent_hub_okta_client_id" {
  value       = module.okta_agent_hub_spa_dev.okta_spa_app.client_id
  description = "Okta Client ID for Agent Hub"
}

output "agent_hub_okta_app_id" {
  value       = module.okta_agent_hub_spa_dev.okta_spa_app.id
  description = "Okta Application ID for Agent Hub"
}
