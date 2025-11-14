# Existing variables
variable "env" {
  description = "Short name of the environment for resource names. sandbox, dev, qa, stage, prod "
  type        = string
}

variable "app_project_id" {
  description = "App project"
  type        = string
}

variable "dmz_project_id" {
  description = "DMZ project"
  type        = string
}

variable "mgmt_project_id" {
  description = "MGMT project"
  type        = string
}

variable "region" {
  description = "Region for project resources"
  type        = string
}

variable "zone" {
  description = "The zone where the compute resources should reside."
  type        = string
}

variable "network_project_id" {
  description = "ID of the project containing the VPC used by this project"
  type        = string
}

variable "network" {
  description = "Name of the VPC to use for the project"
  type        = string
}

variable "subnet_internal" {
  description = "The subnet to to use for resources"
  type        = string
}

variable "subnet_dmz" {
  description = "The subnet to to use for publicly accessible resources"
  type        = string
}

variable "vpc_connector" {
  description = "The vpc connector fully qualified path"
  type        = string
}

variable "managers" {
  description = "admin for most of the time"
  type        = set(string)
}

variable "viewers" {
  description = "viewers for Observability and Monitoring"
  type        = set(string)
}

variable "support_users" {
  description = "support users with access to view and search GCP monitoring logs"
  type        = set(string)
}

variable "okta_demo_users" {
  description = "Users who will be assigned as members of demo group and will be able to login to demo app with Okta"
  type        = set(string)
}

variable "okta_admin_users" {
  description = "Users who will be assigned as members of admin group and will be able to login to admin app with Okta"
  type        = set(string)
}

variable "alert_notification_channel_emails" {
  description = "Notification channel for Email service."
  type = map(object({
    display_name  = string
    email_address = string
    enabled       = optional(bool, false)
    force_delete  = optional(bool, false)
  }))
}

variable "mock_prompt_enabled" {
  description = "If true, swaps out the PromptAdapter for a MockPromptAdapter to support load testing"
  type        = string
}

variable "okta_org_name" {
  description = "Organization name (usually name of 3rd-level domain)."
  type        = string
}

variable "okta_base_url" {
  description = "Base URL for Okta (usually 2nd-level domain)."
  type        = string
}

variable "okta_api_token" {
  description = "API Token for managing Okta resources."
  type        = string
}

variable "okta_audience" {
  description = "Audience for Care Coordination Auth Server."
  type        = string
}

variable "okta_service_audience" {
  description = "Audience for Okta Auth Server. (New auth server audience)"
  type        = string
}

variable "okta_service_issuer_url" {
  description = "Issuer URL for Okta Auth Server. (New auth server audience)"
  type        = string
}

variable "demo_redirect_uris" {
  description = "List or redirect_uri values for Highway"
  type        = list(string)
}

variable "demo_trusted_origins" {
  description = "List or trusted origin URLs for Highway"
  type        = list(string)
}

variable "admin_redirect_uris" {
  description = "List or redirect_uri values for Admin"
  type        = list(string)
}

variable "admin_trusted_origins" {
  description = "List or trusted origin URLs for Admin"
  type        = list(string)
}

variable "cloud_run_services" {
  description = "Configuration for Cloud Run services"
  type = map(object({
    service_names       = list(string)
    image_version       = string
    uvicorn_workers     = number
    cpus                = number
    memory              = number
    timeout             = number
    min_instances       = number
    max_instances       = any                  # Can be number or "unlimited"
    concurrency         = optional(number, 80) # Default concurrency
    allow_public_access = bool
  }))
  default = {}
}

variable "apps_version" {
  type        = string
  description = "Default version for all apps"
}

variable "artifact_registry_additional_service_account_readers" {
  type        = list(string)
  default     = []
  description = "Additional artifact registry readers"
}

# New variables
variable "autoscribe_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for autoscribe"
}

variable "nlparse_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for nlparse"
}

variable "extract_and_fill_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for extract_and_fill"
}

variable "paperglass_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for paperglass"
}

variable "demo_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for demo"
}

variable "frontends_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for frontends"
}

variable "nurse_assistant_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for nurse assistant"
}

variable "skysense_scribe_api_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for skysense scribe API"
}

variable "support_ui_app_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for support UI app"
}

variable "forms_widgets_host" {
  type        = string
  description = "Host for forms widgets"
}

variable "forms_api" {
  type        = string
  description = "API endpoint for forms"
}

variable "forms_api_key" {
  type        = string
  description = "API key for forms"
}

variable "autoscribe_aws_role_arn" {
  type        = string
  description = "AWS role ARN for autoscribe"
}

variable "nlparse_region" {
  type        = string
  description = "Region for nlparse"
}

