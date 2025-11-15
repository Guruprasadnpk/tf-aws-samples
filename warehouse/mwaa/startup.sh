#!/bin/bash
set -eux
export ENVIRONMENT="dev"
export GCP_PROJECT_ID="gurppup-123"
export BIGQUERY_DATASET="aws_mwaa_dataset"
export BIGQUERY_LOCATION="US"
export DBT_THREADS=4
export DBT_VENV_PATH="${AIRFLOW_HOME}/dbt_venv"
export DBT_PROJECT_PATH="${AIRFLOW_HOME}/dags/dbt"

export PIP_USER=false
python3 -m venv "${DBT_VENV_PATH}"
${DBT_VENV_PATH}/bin/pip install dbt-bigquery
export PIP_USER=true
${DBT_VENV_PATH}/bin/pip install boto3

# Download GCP OIDC credential JSON from AWS Secrets Manager
export SECRET_NAME="gcp-oidc-creds"
export REGION_NAME="${AWS_REGION:-us-west-2}"
export CREDS_PATH="/tmp/gcp-oidc-creds.json"

python3 <<EOF
import boto3, os
secret_name = os.environ["SECRET_NAME"]
region_name = os.environ["REGION_NAME"]
creds_path = os.environ["CREDS_PATH"]
client = boto3.client("secretsmanager", region_name=region_name)
secret = client.get_secret_value(SecretId=secret_name)["SecretString"]
with open(creds_path, "w") as f:
    f.write(secret)
EOF

export GOOGLE_APPLICATION_CREDENTIALS=${CREDS_PATH}

# Set region default if not provided
#AWS_REGION=${AWS_REGION:-us-west-2}

# (Optional) Ensure awscli exists - MWAA images include it by default
# which aws || pip install awscli

# Generate dbt profiles.yml at container startup using Airflow Connection secret
#python3 /usr/local/airflow/dags/render_profiles_from_airflow_conn.py
