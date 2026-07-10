import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rachepallinandini_db_user:Nandini2005@cluster0.dli41nw.mongodb.net/")
DB_NAME = os.getenv("DB_NAME", "RealTimeChatDB")
