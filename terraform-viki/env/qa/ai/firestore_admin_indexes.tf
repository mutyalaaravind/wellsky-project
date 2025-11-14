# Firestore Indexes for Admin API Collections
# These indexes support queries in the admin API's Firestore adapters

# ============================================================================
# CRITICAL: admin_rbac_roles - List Active Roles with Ordering
# ============================================================================
# Location: admin/api/src/infrastructure/adapters/role_firestore_adapter.py:156-166
# Query: .where(active == True).order_by('audit.created_on')
# Purpose: List roles with pagination, ordered by creation date
resource "google_firestore_index" "admin_rbac_roles_active_created" {
  project    = var.app_project_id
  database   = google_firestore_database.viki_database.name
  collection = "admin_rbac_roles"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "audit.created_on"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# ============================================================================
# admin_rbac_roles - Find Roles by Inheritance
# ============================================================================
# Location: admin/api/src/infrastructure/adapters/role_firestore_adapter.py:194-195
# Query: .where(inherits array_contains role_id).where(active == True)
# Purpose: Find all roles that inherit from a specific role
resource "google_firestore_index" "admin_rbac_roles_inherits_active" {
  project    = var.app_project_id
  database   = google_firestore_database.viki_database.name
  collection = "admin_rbac_roles"

  fields {
    field_path   = "inherits"
    array_config = "CONTAINS"
  }

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }
}

# ============================================================================
# COLLECTION GROUP: subjects - List Active Subjects
# ============================================================================
# Location: admin/api/src/adapters/demo_subjects_firestore_adapter.py:109-111
# Query: .where(active == True).order_by('created_at', DESC)
# Purpose: List active demo subjects for an app
resource "google_firestore_index" "demo_subjects_active_created" {
  project     = var.app_project_id
  database    = google_firestore_database.viki_database.name
  collection  = "subjects"
  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# ============================================================================
# COLLECTION GROUP: documents - List Active Documents by Creation Date
# ============================================================================
# Location: admin/api/src/adapters/document_firestore_adapter.py:129-132
# Query: .where(active == True).order_by('created_at', DESC)
# Purpose: List active documents for a subject
resource "google_firestore_index" "documents_active_created" {
  project     = var.app_project_id
  database    = google_firestore_database.viki_database.name
  collection  = "documents"
  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# ============================================================================
# COLLECTION GROUP: documents - Find Document by ID and Active Status
# ============================================================================
# Location: admin/api/src/adapters/document_firestore_adapter.py:177-179
# Query: collection_group('documents').where(id == doc_id).where(active == True)
# Purpose: Find a specific document across all app_ids and subject_ids
resource "google_firestore_index" "documents_id_active" {
  project     = var.app_project_id
  database    = google_firestore_database.viki_database.name
  collection  = "documents"
  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }
}

# ============================================================================
# COLLECTION GROUP: entities - List Entities by Type and Creation
# ============================================================================
# Location: admin/api/src/infrastructure/adapters/entity_firestore_adapter.py:207-213
# Query: .where(entity_type == type).order_by('created_at')
# Purpose: List entities filtered by type, ordered by creation
resource "google_firestore_index" "entities_type_created" {
  project     = var.app_project_id
  database    = google_firestore_database.viki_database.name
  collection  = "entities"
  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "entity_type"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
}

# ============================================================================
# COLLECTION GROUP: entities - List Entities by Source and Creation
# ============================================================================
# Location: admin/api/src/infrastructure/adapters/entity_firestore_adapter.py:209-213
# Query: .where(source_id == source).order_by('created_at')
# Purpose: List entities filtered by source document, ordered by creation
resource "google_firestore_index" "entities_source_created" {
  project     = var.app_project_id
  database    = google_firestore_database.viki_database.name
  collection  = "entities"
  query_scope = "COLLECTION_GROUP"

  fields {
    field_path = "source_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
}

# ============================================================================
# paperglass_app_config - List Active App Configs by Creation
# ============================================================================
# Query: .where(active == True).order_by('created_at', DESC)
# Purpose: List active app configurations ordered by creation date
resource "google_firestore_index" "paperglass_app_config_active_created" {
  project    = var.app_project_id
  database   = google_firestore_database.viki_database.name
  collection = "paperglass_app_config"

  fields {
    field_path = "active"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "DESCENDING"
  }
}
