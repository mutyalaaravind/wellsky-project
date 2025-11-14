// IAM roles for human managers

// Allow managers to read/write Firestore
// https://stackoverflow.com/a/63705243
resource "google_project_iam_member" "firestore_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/datastore.user"
  member   = each.value
}

// Allow managers to manage Cloud Run
resource "google_project_iam_member" "cloud_run_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/run.admin"
  member   = each.value
}

// Allow managers to import/export Firestore
resource "google_project_iam_member" "firestore_manager_import_export" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/datastore.importExportAdmin"
  member   = each.value
}

// Allow managers to manage Firestore indices
resource "google_project_iam_member" "firestore_manager_indices" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/datastore.indexAdmin"
  member   = each.value
}

// Allow managers to manage Eventarc (https://github.com/hashicorp/terraform-provider-google/issues/14597)
resource "google_project_iam_member" "eventarc_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/eventarc.admin"
  member   = each.value
}

// Allow managers to manage GCS
resource "google_project_iam_member" "storage_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/storage.admin"
  member   = each.value
}

// Allow managers to have iam.serviceAccounts.ActAs permission (TODO: temporary, required for Eventarc trigger creation via GCP UI)
resource "google_project_iam_member" "service_account_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/iam.serviceAccountUser"
  member   = each.value
}

// Allow managers to manage PubSub
resource "google_project_iam_member" "pubsub_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/pubsub.admin"
  member   = each.value
}

// Allow managers to manage BigQuery
resource "google_project_iam_member" "bigquery_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/bigquery.admin"
  member   = each.value
}

// Allow managers to SSH into instances (https://cloud.google.com/iap/docs/managing-access#roles)
resource "google_project_iam_member" "iap_https_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/iap.httpsResourceAccessor"
  member   = each.value
}
resource "google_project_iam_member" "iap_tunnel_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/iap.tunnelResourceAccessor"
  member   = each.value
}
resource "google_project_iam_member" "os_admin_login_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/compute.osAdminLogin"
  member   = each.value
}

// Allow managers to manage IAM roles
resource "google_project_iam_member" "iam_admin_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/iam.securityAdmin"
  member   = each.value
}

// Allow managers to manage Firebase (e. g. delete extensions)
resource "google_project_iam_member" "firebase_admin_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/firebase.admin"
  member   = each.value
}

// Allow managers to impersonate SAs
resource "google_project_iam_member" "impersonator_manager_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/iam.serviceAccountTokenCreator"
  member   = each.value
}

resource "google_project_iam_member" "compute_access" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/compute.instanceAdmin"
  member   = each.value
}

resource "google_project_iam_member" "dataflow_permissions" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/dataflow.admin"
  member   = each.value
}

resource "google_project_iam_member" "service_role_permissions" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/iam.serviceAccountUser"
  member   = each.value
}

resource "google_project_iam_member" "dataform_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/dataform.admin"
  member   = each.value
}

resource "google_project_iam_member" "ai_platform_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/aiplatform.admin"
  member   = each.value
}

resource "google_project_iam_member" "notebooks_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/aiplatform.notebookRuntimeAdmin"
  member   = each.value
}

resource "google_project_iam_member" "notebooks_non_runtime_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/notebooks.admin"
  member   = each.value
}

resource "google_project_iam_member" "service_usage_consumer_role" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/serviceusage.serviceUsageConsumer"
  member   = each.value
}

resource "google_project_iam_member" "document_ai_admin_role" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/documentai.admin"
  member   = each.value
}

resource "google_project_iam_member" "discovery_engine_admin_role" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/discoveryengine.admin"
  member   = each.value
}

resource "google_project_iam_member" "service_usage_admin_role" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/serviceusage.serviceUsageAdmin"
  member   = each.value
}

resource "google_project_iam_member" "colab_runtime" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/aiplatform.colabEnterpriseAdmin"
  member   = each.value
}

resource "google_project_iam_member" "workstation_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/workstations.admin"
  member   = each.value
}

// Allow managers to import/export Firestore
resource "google_project_iam_member" "fhirstore_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/healthcare.fhirStoreAdmin"
  member   = each.value
}

// Allow managers to configure application integration service
resource "google_project_iam_member" "app_integrations_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/integrations.integrationAdmin"
  member   = each.value
}

resource "google_project_iam_member" "marketplace_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/consumerprocurement.entitlementManager"
  member   = each.value
}

resource "google_project_iam_member" "cloud_tasks_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/cloudtasks.admin"
  member   = each.value
}

resource "google_project_iam_member" "app_integration_editor_manager" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/integrations.integrationEditor"
  member   = each.value
}

resource "google_project_iam_member" "api_keys_admin_manager" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/serviceusage.apiKeysAdmin"
  member   = each.value
}

resource "google_project_iam_member" "logging_viewer" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/logging.viewer"
  member   = each.value
}

resource "google_project_iam_member" "managers_big_query_job_user_account_permissions" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/bigquery.jobUser"
  member   = each.value
}

resource "google_project_iam_member" "montoring_dashboard_editorr" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/monitoring.dashboardEditor"
  member   = each.value
}

resource "google_project_iam_member" "montoring_editor" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/monitoring.editor"
  member   = each.value
}

resource "google_project_iam_member" "cloud_task_queue_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/cloudtasks.queueAdmin"
  member   = each.value
}

# synthetic monitoring cloud function permissions in dmz project
resource "google_project_iam_member" "cloud_functions_admin" {
  for_each = var.managers
  project  = var.dmz_project_id
  role     = "roles/cloudfunctions.admin"
  member   = each.value
}

resource "google_project_iam_member" "iam_secrets_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/secretmanager.admin"
  member   = each.value
}

resource "google_project_iam_member" "iam_admin_monitoring_annotations_creator" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/monitoring.metricWriter"
  member   = each.value
}

resource "google_project_iam_member" "cloud_logging_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/logging.admin"
  member   = each.value
}

resource "google_project_iam_member" "alloydb_db_user" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/alloydb.databaseUser"
  member   = each.value
}

resource "google_project_iam_member" "dataproc_editor" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/dataproc.editor"
  member   = each.value
}

resource "google_project_iam_member" "alloydb_admin" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/alloydb.admin"
  member   = each.value
}


resource "google_project_iam_member" "resourcemanager_tag_viewer" {
  for_each = var.managers
  project  = var.app_project_id
  role     = "roles/resourcemanager.tagViewer"
  member   = each.value
}
