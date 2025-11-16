from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils import timezone

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

say_goodbye = BashOperator(
        task_id='say_goodbye',
        bash_command="pip freeze",
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

say_hello >> say_goodbye
