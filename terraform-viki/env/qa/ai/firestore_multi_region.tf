resource "google_firestore_database" "viki_database" {
  project     = var.app_project_id
  name        = "viki-${var.env}"
  location_id = "nam5"
  type        = "FIRESTORE_NATIVE"

  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state           = "DELETE_PROTECTION_ENABLED"
}

resource "google_firestore_index" "viki_paperglass_docs_patient_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_documents"

  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }
  fields {
    // We're sorting by id, so it must be defined as last item
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "viki_paperglass_document_index_2" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_documents"

  fields {
    // We're sorting by id, so it must be defined as last item
    field_path = "active"
    order      = "ASCENDING"
  }
  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "viki_paperglass_patient_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "demo_patients"

  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
  fields {
    // We're sorting by id, so it must be defined as last item
    field_path = "active"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "viki_paperglass_patient_index_2" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "demo_patients"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }
  fields {
    // We're sorting by id, so it must be defined as last item
    field_path = "created_at"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "viki_paperglass_document_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_documents"

  fields {
    // We're sorting by id, so it must be defined as last item
    field_path = "active"
    order      = "ASCENDING"
  }
  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "viki_paperglass_pages_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_pages"

  fields {
    // We're sorting by id, so it must be defined as last item
    field_path = "document_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "number"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "viki_medications_extracted_medications_grade_1_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "medications_extracted_medications_grades"

  fields {
    field_path = "extracted_medication_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "viki_medications_extracted_medications_grade_2_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "medications_extracted_medications_grades"

  fields {
    field_path = "extracted_medication_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "document_operation_instance_id"
    order      = "ASCENDING"
  }
}


resource "google_firestore_index" "viki_document_operation_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_document_operation"

  fields {
    field_path = "document_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "operation_type"
    order      = "ASCENDING"
  }
}


# resource "google_firestore_index" "viki_document_operation_instance_log_index" {
#   project = var.app_project_id
#   database = google_firestore_database.viki_database.name

#   collection = "paperglass_document_operation_instance_log"

#   fields {    
#     field_path = "document_id"
#     order      = "ASCENDING"
#   }  

#   fields {    
#     field_path = "document_operation_instance_id"
#     order      = "ASCENDING"
#   }
# }

resource "google_firestore_index" "viki_document_operation_instance_log_index_2" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_document_operation_instance"

  fields {
    field_path = "document_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "document_operation_definition_id"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "medications_collection_group_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "medications"

  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "document_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "document_operation_instance_id"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "testcase_results_summary_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "paperglass_testcase_results_summary"

  fields {
    field_path = "mode"
    order      = "ASCENDING"
  }
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# to manually create vector index, use:
# gcloud firestore indexes composite create --project=viki-qa-app-wsky --database=viki-qa --collection-group=meddb_medispan --query-scope=COLLECTION --field-config=vector-config='{"dimension":"768","flat": "{}"}',field-path=med_embedding

resource "google_firestore_index" "meddb_medispan_compound1_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "meddb_medispan"

  fields {
    field_path = "id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "namedescription"
    order      = "ASCENDING"
  }
  fields {
    field_path = "name"
    order      = "ASCENDING"
  }
}


resource "google_firestore_index" "meddb_merative_compound1_index" {
  project  = var.app_project_id
  database = google_firestore_database.viki_database.name

  collection = "meddb_merative"

  fields {
    field_path = "id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "namedescription"
    order      = "ASCENDING"
  }
  fields {
    field_path = "name"
    order      = "ASCENDING"
  }
}
