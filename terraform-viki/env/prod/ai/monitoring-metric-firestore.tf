resource "google_logging_metric" "firestore_operation_create_metric" {
  name    = "firestore_operation_create_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ creating aggregate\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Firestore Create Operation"
    labels {
      key         = "collection"
      value_type  = "STRING"
      description = "Collection"
    }
  }
  label_extractors = {
    collection = "EXTRACT(jsonPayload.collection)"
  }
}

resource "google_logging_metric" "firestore_operation_update_metric" {
  name    = "firestore_operation_update_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ updating aggregate\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Firestore Update Operation"
    labels {
      key         = "collection"
      value_type  = "STRING"
      description = "Collection"
    }
  }
  label_extractors = {
    collection = "EXTRACT(jsonPayload.collection)"
  }
}

resource "google_logging_metric" "firestore_operation_delete_metric" {
  name    = "firestore_operation_delete_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ deleting aggregate\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Firestore Delete Operation"
    labels {
      key         = "collection"
      value_type  = "STRING"
      description = "Collection"
    }
  }
  label_extractors = {
    collection = "EXTRACT(jsonPayload.collection)"
  }
}

resource "google_logging_metric" "firestore_operation_event_metric" {
  name    = "firestore_operation_event_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ saving event\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Firestore Event Operation"
    labels {
      key         = "collection"
      value_type  = "STRING"
      description = "Collection"
    }
  }
  label_extractors = {
    collection = "EXTRACT(jsonPayload.collection)"
  }
}

resource "google_logging_metric" "firestore_operation_error_metric" {
  name    = "firestore_operation_error_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ error\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Firestore Error"
    labels {
      key         = "excType"
      value_type  = "STRING"
      description = "Exception Type"
    }
  }
  label_extractors = {
    excType = "EXTRACT(jsonPayload.excType)"
  }
}

resource "google_logging_metric" "firestore_operation_rollback_metric" {
  name    = "firestore_operation_rollback_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ rollback\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "Firestore Rollback"    
  }
}


resource "google_logging_metric" "firestore_operation_commit_elapsedtime_metric" {
  name    = "firestore_operation_commit_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ commit complete\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Firestore Commit Elapsed Time"    
  }
  value_extractor = "EXTRACT(jsonPayload.txnElapsedTime)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
}

resource "google_logging_metric" "firestore_operation_commitaction_elapsedtime_metric" {
  name    = "firestore_operation_commitaction_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ commit complete\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Firestore Commit Action Elapsed Time"    
  }
  value_extractor = "EXTRACT(jsonPayload.txnElapsedTimeMid)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
}

resource "google_logging_metric" "firestore_operation_commit_error_elapsedtime_metric" {
  name    = "firestore_operation_commit_error_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ error\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Firestore Commit Error Elapsed Time"    
    labels {
      key         = "excType"
      value_type  = "STRING"
      description = "Exception Type"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.txnElapsedTime)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    excType = "EXTRACT(jsonPayload.excType)"
  }
}

resource "google_logging_metric" "firestore_operation_commitaction_error_elapsedtime_metric" {
  name    = "firestore_operation_commitaction_error_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"FirestoreUnitOfWork::__aexit__ error\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "Firestore Commit Action Error Elapsed Time"    
    labels {
      key         = "excType"
      value_type  = "STRING"
      description = "Exception Type"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.txnElapsedTimeMid)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }
  label_extractors = {
    excType = "EXTRACT(jsonPayload.excType)"
  }
}