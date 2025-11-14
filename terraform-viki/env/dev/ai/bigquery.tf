locals {
  # List all SQL files in the dedup_sql directory
  query_files = fileset("${path.module}/bq_schema_changes", "*.sql")
}

resource "null_resource" "bigquery_ddl" {
  for_each = local.query_files
  provisioner "local-exec" {
    command = <<EOT
      bq --project_id=${var.app_project_id} query --use_legacy_sql=false \
        "$(cat ${path.module}/bq_schema_changes/${each.value})"
    EOT
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "google_bigquery_dataset" "audit_log_dataset" {
  // Create only if `enable_bigquery` is set and `bigquery_dataset_id` is empty
  project       = var.app_project_id
  dataset_id    = "audit_log_dataset"
  friendly_name = "Dataset for Audit Log (${var.env})"
  description   = "audit log data"
  location      = var.region
  labels        = var.labels

  access {
    role          = "OWNER"
    user_by_email = local.terraform_agent_email
  }

  access {
    role          = "OWNER"
    user_by_email = local.tfe_agent_email
  }

  # Default project permissions
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }
}

resource "google_bigquery_table" "audit_log_table" {
  #   for_each            = { for config in var.claims_gcs_to_bq : config.name => config }
  deletion_protection = false #ToDo: in prod it needs to be true
  project             = var.app_project_id
  table_id            = "audit_log_table"
  dataset_id          = google_bigquery_dataset.audit_log_dataset.dataset_id
  labels              = var.labels

  time_partitioning {
    type  = "DAY"
    field = "processed_at"
  }

  clustering = ["app_id", "tenant_id", "processed_at", "patient_id"]

  schema = <<EOF
    [
        {
            "name": "app_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Application identifier"
        },
        {
            "name": "tenant_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Tenant identifier"
        },
        {
            "name": "patient_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Patient identifier"
        },
        {
            "name": "document_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Document identifier"
        },
        {
            "name": "run_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Run identifier"
        },
        {
            "name": "step_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Step identifier"
        },
        {
            "name": "page_number",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Page number"
        },
        {
            "name": "iteration",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Iteration count"
        },
        {
            "name": "processed_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE",
            "description": "Processing timestamp"
        },
        {
            "name": "model_name",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Name of the model used"
        },
        {
            "name": "max_output_tokens",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Maximum output tokens"
        },
        {
            "name": "temperature",
            "type": "FLOAT",
            "mode": "NULLABLE",
            "description": "Temperature parameter"
        },
        {
            "name": "top_p",
            "type": "FLOAT",
            "mode": "NULLABLE",
            "description": "Top p parameter"
        },
        {
            "name": "prompt_length",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Length of the prompt"
        },
        {
            "name": "prompt_tokens",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Number of prompt tokens"
        },
        {
            "name": "billing_total_tokens",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Total tokens for billing"
        },
        {
            "name": "billing_total_billable_characters",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Total billable characters"
        },
        {
            "name": "burndown_rate",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Burndown rate"
        },
        {
            "name": "response_length",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Length of the response"
        },
        {
            "name": "response_tokens",
            "type": "INTEGER",
            "mode": "NULLABLE",
            "description": "Number of response tokens"
        },
        {
            "name": "elapsed_time",
            "type": "FLOAT",
            "mode": "NULLABLE",
            "description": "Elapsed time"
        },
        {
            "name": "hasImage",
            "type": "BOOLEAN",
            "mode": "NULLABLE",
            "description": "Whether the prompt contains an image"
        },
        {
            "name": "hasBinaryData",
            "type": "BOOLEAN",
            "mode": "NULLABLE",
            "description": "Whether the prompt contains binary data"
        },
        {
            "name": "input",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Input prompt"
        },
        {
            "name": "output",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Model output"
        },
        {
            "name": "error",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error message if any"
        }
    ]
    EOF
}

# locals {
#   # Map collections to Eventarc events
#   bg_source_trigger_map = {
#     // List of collections to create a "created" trigger for
#     created = [
#       {
#         collection  = "paperglass_documents",
#         identifier  = "doc"

#       },
#       {
#         collection  = "paperglass_document_operation_instance_log",
#         identifier  = "doc_ops_inst_log"
#       }
#     ]
#   }
#   bg_source_triggers = flatten([
#     for event, definitions in local.bg_source_trigger_map : [
#       for definition in definitions : {
#         event       = event,
#         collection  = definition.collection
#         identifier  = definition.identifier
#       }
#     ]
#   ])
# }

# resource "google_bigquery_dataset" "viki_dataset" {
#   // Create only if `enable_bigquery` is set and `bigquery_dataset_id` is empty
#   project       = var.app_project_id
#   dataset_id    = "${var.env}_viki_dataset"
#   friendly_name = "Dataset for firestore (${var.env})"
#   description   = "Data streaming from firestore to bigquery"
#   location      = var.region
#   labels        = var.labels
# }

# resource "google_eventarc_trigger" "firestore_trigger_and_write_to_bq" {
#   for_each = { for trigger in local.bg_source_triggers : "${trigger.collection}_${trigger.event}" => trigger }

#   project  = var.app_project_id
#   name     = format("%s-bqsync-%s-%s-%s", var.env, replace(each.value.identifier, "_", "-"), each.value.event, "viki-${var.env}")
#   location = "nam5"
#   matching_criteria {
#     attribute = "type"
#     value     = "google.cloud.firestore.document.v1.written"
#   }
#   matching_criteria {
#     attribute = "database"
#     value     = google_firestore_database.viki_database.name
#   }
#   matching_criteria {
#     attribute = "document"
#     value     = "${each.value.collection}/*"
#     operator  = "match-path-pattern"
#   }

#   destination {
#     cloud_run_service {
#       service = module.paperglass_events.name
#       region  = var.region # The region the Cloud Run service is deployed in
#       path    = "/eventarc/bqsync"
#     }
#   }
#   service_account = module.ai_sa.email

#   # https://github.com/hashicorp/terraform-provider-google/issues/14597
#   event_data_content_type = "application/protobuf"

#   labels = var.labels
# }

# # resource "google_firebase_extensions_instance" "bigquery_export" {
# #   for_each = var.firestore_to_bq_streaming_enabled ? { for collection in local.firestore_collections : collection => {
# #     name        = collection
# #     name_dashes = replace(collection, "_", "-")
# #   } } : {}
# #   provider    = google-beta
# #   project     = var.app_project_id
# #   instance_id = "viki-data-bq-${each.value.name_dashes}"
# #   config {
# #     extension_ref     = "firebase/firestore-bigquery-export" #https://extensions.dev/extensions/firebase/firestore-bigquery-export
# #     extension_version = "0.1.55"

# #     params = {
# #       BIGQUERY_PROJECT_ID           = var.app_project_id
# #       COLLECTION_PATH               = each.value.name
# #       DATASET_ID                    = google_bigquery_dataset.viki_dataset.dataset_id
# #       DATASET_LOCATION              = var.region
# #       LOCATION                      = var.region
# #       TABLE_ID                      = "${each.value.name}"
# #       TABLE_PARTITIONING            = "DAY"
# #       TIME_PARTITIONING_FIELD       = "timestamp"
# #       CLUSTERING                    = "document_name,document_id"
# #       USE_NEW_SNAPSHOT_QUERY_SYNTAX = "yes"
# #       WILDCARD_IDS                  = true
# #       LOG_FAILED_EXPORTS            = "yes"
# #     }
# #   }
# # }

# resource "google_pubsub_schema" "raw_change_log_schema" {
#   name    = "viki_raw_change_log"
#   type    = "AVRO"
#   project = var.app_project_id
#   definition = jsonencode({
#     type = "record",
#     name = "documents",
#     fields = [
#       { name = "id", type = "string" },
#       { name = "app_id", type = "string" },
#       { name = "tenant_id", type = "string" },
#       { name = "patient_id", type = "string" },
#       { name = "document_id", type = "string" },
#       { name = "created_at", type = "string" },
#       { name = "modified_at", type = "string" },
#       { name = "created_by", type = "string" },
#       { name = "modified_by", type = "string" },
#       { name = "old_data", type = "string" },
#       { name = "data", type = "string" },
#       { name = "operation", type = "string" },
#       { name = "timestamp", type = "string" },
#       { name = "source_collection_name", type = "string" },
#       { name = "event_id", type = "string", default="" }
#     ],
#   })
# }

# resource "google_pubsub_topic" "raw_change_log_topic" {
#   name       = "raw-change-log-topic"
#   project    = var.app_project_id
#   depends_on = [google_pubsub_schema.raw_change_log_schema]

#   schema_settings {
#     schema   = "projects/${var.app_project_id}/schemas/viki_raw_change_log"
#     encoding = "JSON"
#   }
#   labels = var.labels

# }

# resource "google_bigquery_table" "raw_change_log_table" {
#   #   for_each            = { for config in var.claims_gcs_to_bq : config.name => config }
#   deletion_protection = false #ToDo: in prod it needs to be true
#   project             = var.app_project_id
#   table_id            = "raw_change_log_table"
#   dataset_id          = google_bigquery_dataset.viki_dataset.dataset_id
#   labels              = var.labels

#   time_partitioning {
#     type  = "DAY"
#     field = "publish_time"
#   }

#   clustering = ["app_id", "tenant_id", "created_at", "patient_id"]

#   schema = <<EOF
#     [
#         {
#             "name"        : "id",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "id of the document"
#         },
#         {
#             "name"        : "app_id",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "app_id of the document"
#         },
#         {
#             "name"        : "tenant_id",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "tenant_id of the document"
#         },
#         {
#             "name"        : "patient_id",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "patient_id of the document"
#         },
#         {
#             "name"        : "document_id",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "document_id of the document"
#         },
#         {
#             "name"        : "created_at",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "created_at of the document"
#         },
#         {
#             "name"        : "modified_at",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "modified_at of the document"
#         },
#         {
#             "name"        : "created_by",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "created_by of the document"
#         },
#         {
#             "name"        : "modified_by",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "modified_by of the document"
#         },
#         {
#             "name"        : "old_data",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "data before change. emtpy for create operation"
#         },
#         {
#             "name"        : "data",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "actual data"
#         },
#         {
#             "name"        : "operation",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "CREATE,UPDATE or DELETE"
#         },
#         {
#             "name"        : "timestamp",
#             "type"        : "TIMESTAMP",
#             "mode"        : "NULLABLE",
#             "description" : "timestamp of event"
#         },
#         {
#             "name"        : "source_collection_name",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "source firestore collection name"
#         },
#         {
#             "name"        : "message_id",
#             "type"        : "string",
#             "mode"        : "NULLABLE",
#             "description" : "timestamp of the event"
#         },
#         {
#             "name"        : "event_id",
#             "type"        : "string",
#             "mode"        : "NULLABLE",
#             "description" : "timestamp of the event"
#         },
#         {
#             "name"        : "publish_time",
#             "type"        : "TIMESTAMP",
#             "mode"        : "NULLABLE",
#             "description" : "timestamp of the event"
#         },
#         {
#             "name"        : "subscription_name",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "attributes of the event"
#         },
#         {
#             "name"        : "attributes",
#             "type"        : "STRING",
#             "mode"        : "NULLABLE",
#             "description" : "attributes of the event"
#         }
#     ]
#     EOF
# }

# resource "google_pubsub_subscription" "raw_changelog_subscription" {
#   name    = "raw_changelog_subscription"
#   topic   = google_pubsub_topic.raw_change_log_topic.id
#   project = var.app_project_id
#   bigquery_config {
#     table = "${google_bigquery_table.raw_change_log_table.project}.${google_bigquery_table.raw_change_log_table.dataset_id}.${google_bigquery_table.raw_change_log_table.table_id}"
#     service_account_email = module.ai_sa.email
#     write_metadata = true
#     use_topic_schema = true
#   }
#   labels = var.labels
# }
