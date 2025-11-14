
module "alloydb_proxy" {
  source  = "terraform.wellsky.net/wellsky/reverse-proxy/gcp"
  version = "1.0.1"

  project_id   = var.app_project_id
  name         = "alloydb-proxy"
  image_name   = "ubuntu-2204-lts-20230127-a8f8e62"
  subnetwork   = "projects/${var.network_project_id}/regions/${var.region}/subnetworks/${var.subnet_internal}"
  zone         = var.zone
  network_tags = var.network_tags
  port_map     = {}

  labels       = var.labels
  extra_labels = { "tf-policy" = "exclude" }
}