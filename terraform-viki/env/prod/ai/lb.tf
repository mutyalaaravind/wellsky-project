locals {
  dns_name = "ai.viki-${var.env}-app.prj.gcp.wellsky.io."
  // Stolen from https://github.com/mediwareinc/aos-monorepo/blob/1d73a12c1a40e31050792600d1f0a25d2e79e9f9/terraform-gcp/env/qa/lb.tf#L4
  network_name = "wsky-viki-ai-${var.env}-lb"
  response_headers = [
    # "Content-Security-Policy: default-src 'self' 'unsafe-inline' *.wellsky.io https://fonts.googleapis.com https://code.getmdl.io https://fonts.gstatic.com https://js-agent.newrelic.com https://bam-cell.nr-data.net;",
    "Referrer-Policy: no-referrer",
    "Strict-Transport-Security: max-age=31536000; includeSubDomains",
    "X-Content-Type-Options: nosniff",
    "X-Frame-Options: DENY"
  ]
}

resource "google_dns_record_set" "lb" {
  project      = var.app_project_id
  managed_zone = "viki-${var.env}-app-pub"
  name         = local.dns_name
  type         = "A"
  ttl          = 300 # 5 min
  rrdatas      = [module.lb.external_ip]
}

module "lb" {
  source  = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
  version = "~> 12.0"
  name    = local.network_name
  project = var.app_project_id

  url_map        = google_compute_url_map.default.self_link
  create_url_map = false

  ssl                             = true
  managed_ssl_certificate_domains = [local.dns_name]
  random_certificate_suffix       = true
  https_redirect                  = true
  labels                          = var.labels

  backends = {
    autoscribe-api = {
      # Backend ID cannot contain underscores
      description = "AutoScribe API"
      groups = [
        {
          group = google_compute_region_network_endpoint_group.neg["autoscribe_api"].id
        }
      ]
      enable_cdn              = false
      security_policy         = null
      custom_request_headers  = null
      custom_response_headers = local.response_headers

      iap_config = {
        enable               = false
        oauth2_client_id     = ""
        oauth2_client_secret = ""
      }

      log_config = {
        enable      = false
        sample_rate = null
      }
    }

    autoscribe-widget = {
      description = "AutoScribe Widget"
      groups = [
        {
          group = google_compute_region_network_endpoint_group.neg["autoscribe_widget"].id
        }
      ]
      enable_cdn              = false
      security_policy         = null
      custom_request_headers  = null
      custom_response_headers = local.response_headers

      iap_config = {
        enable               = false
        oauth2_client_id     = ""
        oauth2_client_secret = ""
      }

      log_config = {
        enable      = false
        sample_rate = null
      }
    }

    demo-dashboard = {
      description = "Demo Dashboard"
      groups = [
        {
          group = google_compute_region_network_endpoint_group.neg["demo_dashboard"].id
        }
      ]
      enable_cdn              = false
      security_policy         = null
      custom_request_headers  = null
      custom_response_headers = local.response_headers

      iap_config = {
        enable               = false
        oauth2_client_id     = ""
        oauth2_client_secret = ""
      }

      log_config = {
        enable      = false
        sample_rate = null
      }
    }
  }
}

resource "google_compute_url_map" "default" {
  project = var.app_project_id

  // note that this is the name of the load balancer
  name            = local.network_name
  default_service = module.lb.backend_services["demo-dashboard"].self_link

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    # SSO
    default_service = module.lb.backend_services["demo-dashboard"].self_link
    name            = "allpaths"

    path_rule {
      paths   = ["/login/callback"]
      service = module.lb.backend_services["demo-dashboard"].self_link

      route_action {
        url_rewrite {
          # Remove prefix before sending request to container
          path_prefix_rewrite = "/"
        }
      }
    }

    path_rule {
      paths = ["/autoscribe"]

      url_redirect {
        path_redirect          = "/autoscribe/"
        redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
        strip_query            = false
      }
    }

    path_rule {
      paths   = ["/autoscribe/api/*"]
      service = module.lb.backend_services["autoscribe-api"].self_link

      route_action {
        url_rewrite {
          # Remove prefix before sending request to container
          path_prefix_rewrite = "/"
        }
      }
    }

    path_rule {
      paths   = ["/autoscribe/*"]
      service = module.lb.backend_services["autoscribe-widget"].self_link

      route_action {
        url_rewrite {
          # Remove prefix before sending request to container
          path_prefix_rewrite = "/"
        }
      }
    }
  }
}
