locals {

  # Firestore index exemptions for large (or monotonic) fields
  firestore_index_exemptions = {
    paperglass_document_operation_instance_log = ["context", "created_at", "created_by", "modified_at", "modified_by"] # query fields: document_id,document_operation_instance_id,step_id,page_number,status
    paperglass_page_operation                  = ["created_at", "created_by", "modified_at", "modified_by"]            #query fields: page_id,document_operation_instance_id,extraction_type,document_id
    paperglass_document_operation_definition   = ["created_at", "created_by", "modified_at", "modified_by"]
  }
  firestore_index_exemptions_flat = flatten([
    for collection_name, field_names in local.firestore_index_exemptions : [
      for field_name in toset(field_names) : {
        collection_name = collection_name
        field_name      = field_name
      }
    ]
  ])
}

resource "google_firestore_field" "firestore_index_exemption" {
  for_each   = { for exemption in local.firestore_index_exemptions_flat : "${exemption.collection_name}.${exemption.field_name}" => exemption }
  provider   = google-beta
  project    = var.app_project_id
  database   = google_firestore_database.viki_database.name
  collection = each.value.collection_name
  field      = each.value.field_name

  index_config {}
}