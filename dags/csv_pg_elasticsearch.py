from airflow import DAG

from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
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
    # 1 -> Create table in postgres.
    # 2 -> Wait for the file using the FileSensor
    # 3 -> Once the file arrives, push the data into postgreSQL
    # 4 -> From postgres, data should go to ElasticSearch via logstash (Plan is to use bash operator)

    # TASK 1 -> Create table in postgres. (//TODO: CHECK IF THE TABLE ALREADY EXISTS)
    create_table = PostgresOperator(
        task_id="Create_table_in_postgres",
        sql="""CREATE TABLE sampletable(
            Date text,
            Open text,
            High text,
            Low text,
            Close text
        );
        """,
    )

    # TASK 2 -> Wait for the file using the FileSensor
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    # Function that writes data to postgres, uses psycopg2
    def write_data():
        # # replace the x00 characters before the insert
        # with open("data.csv", "r") as reader, open("test.csv", "w") as writer:
        #     print("this is the reader")
        #     print(reader)
        #     print("the endd")
        #     for row in reader:
        #         print(row)
        #         writer.write(row.replace("\u0000", ""))

        # push data to pg
        conn = psycopg2.connect("host=localhost dbname=testdb user=testuser")
        cur = conn.cursor()
        with open("sample1.csv", "r",) as f:
            next(f)
            cur.copy_from(f, "sampletable", sep=",")
        conn.commit()

    # TASK 3 -> Once the file arrives, push the data into postgreSQL
    push_data_to_pg = PythonOperator(
        task_id="Write_csv_data_to_db", python_callable=write_data
    )

    # TASK 4 -> From postgres, data should go to ElasticSearch via logstash (Plan is to use bash operator)
    push_data_to_elastic = BashOperator(
        task_id="export_data_to_elasticsearch",
        bash_command="/Users/yudi/ELK/logstash-7.10.0/bin/logstash -f /Users/yudi/ELK/logstash-7.10.0/bin/logstash-simple.conf",
    )

    create_table >> push_data_to_pg >> push_data_to_elastic
