from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils import timezone
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['test@yourdomain.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

DAG_ID = "hello_world_scheduled_dag"

dag = DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description='Scheduled Apache Airflow DAG',
    schedule='* 1 * * *',
    start_date=timezone.datetime(2023, 11, 1),
    tags=['aws','demo'],
)

say_hello = BashOperator(
        task_id='say_hello',
        bash_command="echo hello" ,
        dag=dag
    )

check_role_arn = BashOperator(
    task_id='check_role_arn',
    bash_command="aws sts get-caller-identity",
    dag=dag
)

def run_bq_query():
    creds_path = os.environ.get("CREDS_PATH", os.path.expandvars("${AIRFLOW_HOME}/dags/dbt/gcp_oidc_creds.json"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    client = bigquery.Client()
    query_job = client.query("SELECT CURRENT_DATE() as today")
    row = next(query_job.result())
    print(f"Today's date from BigQuery: {row['today']}")

query_bigquery_with_oidc = PythonOperator(
    task_id='query_bigquery_with_oidc',
    python_callable=run_bq_query,
    dag=dag,
)

say_goodbye = BashOperator(
        task_id='say_goodbye',
        bash_command="env",
        dag=dag
    )


# render_dbt_profiles = BashOperator(
#     task_id='render_dbt_profiles',
#     bash_command=(
#         'python3 /usr/local/airflow/dags/dbt_sample_project/render_profiles_from_airflow_conn.py && '
#         'cat /tmp/profiles.yml'
#     ),
#     dag=dag,
# )

#render_dbt_profiles >> say_hello

say_hello >> check_role_arn >> query_bigquery_with_oidc >> say_goodbye
