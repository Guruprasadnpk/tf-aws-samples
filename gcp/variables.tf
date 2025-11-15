variable "project_id" {
  description = "The GCP project ID."
  type        = string
  default     = "gurppup-2885"
}

variable "region" {
  description = "The GCP region for resources."
  type        = string
  default     = "us-west-2"
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID."
  type        = string
  default     = "aws_mwaa_dataset"
}

variable "bq_location" {
  description = "Location for the BigQuery dataset."
  type        = string
  default     = "US"
}

variable "sa_account_id" {
  description = "Service Account ID for MWAA OIDC federation (without @project)."
  type        = string
  default     = "mwaa-oidc-sa"
}

variable "identity_pool_id" {
  description = "ID for Workload Identity Pool to trust AWS OIDC for MWAA."
  type        = string
  default     = "mwaa-oidc-pool"
}

variable "identity_provider_id" {
  description = "ID for Workload Identity Provider inside the pool for MWAA."
  type        = string
  default     = "mwaa-oidc-provider"
}

variable "aws_oidc_issuer_uri" {
  description = "AWS OIDC issuer URI. Typically https://accounts.google.com or a custom AWS OIDC endpoint."
  type        = string
  default     = "arn:aws:iam::293661646409:role/mwaa-oidc-role"
}

variable "aws_role_arn" {
  description = "AWS Role ARN that will access BigQuery (referenced in principalSet)."
  type        = string
  default     = "arn:aws:iam::293661646409:role/mwaa-executor20251112011644352100000002"
}
