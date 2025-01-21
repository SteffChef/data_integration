import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print(os.getenv('DATABASE_URI'))  # Check if this prints your supabase URI

class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY','default_secret_key')
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")