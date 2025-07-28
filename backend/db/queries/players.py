from backend.db.database import get_connection
from psycopg2 import sql

def get_player_id(first_name: str, last_name: str, current_team_id: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:

            query = sql.SQL("SELECT id FROM nba_players WHERE first_name = %s AND last_name = %s")
            cursor.execute(query, (first_name, last_name))
            result = cursor.fetchone()

            if result:
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
            return new_player_id

def get_total_games_played(player_id: int) -> int:
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT games_played FROM nba_player_team_history WHERE player_id = %s")
            cursor.execute(query, (player_id,))
            results = cursor.fetchall() 

            total_games = sum(row[0] for row in results)
            return total_games
        
def get_total_games_played_for_team(player_id: int, team_id: int) -> int:
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT games_played FROM nba_player_team_stints_api WHERE player_id = %s and team_id = %s")
            cursor.execute(query, (player_id, team_id))
            results = cursor.fetchall() 

            total_games = sum(row[0] for row in results)
            return total_games

# using bballref scrapes 
def insert_player_team_stint(player_id, team_id, start_date, end_date, games_played):
    with get_connection() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(
                """
                INSERT INTO nba_player_team_stints (player_id, team_id, first_game_date, last_game_date, games_played)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (player_id, team_id, first_game_date, last_game_date) DO NOTHING
                """,
                (player_id, team_id, start_date, end_date, games_played)  # end_date can be None
            )
        conn.commit()

# using the nba api
def insert_api_player_stint(player_id, team_id, start_date, end_date, games_played, nba_api_player_id):
    """
    Insert or update player stint - will overwrite existing data on reruns
    """
    with get_connection() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(
                """
                INSERT INTO nba_player_team_stints_api (player_id, team_id, first_game_date, last_game_date, games_played, nba_api_player_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, team_id, first_game_date, last_game_date) 
                DO UPDATE SET 
                    last_game_date = EXCLUDED.last_game_date,
                    games_played = EXCLUDED.games_played,
                    nba_api_player_id = EXCLUDED.nba_api_player_id,
                    created_at = CURRENT_TIMESTAMP
                """,
                (player_id, team_id, start_date, end_date, games_played, nba_api_player_id)
            )
        conn.commit()

def move_player_to_team(player_id: int, new_team_id: int):
    with get_connection() as conn: 
        with conn.cursor() as cursor:

            query = sql.SQL("""
                SELECT current_team_id, prev_team_id FROM nba_players 
                WHERE id = %s
            """)
            cursor.execute(query, (player_id,))
            result = cursor.fetchone()

            if not result:
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