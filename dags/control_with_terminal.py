from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
import psycopg2
from psycopg2 import sql


with DAG(
    "Controlling_a_DAG_with_the_terminal",
    description="This DAG is to practice terminal commands to control airflow.",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2018,11,1),
    catchup=False,
) as dag:
    def create_schema(ds, **kwargs):
        print("Remotely received value of {} for key = message".format(kwargs['dag_run'].conf['client_name']))
        try:
            conn = psycopg2.connect(database="testdb", host="localhost")
            cursor = conn.cursor()
            schema_name = kwargs['dag_run'].conf['client_name']
            cursor.execute(
                sql.SQL("create schema {}")
                .format(sql.Identifier(schema_name)))
            conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    test_task = PythonOperator(
        task_id="test_task",
        python_callable=create_schema,
        provide_context = True
    )

    # bash_task = BashOperator(
    #     task_id = "bash-task",
    #     bash_command='echo "Here is the message: '
    #              '{{ dag_run.conf["message"] if dag_run else "" }}" ',
    # )

    test_task