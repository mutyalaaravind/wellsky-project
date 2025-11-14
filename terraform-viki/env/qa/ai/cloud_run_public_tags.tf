# Centralized management of AllUsersIngress tag bindings for Cloud Run services
# This replaces individual tag bindings in the terraform-gcp-cloudrun modules

# Get tag key and value for AllUsersIngress
data "google_tags_tag_key" "public_access_tag_key" {
  parent     = "organizations/531195336225"
  short_name = "allUsersIngress"
}

data "google_tags_tag_value" "public_access_tag_value" {
  parent     = data.google_tags_tag_key.public_access_tag_key.id
  short_name = "true"
}

# Individual tag bindings are now managed in each services_*.tf file
# This file provides shared data sources for tag key/value lookup

# Output for debugging - shows tag key/value IDs
output "tag_key_id" {
  description = "Tag key ID for allUsersIngress"
  value       = data.google_tags_tag_key.public_access_tag_key.id
}

output "tag_value_id" {
  description = "Tag value ID for allUsersIngress=true"
  value       = data.google_tags_tag_value.public_access_tag_value.id
}