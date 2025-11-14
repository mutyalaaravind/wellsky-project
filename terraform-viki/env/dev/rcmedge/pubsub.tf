module "rcmedge_pubsub_topic" {
  source         = "terraform.wellsky.net/wellsky/pubsub/gcp"
  version        = "1.0.0"
  topic          = "execute_claim_rule"
  iam_publishers = [module.rcmedge_sa.iam_email]
  push_subscriptions = [
    {
      name                  = "execute_claim_rule-subscription"
      push_endpoint         = "${module.rcmedge_rules_events.url}/pubsub/execute_claim_rule"
      service_account_email = module.rcmedge_sa.email
      ack_deadline_seconds = 600
    }
  ]
  labels     = var.labels
  project_id = var.app_project_id
  depends_on = [module.rcmedge_rules_events]
}


module "rcmedge_claim_rules_extractor_pubsub_topic" {
  source         = "terraform.wellsky.net/wellsky/pubsub/gcp"
  version        = "1.0.0"
  topic          = "extract_claim_rules"
  iam_publishers = [module.rcmedge_sa.iam_email]
  push_subscriptions = [
    {
      name                  = "extract_claim_rules-subscription"
      push_endpoint         = "${module.rcmedge_rules_events.url}/pubsub/extract_claim_rules"
      service_account_email = module.rcmedge_sa.email
      ack_deadline_seconds = 600
    }
  ]
  labels     = var.labels
  project_id = var.app_project_id
  depends_on = [module.rcmedge_rules_events]
}