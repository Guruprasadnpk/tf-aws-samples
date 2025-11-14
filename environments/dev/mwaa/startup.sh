#!/bin/bash
set -eux
export DBT_VENV_PATH="${AIRFLOW_HOME}/dbt_venv"
export DBT_PROJECT_PATH="${AIRFLOW_HOME}/dags/dbt"

export PIP_USER=false
python3 -m venv "${DBT_VENV_PATH}"
${DBT_VENV_PATH}/bin/pip install dbt-postgres
export PIP_USER=true

# Set region default if not provided
#AWS_REGION=${AWS_REGION:-us-west-2}

# (Optional) Ensure awscli exists - MWAA images include it by default
# which aws || pip install awscli

# Generate dbt profiles.yml at container startup using Airflow Connection secret
python3 /usr/local/airflow/dags/render_profiles_from_airflow_conn.py
