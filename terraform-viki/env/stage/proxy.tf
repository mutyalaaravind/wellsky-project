
module "hhh_proxy" {
  source  = "git@github.com:mediwareinc/terraform-gcp-reverse-proxy.git?ref=v2.1.0"
  #version = "1.0.1"

  project_id   = var.app_project_id
  name         = "hhh-proxy"
  image_name   = "ubuntu-2204-lts-20240201-ce9b358"
  subnetwork   = "projects/${var.network_project_id}/regions/${var.region}/subnetworks/${var.subnet_internal}"
  zone         = var.zone
  network_tags = var.network_tags
  port_map = {
    10080 = {
      ip   = var.hhh_ip
      port = 80
    }
    10443 = {
      ip   = var.hhh_ip
      port = 443
    }
    80 = {
      ip   = "192.178.52.174" //google ip just for testing
      port = 80
    }
    443 = {
      ip   = "192.178.52.174" //google ip just for testing
      port = 443
    }
  }

  labels       = merge(var.labels, { exposure = "public" })
  #extra_labels = { "tf-policy" = "exclude" }
  resource_policies = var.vm_autoshutdown_policy.enabled ? [
    google_compute_resource_policy.vm_nightly_shutdown[0].id
  ] : []
}

# resource "google_iap_tunnel_instance_iam_member" "iap_tunnel_member" {
#   for_each = toset(var.managers)
#   project  = var.app_project_id
#   instance = module.hhh_proxy.instance_id
#   zone     = var.region
#   role     = "roles/iap.tunnelResourceAccessor"
#   member   = each.value
# }



# resource "google_compute_instance_iam_member" "compute_instance_member" {
#   for_each      = toset(var.managers)
#   project       = var.app_project_id
#   instance_name = module.hhh_proxy.name
#   zone          = var.region
#   role          = "roles/compute.instanceAdmin.v1"
#   member        = each.value
# }