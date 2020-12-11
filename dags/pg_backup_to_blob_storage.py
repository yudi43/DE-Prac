import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.sensors.file_sensor import FileSensor

from azure.storage.blob import BlobClient

from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

container_name = "your_container_name"
connection_string = "your_connection_string"

with DAG(
    "Send_PG_backup_to_Azure_Blob_Storage",
    description="This pipeline is made for taking backup of postgres database and seding to Azure data blob in tar.gz format",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2019, 11, 1),
    catchup=False
) as dag:

    # TASK 1: Take backup of a database on local storage (in tar.gz format).
    create_backup = BashOperator(
        task_id = "Create_backup_of_localdb",
        bash_command="pg_dump -U yudi sample_database -F tar -f ~/workspace/DE-Prac/dags/backup.tar.gz"
    )

    # TASK 2: Sense the backup file, wait until it appears.
    file_sensing_task = FileSensor(
        task_id="sense_the_backup_file",
        filepath="backup.tar.gz",
        fs_conn_id="my_file_system",
        poke_interval=10,
    )

    # TASK 3: Upload it to azure data blob
    def upload_data():
        print("WORKING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        blob_name="pg_backup"
        blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=blob_name)
        with open("/Users/yudi/workspace/DE-Prac/dags/backup.tar.gz", "rb") as data:
            blob.upload_blob(data)


    upload_to_blob_storage = PythonOperator(
        task_id="upload_to_blob_storage",   
        python_callable=upload_data,
    )

    create_backup >> file_sensing_task >> upload_to_blob_storage

