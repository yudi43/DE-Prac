from airflow import DAG

# from airflow.operators.postgres_operator import PostgresOpeartor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

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

    def test():
        print("test")

    create_table = PythonOperator(
        task_id="Create_table_in_postgres", python_callable=test
    )

    print_something = PythonOperator(
        task_id="Test_the_damn_script", python_callable=test
    )

    create_table >> print_something

