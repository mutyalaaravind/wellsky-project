
resource "google_logging_metric" "bigquery_jobcompleted_metric" {
  name    = "bigquery_jobcompleted_metric"
  project = var.app_project_id
  filter  = "protoPayload.serviceName: \"bigquery.googleapis.com\" AND protoPayload.serviceData.jobCompletedEvent.eventName: \"query_job_completed\""
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "BigQuery Job Completed"

    labels {
      key         = "severity"
      value_type  = "STRING"
      description = "Severity"
    }
  }
  label_extractors = {    
    severity = "EXTRACT(severity)",
  }  
}

resource "google_logging_metric" "bigquery_error_metric" {
  name    = "bigquery_error_metric"
  project = var.app_project_id
  filter  = "protoPayload.serviceName: \"bigquery.googleapis.com\" AND protoPayload.serviceData.jobCompletedEvent.job.jobStatus.error.message: * AND severity=ERROR"
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "BigQuery Error"

    labels {
      key         = "error_code"
      value_type  = "STRING"
      description = "Error Code"
    }
  }
  label_extractors = {    
    error_code = "EXTRACT(protoPayload.serviceData.jobCompletedEvent.job.jobStatus.error.code)",
  }  
}

resource "google_logging_metric" "bigquery_error_quotaexceeded_metric" {
  name    = "bigquery_error_quotaexceeded_metric"
  project = var.app_project_id
  filter  = "protoPayload.serviceName: \"bigquery.googleapis.com\" AND protoPayload.serviceData.jobCompletedEvent.job.jobStatus.error.message: \"Quota exceeded:\" AND severity=ERROR"
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "BigQuery Quota Exceeded"

    labels {
      key         = "table"
      value_type  = "STRING"
      description = "Table"
    }
    labels {
      key         = "error_code"
      value_type  = "STRING"
      description = "Error Code"
    }
  }
  label_extractors = {
    table = "EXTRACT(protoPayload.serviceData.jobCompletedEvent.job.jobConfiguration.load.destinationTable.tableId)",
    error_code = "EXTRACT(protoPayload.serviceData.jobCompletedEvent.job.jobStatus.error.code)",
  }  
}