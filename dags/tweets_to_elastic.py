import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import tweepy as tw

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_TOKEN_SECRET")

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

api.update_status(
    "From now on, some my tweets will be from a python script. Like this one!"
)
