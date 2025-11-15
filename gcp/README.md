# MWAA ✕ GCP BigQuery OIDC Federation

This directory provides Terraform configurations to enable secure, keyless access from AWS MWAA (Airflow) to Google BigQuery using Workload Identity Federation with OIDC.

## High-Level Steps
1. **AWS**: Create an IAM role for MWAA to use for GCP federation (see `../aws/mwaa_oidc_role.tf`).
2. **GCP**: Set up BigQuery, Service Account, Workload Identity Pool, Provider, and trust relationship to your AWS role (see this directory's Terraform).
3. **MWAA (dbt DAGs)**: Use Workload Identity Federation JSON config as credentials for dbt to connect to BigQuery, never passing static keys.

## 1. Prerequisites
- Existing GCP project (`project_id`) and AWS account.
- Terraform (v1.3+ recommended) and AWS/GCP CLIs authenticated.

## 2. AWS Setup
Apply the Terraform in `../aws/mwaa_oidc_role.tf`:

```bash
cd ../aws
terraform init
terraform apply
```

Copy the output `mwaa_bq_oidc_role_arn` for use in the GCP step.

## 3. GCP Setup
Edit your `terraform.tfvars`:

```hcl
project_id          = "your-gcp-project-id"
region              = "us-central1"
aws_role_arn        = "<output arn from AWS>"
aws_oidc_issuer_uri = "https://sts.amazonaws.com" # Or your AWS OIDC issuer URI
bq_dataset_id       = "aws_mwaa_dataset"
# ... (fill in additional values as needed)
```

Apply the GCP Terraform:

```bash
cd ../gcp
terraform init
terraform apply
```

Note and save the outputs: service account email, pool ID, provider ID, dataset, etc.

## 4. MWAA & dbt Configuration
- In your Airflow environment (MWAA), configure dbt to use GCP via **Workload Identity Federation**, not service account keys!

### Example GCP Federation Credentials JSON (to use as `GOOGLE_APPLICATION_CREDENTIALS`):
Fill in values with your TF outputs:

```json
{
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/<POOL_ID>/providers/<PROVIDER_ID>",
  "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
  "token_url": "https://sts.googleapis.com/v1/token",
  "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/<SERVICE_ACCOUNT_EMAIL>:generateAccessToken",
  "credential_source": {
    "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/<ROLE_NAME>",
    "headers": {
      "Metadata-Flavor": "Amazon"
    },
    "format": {
      "type": "text"
    }
  }
}
```

- Save this JSON to a file (e.g., `/opt/airflow/secrets/gcp_federation.json`) and set the Airflow env var:
  - `GOOGLE_APPLICATION_CREDENTIALS` = path to that file.

### dbt profiles.yml snippet:
```yaml
<profile-name>:
  target: prod
  outputs:
    prod:
      type: bigquery
      method: oauth
      project: "<your-gcp-project>"
      dataset: "<your-dataset>"
      location: US
      threads: 2
      timeout_seconds: 300
```

---

## References
- https://cloud.google.com/iam/docs/workload-identity-federation
- https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile
- https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html