variable "aws_default_region" {
  type        = string
  description = "Default AWS region"
}

variable "okta_disable" {
  type        = bool
  default     = false
  description = "Flag to disable Okta"
}

variable "extraction_vertex_ai_index_size" {
  type        = string
  description = "Size of the extraction vertex AI index"
}

variable "fhir_server_url" {
  type        = string
  description = "URL for FHIR server"
}

variable "fhir_data_store" {
  type        = string
  description = "FHIR data store name"
}

variable "fhir_data_set" {
  type        = string
  description = "FHIR data set name"
}

variable "fhir_search_store_id" {
  type        = string
  description = "FHIR search store ID"
}

variable "medispan_api_url" {
  type        = string
  description = "URL for Medispan API"
}

variable "medispan_page_size" {
  type        = string
  description = "Page size for Medispan API"
}

variable "hhh_ip" {
  type        = string
  description = "IP address for HHH"
}

variable "hhh_gcs_sa_email" {
  type        = string
  description = "Email for HHH GCS service account"
}

variable "proxy_url" {
  type        = string
  description = "URL for proxy"
}

variable "okta_issuer_url" {
  type        = string
  description = "Issuer URL for Okta"
}

variable "multimodal_temperature" {
  type        = string
  description = "Temperature for multimodal"
}

variable "opentelemetry_disabled" {
  type        = string
  description = "Flag to disable OpenTelemetry"
}

variable "opentelemetry_otlp_endpoint" {
  type        = string
  description = "OTLP Endpoint for OpenTelemetry"
}

variable "gcp_trace_enabled" {
  type        = string
  description = "Flag to enable GCP trace"
}

variable "cloudtask_queue_resolver_version" {
  type        = string
  description = "Version for cloudtask queue resolver"
}

variable "cloudtask_max_concurrent_dispatches" {
  type        = string
  description = "Max concurrent dispatches for cloudtask"
}

variable "cloudtask_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for cloudtask"
}

variable "cloudtask_quarantine_max_concurrent_dispatches" {
  type        = string
  description = "Max concurrent dispatches for cloudtask quarantine"
}

variable "cloudtask_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for cloudtask quarantine"
}

variable "registered_app_ids" {
  type        = list(string)
  description = "List of registered app IDs"
}

variable "orchestration_grader_schedule_window_enabled" {
  type        = string
  description = "Flag to enable orchestration grader schedule window"
}

variable "command_outofband_cloudtask_enabled" {
  description = "Flag to enable command out-of-band cloud task processing"
  type        = string
}

variable "network_tags" {
  type        = list(string)
  default     = []
  description = "A list of network tags to attach to the instance."
}

variable "allow_public_access" {
  type        = bool
  default     = true
  description = "Allow public access to the cloud run."
}

variable "allow_public_access_widget" {
  type        = bool
  default     = true
  description = "Flag to allow public access for widget"
}

variable "newrelic_account_id" {
  type        = number
  description = "New Relic account ID"
}

variable "newrelic_service_account_id" {
  type        = string
  description = "New Relic service account ID"
}

variable "newrelic_application_id" {
  type        = string
  description = "New Relic application ID"
}

variable "newrelic_trust_key" {
  type        = string
  description = "New Relic trust key"
}

variable "newrelic_api_key" {
  type        = string
  description = "New Relic API key"
}

variable "newrelic_api_license_key" {
  type        = string
  description = "New Relic API license key"
}

variable "newrelic_api_browser_key" {
  type        = string
  description = "New Relic API browser key"
}

variable "newrelic_api_user_key" {
  type        = string
  description = "New Relic API user key"
}

variable "newrelic_trace_enabled" {
  type        = string
  description = "Flag to enable New Relic trace"
}

variable "step_classify_llm_model" {
  type        = string
  description = "LLM model for step classification"
}

variable "step_extractmedication_llm_model" {
  type        = string
  description = "LLM model for medication extraction"
}

variable "step_medispanmatch_llm_model" {
  type        = string
  description = "LLM model for Medispan matching"
}

variable "medication_extraction_api_url" {
  type        = string
  description = "URL for medication extraction API"
}

variable "medication_extraction_api_2_url" {
  type        = string
  description = "URL for medication extraction API 2"
}

variable "medication_extraction_default_api_url" {
  type        = string
  description = "Default URL for medication extraction API"
}

variable "medication_extraction_high_api_url" {
  type        = string
  description = "High priority URL for medication extraction API"
}

variable "medication_extraction_quarantine_api_url" {
  type        = string
  description = "Quarantine URL for medication extraction API"
}

variable "cloudtask_v4_extraction_entrypoint_default_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint default"
}

variable "cloudtask_v4_extraction_entrypoint_priority_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint priority"
}

