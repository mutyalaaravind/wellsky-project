data "google_compute_network" "redis" {
  name    = var.network
  project = var.network_project_id
}


module "redis" {
  source       = "git@github.com:mediwareinc/terraform-gcp-memorystore?ref=v0.3.2"
  name         = "${local.name_prefix}-redis"
  display_name = "${local.name_prefix}-redis"

  project = var.app_project_id
  region  = var.region

  tier           = "BASIC" # BASIC | STANDARD_HA
  memory_size_gb = var.redis_size
  redis_version  = var.redis_version

  port = var.redis_port

  location_id = var.redis_zone
  #alternative_location_id = var.redis_zone_alt  # For STANDARD_HA tier only

  use_private_g_services = true

  authorized_network = data.google_compute_network.redis.id

  labels = var.labels

  redis_configs = {
    "maxmemory-policy" = var.redis_eviction_policy
    # RDB Configuration for snapshots
    # "save"                          = "900 1 300 10 60 10000"
    # "rdbcompression"                = "yes"
    # "rdbchecksum"                   = "yes"
    # AOF Configuration for maximum durability
    # "appendonly"                    = "yes"
    # "appendfsync"                   = "everysec"
    # "auto-aof-rewrite-percentage"   = "100"
    # "auto-aof-rewrite-min-size"     = "64mb"
  }

  # Database registry =============================================
  # 0: Distributed Job Tracking
}