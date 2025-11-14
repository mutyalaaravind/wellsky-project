# LLM Instructions: Add Support UI Configuration to Production Environment

## Context
This instruction file contains precise steps to add Support UI (React-based Scribe Session Support application) configuration to the production environment in the terraform-viki repository. The configuration is initially added in a commented-out state to allow for controlled deployment when ready.

## Objective
Add Support UI Cloud Run service configuration to the `env/prod` folder, including:
1. New Terraform configuration file for Support UI service
2. Cloud Run service configuration in terraform.tfvars
3. Minor formatting fixes to ensure files end with newlines

## Instructions

### Step 1: Create Support UI Terraform Configuration File

**File Path**: `terraform-viki/env/prod/ai/services_support.tf`

**Action**: Create a new file with the following content:

```terraform
/*
# Support App - React UI for Scribe Session Support
# COMMENTED OUT - Uncomment when ready to deploy to production

module "support_ui_envjson" {
  source              = "git@github.com:mediwareinc/terraform-gcp-secret.git?ref=v0.4.1"
  labels              = var.labels
  managers            = []
  accessors           = ["serviceAccount:${local.ai_sa_email}"]
  name                = "ai-support-ui-${var.env}-envjson"
  project_id          = var.app_project_id
  replication_regions = [var.region]
  secret_data = jsonencode({
    # API URLs for the support app
    API_URLS = {
      LOCAL = "http://127.0.0.1:8000"
      DEV   = "https://skysense-scribe-api-zqftmopgsq-uk.a.run.app"
      QA    = "https://skysense-scribe-api-p32qledfyq-uk.a.run.app"
      STAGE = "https://skysense-scribe-api-zzygbs3ypa-uk.a.run.app"
      PROD  = "https://skysense-scribe-api-cocynqqo6a-uk.a.run.app"
    }
    # Current environment
    ENVIRONMENT      = upper(var.env)
    VERSION          = coalesce(var.cloud_run_services.support_ui.image_version, var.apps_version)

    # OAuth/Authentication settings (if needed in future)
    OKTA_ISSUER      = var.okta_issuer
    OKTA_CLIENT_ID   = var.okta_admin_client_id
    OKTA_DISABLE     = var.okta_disable
  })
  skip_secret_data = false
}

module "support_ui" {
  source                = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name                  = "ai-support-ui"
  location              = var.region
  service_account_email = module.ai_sa.email
  image                 = "${var.region}-docker.pkg.dev/${var.mgmt_project_id}/images/ai-support-ui:${coalesce(var.cloud_run_services.support_ui.image_version, var.apps_version)}"
  port                  = 80

  # Mount the env.json configuration
  volume_mounts = {
    envjson = {
      mount_path = "/usr/share/nginx/html/config/"
    }
  }
  volumes = {
    envjson = {
      secret = {
        secret_name = module.support_ui_envjson.name
        items = [{
          key  = "latest"
          path = "env.json"
        }]
      }
    }
  }

  labels              = var.labels
  ingress             = "all"
  min_instances       = var.cloud_run_services.support_ui.min_instances
  max_instances       = var.cloud_run_services.support_ui.max_instances == "unlimited" ? null : var.cloud_run_services.support_ui.max_instances
  memory              = var.cloud_run_services.support_ui.memory
  cpus                = var.cloud_run_services.support_ui.cpus
  project_id          = var.app_project_id
  timeout             = var.cloud_run_services.support_ui.timeout
  depends_on          = [module.support_ui_envjson]
}

# Tag bindings for public access
resource "google_tags_location_tag_binding" "support_ui_public_access" {
  count     = var.cloud_run_services.support_ui.allow_public_access ? 1 : 0
  location  = var.region
  parent    = "//run.googleapis.com/projects/${data.google_project.app_project.number}/locations/${var.region}/services/ai-support-ui"
  tag_value = data.google_tags_tag_value.public_access_tag_value.id
}

# IAM bindings for public access
resource "google_cloud_run_service_iam_binding" "support_ui_public_invoker" {
  count    = var.cloud_run_services.support_ui.allow_public_access ? 1 : 0
  location = var.region
  project  = var.app_project_id
  service  = "ai-support-ui"
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}

# Output the service URL
output "support_ui_url" {
  value = module.support_ui.url
  description = "URL of the Support UI Cloud Run service"
}
*/
```

**Note**: The entire file content is wrapped in `/* ... */` comment blocks, so it won't be active until uncommented.

### Step 2: Add Support UI Configuration to terraform.tfvars

**File Path**: `terraform-viki/env/prod/terraform.tfvars`

**Action**: Locate the `cloud_run_services` block and add the following commented-out configuration block after the `admin_ui` service configuration (around line 179, after the admin_ui closing brace):

```hcl
  # COMMENTED OUT - Uncomment when ready to deploy to production
  # support_ui = {
  #   image_version       = ""
  #   uvicorn_workers     = 1
  #   cpus                = 1
  #   memory              = 512
  #   timeout             = 600
  #   min_instances       = 0
  #   max_instances       = 2
  #   allow_public_access = true
  # }
```

**Exact Location**: Add this block after the `admin_ui` configuration block and before the closing brace of `cloud_run_services`.

### Step 3: Ensure Files End with Newlines

**File Path**: `terraform-viki/env/prod/variables.tf`

**Action**: Ensure the file ends with a newline character after the closing brace of the last variable definition (`ado_source_sa_account_id`).

**File Path**: `terraform-viki/env/prod/iam-viewers.tf`

**Action**: Ensure the file ends with a newline character after the closing brace of the last resource (`google_project_iam_member.support_users_bigquery_job_user`).

## Validation Steps

After applying these changes, run the following commands to verify:

```bash
# 1. Check that the new file exists
ls -la terraform-viki/env/prod/ai/services_support.tf

# 2. Verify the file is properly commented out
grep -c "^/\*" terraform-viki/env/prod/ai/services_support.tf  # Should return 1
grep -c "^\*/" terraform-viki/env/prod/ai/services_support.tf  # Should return 1

# 3. Check terraform.tfvars for the support_ui block
grep -A 10 "# support_ui" terraform-viki/env/prod/terraform.tfvars

# 4. Verify git diff shows the expected changes
cd terraform-viki && git diff env/prod/
```

## Deployment Notes

When ready to deploy Support UI to production:

1. **In `env/prod/ai/services_support.tf`**: Remove the opening `/*` and closing `*/` comment markers
2. **In `env/prod/terraform.tfvars`**: Uncomment the `support_ui` block by removing the `#` characters
3. Set the appropriate `image_version` if needed (or leave empty to use `apps_version`)
4. Run terraform plan to review changes
5. Apply terraform changes

## Technical Details

**Service Configuration**:
- **Name**: ai-support-ui
- **Type**: Cloud Run service
- **Port**: 80 (nginx)
- **Resources**: 1 CPU, 512MB RAM
- **Scaling**: 0-2 instances
- **Access**: Public (when enabled)
- **Configuration**: env.json mounted from GCP Secret Manager

**Dependencies**:
- Requires `module.ai_sa` (AI service account)
- Uses terraform modules from mediwareinc GitHub repositories
- Depends on GCP Secret Manager for environment configuration

## Summary

This configuration adds the Support UI service to production in a safe, commented-out state. The infrastructure code is present but inactive, allowing for easy activation when the service is ready for production deployment.
