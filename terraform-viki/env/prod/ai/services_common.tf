locals {
  api_services = tomap({
    autoscribe_api          = module.autoscribe_api,
    extract_and_fill_api    = module.extract_and_fill_api,
    extract_and_fill_events = module.extract_and_fill_events,
    nlparse_api             = module.nlparse_api,
    paperglass_api          = module.paperglass_api,
    paperglass_events       = module.paperglass_events,
    medispan_api            = module.medispan_api,
    medispan_api_quarantine = module.medispan_api_quarantine,
    medispan_api_high       = module.medispan_api_high
    skysense-scribe-api     = module.skysense-scribe-api
    admin_api               = module.admin_api
  })
  frontend_services = tomap({
    autoscribe_widget       = module.autoscribe_widget,
    extract_and_fill_widget = module.extract_and_fill_widget,
    demo_dashboard          = module.demo_dashboard,
    nlparse_widget          = module.nlparse_widget,
    paperglass_widget       = module.paperglass_widget,
    admin_ui                = module.admin_ui
  })
}

resource "google_compute_region_network_endpoint_group" "neg" {
  for_each              = merge(local.api_services, local.frontend_services)
  project               = var.app_project_id
  name                  = "${replace(each.key, "_", "-")}-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  cloud_run {
    service = each.value.name
  }
}
