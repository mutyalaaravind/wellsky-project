module "deepgram-wellsky-hosted" {
  source  = "terraform.wellsky.net/wellsky/vm-container/gcp"
  version = "0.5.0"
  # insert required variables here

  project_id      = var.app_project_id
  instance_name   = "deepgram-wellsky-poc"
  region          = var.region
  container_image = "deepgram-ubatntu"
  subnetwork      = "projects/${var.network_project_id}/regions/${var.region}/subnetworks/${var.subnet_internal}"
  zone            = var.zone
  labels          = var.labels
  desired_status  = "TERMINATED"
  service_account = "viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com"
  extra_labels    = { "tf-policy" = "exclude" }
  network_tags    = ["allow-internet-egress", "health-check", "viki-dev-network"]
  boot_disk = ({
    image       = "deepgram-ubatntu"
    auto_delete = true
    source      = null
    device_name = "deepgram-wellsky-poc"
    mode        = "READ_WRITE" # The mode in which to attach this disk, either READ_WRITE or READ_ONLY
    size        = 50
  })
}

#module "deepgram-wellsky-hosted_gpu" {
#  source  = "terraform.wellsky.net/wellsky/vm-container/gcp"
#  version = "0.5.0"
# insert required variables here

#   project_id       = var.app_project_id
#   instance_name    = "deepgram-wellsky-poc2"
#   region           = var.region
#   container_image  = "deepgram-ubatntu"
#   subnetwork       = "projects/${var.network_project_id}/regions/${var.region}/subnetworks/${var.subnet_internal}"
#   zone             = var.zone
#   labels           = var.labels
#   service_account  = "viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com"
#   extra_labels     = { "tf-policy" = "exclude" }
#   network_tags     =  ["allow-internet-egress", "health-check", "viki-dev-network"]
#  instance_type    = "nvidia-tesla-t4"
#   boot_disk        = ({
#                       image       = "deepgram-ubatntu"
#                        auto_delete = true
#                        source      = null
#                        device_name = "deepgram-wellsky-poc"
#                        mode        = "READ_WRITE" # The mode in which to attach this disk, either READ_WRITE or READ_ONLY
#                        size        = 50
#                    })
#}

