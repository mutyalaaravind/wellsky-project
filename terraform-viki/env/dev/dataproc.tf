# Required variables
variable "dataproc_cluster_prefix" {
  description = "Prefix for the Dataproc cluster name"
  type        = string
  default     = "medispan"
}

variable "spark_job_file" {
  description = "Name of the PySpark job file in the GCS bucket"
  type        = string
  default     = "json_to_pgvector.py"
}

resource "google_storage_bucket" "spark_job_bucket" {
  project                     = var.app_project_id
  name                        = "viki-spark-jobs-${var.env}"
  location                    = var.region
  uniform_bucket_level_access = true
  labels                      = var.labels
}

resource "google_storage_bucket" "dataproc_staging_bucket" {
  project                     = var.app_project_id
  name                        = "viki-dataproc-staging-${var.env}"
  location                    = var.region
  uniform_bucket_level_access = true
  labels                      = var.labels
}

resource "google_storage_bucket" "dataproc_temp_bucket" {
  project                     = var.app_project_id
  name                        = "viki-dataproc-temp-${var.env}"
  location                    = var.region
  uniform_bucket_level_access = true
  labels                      = var.labels
}

# Dataproc Batch Template
resource "google_dataproc_workflow_template" "medispan_template" {
  name     = "medispan-batch-template"
  location = var.region
  project  = var.app_project_id

  jobs {
    step_id = "medispan_processing"

    pyspark_job {
      main_python_file_uri = "gs://${google_storage_bucket.spark_job_bucket.name}/${var.spark_job_file}"

      #python_file_uris = [ "gs://${google_storage_bucket.spark_job_bucket.name}/dependencies.zip" ]

      properties = {
        "spark.executor.memory"           = "4g"
        "spark.driver.memory"             = "2g"
        "spark.executor.cores"            = "2"
        "spark.driver.cores"              = "1"
        "spark.executor.instances"        = "2"
        "spark.driver.extraJavaOptions"   = "-Djava.security.manager=allow"
        "spark.executor.extraJavaOptions" = "-Djava.security.manager=allow"
        "spark.driver.extraClassPath"     = "gs://${google_storage_bucket.spark_job_bucket.name}/postgresql-42.7.5.jar"
        "spark.executor.extraClassPath"   = "gs://${google_storage_bucket.spark_job_bucket.name}/postgresql-42.7.5.jar"
      }

      args = [
        "--input=gs://${google_storage_bucket.spark_job_bucket.name}/input-files/meddb.json",
        "--pg-table=medispan_drugs_gcp_768",
        "--pg-host=${google_alloydb_instance.primary.ip_address}",
        "--pg-user=postgres",
        "--pg-password=${var.alloydb_password}",
        "--pg-database=vectordb",
        "--embedding-type=gcp",
        "--gcp-project=${var.app_project_id}",
        "--gcp-location=${var.region}",
        "--gcp-model=text-embedding-005",
      ]
    }
  }

  placement {
    managed_cluster {
      cluster_name = "${var.dataproc_cluster_prefix}-workflow-template"
      config {
        gce_cluster_config {
          #network      = "projects/${var.network_project_id}/global/networks/${var.network}"
          subnetwork       = "projects/${var.network_project_id}/regions/${var.region}/subnetworks/${var.subnet_internal}"
          internal_ip_only = true
          service_account  = google_service_account.dataproc_sa.email
          tags             = var.network_tags
        }

        initialization_actions {
          executable_file = "gs://${google_storage_bucket.spark_job_bucket.name}/init-actions.sh"
        }

        staging_bucket = google_storage_bucket.dataproc_staging_bucket.name

        temp_bucket = google_storage_bucket.dataproc_temp_bucket.name

        software_config {
          image_version = "2.1"
        }
      }
    }
  }
}

# Service account for Dataproc
resource "google_service_account" "dataproc_sa" {
  account_id   = "dataproc-sa-${var.env}"
  display_name = "Service Account for Dataproc Serverless"
  project      = var.app_project_id
}

# Grant necessary roles to the service account
resource "google_project_iam_member" "dataproc_worker" {
  project = var.app_project_id
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.dataproc_sa.email}"
}

resource "google_storage_bucket_iam_member" "spark_job_bucket_access" {
  bucket = google_storage_bucket.spark_job_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.dataproc_sa.email}"
}

resource "google_storage_bucket_iam_member" "github_build_bucket_access" {
  bucket = google_storage_bucket.spark_job_bucket.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${local.github_sa_email}"
}

/*
INSTRUCTIONS TO USE THE DATAPROC WORKFLOW TEMPLATE:

1. First, upload your PySpark job file to the GCS bucket:
   gsutil cp medispan_processing.py gs://${var.spark_job_bucket}/

2. The workflow template will be created when you run:
   terraform apply

3. To instantiate a new batch job from the template:
   gcloud dataproc workflow-templates instantiate medispan-batch-template \
     --project=${var.app_project_id} \
     --region=${var.region}

   The template will create an ephemeral cluster with name format:
   ${var.dataproc_cluster_prefix}-MMDD (e.g., medispan-0317)

4. Monitor the workflow progress in the Google Cloud Console or via:
   gcloud dataproc operations list --region=${var.region}

Note: Remember to:
- Update the source_table parameter to your actual source table
- Ensure network connectivity between Dataproc and AlloyDB
- The service account has the necessary permissions

The template creates an ephemeral cluster for each job execution with:
- Internal IP only (no external IP addresses)
- Configured to use company VPC network and internal subnet
- Network tags for existing firewall rules compatibility
- Dedicated staging and temp buckets for job execution
- Dataproc 2.1 image with standard configuration:
  * 4GB executor memory
  * 2GB driver memory
  * 2 executor cores
  * 2 executor instances

VPC Network Configuration:
- Uses shared VPC network: ${var.network}
- Internal subnet: ${var.subnet_internal}
- Network project: ${var.network_project_id}
- Internal IP only mode enabled
*/