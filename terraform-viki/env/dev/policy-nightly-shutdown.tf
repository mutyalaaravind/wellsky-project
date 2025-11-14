resource "google_compute_resource_policy" "vm_nightly_shutdown" {
  count       = var.vm_autoshutdown_policy.enabled ? 1 : 0

  name        = "${local.name_prefix}-vm-nightly-shutdown"
  region      = var.region
  description = "Stop/Start VM instances"
  project     = var.app_project_id

  instance_schedule_policy {
    vm_start_schedule {
      schedule = var.vm_autoshutdown_policy.schedule_start
    }
    vm_stop_schedule {
      schedule = var.vm_autoshutdown_policy.schedule_stop
    }
    time_zone = var.vm_autoshutdown_policy.timezone
  }
}
