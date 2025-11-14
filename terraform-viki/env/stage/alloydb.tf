# gcloud compute ssh hhh-proxy \
#        --tunnel-through-iap \
#        --zone=us-east4-a \
#        --project=viki-stage-app-wsky \
#        --ssh-flag="-L 5433:10.235.120.63:5432"

# AlloyDB Cluster
resource "google_alloydb_cluster" "primary" {
  cluster_id = "medispan-cluster"
  project    = var.app_project_id
  location   = var.region

  initial_user {
    password = var.alloydb_password
    user     = "postgres"
  }

  network_config {
    network = "projects/${var.network_project_id}/global/networks/${var.network}"
  }
}

# resource "google_alloydb_cluster" "primary_public" {
#   cluster_id = "medispan-cluster-public"
#   project = var.app_project_id
#   location   = var.region

#   initial_user {
#     password = var.alloydb_password
#     user     = "postgres"
#   }

#   database_version = "POSTGRES_14"
# }

# Primary instance - DISABLED for cost savings
# Uncomment this resource to re-enable the AlloyDB instance
# resource "google_alloydb_instance" "primary" {
#   cluster       = google_alloydb_cluster.primary.name
#   instance_id   = "medispan-instance"
#   instance_type = "PRIMARY"
#
#   machine_config {
#     cpu_count = 4
#   }
#
#   depends_on = [google_alloydb_cluster.primary]
# }

# Create the medispan_drugs table and ANN index
# 


# command to create backup
# gcloud auth login
# gcloud alloydb clusters export medispan-cluster  --database=vectordb --gcs-uri=gs://viki-ai-provisional-dev/alloydb/backups --region=us-east4 --sql

# command to restore to new env
# gsutil cp gs://viki-ai-provisional-dev/alloydb/backups gs://viki-ai-provisional-{env}/alloydb/backups

# gcloud alloydb clusters import medispan-cluster --project viki-stage-app-wsky --gcs-uri=gs://viki-ai-provisional-qa/alloydb/backups --region=us-east4 --sql
