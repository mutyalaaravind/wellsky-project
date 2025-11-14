# locals {
#   mgmt   = "dev"
#   region = "us-central1"
# }
# resource "google_notebooks_runtime" "default_runtime" {
#   #for_each = var.collab_admins
#   name     = "viki-notebooks-runtime-script-1"
#   location = local.region
#   project  = var.app_project_id
#   access_config {
#     access_type   = "SINGLE_USER"
#     runtime_owner = "user:balki.nakshatrala@wellsky.com"
#   }
#   software_config {
#     install_gpu_driver = true
#     post_startup_script_behavior = "RUN_EVERY_START"
#   }
#   virtual_machine {
#     virtual_machine_config {
#       machine_type = "g2-standard-16"
#       data_disk {
#         initialize_params {
#           disk_size_gb = "100"
#           disk_type    = "PD_STANDARD"
#         }
#       }
#       accelerator_config {
#         core_count = "1"
#         type       = "NVIDIA_L4"
#       }
#       network = "/projects/core-prod-vpc-${local.mgmt}-01-wsky/global/networks/vpc-app-${local.mgmt}-01"
#       subnet  = "https://www.googleapis.com/compute/v1/projects/core-prod-vpc-${local.mgmt}-01-wsky/regions/${local.region}/subnetworks/subnet-viki-${local.mgmt}-int-ue4"
#     }
#   }
# }