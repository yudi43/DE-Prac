from airflow import DAG

from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.utils.trigger_rule import TriggerRule

from datetime import datetime
import psycopg2

dag = DAG(
    "Write_data_to_postgres_then_to_elasticsearch",
    description="This dag is used to write data from a csv file to postgres then to elastic search via logstash",
    start_date=datetime(2020, 8, 11),
    catchup=False,
)

with dag:
    # There will be 4 tasks,
    # 1 -> Check if the table already exists.
    # 2 -> Create table in postgres OR Wait for the file using the FileSensor (If the table is already there, I am using BranchPythonOperator for that.)
    # 3 -> Once the file arrives, push the data into postgreSQL
    # 4 -> From postgres, data should go to ElasticSearch via logstash (Plan is to use bash operator)

    def check_table():
        return "sense_the_csv"

    check_for_table = BranchPythonOperator(
        task_id="Check_for_table", python_callable=check_table,
    )

    # TASK 2 (Case if the table is not already there.) -> Create table in postgres.
    create_table = PostgresOperator(
        task_id="Create_Table_in_Postgres",
        sql="""CREATE TABLE sampletable(
            Date text,
            Open text,
            High text,
            Low text,
            Close text
        );
        """,
    )

    # TASK 2 (If the table is there, then this will be the second task) -> Wait for the file using the FileSensor
    file_sensing_task = FileSensor(
        trigger_rule=TriggerRule.ONE_SUCCESS,
        task_id="sense_the_csv",
        filepath="sample1.csv",
        fs_conn_id="my_file_system",
        poke_interval=10,
    )

    # Function that writes data to postgres, uses psycopg2
    def write_data():
        # push data to pg
        conn = psycopg2.connect("host=localhost dbname=testdb user=testuser")
        cur = conn.cursor()
        with open("sample1.csv", "r",) as f:
            next(f)
            cur.copy_from(f, "sampletable", sep=",")
        conn.commit()

    # TASK 3 -> Once the file arrives, push the data into postgreSQL
    push_data_to_pg = PythonOperator(
        task_id="Sensed_CSV_to_Postgres", python_callable=write_data
    )

    # TASK 4 -> From postgres, data should go to ElasticSearch via logstash (Plan is to use bash operator)
    push_data_to_elastic = BashOperator(
        task_id="Postgres_to_ElasticSearch",
        bash_command="/Users/yudi/ELK/logstash-7.10.0/bin/logstash -f /Users/yudi/ELK/logstash-7.10.0/bin/logstash-simple.conf",
    )

    check_for_table >> create_table >> file_sensing_task >> push_data_to_pg >> push_data_to_elastic
    check_for_table >> file_sensing_task >> push_data_to_pg >> push_data_to_elastic
