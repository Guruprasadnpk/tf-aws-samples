"""
Sample dbt DAG using cosmos for MWAA
"""
from airflow import DAG
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
import pendulum

# dbt_project_path is required, profiles_path is optional and set in ProfileConfig
PROJECT_CONFIG = ProjectConfig(
    dbt_project_path="/usr/local/airflow/dags/dbt/"
)
PROFILE_CONFIG = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profiles_yml_filepath="/usr/local/airflow/dags/dbt/profiles.yml"
)
EXECUTION_CONFIG = ExecutionConfig(
    dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt"
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False
}

dag = DAG(
    dag_id="dbt_cosmos_sample_dag",
    schedule="@daily",
    default_args=default_args,
    start_date=pendulum.now().subtract(days=1),
    catchup=False,
    tags=["dbt", "cosmos", "sample"]
)

with dag:
    dbt_tg = DbtTaskGroup(
        group_id="dbt_run_and_test",
        project_config=PROJECT_CONFIG,
        profile_config=PROFILE_CONFIG,
        execution_config=EXECUTION_CONFIG
    )

dbt_tg
