import os
import psycopg2
from psycopg2 import sql
from psycopg2 import Error
from datetime import datetime
import pandas as pd
from airflow import DAG
from airflow.operators import python_operator

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

dag = DAG("Check_for_new_entries_and_send_mail", description = "This dag is to check if there were new entries made in the database, if so then send mail to users at the end of the day.", start_date = datetime(2020, 8, 11), catchup = False)

with dag:
    #task 1: check if there were new entries made today.
    def get_todays_entries_and_send_mail():
        entries_made_today = [] # This list will hold all the entries that were made today.
        usr_pwd = "selectionplss"

        try:
            # Define schema and table names respectively
            schema_name = 'public'
            table_name = 'DailySiteReportData';
            connection = psycopg2.connect(user = "abhijeet", password = "9zsU5DmuTZ6kyFR", host = "localhost", port = "5433", database = "efw")
            cursor = connection.cursor()

            # Get all the columns information
            cursor.execute(sql.SQL("SELECT * FROM {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name)
            ))
            colnames = [desc[0] for desc in cursor.description] # This list will contain all the column names.
            
            # Get the index of column named "date"
            index_of_date = colnames.index('date')
            todays_date = datetime.today().strftime('%Y-%m-%d')

            table = cursor.fetchall() 
            for entry in table:
                if entry[index_of_date].strftime('%Y-%m-%d') == todays_date:
                    entries_made_today.append(entry)

            # Create a dataframe and save as .xlsx file.
            df = pd.DataFrame(entries_made_today, columns = colnames) 
            file_name = "test.xlsx"
            out_path = '/Users/yudi/workspace/DE-Prac/dags/' + file_name;
            df.to_excel(out_path)
            print('Excel sheet saved with ' + str(len(entries_made_today)) + ' entries.')
        except (Exception, Error) as error:
            print("Error while connecting to Postgres", error)
        finally:
            if(connection):
                cursor.close()
                connection.close()
                print("Postgres connection is closed")

        ####### Code below is to send the mail, if there are any entries made on that day.
        if(len(entries_made_today) > 0):
            subject = "An email with attachment from Python"
            body = "This is an email with attachment sent from Python"
            sender_email = "singh.yudi10@gmail.com"
            receiver_email = "arun.shenoy@joulon.com"
            password = usr_pwd

            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            # Add body to email
            message.attach(MIMEText(body, "plain"))

            filename = "/Users/yudi/workspace/DE-Prac/dags/test.xlsx"

            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
            text = message.as_string()

            # Log in to server using secure context and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, text)


    check_entries_and_send_mail = python_operator.PythonOperator(
        task_id = "check_entries_and_send_email",
        python_callable = get_todays_entries_and_send_mail
    )

    check_entries_and_send_mail

