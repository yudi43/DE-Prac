import uuid
from datetime import datetime
from airflow import DAG
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

import psycopg2

with DAG(
    "Write_data_to_PG",
    description="This DAG is for writing data to postgres.",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2018, 11, 1),
    catchup=False,
) as dag:
    create_table = PostgresOperator(
        task_id="create_table",
        sql="""CREATE TABLE sampletable(
            Date text,
            Open text,
            High text,
            Low text,
            Close text
        );
        """,
    )

    def my_func():
        print("Creating table in database.")
        conn = psycopg2.connect("host=localhost dbname=testdb user=testuser")
        print(conn)

        cur = conn.cursor()
        print(cur)

        with open("sample1.csv", "r") as f:
            next(f)  # Skip the header row.
            cur.copy_from(f, "sampletable", sep=",")

        conn.commit()
        print(conn)
        print("DONE!!!!!!!!!!!.")

    file_sensing_task = FileSensor(
        task_id="sense_the_csv",
        filepath="sample1.csv",
        fs_conn_id="my_file_system",
        poke_interval=10,
    )

    python_task = PythonOperator(task_id="populate_data", python_callable=my_func)

    create_table >> file_sensing_task >> python_task

#
# ----------------------------------------------------------------------------------------------------------------------
#
# from airflow import DAG
# from airflow.operators.dummy_operator import DummyOperator
# from airflow.operators.python_operator import PythonOperator
# import psycopg2
# import uuid
#
# from datetime import datetime
#
# # dag_params = {
# #     'dag_id': 'PostgresOperator_dag',
# #     'start_date': datetime(2019, 10, 7),
# #     'schedule_interval': None
# # }
#
#
# def my_func():
#     print('Creating table in database.')
#     conn = psycopg2.connect("host=localhost dbname=testdb user=testuser")
#     cur = conn.cursor()
#     insert_query = "INSERT INTO users VALUES {}".format("88899923, datetime.now(), ab23a3d202")
#     cur.execute(insert_query)
#     conn.commit()
#     print('DONE!!!!!!!!!!!.')
#
#
# # with DAG(**dag_params) as dag:
# with DAG('Write_data_to_PG', description='This DAG is for writing data to postgres.', schedule_interval='*/5 * * * *', start_date=datetime(2018, 11, 1),
#          catchup=False) as dag:
#     dummy_task = DummyOperator(task_id='dummy_task', retries=3)
#     python_task = PythonOperator(task_id='python_task', python_callable=my_func)
#
#     dummy_task >> python_task
