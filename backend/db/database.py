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
FROM nba_players p
JOIN nba_player_team_history pth ON p.id = pth.player_id
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

def get_player_id(first_name: str, last_name: str, current_team_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    query = sql.SQL("SELECT id FROM nba_players WHERE first_name = %s AND last_name = %s")
    cursor.execute(query, (first_name, last_name))
    result = cursor.fetchone()

    if result:
        cursor.close()
        conn.close()
        return result[0]
    
    # If player doesn't exist, insert them
    insert_query = sql.SQL("""
        INSERT INTO nba_players (first_name, last_name, current_team_id, prev_team_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """)
    cursor.execute(insert_query, (first_name, last_name, current_team_id, current_team_id))  # Default prev_team_id = current_team_id
    new_player_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    
    return new_player_id


def get_current_nba_roster(team_id: int):
    """Returns a set of players currently on an NBA team's roster from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = sql.SQL("SELECT first_name, last_name FROM nba_players WHERE current_team_id = %s")
    cursor.execute(query, (team_id,)) 

    res = cursor.fetchall() 
    
    # convert to a set of full names for easy comparison
    current_roster = {(row[0], row[1]) for row in res}  # ("LeBron", "James")


    cursor.close()
    conn.close()

    return current_roster


def insert_player_team_history(player_id: int, team_id: int, games_played: int):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = sql.SQL("""
        INSERT INTO nba_player_team_history (player_id, team_id, games_played)
        VALUES (%s, %s, %s)
        ON CONFLICT (player_id, team_id) DO UPDATE 
        SET games_played = EXCLUDED.games_played
    """)
    cursor.execute(insert_query, (player_id, team_id, games_played))
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
            revenge_games.append([f"{player[1]} {player[2]}", player[4], None]) 

    return revenge_games

def move_player_to_team(player_id: int, new_team_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    query = sql.SQL("""
        SELECT current_team_id, prev_team_id FROM nba_players 
        WHERE id = %s
    """)
    cursor.execute(query, (player_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return  

    current_team, prev_team = result

    print(f"🔍 Moving Player ID {player_id}: Current Team {current_team} → New Team {new_team_id}, Prev Team {prev_team}")

    # Ensure prev_team_id doesn't get overwritten if the player is currently on team 31
    new_prev_team_id = prev_team if current_team == 31 else current_team  

    update_query = sql.SQL("""
        UPDATE nba_players 
        SET prev_team_id = %s, 
            current_team_id = %s 
        WHERE id = %s
    """)
    cursor.execute(update_query, (new_prev_team_id, new_team_id, player_id))
    
    conn.commit()
    cursor.close()
    conn.close()


def get_current_team_id(player_id: int) -> int:
    """Retrieve the current team ID of a player from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT current_team_id FROM nba_players WHERE id = %s", (player_id,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return result[0] if result else None

def update_prev_team_id(player_id: int, prev_team_id: int):
    """Updates a player's prev_team_id in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    update_query = sql.SQL("""
        UPDATE nba_players 
        SET prev_team_id = %s
        WHERE id = %s
    """)
    
    cursor.execute(update_query, (prev_team_id, player_id))
    conn.commit()
    cursor.close()
    conn.close()

def check_first_revenge_game(player_id: int, team_id: int) -> bool:
    """Checks if a player's first revenge game against a team is recorded."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT 1 FROM nba_first_revenge_games WHERE player_id = %s AND team_id = %s LIMIT 1"
    cursor.execute(query, (player_id, team_id))
    exists = cursor.fetchone()

    cursor.close()
    conn.close()

    return not exists  # (first-time revenge game)

def insert_first_revenge_game(player_id: int, team_id: int):
    """Inserts a first-time revenge game record."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO nba_first_revenge_games (player_id, team_id) VALUES (%s, %s)"
    cursor.execute(query, (player_id, team_id))

    conn.commit()
    cursor.close()
    conn.close()