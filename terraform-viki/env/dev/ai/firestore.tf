resource "google_firestore_database" "database" {
  project     = var.app_project_id
  name        = "ai-${var.env}"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

resource "google_firestore_database" "default_database" {
  project     = var.app_project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state           = "DELETE_PROTECTION_ENABLED"
}

resource "google_firestore_index" "paperglass_docs_patient_index" {
  project = var.app_project_id

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

resource "google_firestore_index" "paperglass_page_lbis_index" {
  project = var.app_project_id

  collection = "paperglass_page_lbis"

  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "labels"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "paperglass_patient_index" {
  project = var.app_project_id

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

resource "google_firestore_index" "paperglass_patient_index_2" {
  project = var.app_project_id

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

resource "google_firestore_index" "paperglass_document_index" {
  project = var.app_project_id

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

resource "google_firestore_index" "paperglass_pages_index" {
  project = var.app_project_id

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

resource "google_firestore_index" "medications_extracted_medications_grade_1_index" {
  project = var.app_project_id

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

resource "google_firestore_index" "medications_extracted_medications_grade_2_index" {
  project = var.app_project_id

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

resource "google_firestore_index" "scribe_patients_name_index" {
  project = var.app_project_id

  collection = "skysense-scribe-patients"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "app_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "assignee_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "tennant_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "name"
    order      = "ASCENDING"
  }

}

resource "google_firestore_index" "scribe_patients_lastsession_index" {
  project = var.app_project_id

  collection = "skysense-scribe-patients"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "app_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "assignee_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "tennant_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "last_session_time"
    order      = "DESCENDING"
  }

}

resource "google_firestore_index" "scribe_assessments_patient_index" {
  project = var.app_project_id

  collection = "skysense-scribe-assessments"

  fields {
    field_path = "app_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "assignee_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "tennant_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

}

resource "google_firestore_index" "scribe_scribes_app_patient_index" {
  project = var.app_project_id

  collection = "skysense-scribe-scribes"

  fields {
    field_path = "app_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "archived"
    order      = "ASCENDING"
  }

  fields {
    field_path = "assignee_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "tennant_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "server_creation_time"
    order      = "DESCENDING"
  }

}

resource "google_firestore_index" "scribe_scibes_patient_index" {
  project = var.app_project_id

  collection = "skysense-scribe-scribes"

  fields {
    field_path = "archived"
    order      = "ASCENDING"
  }

  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "server_creation_time"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "scribe_scibes_support_patient_index" {
  project = var.app_project_id

  collection = "skysense-scribe-scribes"

  fields {
    field_path = "app_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "archived"
    order      = "ASCENDING"
  }

  fields {
    field_path = "patient_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "server_creation_time"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "scribe_patient_app_name_index" {
  project = var.app_project_id

  collection = "skysense-scribe-patients"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "app_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "name"
    order      = "ASCENDING"
  }

}

resource "google_firestore_index" "scribe_patient_facility_name_index" {
  project = var.app_project_id

  collection = "skysense-scribe-patients"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "assignee_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "name"
    order      = "ASCENDING"
  }

}

resource "google_firestore_index" "scribe_patient_name_index" {
  project = var.app_project_id

  collection = "skysense-scribe-patients"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "name"
    order      = "ASCENDING"
  }

}