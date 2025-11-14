# THIS FILE SHOULD NOT BE COPIED TO OTHER ENVIRONMENT DIRECTORIES 
# This file is ignored during a promotion and must be redefined in each cluster definition.

env             = "prod"
app_project_id  = "viki-prod-app-wsky"
dmz_project_id  = "viki-prod-dmz-wsky"
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
  "user:ashwani.verma@wellsky.com"
]

viewers = [
  "user:chris.may@wellsky.com",
  "user:richard.gu@wellsky.com",
]

support_users = [
  "user:aravind.mutyala@wellsky.com",
  "user:eric.coiner@wellsky.com"
]

okta_demo_users = [
  "vipindas.koova@wellsky.com",
  "balki.nakshatrala@wellsky.com",
  "eric.coiner@wellsky.com",
  "matt.moore@wellsky.com",
  "nicole.jackson@wellsky.com",
  "meenu.kamboj@wellsky.com",
  "pratik.soni@wellsky.com",
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

okta_org_name = "wellsky-ciam"
okta_base_url = "okta.com"
okta_audience = "viki.dev.wellsky.io"
#okta_server_audience = "viki.prod.wellsky.io"
okta_service_audience   = "viki.prod.wellsky.io"
okta_service_issuer_url = "https://wellsky-ciam.okta.com/oauth2/ausp4grwqqlMCEgBa5d7"


# Cannot be same in dev & QA
demo_redirect_uris   = ["https://ai.viki-prod-app.prj.gcp.wellsky.io/login/callback"]
demo_trusted_origins = ["https://ai.viki-prod-app.prj.gcp.wellsky.io"]

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
skysense_scribe_api_version = "23b7447c577d95aa9133d96478af009981a37324"


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
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 10
    allow_public_access = true
  }
  paperglass_events = {
    image_version       = ""
    uvicorn_workers     = 9
    cpus                = 4
    memory              = 4096
    timeout             = 600
    min_instances       = 0
    max_instances       = 10
    concurrency         = 20
    allow_public_access = true
  }
  paperglass_api_external = {
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
    image_version       = ""
    uvicorn_workers     = 1
    cpus                = 1
    memory              = 512
    timeout             = 600
    min_instances       = 0
    max_instances       = 2
    allow_public_access = false
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

hhh_ip           = ""
hhh_gcs_sa_email = "service-752542941384@gs-project-accounts.iam.gserviceaccount.com"

proxy_url = "https://kinnser.net"

okta_issuer_url = "https://wellsky-ciam.okta.com/oauth2/ausf79o4jdnCkJlOy5d7/v1/token"

multimodal_temperature = "0.0"

opentelemetry_disabled      = "false" # Set to "true" to disable OpenTelemetry
opentelemetry_otlp_endpoint = ""      # Set to the OTLP endpoint to send traces to

gcp_trace_enabled = "false"

cloudtask_queue_resolver_version = "v2"

cloudtask_max_concurrent_dispatches = "1500"
cloudtask_max_dispatches_per_second = "300"

cloudtask_quarantine_max_concurrent_dispatches = "1500"
cloudtask_quarantine_max_dispatches_per_second = "300"

# Used by the cloudtask queue resolver to determine if the app_id has a dedicated queue or not.  If not on this list, then it will use the default queues.
registered_app_ids = [
  "007",
  "hhh",
  "ltc"
]

cloudtask_v4_extraction_entrypoint_default_max_dispatches_per_second                   = "2.65" # Reduced from 2.75 to 2.65 to avoid buildup in the classification queue
cloudtask_v4_extraction_entrypoint_priority_max_dispatches_per_second                  = "3"
cloudtask_v4_extraction_entrypoint_quarantine_max_dispatches_per_second                = "2.65"
cloudtask_v4_extraction_entrypoint_default_default_max_dispatches_per_second           = "2.75"
cloudtask_v4_extraction_entrypoint_default_high_max_dispatches_per_second              = "3"
cloudtask_v4_extraction_entrypoint_default_quarantine_max_dispatches_per_second        = "2.5"
cloudtask_v4_extraction_entrypoint_hhh_default_max_dispatches_per_second               = "2.75"
cloudtask_v4_extraction_entrypoint_hhh_high_max_dispatches_per_second                  = "3"
cloudtask_v4_extraction_entrypoint_hhh_quarantine_max_dispatches_per_second            = "2.75"
cloudtask_v4_extraction_entrypoint_ltc_default_max_dispatches_per_second               = "0.5"
cloudtask_v4_extraction_entrypoint_ltc_high_max_dispatches_per_second                  = "1"
cloudtask_v4_extraction_entrypoint_ltc_quarantine_max_dispatches_per_second            = "0.5"
cloudtask_v4_extraction_entrypoint_007_default_max_dispatches_per_second               = "1"
cloudtask_v4_extraction_entrypoint_007_high_max_dispatches_per_second                  = "2"
cloudtask_v4_extraction_entrypoint_007_quarantine_max_dispatches_per_second            = "1"
cloudtask_paperglass_classification_quarantine_max_dispatches_per_second               = "20"
cloudtask_paperglass_extraction_quarantine_max_dispatches_per_second                   = "20"
cloudtask_paperglass_command_schedule_max_dispatches_per_second                        = "50"
cloudtask_v4_status_check_quarantine_max_dispatches_per_second                         = "100"
cloudtask_v4_paperglass_integration_status_update_quarantine_max_dispatches_per_second = "100"
cloudtask_v4_paperglass_medications_integration_quarantine_max_dispatches_per_second   = "100"

orchestration_grader_schedule_window_enabled = "true"

mock_prompt_enabled = "false"

command_outofband_cloudtask_enabled = "false"

step_classify_llm_model          = "gemini-2.5-flash-lite"
step_extractmedication_llm_model = "gemini-2.5-flash-lite"
step_medispanmatch_llm_model     = "gemini-2.5-flash-lite"

medication_extraction_api_url            = "https://ai-medication-extraction-884147005953.us-east4.run.app"
medication_extraction_api_2_url          = "https://ai-medication-extraction-2-884147005953.us-east4.run.app"
medication_extraction_default_api_url    = "https://ai-medication-extraction-default-446272789005.us-east4.run.app"
medication_extraction_high_api_url       = "https://ai-medication-extraction-high-446272789005.us-east4.run.app"
medication_extraction_quarantine_api_url = "https://ai-medication-extraction-quarantine-446272789005.us-east4.run.app"

medication_extraction_version = ""

network_tags = [
  "health-check",
  "allow-internet-egress",
]

allow_public_access        = true
allow_public_access_widget = true

firestore_to_bq_streaming_enabled = false

newrelic_account_id         = "6300154"     #VIKI_PROD
newrelic_service_account_id = "qy6lzm7zkr0" #VIKI_PROD
newrelic_application_id     = "1120362532"
newrelic_trust_key          = "672447"
newrelic_api_browser_key    = "NRJS-1a520371fe402fc0f28" # Why, you ask?  This will be exposed publicly in the browser js, so why complicate things...
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
  environment   = "production"
  application   = ""
  service       = ""
}

# Scribe web component variables
web_components_site_id = "scribe-web-components"

ado_source_sa_account_id = "prod-viki-ado-mediwareis"


# CloudSQL Configuration
enable_cloudsql = false
