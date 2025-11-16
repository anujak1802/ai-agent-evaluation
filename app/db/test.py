from dotenv import load_dotenv
import os

print("Loading .env...")
load_dotenv()

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
