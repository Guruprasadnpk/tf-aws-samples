"""
Sample dbt DAG using cosmos for MWAA
"""
import os
from datetime import datetime
from pathlib import Path

from airflow import DAG
from cosmos import DbtDag, ProjectConfig, ProfileConfig, RenderConfig, TestBehavior
from cosmos.config import ExecutionConfig

# Set up DBT project and profile paths (inside the Airflow container)
DBT_PROJECT_PATH = Path("/usr/local/airflow/dags/dbt")

# ProjectConfig - points to directory with dbt_project.yml for jaffle_shop
project_config = ProjectConfig(
    DBT_PROJECT_PATH,
)

# ProfileConfig - points to profiles.yml and uses profile/target for BigQuery
profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profiles_yml_filepath=str(DBT_PROJECT_PATH / "profiles.yml"),
)

execution_config = ExecutionConfig(
    dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt"
)

# Optional: RenderConfig - ensures build/test behavior
render_config = RenderConfig(
    test_behavior=TestBehavior.BUILD,
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False
}

dbt_build_dag = DbtDag(
    # dbt/cosmos-specific parameters
    project_config=project_config,
    render_config=render_config,
    profile_config=profile_config,
    execution_config=execution_config,
    operator_args={
        "install_deps": True,  # install any necessary dependencies before running any dbt command
        "full_refresh": False,  # set to True if you want a full refresh
    },
    # normal DAG parameters
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    dag_id="dbt_cosmos_sample_dag",
    default_args=default_args,
)
