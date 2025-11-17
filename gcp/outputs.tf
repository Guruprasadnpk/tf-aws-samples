output "service_account_email" {
  value = google_service_account.mwaa_oidc_sa.email
}

output "bq_dataset_id" {
  value = google_bigquery_dataset.aws_mwaa_dataset.dataset_id
}

output "workload_identity_pool_id" {
  value = google_iam_workload_identity_pool.aws_pool.workload_identity_pool_id
}

output "workload_identity_provider_id" {
  value = google_iam_workload_identity_pool_provider.aws_provider.workload_identity_pool_provider_id
}

output "workload_identity_provider_resource" {
  description = "Full resource name of the Workload Identity Provider"
  value = google_iam_workload_identity_pool_provider.aws_provider.name
}
