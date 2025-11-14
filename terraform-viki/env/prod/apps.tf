module "ai" {
  source = "./ai"

  app_project_id          = var.app_project_id
  dmz_project_id          = var.dmz_project_id
  mgmt_project_id         = var.mgmt_project_id
  env                     = var.env
  region                  = var.region
  okta_issuer             = module.okta_auth_server.okta_auth_server.issuer
  okta_audience           = var.okta_audience
  okta_scopes             = local.okta_scopes
  okta_service_issuer_url = var.okta_service_issuer_url
  okta_service_audience   = var.okta_service_audience
  okta_demo_client_id     = module.okta_demo_spa.okta_spa_app.client_id
  okta_admin_client_id    = module.okta_admin_spa.okta_spa_app.client_id
  cloud_run_services      = var.cloud_run_services
  apps_version            = var.apps_version
  labels                  = var.labels

  alert_notification_channel_emails = var.alert_notification_channel_emails

  autoscribe_version            = coalesce(var.autoscribe_version, var.apps_version)
  extract_and_fill_version      = coalesce(var.extract_and_fill_version, var.apps_version)
  demo_version                  = coalesce(var.demo_version, var.apps_version)
  nlparse_version               = coalesce(var.nlparse_version, var.apps_version)
  paperglass_version            = coalesce(var.cloud_run_services.paperglass_api.image_version, var.apps_version)
  frontends_version             = coalesce(var.frontends_version, var.apps_version)
  medication_extraction_version = coalesce(var.medication_extraction_version, var.apps_version)
  nurse_assistant_version       = coalesce(var.nurse_assistant_version, var.apps_version)
  medispan_api_version          = var.medispan_api_version
  skysense_scribe_api_version   = var.skysense_scribe_api_version

  forms_widgets_host                             = var.forms_widgets_host
  forms_api                                      = var.forms_api
  forms_api_key                                  = var.forms_api_key
  autoscribe_aws_role_arn                        = var.autoscribe_aws_role_arn
  nlparse_region                                 = var.nlparse_region
  aws_default_region                             = var.aws_default_region
  okta_disable                                   = var.okta_disable
  managers                                       = var.managers
  fhir_server_url                                = var.fhir_server_url
  fhir_data_store                                = var.fhir_data_store
  fhir_data_set                                  = var.fhir_data_set
  fhir_search_store_id                           = var.fhir_search_store_id
  medispan_api_url                               = var.medispan_api_url
  medispan_page_size                             = var.medispan_page_size
  okta_issuer_url                                = var.okta_issuer_url
  proxy_url                                      = var.proxy_url
  vpc_connector                                  = var.vpc_connector
  multimodal_temperature                         = var.multimodal_temperature
  orchestration_grader_schedule_window_enabled   = var.orchestration_grader_schedule_window_enabled
  command_outofband_cloudtask_enabled            = var.command_outofband_cloudtask_enabled
  cloudtask_max_concurrent_dispatches            = var.cloudtask_max_concurrent_dispatches
  cloudtask_max_dispatches_per_second            = var.cloudtask_max_dispatches_per_second
  cloudtask_quarantine_max_concurrent_dispatches = var.cloudtask_quarantine_max_concurrent_dispatches
  cloudtask_quarantine_max_dispatches_per_second = var.cloudtask_quarantine_max_dispatches_per_second

  opentelemetry_disabled      = var.opentelemetry_disabled
  opentelemetry_otlp_endpoint = var.opentelemetry_otlp_endpoint

  allow_public_access        = var.allow_public_access
  allow_public_access_widget = var.allow_public_access_widget

  firestore_to_bq_streaming_enabled = var.firestore_to_bq_streaming_enabled

  hhh_gcs_sa_email = var.hhh_gcs_sa_email

  mock_prompt_enabled = var.mock_prompt_enabled

  gcp_trace_enabled = var.gcp_trace_enabled

  newrelic_account_id      = var.newrelic_account_id
  newrelic_application_id  = var.newrelic_application_id
  newrelic_api_key         = var.newrelic_api_key
  newrelic_trust_key       = var.newrelic_trust_key
  newrelic_api_license_key = var.newrelic_api_license_key
  newrelic_api_browser_key = var.newrelic_api_browser_key
  newrelic_api_user_key    = var.newrelic_api_user_key
  newrelic_trace_enabled   = var.newrelic_trace_enabled

  step_classify_llm_model          = var.step_classify_llm_model
  step_extractmedication_llm_model = var.step_extractmedication_llm_model
  step_medispanmatch_llm_model     = var.step_medispanmatch_llm_model

  medication_extraction_api_url   = var.medication_extraction_api_url
  medication_extraction_api_2_url = var.medication_extraction_api_2_url

  medication_extraction_default_api_url    = var.medication_extraction_default_api_url
  medication_extraction_high_api_url       = var.medication_extraction_high_api_url
  medication_extraction_quarantine_api_url = var.medication_extraction_quarantine_api_url

  paperglass_api_token = var.paperglass_api_token

  entity_extraction_api_url = "https://ai-entity-extraction-${local.cloud_run_base_url}"
  djt_api_url               = "https://ai-distributed-job-tracking-${local.cloud_run_base_url}"
  admin_api_url             = "https://ai-admin-api-${local.cloud_run_base_url}"
  paperglass_api_url        = "https://ai-paperglass-api-${local.cloud_run_base_url}"

  cloudtask_queue_resolver_version = var.cloudtask_queue_resolver_version

  registered_app_ids = var.registered_app_ids

  cloudtask_v4_extraction_entrypoint_default_max_dispatches_per_second                   = var.cloudtask_v4_extraction_entrypoint_default_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_priority_max_dispatches_per_second                  = var.cloudtask_v4_extraction_entrypoint_priority_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_quarantine_max_dispatches_per_second                = var.cloudtask_v4_extraction_entrypoint_quarantine_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_default_default_max_dispatches_per_second           = var.cloudtask_v4_extraction_entrypoint_default_default_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_default_high_max_dispatches_per_second              = var.cloudtask_v4_extraction_entrypoint_default_high_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_default_quarantine_max_dispatches_per_second        = var.cloudtask_v4_extraction_entrypoint_default_quarantine_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second               = var.cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second                  = var.cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second            = var.cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second               = var.cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second                  = var.cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second            = var.cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second               = var.cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second                  = var.cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second
  cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second            = var.cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second
  cloudtask_paperglass_classification_quarantine_max_dispatches_per_second               = var.cloudtask_paperglass_classification_quarantine_max_dispatches_per_second
  cloudtask_paperglass_extraction_quarantine_max_dispatches_per_second                   = var.cloudtask_paperglass_extraction_quarantine_max_dispatches_per_second
  cloudtask_paperglass_command_schedule_max_dispatches_per_second                        = var.cloudtask_paperglass_command_schedule_max_dispatches_per_second
  cloudtask_v4_status_check_quarantine_max_dispatches_per_second                         = var.cloudtask_v4_status_check_quarantine_max_dispatches_per_second
  cloudtask_v4_paperglass_integration_status_update_quarantine_max_dispatches_per_second = var.cloudtask_v4_paperglass_integration_status_update_quarantine_max_dispatches_per_second
  cloudtask_v4_paperglass_medications_integration_quarantine_max_dispatches_per_second   = var.cloudtask_v4_paperglass_medications_integration_quarantine_max_dispatches_per_second

  collab_admins        = var.collab_admins
  audit_logger_api_url = var.audit_logger_api_url

  alloydb_password               = var.alloydb_password
  alloydb_ip_address             = google_alloydb_instance.primary.ip_address
  alloydb_user_username          = var.alloydb_user_username
  alloydb_user_password          = var.alloydb_user_password
  meddb_active_repo              = var.meddb_active_repo
  meddb_table_medispan           = var.meddb_table_medispan
  meddb_table_merative           = var.meddb_table_merative
  meddb_search_function_medispan = var.meddb_search_function_medispan
  meddb_search_function_merative = var.meddb_search_function_merative

  scribe_jwt_secret             = var.scribe_jwt_secret
  scribe_superuser_password     = var.scribe_superuser_password

  network_project_id = var.network_project_id
  network            = var.network
  redis_host         = module.redis.host
  redis_port         = module.redis.port
}
