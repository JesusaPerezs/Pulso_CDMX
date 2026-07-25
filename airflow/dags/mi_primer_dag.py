from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id = "mi_primer_dag",
    start_date = datetime(2026, 1, 1),
    schedule = "@daily",
    catchup=False,
    tags=["pueba"],
) as dag:

    tarea_1 = BashOperator(
        task_id="saludar",
        bash_command="echo 'Hola desde Airflow!'",
    )

    tarea_2 = BashOperator(
        task_id = "despedir",
        bash_command="echo 'Adios desde Airflow'",
    )
    tarea_1 >> tarea_2