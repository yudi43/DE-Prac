from airflow import DAG
from datetime import datetime

with DAG(
    "Send PG backup to Azure Data Blob",
    description="This pipeline is made for taking backup of postgres database and seding to Azure data blob in tar.gz format",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2019, 11, 1),
    catchup=False
) as dag:
    print("do something")

    # SPLITTING THE TASKS:

    # TASK 1: Take backup of a database on local storage (in tar.gz format).
    # TASK 2: Encrypt the backup.
    # TASK 3: Upload it to azure data blob

    
