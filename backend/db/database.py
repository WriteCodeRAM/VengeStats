import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    try:
        if db_url:
            # prod
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgres://", 1)
            return psycopg2.connect(db_url)
        else:
            # local fallback
            return psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", 5432),
            )
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise
