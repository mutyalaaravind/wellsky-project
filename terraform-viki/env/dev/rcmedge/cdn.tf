locals {
  frontends     = toset(["web"])
  cdn_subdomain = "rcmedge-cdn"
  cdn_dns_name  = "${local.cdn_subdomain}.${data.google_dns_managed_zone.cdn_dns_zone.dns_name}"
  cdn_dns_zone  = "viki-${var.env}-dmz-pub"

  env_jsons = {
    web = {
      VERSION      = var.rcmedge_version,
      API_BASE_URL = module.rcmedge_rules_api.url,
    }
  }
}

data "google_dns_managed_zone" "cdn_dns_zone" {
  project = var.dmz_project_id
  name    = local.cdn_dns_zone
}

module "rcmedge_cdn" {
  source               = "git@github.com:mediwareinc/terraform-gcp-website-bucket?ref=v1.0.0"
  bucket_location      = "US"
  bucket_objectadmins  = var.managers
  bucket_project_id    = var.dmz_project_id
  bucket_storageadmins = var.managers
  dns_name             = local.cdn_dns_name
  dns_project_id       = var.dmz_project_id
  dns_zone             = local.cdn_dns_zone
  name                 = "rcmedge-cdn-${var.env}"
  labels               = var.labels
  enable_cdn           = true
  #main_page            = "/web/latest/index.html"
  #not_found_page       = "404.html"
}

data "google_storage_bucket" "static_bucket" {
  name = "viki-static-dev" // TODO: Reference parent module's static_bucket.name
}

locals {
  // Source path
  // E.g. bundle.js path would be: gs://viki-static-dev/frontends/sample/dev-368-gcf8f64e/static/js/bundle.js
  frontends_source_dir_prefix = "gs://${data.google_storage_bucket.static_bucket.name}/rcmedge"
  // Destination path
  // E.g. bundle.js path would be: gs://viki-ai-cdn-dev/frontends/sample/latest/static/js/bundle.js
  cdn_target_dir_prefix = "gs://${module.rcmedge_cdn.website_bucket}"
}

resource "null_resource" "rcm_edge_cdn_static_content" {
  for_each = local.frontends
  triggers = {
    # Copy assets from the source bucket to the CDN bucket only if the version changes
    version = var.rcmedge_version
  }
  provisioner "local-exec" {
    command = <<-EOT
      # Copy microfrontend's static content to the CDN bucket
      gsutil -m cp -r ${local.frontends_source_dir_prefix}/${each.value}/${var.rcmedge_version}/* ${local.cdn_target_dir_prefix}/${each.value}/latest
      gsutil -m cp -r ${local.frontends_source_dir_prefix}/${each.value}/${var.rcmedge_version} ${local.cdn_target_dir_prefix}/${each.value}/${var.rcmedge_version}

      # Copy microfrontend's env.json to the CDN bucket
      cat > /tmp/env_${each.value}.json <<EOF
      ${jsonencode(local.env_jsons[each.value])}
      EOF
      gsutil cp /tmp/env_${each.value}.json ${local.cdn_target_dir_prefix}/${each.value}/latest/config/env.json
      gsutil cp /tmp/env_${each.value}.json ${local.cdn_target_dir_prefix}/${each.value}/${var.rcmedge_version}/config/env.json
    EOT
  }
  depends_on = [module.rcmedge_cdn]
}

resource "null_resource" "rcm_edge_invalidate_cdn_cache" {
  provisioner "local-exec" {
    command = "gcloud compute url-maps invalidate-cdn-cache rcmedge-cdn-${var.env}-url-map --path '/*' --project ${var.dmz_project_id}"
  }

  triggers = {
    commit_id = var.rcmedge_version
  }

}
