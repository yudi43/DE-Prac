from airflow import DAG
#import operators...
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2


with DAG(
    "Controlling_a_DAG_with_the_terminal",
    description="This DAG is to practice terminal commands to control airflow.",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2018,11,1),
    catchup=False,
) as dag:
    def my_func():
        print("This is a test..")
    
    test_task = PythonOperator(
        task_id="test_task",
        python_callable=my_func
    )

    test_task