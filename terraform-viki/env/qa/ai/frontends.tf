locals {
  frontends     = toset(["sample", "medwidget"])
  cdn_subdomain = "ai-cdn"
  cdn_dns_name  = "${local.cdn_subdomain}.${data.google_dns_managed_zone.dns_zone.dns_name}"
  cdn_dns_zone  = "viki-${var.env}-dmz-pub"

  env_jsons = {
    sample = {
      VERSION = var.frontends_version,
    },
    medwidget = {
      API_URL                  = var.paperglass_api_secondary_url,
      VERSION                  = var.frontends_version,
      NEWRELIC_ACCOUNT_ID      = var.newrelic_account_id,
      NEWRELIC_APPLICATION_ID  = var.newrelic_application_id,
      NEWRELIC_TRUST_KEY       = var.newrelic_trust_key,
      NEWRELIC_API_BROWSER_KEY = var.newrelic_api_browser_key,
    },
  }
}

data "google_dns_managed_zone" "cdn_dns_zone" {
  project = var.dmz_project_id
  name    = local.cdn_dns_zone
}

module "cdn" {
  source               = "git@github.com:mediwareinc/terraform-gcp-website-bucket?ref=v1.0.0"
  bucket_location      = "US"
  bucket_objectadmins  = var.managers
  bucket_project_id    = var.dmz_project_id
  bucket_storageadmins = var.managers
  dns_name             = local.cdn_dns_name
  dns_project_id       = var.dmz_project_id
  dns_zone             = local.cdn_dns_zone
  name                 = "viki-ai-cdn-${var.env}"
  labels               = var.labels
  enable_cdn           = true
  /* main_page = "index.html" */
  /* not_found_page = "404.html" */
}

data "google_storage_bucket" "static_bucket" {
  name = "viki-static-dev" // TODO: Reference parent module's static_bucket.name
}

locals {
  // Source path
  // E.g. bundle.js path would be: gs://viki-static-dev/frontends/sample/dev-368-gcf8f64e/static/js/bundle.js
  frontends_source_dir_prefix = "gs://${data.google_storage_bucket.static_bucket.name}/frontends"
  // Destination path
  // E.g. bundle.js path would be: gs://viki-ai-cdn-dev/frontends/sample/latest/static/js/bundle.js
  cdn_target_dir_prefix = "gs://${module.cdn.website_bucket}"
}

resource "null_resource" "cdn_static_content" {
  for_each = local.frontends
  triggers = {
    # Copy assets from the source bucket to the CDN bucket only if the version changes
    version = var.frontends_version
  }
  provisioner "local-exec" {
    command = <<-EOT
      # Copy microfrontend's static content to the CDN bucket
      gsutil -m cp -r ${local.frontends_source_dir_prefix}/${each.value}/${var.frontends_version}/* ${local.cdn_target_dir_prefix}/${each.value}/latest
      gsutil -m cp -r ${local.frontends_source_dir_prefix}/${each.value}/${var.frontends_version} ${local.cdn_target_dir_prefix}/${each.value}/${var.frontends_version}

      # Copy microfrontend's env.json to the CDN bucket
      cat > /tmp/env_${each.value}.json <<EOF
      ${jsonencode(local.env_jsons[each.value])}
      EOF
      gsutil cp /tmp/env_${each.value}.json ${local.cdn_target_dir_prefix}/${each.value}/latest/config/env.json
      gsutil cp /tmp/env_${each.value}.json ${local.cdn_target_dir_prefix}/${each.value}/${var.frontends_version}/config/env.json
    EOT
  }
  depends_on = [module.cdn]
}

resource "null_resource" "invalidate_cdn_cache" {
  provisioner "local-exec" {
    command = "gcloud compute url-maps invalidate-cdn-cache viki-ai-cdn-${var.env}-url-map --path '/*' --project ${var.dmz_project_id}"
  }

  triggers = {
    commit_id = var.frontends_version
  }

}
