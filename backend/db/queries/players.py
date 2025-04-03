from backend.db.database import get_connection
import psycopg2
from psycopg2 import sql

# put all the player realted queries here 

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
