from backend.db.database import get_connection
import psycopg2
from psycopg2 import sql

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