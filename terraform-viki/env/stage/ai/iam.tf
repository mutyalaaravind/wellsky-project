locals {
  // Required when creating a secret because it tries to for_each over accessors
  ai_sa_id    = "viki-ai-${var.env}-sa"
  ai_sa_email = "${local.ai_sa_id}@${var.app_project_id}.iam.gserviceaccount.com"
}

module "ai_sa" {
  source       = "git@github.com:mediwareinc/terraform-gcp-service-account.git?ref=v0.4.11"
  account_id   = local.ai_sa_id
  display_name = "VIKI AI service account ${var.env}"
  project_id   = var.app_project_id
  labels       = var.labels
}

resource "google_cloud_run_service_iam_member" "ai_service_invocation" {
  for_each = local.api_services
  project  = var.app_project_id
  service  = each.value.name
  location = each.value.location
  role     = "roles/run.invoker"
  member   = module.ai_sa.iam_email
}

resource "google_project_iam_member" "ai_aiplatform_admin" {
  project = var.app_project_id
  role    = "roles/aiplatform.admin"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "ai_speech_admin" {
  project = var.app_project_id
  role    = "roles/speech.admin"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "ai_documentai_admin" {
  project = var.app_project_id
  role    = "roles/documentai.admin"
  member  = module.ai_sa.iam_email
}

# Allows viki to export spans to Cloud Trace
resource "google_project_iam_member" "opentelemetry_agent" {
  project = var.app_project_id
  role    = "roles/cloudtrace.agent"
  member  = module.ai_sa.iam_email
}

# this default sa needs storage permissiosn to create the extraction index
resource "google_storage_bucket_iam_member" "ai_vertex_storage_admin" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.admin"
  member = "serviceAccount:service-${data.google_project.app_project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}

# Grant AI Platform service account access to the viki-ai-provisional bucket
resource "google_storage_bucket_iam_member" "ai_vertex_provisional_bucket_access" {
  bucket = module.ai_provisional_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:service-${data.google_project.app_project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "ai_firestore_access" {
  project = var.app_project_id
  role    = "roles/datastore.user"
  member  = module.ai_sa.iam_email
}

resource "google_pubsub_topic_iam_member" "event_orchestration_complete_topic_pubsub_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.event_orchestration_complete_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}

resource "google_pubsub_topic_iam_member" "event_medication_publish_topic_pubsub_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.event_medication_publish_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}

resource "google_pubsub_topic_iam_member" "command_scheduledwindow_1_topic_pubsub_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.command_scheduledwindow_1_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}
resource "google_project_iam_member" "ai_eventarc_events" {
  project = var.app_project_id
  role    = "roles/eventarc.eventReceiver"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "ai_healthcare" {
  project = var.app_project_id
  role    = "roles/healthcare.nlpServiceViewer"
  member  = module.ai_sa.iam_email
}

// Allow backend to sign GCS URLs
resource "google_project_iam_member" "ai_storage_signer" {
  project = var.app_project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "sa_act_as" {
  project = var.app_project_id
  role    = "roles/iam.serviceAccountUser"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "notebook_admin" {
  project = var.app_project_id
  role    = "roles/notebooks.admin"
  member  = module.ai_sa.iam_email
}

# this is needed for the notebook to be able to access the storage bucket
resource "google_project_iam_member" "sstorage_admin" {
  project = var.app_project_id
  role    = "roles/storage.admin"
  member  = module.ai_sa.iam_email
}

# discovery engine admin
resource "google_project_iam_member" "discovery_engine_admin" {
  project = var.app_project_id
  role    = "roles/discoveryengine.admin"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "healthcare_fhir_store_admin" {
  project = var.app_project_id
  role    = "roles/healthcare.fhirStoreAdmin"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "healthcare_fhir_store_resource_editor" {
  project = var.app_project_id
  role    = "roles/healthcare.fhirResourceEditor"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "cloud_tasks_admin" {
  project = var.app_project_id
  role    = "roles/cloudtasks.admin"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "app_integration_editor" {
  project = var.app_project_id
  role    = "roles/integrations.integrationEditor"
  member  = module.ai_sa.iam_email
}

data "google_project" "app_project" {
  project_id = var.app_project_id
}

resource "google_project_iam_member" "aiplatform_user_account_permissions" {
  project = var.app_project_id
  role    = "roles/aiplatform.user"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "aiplatform_viewer_account_permissions" {
  project = var.app_project_id
  role    = "roles/aiplatform.viewer"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "medlm_service_viewer" {
  project = var.app_project_id
  role    = "roles/healthcare.medlmServiceViewer"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_binding" "eventarc_viewer_binding" {
  project = var.app_project_id
  role    = "roles/eventarc.viewer"

  members = [
    "serviceAccount:${module.ai_sa.email}"
  ]
}

resource "google_pubsub_topic_iam_member" "extraction_pubsub_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.orchestraction_extraction_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_binding" "eventarc_admin_binding" {
  project = var.app_project_id
  role    = "roles/eventarc.admin"

  members = [
    "serviceAccount:${module.ai_sa.email}"
  ]
}

# resource "google_pubsub_topic_iam_member" "raw_change_log_pubsub_publisher" {
#   project = var.app_project_id
#   topic   = google_pubsub_topic.raw_change_log_topic.name
#   role    = "roles/pubsub.publisher"
#   member  = module.ai_sa.iam_email
# }

resource "google_project_iam_member" "bq_permissions" {
  project = var.app_project_id
  role    = "roles/bigquery.dataEditor"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "bg_metadata_vewer" {
  project = var.app_project_id
  role    = "roles/bigquery.metadataViewer"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "bigquery_jobs_role" {
  project = var.app_project_id
  role    = "roles/bigquery.jobUser"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "cloud_sink_bigquery_editor_role" {
  project = var.app_project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${data.google_project.app_project.number}@gcp-sa-logging.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cloud_sink_bigquery_jobs_role" {
  project = var.app_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:service-${data.google_project.app_project.number}@gcp-sa-logging.iam.gserviceaccount.com"
}

resource "google_pubsub_topic_iam_member" "medication_extraction_v4_pubsub_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.medication_extraction_v4_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}

resource "google_pubsub_topic_iam_member" "paperglass_integration_pubsub_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.paperglass_integration_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}

resource "google_pubsub_topic_iam_member" "medication_extraction_doc_status_topic_publisher" {
  project = var.app_project_id
  topic   = google_pubsub_topic.medication_extraction_doc_status_topic.name
  role    = "roles/pubsub.publisher"
  member  = module.ai_sa.iam_email
}

resource "google_project_iam_member" "monitoring_annotations_creator" {
  project = var.app_project_id
  role    = "roles/monitoring.metricWriter"
  member  = module.ai_sa.iam_email
}

# resource "google_pubsub_topic_iam_member" "hhh_pubsub_subscriber" {
#   project = var.app_project_id
#   topic   = "projects/hhh-dev-app-wsky/topics/HHH-AM-Attachments"
#   role    = "roles/pubsub.subscriber"
#   member  = module.ai_sa.iam_email
# }

# Grant summarization agents stage service account access to AI Platform
resource "google_project_iam_member" "summarization_agents_stage_ai_access" {
  project = var.app_project_id
  role    = "roles/aiplatform.admin"
  member  = "serviceAccount:summarization-agents-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com"
}

# Grant summarization agents stage service account Vertex AI user permissions
resource "google_project_iam_member" "summarization_agents_stage_vertex_ai_user" {
  project = var.app_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:summarization-agents-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com"
}

# Grant sonny summarization agents stage service account Vertex AI user permissions
resource "google_project_iam_member" "sonny_summarization_agents_stage_vertex_ai_user" {
  project = var.app_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:summarization-agents-stage-sa@sonny-stage-app-wsky.iam.gserviceaccount.com"
}

# Grant summarization agents stage service account ability to invoke Cloud Run services
resource "google_project_iam_member" "summarization_agents_stage_cloud_run_invoker" {
  project = var.app_project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:summarization-agents-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com"
}

# Grant summarization agents stage service account ability to read and write to Cloud Storage buckets
resource "google_project_iam_member" "summarization_agents_stage_storage_object_admin" {
  project = var.app_project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:summarization-agents-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com"
}

# Grant summarization agents stage service account access to Firestore DB
resource "google_project_iam_member" "summarization_agents_stage_firestore_access" {
  project = var.app_project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:summarization-agents-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com"
}

# Grant AI service account Cloud SQL permissions for proxy access
resource "google_project_iam_member" "ai_cloudsql_client" {
  project = var.app_project_id
  role    = "roles/cloudsql.client"
  member  = module.ai_sa.iam_email
}
