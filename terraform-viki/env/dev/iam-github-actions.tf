
# Grant Vertex AI admin permissions
resource "google_project_iam_member" "github_actions_aiplatform_admin" {
  project = var.app_project_id
  role    = "roles/aiplatform.admin"
  member  = module.github_builder[0].iam_email
}

# Grant Vertex AI user permissions (required for model access)
resource "google_project_iam_member" "github_actions_aiplatform_user" {
  project = var.app_project_id
  role    = "roles/aiplatform.user"
  member  = module.github_builder[0].iam_email
}

# Grant access to Claude Sonnet 4 model via AI Platform model user role
resource "google_project_iam_member" "github_actions_aiplatform_modeluser" {
  project = var.app_project_id
  role    = "roles/aiplatform.modelUser"
  member  = module.github_builder[0].iam_email
}

# Grant access to service account token creator (needed for AI Platform authentication)
resource "google_project_iam_member" "github_actions_token_creator" {
  project = var.app_project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = module.github_builder[0].iam_email
}

resource "google_project_iam_member" "github_actions_secret_assessor" {
  project = var.app_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = module.github_builder[0].iam_email
}