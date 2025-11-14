locals {
  admin_dns_name = "admin.viki-${var.env}-app.prj.gcp.wellsky.io."
  admin_network_name = "wsky-viki-ai-admin-${var.env}-lb"
}

# TEMPORARILY COMMENTED OUT TO ALLOW SECRET IMPORTS
# resource "google_dns_record_set" "admin_lb" {
#   project      = var.app_project_id
#   managed_zone = "viki-${var.env}-app-pub"
#   name         = local.admin_dns_name
#   type         = "A"
#   ttl          = 300 # 5 min
#   rrdatas      = [module.admin_lb.external_ip]
# }

# TEMPORARILY COMMENTED OUT TO ALLOW SECRET IMPORTS
# module "admin_lb" {
#   source  = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
#   version = "~> 12.0"
#   name    = local.admin_network_name
#   project = var.app_project_id
#
#   url_map        = google_compute_url_map.admin.self_link
#   create_url_map = false
#
#   ssl                             = true
#   managed_ssl_certificate_domains = [local.admin_dns_name]
#   random_certificate_suffix       = true
#   https_redirect                  = true
#   labels                          = var.labels
#
#   backends = {
#     admin-api = {
#       description = "Admin API"
#       groups = [
#         {
#           group = google_compute_region_network_endpoint_group.neg["admin_api"].id
#         }
#       ]
#       enable_cdn              = false
#       security_policy         = null
#       custom_request_headers  = null
#       custom_response_headers = local.response_headers
#
#       iap_config = {
#         enable               = false
#         oauth2_client_id     = ""
#         oauth2_client_secret = ""
#       }
#
#       log_config = {
#         enable      = false
#         sample_rate = null
#       }
#     }
#
#     admin-ui = {
#       description = "Admin UI"
#       groups = [
#         {
#           group = google_compute_region_network_endpoint_group.neg["admin_ui"].id
#         }
#       ]
#       enable_cdn              = false
#       security_policy         = null
#       custom_request_headers  = null
#       custom_response_headers = local.response_headers
#
#       iap_config = {
#         enable               = false
#         oauth2_client_id     = ""
#         oauth2_client_secret = ""
#       }
#
#       log_config = {
#         enable      = false
#         sample_rate = null
#       }
#     }
#   }
# }
#
# resource "google_compute_url_map" "admin" {
#   project = var.app_project_id
#
#   name            = local.admin_network_name
#   default_service = module.admin_lb.backend_services["admin-ui"].self_link
#
#   host_rule {
#     hosts        = ["*"]
#     path_matcher = "adminpaths"
#   }
#
#   path_matcher {
#     default_service = module.admin_lb.backend_services["admin-ui"].self_link
#     name            = "adminpaths"
#
#     path_rule {
#       paths   = ["/login/callback"]
#       service = module.admin_lb.backend_services["admin-ui"].self_link
#
#       route_action {
#         url_rewrite {
#           path_prefix_rewrite = "/"
#         }
#       }
#     }
#
#     path_rule {
#       paths   = ["/api/*"]
#       service = module.admin_lb.backend_services["admin-api"].self_link
#
#       route_action {
#         url_rewrite {
#           path_prefix_rewrite = "/"
#         }
#       }
#     }
#   }
# }