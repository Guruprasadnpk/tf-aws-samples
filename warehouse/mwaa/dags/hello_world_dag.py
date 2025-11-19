import os
from datetime import datetime

import boto3
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

from google.auth import aws as google_auth_aws
from google.auth.transport.requests import Request
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Config via environment variables (set these in your MWAA environment)
#
# GCP_AUDIENCE       : the "audience" string from your GCP external account /
#                      workload identity provider config
# GCP_PROJECT        : GCP project id for BigQuery
# AWS_OIDC_ROLE_ARN  : arn:aws:iam::293661646409:role/mwaa-oidc-role
# AWS_REGION         : AWS region for STS / signing (e.g. "us-west-2")
# ---------------------------------------------------------------------------

GCP_AUDIENCE = os.environ["GCP_AUDIENCE"]
GCP_PROJECT = os.environ["GCP_PROJECT_ID"]
AWS_OIDC_ROLE_ARN = os.environ.get("AWS_OIDC_ROLE_ARN")
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")


def _assume_oidc_role_if_needed(base_session: boto3.Session) -> boto3.Session:
    """
    If AWS_OIDC_ROLE_ARN is set, assume that role from the MWAA
    execution role and return a new boto3.Session built from the
    temporary credentials. Otherwise just return the base session.

    This keeps a clean separation:
      - MWAA execution role: airflow / infra access
      - mwaa-oidc-role     : used only for AWS→GCP federation
    """
    if not AWS_OIDC_ROLE_ARN:
        return base_session

    sts = base_session.client("sts", region_name=AWS_REGION)
    resp = sts.assume_role(
        RoleArn=AWS_OIDC_ROLE_ARN,
        RoleSessionName="mwaa-bigquery-oidc-session",
    )

    creds = resp["Credentials"]

    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=AWS_REGION,
    )


def query_bigquery_with_oidc(**_kwargs):
    """
    Task:
      1. Get AWS creds from MWAA (optionally via mwaa-oidc-role).
      2. Exchange them for a GCP access token using Workload Identity Federation.
      3. Run a simple BigQuery query to validate everything is wired correctly.
    """

    # 1) Base session uses MWAA execution role credentials
    base_session = boto3.Session()

    # 2) Optionally assume the mwaa-oidc-role
    aws_session = _assume_oidc_role_if_needed(base_session)

    # 3) Let google-auth use this session to call STS + GCP STS.
    # Some google-auth versions (including the one bundled with MWAA) do not
    # yet implement Credentials.from_session, so we construct the credentials
    # manually from the boto3 session's underlying credentials.
    session_creds = aws_session.get_credentials()
    if session_creds is None:
        raise RuntimeError("No AWS credentials available in boto3 session")

    frozen_creds = session_creds.get_frozen_credentials()

    aws_creds = google_auth_aws.Credentials(
        access_key_id=frozen_creds.access_key,
        secret_access_key=frozen_creds.secret_key,
        session_token=frozen_creds.token,
        region=AWS_REGION,
        audience=GCP_AUDIENCE,
        subject_token_type="urn:ietf:params:aws:token-type:aws4_request",
    )

    # 4) Force a refresh to get an access token (good for debugging)
    aws_creds.refresh(Request())

    # 5) Use those credentials with BigQuery
    bq_client = bigquery.Client(
        project=GCP_PROJECT,
        credentials=aws_creds,
    )

    query = "SELECT 1 AS col"
    job = bq_client.query(query)
    rows = list(job.result())
    for row in rows:
        print(f"BigQuery result row: col={row.col}")

    # Log some identity info (optional, but handy)
    print(f"Successfully queried BigQuery in project {GCP_PROJECT}")


# ---------------------------------------------------------------------------
# Airflow DAG definition
# ---------------------------------------------------------------------------

local_tz = pendulum.timezone("UTC")

with DAG(
    dag_id="hello_world_scheduled_dag",
    schedule=None,  # or "0 * * * *" etc
    start_date=datetime(2025, 1, 1, tzinfo=local_tz),
    catchup=False,
    tags=["example", "bigquery", "oidc"],
) as dag:

    query_bigquery_task = PythonOperator(
        task_id="query_bigquery_with_oidc",
        python_callable=query_bigquery_with_oidc,
    )

    # If you have other tasks (e.g. a "hello_world" print), you can chain them:
    # hello_task >> query_bigquery_task
