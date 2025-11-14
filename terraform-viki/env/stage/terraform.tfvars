# THIS FILE SHOULD NOT BE COPIED TO OTHER ENVIRONMENT DIRECTORIES
# This file is ignored during a promotion and must be redefined in each cluster definition.

env             = "stage"
app_project_id  = "viki-stage-app-wsky"
dmz_project_id  = "viki-stage-dmz-wsky"
mgmt_project_id = "viki-prod-mgmt-wsky"

region = "us-east4"
zone   = "us-east4-a"

network_project_id = "core-prod-vpc-prod-01-wsky"
network            = "vpc-app-prod-01"
subnet_internal    = "subnet-viki-prod-int-ue4"
subnet_dmz         = "subnet-viki-prod-dmz-ue4"

vpc_connector = "projects/core-prod-vpc-prod-01-wsky/locations/us-east4/connectors/viki-prod-01"

managers = [
  "user:vipindas.koova@wellsky.com",
  "user:balki.nakshatrala@wellsky.com",
  "user:joel.dolisy@wellsky.com",
  "user:eric.coiner@wellsky.com",
  "user:maureen.oconnor@wellsky.com",
  "user:richard.gu@wellsky.com",
  "user:ashwani.verma@wellsky.com",
  "user:aravind.mutyala@wellsky.com"
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
  "maureen.oconnor@wellsky.com",
  "celeste.cantrell@wellsky.com",
  "balki.nakshatrala@wellsky.com",
  "eric.coiner@wellsky.com",
  "manivarsh.adi@wellsky.com",
  "aravind.mutyala@wellsky.com",
  "valarie.johnson@wellsky.com",
  "matt.moore@wellsky.com",
  "nicole.jackson@wellsky.com",
  "pratik.soni@wellsky.com",
  "meenu.kamboj@wellsky.com",
  "ashwani.verma@wellsky.com"
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

okta_org_name = "wellsky-ciam"
okta_base_url = "okta.com"
okta_audience = "viki.prod.wellsky.io"
#okta_server_audience = "viki.prod.wellsky.io"
okta_service_audience   = "viki.stage.wellsky.io" # qa and dev share same audience (New auth server audience)
okta_service_issuer_url = "https://wellsky-ciam.okta.com/oauth2/ausoijlmsbrPBXa2j5d7"

# Cannot be same in dev & QA
demo_redirect_uris   = ["https://ai.viki-stage-app.prj.gcp.wellsky.io/login/callback"]
demo_trusted_origins = ["https://ai.viki-stage-app.prj.gcp.wellsky.io"]

admin_redirect_uris   = ["https://admin.viki-stage-app.prj.gcp.wellsky.io/login/callback"]
admin_trusted_origins = ["https://admin.viki-stage-app.prj.gcp.wellsky.io"]

apps_version                = "b06f99c83291fd76d1c57e85e6493b17de157ae8"
autoscribe_version          = ""
extract_and_fill_version    = ""
demo_version                = ""
nlparse_version             = ""
paperglass_version          = ""
frontends_version           = ""
medispan_api_version        = "446a8f241d36897898abf607bd45ea9f9d2a441b"
skysense_scribe_api_version = "4ddabd26c285674255799f39d8ee35012d562b6d"
support_ui_app_version      = "7eba92936dcb6fd196955dbaa00d3c19494cdf3c"


cloud_run_services = {
  paperglass_widget = {
    service_names       = ["ai-paperglass-widget"]
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
    service_names       = ["ai-paperglass-api"]
    image_version       = ""
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 10
    allow_public_access = true
  }
  paperglass_events = {
    service_names       = ["ai-paperglass-events"]
    image_version       = ""
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 10
    concurrency         = 5
    allow_public_access = true
  }
  paperglass_external_api = {
    service_names       = ["ai-paperglass-external-api"]
    image_version       = ""
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 10
    allow_public_access = true
  }
  entity_extraction = {
    service_names       = ["ai-entity-extraction"]
    image_version       = ""
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 10
    allow_public_access = false
  }
  distributed_job_tracking = {
    service_names       = ["ai-distributed-job-tracking"]
    image_version       = ""
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 5
    allow_public_access = false
  }
  admin_api = {
    service_names       = ["ai-admin-api"]
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
    service_names       = ["ai-admin-ui"]
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
    service_names       = ["ai-nlparse-api"]
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
    service_names       = ["ai-nlparse-widget"]
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
    service_names       = ["ai-autoscribe-api"]
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
    service_names       = ["ai-autoscribe-widget"]
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
    service_names       = ["ai-extract-and-fill-api"]
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
    service_names       = ["ai-extract-and-fill-events"]
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
    service_names       = ["ai-extract-and-fill-events-vertexai"]
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
    service_names       = ["ai-extract-and-fill-widget"]
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
    service_names       = ["ai-medication-extraction"]
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
    service_names       = ["ai-medication-extraction-2"]
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
    service_names       = ["ai-medication-extraction-default"]
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
    service_names       = ["ai-medication-extraction-high"]
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
    service_names       = ["ai-medication-extraction-quarantine"]
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
    service_names       = ["ai-demo-api"]
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
    service_names       = ["ai-demo-dashboard"]
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
    service_names       = ["ai-nurse-assistant"]
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
    service_names       = ["ai-medispan-api-high", "ai-medispan-api-default", "ai-medispan-api-quarantine"]
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = false
  }
  # Skysense Scribe Services (previously hardcoded as always public)
  skysense_scribe_api = {
    service_names       = ["skysense-scribe-api"]
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  skysense_scribe_ws = {
    service_names       = ["skysense-scribe-ws"]
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  skysense_scribe_tool = {
    service_names       = ["skysense-scribe-tool"]
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  # Summarization Services (previously hardcoded as always public)
  summarization_agent_ui_server = {
    service_names       = ["summarization-agent-ui-server"]
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  # summarization_hope_mcp_server = {
  #   service_names       = ["summarization-demo-mcp-server"]
  #   image_version       = ""
  #   uvicorn_workers     = 1
  #   cpus                = 1
  #   memory              = 512
  #   timeout             = 600
  #   min_instances       = 0
  #   max_instances       = 2
  #   allow_public_access = true
  # }
  paperglass_api_secondary = {
    service_names       = ["ai-paperglass-api-secondary"]
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
    service_names       = ["ai-paperglass-external-events"]
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
    service_names       = ["ai2-autoscribe-api"]
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = true
  }
  support_ui = {
    service_names       = ["ai-support-ui"]
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

forms_widgets_host      = "https://cf-widgets-lb4cqj4ohq-uk.a.run.app" # CF for now pointing to QA
forms_api               = "https://cf-api-lb4cqj4ohq-uk.a.run.app/graphql"
forms_api_key           = ""
autoscribe_aws_role_arn = "arn:aws:iam::396116668159:role/viki-autoscribe-dev"
nlparse_region          = "us-central1"
aws_default_region      = "us-east-1"
okta_disable            = false

extraction_vertex_ai_index_size = "SHARD_SIZE_SMALL"

medispan_api_url   = "https://ct.dev.wellsky.io/api/v1/drug/information/search"
medispan_page_size = "100"

fhir_server_url      = "https://healthcare.googleapis.com/v1/projects/viki-dev-app-wsky/locations/us-central1/datasets/viki-dataset/fhirStores"
fhir_data_store      = "viki-fhir-store"
fhir_data_set        = "viki-dataset"
fhir_search_store_id = "fhir-store-search"

hhh_ip           = "10.12.60.20" #stg.kinnser.net internal ip address (after you connect to VPN)
hhh_gcs_sa_email = "service-852814922729@gs-project-accounts.iam.gserviceaccount.com"

proxy_url = "https://10.200.50.8:10443"

okta_issuer_url = "https://wellsky-ciam.okta.com/oauth2/aushirk9h5LbqrTwi5d7/v1/token"

multimodal_temperature = "0.0"

opentelemetry_disabled      = "false" # Set to "true" to disable OpenTelemetry
opentelemetry_otlp_endpoint = ""      # Set to the OTLP endpoint to send traces to

gcp_trace_enabled = "false"

cloudtask_queue_resolver_version = "v2"

cloudtask_max_concurrent_dispatches = "1500"
cloudtask_max_dispatches_per_second = "300"

cloudtask_quarantine_max_concurrent_dispatches = "1000"
cloudtask_quarantine_max_dispatches_per_second = "1.2"

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

medication_extraction_api_url            = "https://ai-medication-extraction-884147005953.us-east4.run.app"
medication_extraction_api_2_url          = "https://ai-medication-extraction-2-884147005953.us-east4.run.app"
medication_extraction_default_api_url    = "https://ai-medication-extraction-default-884147005953.us-east4.run.app"
medication_extraction_high_api_url       = "https://ai-medication-extraction-high-884147005953.us-east4.run.app"
medication_extraction_quarantine_api_url = "https://ai-medication-extraction-quarantine-884147005953.us-east4.run.app"

medication_extraction_version = ""

network_tags = [
  "health-check",
  "allow-internet-egress",
  "viki-stage-network"
]

allow_public_access        = true
allow_public_access_widget = true

firestore_to_bq_streaming_enabled = false

newrelic_account_id         = "6300155"     #"VIKI-NONProd"
newrelic_service_account_id = "r2r7l9zln3n" #VIKI_NONPROD
newrelic_application_id     = "1120362531"
newrelic_trust_key          = "672447"
newrelic_api_browser_key    = "NRJS-8f75d96a5ff55d624d5" # Why, you ask?  This will be exposed publicly in the browser js, so why complicate things...
newrelic_trace_enabled      = "false"

alloydb_ip_address             = "10.235.120.117" # Using static IP while AlloyDB instance is disabled
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
  environment   = "stage"
  application   = ""
  service       = ""
}

# Scribe web component variables
web_components_site_id = "scribe-web-components-stage"

ado_source_sa_account_id = "prod-viki-new-ado-mediwareis"


# CloudSQL Configuration
enable_cloudsql = false

vm_autoshutdown_policy = {
    enabled             = true
    schedule_start      = "0 7 * * 1-5"  # 8:00 AM Monday to Friday
    schedule_stop       = "0 21 * * 1-5" # 8:00 PM Monday to Friday
    timezone            = "US/Central"
  }
