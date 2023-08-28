from dotenv import load_dotenv,find_dotenv
from pymongo import MongoClient
import os

load_dotenv(find_dotenv())

mongodb_url = os.environ.get("MONGODB_URL")
client = MongoClient(mongodb_url)

attraction_db = client.attraction