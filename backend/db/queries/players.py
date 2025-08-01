from backend.db.database import get_connection
import datetime
from backend.db.queries.teams import team_id_to_abbr, team_id_to_full_name
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

# returns a list of teams a player has played for 
# [team id , start year, end year, games played] 
def get_player_career_history(player_id: int):
    with get_connection() as conn: 
        with conn.cursor() as cursor: 
            query = sql.SQL("SELECT team_id, first_game_date, last_game_date, games_played FROM nba_player_team_stints_api WHERE player_id = %s") 
            cursor.execute(query, (player_id,))
            results = cursor.fetchall() 

            if not results:
                return []

            # Sort by start date (index 1)
            sorted_results = sorted(results, key=lambda x: x[1])
            
            # Merge consecutive intervals for the same team
            merged = []
            
            for team_id, start_date, end_date, games in sorted_results:
                # If this is the same team as the last entry, merge them
                if merged and merged[-1][0] == team_id:
                    # Update the end date to the later one and sum games
                    prev_team_id, prev_start, prev_end, prev_games = merged[-1]
                    new_end = end_date if end_date else prev_end
                    if prev_end and end_date:
                        new_end = max(prev_end, end_date)
                    elif end_date:
                        new_end = end_date
                    else:
                        new_end = prev_end
                    
                    merged[-1] = (team_id, prev_start, new_end, prev_games + games)
                else:
                    # Add new entry
                    merged.append((team_id, start_date, end_date, games))
            
            formatted_career = [] 

            for team_id, start, end, gp in merged: 
                start_year = start.year
                end_year = end.year if end else None  # None for current team
                
                formatted_career.append({
                    'team_abbr': team_id_to_abbr[team_id],
                    'team_full_name': team_id_to_full_name[team_id], 
                    'start_year': start_year,
                    'end_year': end_year,
                    'games_played': gp,
                    'is_current': end is None
                })

            return formatted_career

# Test it
career = get_player_career_history(234)
print(career)

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


# sort based on index 1 (start date)
# merge intervals type thing where we use the later end date if the next idx is the same team as well (for instances like KD (SEA -> OKC)) 