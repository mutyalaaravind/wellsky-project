# THIS FILE SHOULD NOT BE COPIED TO OTHER ENVIRONMENT DIRECTORIES
# This file is ignored during a promotion and must be redefined in each cluster definition.

env             = "qa"
app_project_id  = "viki-qa-app-wsky"
dmz_project_id  = "viki-qa-dmz-wsky"
mgmt_project_id = "viki-dev-mgmt-wsky"

region = "us-east4"
zone   = "us-east4-a"

network_project_id = "core-prod-vpc-dev-01-wsky"
network            = "vpc-app-dev-01"
subnet_internal    = "subnet-viki-dev-int-ue4"
subnet_dmz         = "subnet-viki-dev-dmz-ue4"

vpc_connector = "projects/core-prod-vpc-dev-01-wsky/locations/us-east4/connectors/viki-dev-01"

managers = [
  "user:vipindas.koova@wellsky.com",
  "user:balki.nakshatrala@wellsky.com",
  "user:pratik.soni@wellsky.com",
  "user:suryakant.devkar@wellsky.com",
  "user:joel.dolisy@wellsky.com",
  "user:rahil.kidwai@wellsky.com",
  "user:eric.coiner@wellsky.com",
  "user:aravind.mutyala@wellsky.com",
  "user:ashwani.verma@wellsky.com",
  "user:anthony.collier@wellsky.com",
  "user:richard.gu@wellsky.com"
]

viewers = [
  "user:chris.may@wellsky.com"
]

support_users = [
  "user:aravind.mutyala@wellsky.com",
  "user:eric.coiner@wellsky.com"
]

okta_demo_users = [
  "vipindas.koova@wellsky.com",
  "manivarsh.adi@wellsky.com",
  "eric.coiner@wellsky.com",
  "maureen.oconnor@wellsky.com",
  "pratik.soni@wellsky.com",
  "aravind.mutyala@wellsky.com",
  "matt.moore@wellsky.com",
  "nicole.jackson@wellsky.com",
  "meenu.kamboj@wellsky.com",
  "ashwani.verma@wellsky.com",
]

okta_admin_users = [
  "balki.nakshatrala@wellsky.com",
  "vipindas.koova@wellsky.com",
  "eric.coiner@wellsky.com",
  "rahil.kidwai@wellsky.com",
  "pratik.soni@wellsky.com",
  "aravind.mutyala@wellsky.com",
  "richard.gu@wellsky.com",
  "ashwani.verma@wellsky.com"
]

alert_notification_channel_emails = {
  "vikialerts-teams-channel" = {
    email_address = "c9071af2.WellSky.com@amer.teams.ms"
    display_name  = "Viki Teams Notification Channel"
    force_delete  = true
    enabled       = true
  },
  "eric.coiner@wellsky.com" = {
    email_address = "eric.coiner@wellsky.com"
    display_name  = "Eric Coiner"
    force_delete  = true
    enabled       = true
  }
}

okta_org_name           = "wellsky-ciam"
okta_base_url           = "oktapreview.com"
okta_audience           = "viki.prod.wellsky.io" # qa and dev share same audience
okta_service_audience   = "viki.dev.wellsky.io"  # qa and dev share same audience (New auth server audience)
okta_service_issuer_url = "https://wellsky-ciam.oktapreview.com/oauth2/ausly1nwi0St4ZVs61d7"

# Cannot be same in dev & QA
demo_redirect_uris   = ["https://ai.viki-qa-app.prj.gcp.wellsky.io/login/callback"]
demo_trusted_origins = ["https://ai.viki-qa-app.prj.gcp.wellsky.io"]

admin_redirect_uris   = ["https://ai-admin-ui-18900418456.us-east4.run.app/login/callback"]
admin_trusted_origins = ["https://ai-admin-ui-18900418456.us-east4.run.app"]

apps_version                = "469c8794600162a67f0f611d5e2a9fcda2f7dc63"
autoscribe_version          = ""
extract_and_fill_version    = ""
demo_version                = ""
nlparse_version             = ""
paperglass_version          = ""
frontends_version           = ""
nurse_assistant_version     = "02abe0a6874b9d108417277364d77454415c8d76"
medispan_api_version        = "98c65bfece46f3659568c2a8e8cb8cfa9d20cffb"
skysense_scribe_api_version = "3e9db832eafbd4243b2cb2abf8939c86b5a8f2ac"
skysense_scribe_support_tool_app_version      = "7eba92936dcb6fd196955dbaa00d3c19494cdf3c"

