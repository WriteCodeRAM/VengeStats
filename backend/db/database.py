import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def get_player_id(first_name: str, last_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    query = sql.SQL("SELECT id FROM players WHERE first_name = %s AND last_name = %s")
    cursor.execute(query, (first_name, last_name))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

def insert_player_team_history(player_id: int, team_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = sql.SQL("""
        INSERT INTO player_team_history (player_id, team_id)
        VALUES (%s, %s)
        ON CONFLICT (player_id, team_id) DO NOTHING
    """)
    cursor.execute(insert_query, (player_id, team_id))
    conn.commit()
    cursor.close()
    conn.close()
