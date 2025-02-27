import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

REVENGE_GAME_QUERY = """
SELECT DISTINCT 
    p.id AS player_id, 
    p.first_name, 
    p.last_name, 
    curr_team.name AS current_team_name,  
    former_team.name AS former_team_name  
FROM players p
JOIN player_team_history pth ON p.id = pth.player_id
JOIN teams curr_team ON p.current_team_id = curr_team.id  -- Get current team
JOIN teams former_team ON pth.team_id = former_team.id  -- Get former team
WHERE 
    (p.current_team_id = %s AND pth.team_id = %s)  -- Player is currently on Team A, used to be on Team B
    OR 
    (p.current_team_id = %s AND pth.team_id = %s); -- Player is currently on Team B, used to be on Team A
"""

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

# gonna pass the list of team ids here 
def get_revenge_games(schedule):
    conn = get_connection()
    cursor = conn.cursor()
    
    revenge_games = []
    for away_team, home_team in schedule:  
        cursor.execute(REVENGE_GAME_QUERY, (away_team, home_team, home_team, away_team))
        players = cursor.fetchall()  

        for player in players:
            revenge_games.append(f"{player[1]} {player[2]} is facing his former team {player[4]} today!") 

    return revenge_games