cloud_run_services = {
  paperglass_widget = {    
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  paperglass_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 2048
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  paperglass_events = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 2048
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    concurrency         = 5
    allow_public_access = true
  }
  paperglass_external_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 2048
    timeout             = 180
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  entity_extraction = {
    image_version       = ""
    uvicorn_workers     = 2
    cpus                = 4
    memory              = 4096
    timeout             = 180
    min_instances       = 0
    max_instances       = "unlimited"
    allow_public_access = false
  }
  distributed_job_tracking = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 2
    memory              = 1024
    timeout             = 180
    min_instances       = 0
    max_instances       = 2
    allow_public_access = false
  }
  admin_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  admin_ui = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  nlparse_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  nlparse_widget = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 256
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  autoscribe_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  autoscribe_widget = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 256
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  extract_and_fill_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  extract_and_fill_events = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  extract_and_fill_events_vertexai = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  extract_and_fill_widget = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 256
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  medication_extraction_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  medication_extraction_api_2 = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  medication_extraction_default_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  medication_extraction_high_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  medication_extraction_quarantine_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  demo_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  demo_dashboard = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 256
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  nurse_assistant = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  medispan_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 2
    memory              = 2048
    timeout             = 180
    min_instances       = 0
    max_instances       = 2
    allow_public_access = false
  }
  # Skysense Scribe Services (previously hardcoded as always public)
  skysense_scribe_api = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 4096
    concurrency         = 32
    timeout             = 900
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  skysense_scribe_events = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 2048
    concurrency         = 8
    timeout             = 900
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  skysense_scribe_ws = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 2
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  skysense_scribe_tool = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 2
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  # Summarization Services (previously hardcoded as always public)
  summarization_agent_ui_server = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 2048
    timeout             = 900
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  summarization_hope_mcp_server = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 2048
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  paperglass_api_secondary = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 2048
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  paperglass_external_events = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 4
    memory              = 2048
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    concurrency         = 5
    allow_public_access = true
  }
  autoscribe_api_secondary = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }

  skysense_scribe_support_tool = {
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
}

forms_widgets_host      = "https://cf-widgets-vitumuotya-uk.a.run.app" # Dev CF
forms_api               = "https://cf-api-vitumuotya-uk.a.run.app/graphql"
forms_api_key           = ""
autoscribe_aws_role_arn = "arn:aws:iam::396116668159:role/viki-autoscribe-qa"
nlparse_region          = "us-central1"
aws_default_region      = "us-east-1"
okta_disable            = false

extraction_vertex_ai_index_size = "SHARD_SIZE_SMALL"

medispan_api_url   = "https://ct.dev.wellsky.io/api/v1/drug/information/search"
medispan_page_size = "100"

fhir_server_url      = ""
fhir_data_store      = ""
fhir_data_set        = ""
fhir_search_store_id = ""

hhh_ip           = "10.12.40.20" #qa.kinnser.net internal ip address (after you connect to VPN)
hhh_gcs_sa_email = "service-852814922729@gs-project-accounts.iam.gserviceaccount.com"

proxy_url = "https://10.201.145.220:10443"

okta_issuer_url = "https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7/v1/token"

multimodal_temperature = "0.0"

opentelemetry_disabled      = "false" # Set to "true" to disable OpenTelemetry
opentelemetry_otlp_endpoint = ""      # Set to the OTLP endpoint to send traces to

gcp_trace_enabled = "false"

cloudtask_queue_resolver_version = "v2"

cloudtask_max_concurrent_dispatches = "6"
cloudtask_max_dispatches_per_second = "1"

cloudtask_quarantine_max_concurrent_dispatches = "6"
cloudtask_quarantine_max_dispatches_per_second = "1"

# Used by the cloudtask queue resolver to determine if the app_id has a dedicated queue or not.  If not on this list, then it will use the default queues.
registered_app_ids = [
  "007",
  "hhh",
  "ltc"
]

