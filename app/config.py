import os

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 120
ALGORITHM = "HS256"
SECRET_KEY = "your_secret_key"
TIMEZONE = "Asia/Taipei"

USER_COLLECTION = "user"
CONTEST_COLLECTION = "contest"

MONGO_URL = "mongodb://@localhost:27017"
MONGO_DB = ""

REDIS_URL = "redis://localhost:6379"
