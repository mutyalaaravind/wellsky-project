
output "external_pubsub_topic_id" {
  value = module.ai.external_files_topic_id
}

output "okta_admin_group_id" {
	  value = module.okta_admin_group.group.id
	}

output "okta_regular_users_group_id" {
	  value = module.okta_regular_users_group.group.id
	}
