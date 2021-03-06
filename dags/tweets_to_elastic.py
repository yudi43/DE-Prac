import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import tweepy as tw
import psycopg2

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_TOKEN_SECRET")

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


class Tweet:
    def __init__(self, message, name, screen_name, id_string, location):
        self.message = message
        self.name = name
        self.screen_name = screen_name
        self.id_string = id_string
        self.location = location


class MyStreamListener(tw.StreamListener):
    def on_status(self, status):
        new_tweet = Tweet(
            status.text,
            status.user.name,
            status.user.screen_name,
            status.user.id_str,
            status.user.location,
        )
        print(new_tweet.message)
        try:

            connection = psycopg2.connect("host=localhost dbname=testdb user=testuser")
            cursor = connection.cursor()
            postgres_insert_query = """
                INSERT INTO tweets(text, name, screen_name, id_string, location) VALUES (%s, %s, %s, %s, %s)
            """
            data_to_insert = (
                new_tweet.message,
                new_tweet.name,
                new_tweet.screen_name,
                new_tweet.id_string,
                new_tweet.location,
            )
            cursor.execute(postgres_insert_query, data_to_insert)
            connection.commit()
            count = cursor.rowcount
            print(count, " Record inserted successfully into the tweets table.")
        except (Exception, psycopg2.Error) as Error:
            print("This is the error: " + str(Error))
            if not connection:
                print("Failed to insert the data into the tweets table.")
                return False
        finally:
            # closing the database connection
            if not connection:
                cursor.close()
                connection.close()
                print("Postgres connection is closed.")
                return False
        return True

    def on_error(self, status_code):
        if status_code == 420:
            return False


myStreamListener = MyStreamListener()
myStream = tw.Stream(auth=api.auth, listener=myStreamListener)

myStream.filter(track=["trump"], is_async=True)
# text, user {'name', 'id_str', 'location', 'screen_name'}
