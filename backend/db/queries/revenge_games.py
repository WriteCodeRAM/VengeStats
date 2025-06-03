from backend.db.database import get_connection
from backend.types_def import NBARevengeGame
from typing import List, Tuple

REVENGE_GAME_QUERY = """
SELECT DISTINCT 
    p.id AS player_id, 
    p.first_name, 
    p.last_name, 
    curr_team.name AS current_team_name,  
    former_team.name AS former_team_name,
    former_team.id AS opponent_team_id
FROM nba_players p
JOIN nba_player_team_history pth ON p.id = pth.player_id
JOIN teams curr_team ON p.current_team_id = curr_team.id
JOIN teams former_team ON pth.team_id = former_team.id
WHERE 
    (p.current_team_id = %s AND pth.team_id = %s)
    OR 
    (p.current_team_id = %s AND pth.team_id = %s);
"""

def get_revenge_games(schedule: List[Tuple[int, int]]) -> List[NBARevengeGame]:
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            revenge_games = []
            for away_team, home_team in schedule:  
                cursor.execute(REVENGE_GAME_QUERY, (away_team, home_team, home_team, away_team))
                players = cursor.fetchall()  
                for player in players:
                    revenge_games.append([
                        f"{player[1]} {player[2]}",  # Full name
                        player[4],                   # Former team name
                        None,                        # Injury status
                        player[0],                   # Player ID
                        player[5],                    # Opponent team ID
                        None
                    ])
            return revenge_games



def check_first_revenge_game(player_id: int, team_id: int) -> bool:
    """Checks if a player's first revenge game against a team is recorded."""
    with get_connection() as conn: 
        with conn.cursor() as cursor:

            query = "SELECT 1 FROM nba_first_revenge_games WHERE player_id = %s AND team_id = %s LIMIT 1"
            cursor.execute(query, (player_id, team_id))
            exists = cursor.fetchone()
            return not exists  # (first-time revenge game)

def insert_first_revenge_game(player_id: int, team_id: int):
    """Inserts a first-time revenge game record."""
    with get_connection() as conn: 
        with conn.cursor() as cursor:

            query = "INSERT INTO nba_first_revenge_games (player_id, team_id) VALUES (%s, %s)"
            cursor.execute(query, (player_id, team_id))
            conn.commit()