# locals {
#   mgmt = "dev"
#   region = "us-central1"
# }
# resource "google_notebooks_runtime" "default_runtime" {
#   name = "viki-notebooks-runtime-script"
#   location = local.region
#   project = var.app_project_id
#   access_config {
#     access_type = "SERVICE_ACCOUNT"
#     runtime_owner =  module.ai_sa.email
#   }
#   software_config {
#     post_startup_script_behavior = "RUN_EVERY_START"
#   }
#   virtual_machine {
#     virtual_machine_config {
#       machine_type = "n1-standard-4"
#       data_disk {
#         initialize_params {
#           disk_size_gb = "100"
#           disk_type = "PD_STANDARD"
#         }
#       }
#       network = "/projects/core-prod-vpc-${local.mgmt}-01-wsky/global/networks/vpc-app-${local.mgmt}-01"
#       subnet = "https://www.googleapis.com/compute/v1/projects/core-prod-vpc-${local.mgmt}-01-wsky/regions/${local.region}/subnetworks/subnet-viki-${local.mgmt}-int-ue4"
#     }
#   }
# }