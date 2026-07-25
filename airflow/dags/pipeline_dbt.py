from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Comando base para llamar dbt dentro del contenedor.
# Usamos 'python -m dbt.cli.main' porque el ejecutable 'dbt' no está en el PATH.
DBT_DIR = "/opt/airflow/dbt"
DBT = f"python -m dbt.cli.main"

with DAG(
    dag_id="pipeline_dbt",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["pulso_cdmx", "dbt"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"{DBT} run --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{DBT} test --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}",
    )

    dbt_run >> dbt_test