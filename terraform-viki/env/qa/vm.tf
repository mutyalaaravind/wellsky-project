# data "google_compute_network" "default" {
#   name    = var.network
#   project = var.network_project_id
# }

data "google_compute_image" "ubuntu" {
  family  = "ubuntu-2204-lts"
  project = "org-dev-images-wsky"
}

resource "random_id" "this" {
  byte_length = 4
}

data "google_project" "default" {
  project_id = var.app_project_id
}

resource "google_project_iam_member" "gce_sa_vm_start" {
  project = var.app_project_id
  role    = "organizations/531195336225/roles/instance_state_admin_wsky"

  member = "serviceAccount:service-${data.google_project.default.number}@compute-system.iam.gserviceaccount.com"
}


module "hhh_dev_env_vm" {
  source     = "git@github.com:mediwareinc/terraform-gcp-vm.git?ref=v0.6.12"
  name       = "hhh-dev-vm-${random_id.this.hex}"
  zone       = var.zone
  project_id = var.app_project_id

  network_project_id = var.network_project_id
  machine_type       = "e2-standard-4"
  image              = data.google_compute_image.ubuntu.self_link
  boot_size          = 50

  resource_policies = var.vm_autoshutdown_policy.enabled ? [
    google_compute_resource_policy.vm_nightly_shutdown[0].id
  ] : []

  subnetwork   = var.subnet_internal
  network_tags = var.network_tags

  labels = var.labels

  depends_on = [google_project_iam_member.gce_sa_vm_start]
}


# snap install docker
# az acr login --name wellsky.azurecr.io
# gcloud cp -r gs://hh-dev/source .
# gcloud compute ssh --zone "us-east4-a" "hhh-dev-vm-8dad34fc" --tunnel-through-iap --project "viki-dev-app-wsky"
# gcloud compute ssh --zone "us-east4-a" "hhh-dev-vm-8dad34fc" --project "viki-dev-app-wsky" --ssh-flag="-L 12345:10.201.145.200:8500"