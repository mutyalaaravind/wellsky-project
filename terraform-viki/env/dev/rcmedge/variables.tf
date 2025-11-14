variable "app_project_id" {
  description = "The project ID to deploy to"
  type        = string
}

variable "dmz_project_id" {
  description = "The project ID to deploy to"
  type        = string
}

variable "mgmt_project_id" {
  description = "The management project ID for images"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "env" {
  description = "Environment (dev, qa, stage, prod)"
  type        = string
  default     = "dev"
}

variable "rcmedge_version" {
  description = "The version of the rcmedge service to deploy"
  type        = string
}

variable "allow_public_access" {
  description = "Whether to allow public access to the service"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "managers" {
  description = "List of manager emails for the application"
  type        = list(string)
  default     = []
}