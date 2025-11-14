variable "app_project_id" {
  description = "The GCP project ID where the application resources will be created."
  type        = string
}

variable "region" {
  description = "The GCP region where resources will be created."
  type        = string
  default     = "us-central1"
}

variable "labels" {
  description = "A map of labels to apply to resources."
  type        = map(string)
  default     = {}
}

variable "managers" {
  description = "A list of IAM members who will have manager access to the secrets."
  type        = list(string)
  default     = []
}

variable "image_version" {
  description = "The version of the container image to be used in the application."
  type        = string
  default     = ""

}

variable "network_tags" {
  description = "A list of network tags to apply to resources."
  type        = list(string)
  default     = []
}


variable "mgmt_project_id" {
  description = "The GCP project ID where the management resources are located."
  type        = string
}

variable "vpc_connector" {
  description = "The name of the VPC connector to use for Cloud Run services."
  type        = string
}

variable "env" {
  description = "The environment name (e.g., dev, prod)."
  type        = string
}