// Terraform module: GCP BigQuery & OIDC for AWS MWAA

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "project" {
  project_id = var.project_id
}

// Enable BigQuery API
resource "google_project_service" "bigquery" {
  project = var.project_id
  service = "bigquery.googleapis.com"
}

// Create BigQuery Dataset
resource "google_bigquery_dataset" "aws_mwaa_dataset" {
  dataset_id                  = var.bq_dataset_id
  project                     = var.project_id
  location                    = var.bq_location
}

// Service Account for AWS MWAA
resource "google_service_account" "mwaa_oidc_sa" {
  account_id   = var.sa_account_id
  display_name = "SA for AWS MWAA OIDC"
}

// Grant BigQuery roles to SA
resource "google_project_iam_member" "bq_roles" {
  for_each = toset(["roles/bigquery.dataEditor", "roles/bigquery.jobUser"])
  project  = var.project_id
  member   = "serviceAccount:${google_service_account.mwaa_oidc_sa.email}"
  role     = each.key
}

// Workload Identity Pool
resource "google_iam_workload_identity_pool" "aws_pool" {
  provider                  = google
  workload_identity_pool_id = var.identity_pool_id
  display_name              = "AWS OIDC Pool for MWAA"
  description               = "OIDC pool to trust AWS for MWAA access"
  project                   = var.project_id
  disabled                  = false
}

// Workload Identity Provider for AWS OIDC tokens
resource "google_iam_workload_identity_pool_provider" "aws_provider" {
  provider                        = google
  workload_identity_pool_id       = google_iam_workload_identity_pool.aws_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.identity_provider_id
  display_name                    = "AWS OIDC provider"
  description                     = "Trust AWS OIDC tokens (for MWAA)"
  attribute_mapping = {
    "google.subject" = "assertion.sub"
    "attribute.aws_role" = "assertion.arn"
  }
  oidc {
    issuer_uri = var.aws_oidc_issuer_uri
  }
  attribute_condition = "assertion.aud == \"sts.amazonaws.com\""
}

// Allow Service Account impersonation by Pool principal
resource "google_service_account_iam_member" "impersonate_from_pool" {
  service_account_id = google_service_account.mwaa_oidc_sa.name
  role              = "roles/iam.workloadIdentityUser"
  member            = "principalSet://iam.googleapis.com/projects/${data.google_project.project.number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.aws_pool.workload_identity_pool_id}/attribute.aws_role/${var.aws_role_arn}"
}

// Grant the 'roles/run.invoker' IAM role for a Cloud Run job/service to the MWAA OIDC Service Account. Assume existence of a 'google_cloud_run_job' resource named 'sample_job'.
# resource "google_cloud_run_job_iam_member" "mwaa_oidc_invoker" {
#   job    = google_cloud_run_job.sample_job.name
#   region = var.region
#   project = var.project_id
#   role   = "roles/run.invoker"
#   member = "serviceAccount:${google_service_account.mwaa_oidc_sa.email}"
# }

// Required variables (to be defined in variables.tf)
// - project_id
// - region
// - bq_dataset_id
// - bq_location
// - sa_account_id
// - identity_pool_id
// - identity_provider_id
// - aws_oidc_issuer_uri
// - aws_role_arn
