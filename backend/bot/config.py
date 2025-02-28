import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")