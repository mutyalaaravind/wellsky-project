variable "app_project_id" {
}

variable "dmz_project_id" {
}

variable "mgmt_project_id" {
}

variable "env" {
}

variable "region" {
}

variable "okta_issuer" {
}

variable "okta_audience" {
}

variable "okta_scopes" {
  type = map(string)
}


variable "okta_service_issuer_url" {
  type = string
}

variable "okta_service_audience" {
  type = string
}

variable "okta_demo_client_id" {
}

variable "okta_admin_client_id" {
}

variable "cloud_run_services" {
  description = "Configuration for Cloud Run services"
  type = map(object({
    image_version       = string
    uvicorn_workers     = number
    cpus                = number
    memory              = number
    timeout             = number
    min_instances       = number
    max_instances       = any # Can be number or "unlimited"
    concurrency         = number
    allow_public_access = bool
  }))
  default = {}
}

variable "apps_version" {
  type        = string
  description = "Default version for all apps"
}

variable "autoscribe_version" {
}

variable "extract_and_fill_version" {
}

variable "demo_version" {
}

variable "nlparse_version" {
}

variable "paperglass_version" {
}

variable "frontends_version" {
}

variable "forms_widgets_host" {
}

variable "forms_api" {
}

variable "forms_api_key" {
}

variable "labels" {
}

variable "alert_notification_channel_emails" {
}

variable "autoscribe_aws_role_arn" {
}

variable "nlparse_region" {
}

variable "aws_default_region" {
}

variable "okta_disable" {
}

variable "managers" {
}

variable "multimodal_temperature" {
}

variable "opentelemetry_disabled" {
}

variable "opentelemetry_otlp_endpoint" {
}

variable "gcp_trace_enabled" {
}

variable "orchestration_grader_schedule_window_enabled" {
  type = string
}

variable "command_outofband_cloudtask_enabled" {
  type = string
}

variable "cloudtask_max_concurrent_dispatches" {
  type = string
}

variable "cloudtask_max_dispatches_per_second" {
  type = string
}

variable "cloudtask_quarantine_max_concurrent_dispatches" {
  type = string
}

variable "cloudtask_quarantine_max_dispatches_per_second" {
  type = string
}

variable "extraction_vertex_ai_index_size" {
  type    = string
  default = "SHARD_SIZE_SMALL"
}

variable "fhir_server_url" {
  type = string
}

variable "fhir_data_store" {
  type = string
}

variable "fhir_data_set" {
  type = string
}

variable "fhir_search_store_id" {
  type = string
}

variable "medispan_api_url" {
}

variable "medispan_page_size" {
}

variable "mock_prompt_enabled" {
}

variable "hhh_gcs_sa_email" {
  type = string
}

variable "okta_issuer_url" {
  type = string
}

variable "proxy_url" {
  type = string
}

variable "vpc_connector" {
  type = string
}

variable "firestore_to_bq_streaming_enabled" {
  type    = bool
  default = false
}

variable "allow_public_access" {
  description = "Allow public access for cloud run."
  type        = bool
  default     = true
}

variable "allow_public_access_widget" {
  description = "Allow public access for cloud run."
  type        = bool
  default     = true
}

variable "newrelic_account_id" {
  type = string
}

variable "newrelic_application_id" {
  type = string
}

variable "newrelic_trust_key" {
  type = string
}

variable "newrelic_api_key" {
  type = string
}

variable "newrelic_api_license_key" {
  type = string
}

variable "newrelic_api_browser_key" {
  type = string
}

variable "newrelic_api_user_key" {
  type = string
}

variable "newrelic_trace_enabled" {
}

variable "step_classify_llm_model" {
  type = string
}

variable "step_extractmedication_llm_model" {
  type = string
}

variable "step_medispanmatch_llm_model" {
  type = string
}

variable "medication_extraction_api_url" {
  type = string
}

variable "medication_extraction_api_2_url" {
  type = string
}

variable "medication_extraction_default_api_url" {
  type = string
}

variable "medication_extraction_high_api_url" {
  type = string
}

variable "medication_extraction_quarantine_api_url" {
  type = string
}

variable "entity_extraction_api_url" {
  type = string
}

variable "djt_api_url" {
  type = string
}

variable "admin_api_url" {
  type = string
}

variable "paperglass_api_url" {
  type = string
}

variable "medication_extraction_version" {
  type = string
}

variable "cloudtask_queue_resolver_version" {
  description = "Version of the cloudtask queue resolver to use"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_default_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_priority_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint priority queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint quarantine queue"
  type        = string
}

variable "registered_app_ids" {
  description = "List of registered app_ids for the cloudtask queue resolver. If not on this list, then it will use the default queues."
  type        = list(string)
}

variable "cloudtask_v4_extraction_entrypoint_default_default_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_default_high_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint high queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_default_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint quarantine queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint high queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint quarantine queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint high queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint quarantine queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint high queue"
  type        = string
}

variable "cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 extraction entrypoint quarantine queue"
  type        = string
}

variable "cloudtask_paperglass_classification_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for paperglass classification quarantine queue"
  type        = string
}

variable "cloudtask_paperglass_extraction_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for paperglass extraction quarantine queue"
  type        = string
}

variable "cloudtask_paperglass_command_schedule_max_dispatches_per_second" {
  description = "Max dispatches per second for paperglass command schedule queue"
  type        = string
}

variable "cloudtask_v4_status_check_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 status check quarantine queue"
  type        = string
}

variable "cloudtask_v4_paperglass_integration_status_update_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 paperglass integration status update quarantine queue"
  type        = string
}

variable "cloudtask_v4_paperglass_medications_integration_quarantine_max_dispatches_per_second" {
  description = "Max dispatches per second for v4 paperglass medications integration quarantine queue"
  type        = string
}

variable "paperglass_api_token" {
  type = string
}

variable "nurse_assistant_version" {
  type = string
}

variable "skysense_scribe_api_version" {
  type = string
}

variable "collab_admins" {
  description = "Admins for the collab notebook"
  type        = set(string)
}

variable "audit_logger_api_url" {
  type = string
}

variable "alloydb_password" {
  description = "Password for the AlloyDB instance"
  type        = string
  sensitive   = true
}

variable "alloydb_ip_address" {
  description = "IP address for the AlloyDB instance"
  type        = string
}

variable "alloydb_user_username" {
  description = "IP address for the AlloyDB instance"
  type        = string
}

variable "scribe_superuser_password" {
  type        = string
  sensitive   = true
  description = "Password scribe super userr"
}

variable "scribe_jwt_secret" {
  type        = string
  sensitive   = true
  description = "JWT signing secret"
}

variable "alloydb_user_password" {
  description = "IP address for the AlloyDB instance"
  type        = string
  sensitive   = true
}

variable "meddb_active_repo" {
  type = string
}

variable "meddb_table_medispan" {
  type = string
}

variable "meddb_table_merative" {
  type = string
}

variable "meddb_search_function_medispan" {
  type = string
}

variable "meddb_search_function_merative" {
  type = string
}

variable "medispan_api_version" {
  type = string
}

variable "network_project_id" {
  description = "ID of the project containing the VPC used by this project"
  type        = string
}

variable "network" {
  description = "Name of the VPC to use for the project"
  type        = string
}

variable "redis_host" {
  description = "Redis host address"
  type        = string
}

variable "redis_port" {
  description = "Redis port"
  type        = number
}