variable "cloudtask_v4_extraction_entrypoint_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint quarantine"
}

variable "cloudtask_v4_extraction_entrypoint_default_default_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint default default"
}

variable "cloudtask_v4_extraction_entrypoint_default_high_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint default high"
}

variable "cloudtask_v4_extraction_entrypoint_default_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint default quarantine"
}

variable "cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint HHH default"
}

variable "cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint HHH high"
}

variable "cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint HHH quarantine"
}

variable "cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint LTC default"
}

variable "cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint LTC high"
}

variable "cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint LTC quarantine"
}

variable "cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint 007 default"
}

variable "cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint 007 high"
}

variable "cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 extraction entrypoint 007 quarantine"
}

variable "cloudtask_paperglass_classification_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for paperglass classification quarantine"
}

variable "cloudtask_paperglass_extraction_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for paperglass extraction quarantine"
}

variable "cloudtask_paperglass_command_schedule_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for paperglass command schedule"
}

variable "cloudtask_v4_status_check_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 status check quarantine"
}

variable "cloudtask_v4_paperglass_integration_status_update_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 paperglass integration status update quarantine"
}

variable "cloudtask_v4_paperglass_medications_integration_quarantine_max_dispatches_per_second" {
  type        = string
  description = "Max dispatches per second for v4 paperglass medications integration quarantine"
}

variable "medication_extraction_version" {
  type        = string
  description = "Version for medication extraction"
}

# Needed for QA only for Terraform to initiate E2E tests at end of provisioning
variable "paperglass_api_token" {
  type        = string
  description = "API token for Paperglass API to initiate E2E tests at end of provisioning"
  default     = ""
}

variable "alloydb_password" {
  type        = string
  sensitive   = true
  description = "Password for AlloyDB"
}

variable "alloydb_ip_address" {
  type        = string
  description = "IP address for AlloyDB"
}

variable "alloydb_user_username" {
  type        = string
  description = "Username for AlloyDB user"
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
  type        = string
  sensitive   = true
  description = "Password for AlloyDB user"
}

variable "meddb_active_repo" {
  type        = string
  description = "Active repository for MedDB"
}

variable "meddb_table_medispan" {
  type        = string
  description = "Medispan table for MedDB"
}

variable "meddb_table_merative" {
  type        = string
  description = "Merative table for MedDB"
}

variable "meddb_search_function_medispan" {
  type        = string
  description = "Medispan search function for MedDB"
}

variable "meddb_search_function_merative" {
  type        = string
  description = "Merative search function for MedDB"
}

variable "medispan_api_version" {
  type        = string
  description = "Version for medispan API"
}

variable "labels" {
  description = "Default labels"
  type = object({
    owner         = string
    business-unit = string
    environment   = string
    application   = string
    service       = string
  })
}

variable "extra_labels" {
  description = "Extra labels"
  type        = map(string)
  default     = {}
}

variable "web_components_site_id" {
  type        = string
  description = "Site ID for web components"
}

variable "summarization_agents_users" {
  type        = set(string)
  default     = []
  description = "List of redirect_uri values for Summarization"
}

variable "summarization_agents_version" {
  type        = string
  default     = ""
  description = "If not empty, overrides version for summarization agents"
}



variable "audit_logger_api_url" {
  type        = string
  description = "URL for audit logger API"
  default     = "https://example.com" # Provide a dummy URL as default
}

variable "collab_admins" {
  type        = list(string)
  description = "List of collaboration admins"
  default     = []
}

# Redis Cache variables
variable "redis_port" {
  type        = number
  description = "Port for Redis instance"
}

variable "redis_version" {
  type        = string
  description = "Redis version"
}

variable "redis_size" {
  type        = number
  description = "Size of Redis instance in GB"
}

variable "redis_zone" {
  type        = string
  description = "Primary zone for Redis instance"
}

variable "redis_zone_alt" {
  type        = string
  description = "Alternative zone for Redis instance"
}

variable "redis_eviction_policy" {
  type        = string
  description = "Eviction policy for Redis instance"
}

variable "enable_cloudsql" {
  type        = bool
  default     = false
  description = "Flag to enable/disable CloudSQL resources"
}

variable "firestore_to_bq_streaming_enabled" {
  type        = bool
  default     = false
  description = "Flag to enable Firestore to BigQuery streaming"
}

variable "ado_source_sa_account_id" {
  description = "The account_id of the ADO service account to look up. Only used by non-provisioning environments like qa and stage."
  type        = string
  default     = ""
}

variable "vm_autoshutdown_policy" {
  description = "Policy for VM auto shutdown"
  type = object({
    enabled             = bool
    schedule_start      = string
    schedule_stop       = string
    timezone            = string
  })
}
