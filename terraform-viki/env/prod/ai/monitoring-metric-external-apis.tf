
resource "google_logging_metric" "external_hhh_medication_get_metric" {
  name    = "external_hhh_medication_get_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_GET\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Medication Get"    
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_medication_get_elapsedtime_metric" {
  name    = "external_hhh_medication_get_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_GET\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Medication Get Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
  
}

# Medications Add
resource "google_logging_metric" "external_hhh_medication_add_metric" {
  name    = "external_hhh_medication_add_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_ADD\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Medication Add"    
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_medication_add_elapsedtime_metric" {
  name    = "external_hhh_medication_add_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_ADD\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Medication Add Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}

# Freeform add =============================================================================================
resource "google_logging_metric" "external_hhh_medication_freeformadd_metric" {
  name    = "external_hhh_medication_freeformadd_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_FREEFORM_ADD\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Medication Freeform Add"    
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_medication_freeformadd_elapsedtime_metric" {
  name    = "external_hhh_medication_freeformadd_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_FREEFORM_ADD\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Medication Freeform Add Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}

# Medication update =============================================================================================
resource "google_logging_metric" "external_hhh_medication_update_metric" {
  name    = "external_hhh_medication_update_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_UPDATE\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Medication Update"
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_medication_update_elapsedtime_metric" {
  name    = "external_hhh_medication_update_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_UPDATE\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Medication Update Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}

# Medication delete =============================================================================================
resource "google_logging_metric" "external_hhh_medication_delete_metric" {
  name    = "external_hhh_medication_delete_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_DELETE\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Medication Delete"
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_medication_delete_elapsedtime_metric" {
  name    = "external_hhh_medication_delete_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::MEDICATIONS_DELETE\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Medication Delete Elapsed Time"
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}

# Attachments Get =============================================================================================
resource "google_logging_metric" "external_hhh_attachment_get_metric" {
  name    = "external_hhh_attachment_get_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::ATTACHMENTS_GET\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Attachments Get"
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_attachment_get_elapsedtime_metric" {
  name    = "external_hhh_attachment_get_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::ATTACHMENTS_GET\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Attachments Get Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}

# Attachment metadata ===============================================================
resource "google_logging_metric" "external_hhh_attachment_metadata_get_metric" {
  name    = "external_hhh_attachment_metadata_get_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::ATTACHMENT_METADATA_GET\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Attachment Metadata Get"
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_attachment_metadata_get_elapsedtime_metric" {
  name    = "external_hhh_attachment_metadata_get_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::ATTACHMENT_METADATA_GET\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH API Attachment Metadata Get Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}

# HHH Auth ===============================================================
resource "google_logging_metric" "external_hhh_auth_metric" {
  name    = "external_hhh_auth_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::AUTH\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "HHH API Auth"
  
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }

  }
  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }
}


resource "google_logging_metric" "external_hhh_auth_elapsedtime_metric" {
  name    = "external_hhh_auth_elapsedtime_metric"
  project = var.app_project_id
  filter  = "jsonPayload.message: \"METRIC::HHH::AUTH\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "DISTRIBUTION"
    display_name = "HHH Auth Elapsed Time"    
    
    labels {
      key         = "branch"
      value_type  = "STRING"
      description = "Branch"
    }
    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Status"
    }
    labels{
      key         = "error"
      value_type  = "STRING"
      description = "Error"
    }
  }
  value_extractor = "EXTRACT(jsonPayload.elapsed_time)"
  bucket_options {
        explicit_buckets {
      bounds = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 20000, 50000, 100000]
    }
  }

  label_extractors = {
    branch = "EXTRACT(jsonPayload.branch)",
    status = "EXTRACT(jsonPayload.status)",
    error =  "EXTRACT(jsonPayload.error.type)"
  }  
}
