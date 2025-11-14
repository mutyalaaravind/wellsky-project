locals {
  # Map collections to Eventarc events
  trigger_map = {
    // List of collections to create a "created" trigger for
    created = [
      {
        collection  = "extract_embeddings_metadata",
        destination = module.extract_and_fill_events.name,
      },
      {
        collection  = "extract_schema_chunks",
        destination = module.extract_and_fill_events_vertexai.name,
      },
      {
        collection  = "autoscribe_transactions",
        destination = module.extract_and_fill_events.name,
      },
      {
        collection  = "extract_commands",
        destination = module.extract_and_fill_events.name,
      },
      // Paperglass DDD events
      {
        collection  = "paperglass_commands",
        destination = module.paperglass_events.name,
      },
      {
        collection  = "paperglass_events",
        destination = module.paperglass_events.name,
      },
      {
        collection  = "skysense-scribe-assessment-reports",
        destination = module.skysense_scribe_events.name,
      },
      {
        collection  = "skysense-scribe-scribes",
        destination = module.skysense_scribe_events.name,
      },
      {
        collection  = "skysense-scribe-upload-chunks",
        destination = module.skysense_scribe_events.name,
      },
      {
        collection  = "skysense-scribe-assessments",
        destination = module.skysense_scribe_events.name,
      }
    ],
    updated = [
      {
        collection  = "autoscribe_transactions",
        destination = module.extract_and_fill_events.name,
      },
      {
        collection  = "skysense-scribe-scribes",
        destination = module.skysense_scribe_events.name,
      },
      {
        collection  = "skysense-scribe-upload-chunks",
        destination = module.skysense_scribe_events.name,
      },
      {
        collection  = "skysense-scribe-assessment-reports",
        destination = module.skysense_scribe_events.name,
      },
      {
        collection  = "skysense-scribe-assessments",
        destination = module.skysense_scribe_events.name,
      }
    ]
    // List of collections to create a "written" trigger for
    written = [
    ]
  }
  triggers = flatten([
    for event, definitions in local.trigger_map : [
      for definition in definitions : {
        event       = event,
        collection  = definition.collection,
        destination = definition.destination,
      }
    ]
  ])
}

//trigger for ai-{env} db
resource "google_eventarc_trigger" "firestore_trigger" {
  for_each = { for trigger in local.triggers : "${trigger.collection}_${trigger.event}" => trigger }

  project  = var.app_project_id
  name     = format("%s-%s-%s", var.env, replace(each.value.collection, "_", "-"), each.value.event)
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.firestore.document.v1.${each.value.event}"
  }
  matching_criteria {
    attribute = "database"
    value     = google_firestore_database.database.name
  }

  matching_criteria {
    attribute = "document"
    value     = "${each.value.collection}/*"
    operator  = "match-path-pattern"
  }

  destination {
    cloud_run_service {
      service = each.value.destination
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/firestore"
    }
  }
  service_account = module.ai_sa.email

  # https://github.com/hashicorp/terraform-provider-google/issues/14597
  event_data_content_type = "application/protobuf"

  labels = var.labels
}

//triggers for default db
resource "google_eventarc_trigger" "firestore_trigger_default" {
  for_each = { for trigger in local.triggers : "${trigger.collection}_${trigger.event}" => trigger }

  project  = var.app_project_id
  name     = format("%s-%s-%s-%s", var.env, replace(each.value.collection, "_", "-"), each.value.event, "default")
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.firestore.document.v1.${each.value.event}"
  }
  matching_criteria {
    attribute = "database"
    value     = google_firestore_database.default_database.name
  }
  matching_criteria {
    attribute = "document"
    value     = "${each.value.collection}/*"
    operator  = "match-path-pattern"
  }

  destination {
    cloud_run_service {
      service = each.value.destination
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/firestore"
    }
  }
  service_account = module.ai_sa.email

  # https://github.com/hashicorp/terraform-provider-google/issues/14597
  event_data_content_type = "application/protobuf"

  labels = var.labels
}

resource "google_eventarc_trigger" "firestore_trigger_scribe_default" {
  project  = var.app_project_id
  name     = format("%s-%s-%s-%s", var.env, "skysense-scribe-upload-chunks-chunks", "created", "default")
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.firestore.document.v1.created"
  }
  matching_criteria {
    attribute = "database"
    value     = google_firestore_database.default_database.name
  }
  matching_criteria {
    attribute = "document"
    value     = "skysense-scribe-poc-upload-chunks/{docId}/chunks/{chunkId}"
    operator  = "match-path-pattern"
  }

  destination {
    cloud_run_service {
      service = module.skysense_scribe_events.name
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/firestore"
    }
  }

  service_account = module.ai_sa.email

  # https://github.com/hashicorp/terraform-provider-google/issues/14597
  event_data_content_type = "application/protobuf"

  labels = var.labels
}

//triggers for new multi region firestore db
resource "google_eventarc_trigger" "firestore_trigger_viki_database" {
  for_each = { for trigger in local.triggers : "${trigger.collection}_${trigger.event}" => trigger }

  project  = var.app_project_id
  name     = format("%s-%s-%s-%s", var.env, replace(each.value.collection, "_", "-"), each.value.event, "viki-${var.env}")
  location = "nam5"
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.firestore.document.v1.${each.value.event}"
  }
  matching_criteria {
    attribute = "database"
    value     = google_firestore_database.viki_database.name
  }
  matching_criteria {
    attribute = "document"
    value     = "${each.value.collection}/*"
    operator  = "match-path-pattern"
  }

  destination {
    cloud_run_service {
      service = each.value.destination
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/firestore"
    }
  }
  service_account = module.ai_sa.email

  # https://github.com/hashicorp/terraform-provider-google/issues/14597
  event_data_content_type = "application/protobuf"

  labels = var.labels
}

resource "google_eventarc_trigger" "external_files_pubsub_trigger" {
  project  = var.app_project_id
  name     = format("%s-%s", var.env, "external-files")
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  transport {
    pubsub {
      topic = google_pubsub_topic.external_files_topic.id
    }
  }

  service_account = module.ai_sa.email
  destination {
    cloud_run_service {
      service = module.paperglass_external_events.name
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/pubsub/external_files"
    }
  }
  # https://github.com/hashicorp/terraform-provider-google/issues/14597
  #event_data_content_type = "application/protobuf"
  labels = var.labels
}

resource "google_eventarc_trigger" "external_files_hhh_pubsub_trigger" {
  project  = var.app_project_id
  name     = format("%s-%s", var.env, "hhh-external-files-subscription")
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  transport {
    pubsub {
      topic = "projects/hhh-dev-app-wsky/topics/HHH-AM-Attachments" #TODO: update to use var
    }
  }

  service_account = module.ai_sa.email
  destination {
    cloud_run_service {
      service = module.paperglass_external_events.name
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/pubsub/external_files"
    }
  }
  # https://github.com/hashicorp/terraform-provider-google/issues/14597
  #event_data_content_type = "application/protobuf"
  labels = var.labels
}

resource "google_eventarc_trigger" "command_scheduledwindow_1_pubsub_trigger" {
  project  = var.app_project_id
  name     = "command-scheduledwindow-1-trigger-${var.env}"
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  transport {
    pubsub {
      topic = google_pubsub_topic.command_scheduledwindow_1_topic.id
    }
  }

  service_account = module.ai_sa.email
  destination {
    cloud_run_service {
      service = module.paperglass_events.name
      region  = var.region # The region the Cloud Run service is deployed in
      path    = "/eventarc/pubsub/scheduledcommand"
    }
  }

  labels = var.labels
}