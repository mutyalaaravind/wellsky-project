# Example configuring a general-project with the GCP integrations

locals {
  default_metrics_polling_interval = 300

  gcp_labels = var.labels
  gcp_labels_extra = {
    "managed-by" = "terraform"
  }
  gcp_project_id = var.app_project_id

  newrelic_account_id   = var.newrelic_account_id
  newrelic_gcp_sa_email = "${var.newrelic_service_account_id}@newrelic-gcp.iam.gserviceaccount.com"
}

module "new_relic_config" {
  source = "git@github.com:mediwareinc/terraform-newrelic-gcp-integration.git?ref=v0.1.0"

  gcp_project_id   = local.gcp_project_id
  gcp_labels       = local.gcp_labels
  gcp_labels_extra = local.gcp_labels_extra

  newrelic_account_id   = local.newrelic_account_id
  newrelic_gcp_sa_email = local.newrelic_gcp_sa_email


  #   app_engine = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  big_query = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
    fetch_tags               = true
  }

  #   big_table = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  #   composer = {
  #     enabled = false
  #   }

  #   data_flow = {
  #     enabled = true
  #     // use defaults
  #   }

  #   data_proc = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  #   data_store = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  #   fire_base_database = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  #   fire_base_hosting = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  #   fire_base_storage = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  fire_store = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
  }


  functions = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
  }

  // Testing that the variable is optional
  //interconnect = {
  //  enabled = false
  //}

  #   kubernetes = {
  #     enabled = true
  #     //use defaults
  #   }

  load_balancing = {
    enabled = true
    //use defaults
  }

  #   mem_cache = {
  #     enabled = false
  #   }

  pub_sub = {
    enabled = true
    //use defaults
  }

  #   redis = {
  #     enabled = true
  #     //use defaults
  #   }

  router = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
  }

  run = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
  }

  #   spanner = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #     fetch_tags               = false
  #   }

  #   sql = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  storage = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
  }

  #   virtual_machines = {
  #     enabled                  = true
  #     metrics_polling_interval = local.default_metrics_polling_interval
  #   }

  vpc_access = {
    enabled                  = true
    metrics_polling_interval = local.default_metrics_polling_interval
  }
}

# Test Ouputs
# locals {
#   newrelic_cloud_gcp_link_account_id = module.general_example.id
# }