cloudtask_v4_extraction_entrypoint_default_max_dispatches_per_second                   = "1"
cloudtask_v4_extraction_entrypoint_priority_max_dispatches_per_second                  = "1"
cloudtask_v4_extraction_entrypoint_quarantine_max_dispatches_per_second                = "1"
cloudtask_v4_extraction_entrypoint_default_default_max_dispatches_per_second           = "1"
cloudtask_v4_extraction_entrypoint_default_high_max_dispatches_per_second              = "1"
cloudtask_v4_extraction_entrypoint_default_quarantine_max_dispatches_per_second        = "1"
cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second               = "1"
cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second                  = "1"
cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second            = "1"
cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second               = "1"
cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second                  = "1"
cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second            = "1"
cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second               = "1"
cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second                  = "1"
cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second            = "1"
cloudtask_paperglass_classification_quarantine_max_dispatches_per_second               = "1"
cloudtask_paperglass_extraction_quarantine_max_dispatches_per_second                   = "1"
cloudtask_paperglass_command_schedule_max_dispatches_per_second                        = "50"
cloudtask_v4_status_check_quarantine_max_dispatches_per_second                         = "1"
cloudtask_v4_paperglass_integration_status_update_quarantine_max_dispatches_per_second = "1"
cloudtask_v4_paperglass_medications_integration_quarantine_max_dispatches_per_second   = "1"

orchestration_grader_schedule_window_enabled = "true"

mock_prompt_enabled = "false"

command_outofband_cloudtask_enabled = "false"

step_classify_llm_model          = "gemini-2.5-flash-lite"
step_extractmedication_llm_model = "gemini-2.5-flash-lite"
step_medispanmatch_llm_model     = "gemini-2.5-flash-lite"

medication_extraction_api_url            = "https://ai-medication-extraction-18900418456.us-east4.run.app"
medication_extraction_api_2_url          = "https://ai-medication-extraction-2-18900418456.us-east4.run.app"
medication_extraction_default_api_url    = "https://ai-medication-extraction-default-18900418456.us-east4.run.app"
medication_extraction_high_api_url       = "https://ai-medication-extraction-high-18900418456.us-east4.run.app"
medication_extraction_quarantine_api_url = "https://ai-medication-extraction-quarantine-18900418456.us-east4.run.app"

medication_extraction_version = ""

network_tags = [
  "health-check",
  "allow-internet-egress",
  "viki-qa-network"
]

allow_public_access        = true
allow_public_access_widget = true

firestore_to_bq_streaming_enabled = false

newrelic_account_id         = "6300155"     #"VIKI-NONProd"
newrelic_service_account_id = "r2r7l9zln3n" #VIKI_NONPROD
newrelic_application_id     = "1120362530"
newrelic_trust_key          = "672447"
newrelic_api_browser_key    = "NRJS-8f75d96a5ff55d624d5" # Why, you ask?  This will be exposed publicly in the browser js, so why complicate things...
newrelic_trace_enabled      = "false"

alloydb_ip_address             = "" # Unused in QA as apps.py sets as alloydb_ip_address = google_alloydb_instance.primary.ip_address
alloydb_user_username          = "meddb_user"
meddb_active_repo              = "alloydb-wcircuitbreaker" # "alloydb" | "firestore" | "alloydb-wcircuitbreaker"
meddb_table_medispan           = "medispan_drugs_gcp_768_2"
meddb_table_merative           = "merative_drugs_gcp_768_2"
meddb_search_function_medispan = "medispan_search_gcp_768_2"
meddb_search_function_merative = "merative_search_gcp_768_2"

# Redis Cache
redis_port            = 6379
redis_version         = "REDIS_6_X"
redis_size            = 1
redis_zone            = "us-east4-a"
redis_zone_alt        = "us-east4-b"
redis_eviction_policy = "volatile-ttl" // lru, allkeys-lru, volatile-lru, allkeys-random, volatile-random, volatile-ttl, noeviction

audit_logger_api_url = ""

collab_admins = []
labels = {
  owner         = "balki"
  business-unit = "viki"
  environment   = "qa"
  application   = ""
  service       = ""
}

# Scribe web component variables
web_components_site_id = "web-components-site-qa"

ado_source_sa_account_id = "dev-viki-new-ado-mediwareis"


# CloudSQL Configuration
enable_cloudsql = false

vm_autoshutdown_policy = {
    enabled             = true
    schedule_start      = "0 7 * * 1-5"  # 8:00 AM Monday to Friday
    schedule_stop       = "0 21 * * 1-5" # 8:00 PM Monday to Friday
    timezone            = "US/Central"
  }
