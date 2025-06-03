from backend.db.database import get_connection
from psycopg2 import sql

teams = {
    "ATL": 1, "BOS": 2,  
    "NJN": 3, "BRK": 3, "BKN": 3,  # NEW JERSEY NETS NAHHHHHH BROOK LOPEZ 
    "CHO": 4, "CHA": 4,  
    "CHI": 5, "CLE": 6, "DAL": 7, "DEN": 8, "DET": 9,  
    "GSW": 10, "GS": 10,  
    "HOU": 11, "IND": 12, "LAC": 13, "LAL": 14,  
    "MEM": 15, "MIA": 16, "MIL": 17, "MIN": 18,  
    "NOP": 19, "NOH": 19, "NOK": 19, "NO": 19,  # NEW ORLEANS HORNETS / NOK (CP3)
    "NYK": 20, "NY": 20,  
    "OKC": 21, "SEA": 21,  # SEATTLE SUPERSONICS NAHHHH JEFF GREEN JUST BROKE MY SCRIPT  
    "ORL": 22, "PHI": 23, "PHO": 24, "PHX": 24,  
    "POR": 25, "SAC": 26, "SAS": 27, "SA": 27,  
    "TOR": 28, "UTA": 29, "UTAH": 29,  
    "WAS": 30, "WSH": 30,  
}

def get_current_nba_roster(team_id: int):
    """Returns a set of players currently on an NBA team's roster from the database."""
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            
            query = sql.SQL("SELECT first_name, last_name FROM nba_players WHERE current_team_id = %s")
            cursor.execute(query, (team_id,)) 
            res = cursor.fetchall() 
            
            # convert to a set of full names for easy comparison
            current_roster = {(row[0], row[1]) for row in res}  # ("LeBron", "James")
            return current_roster


def get_current_team_id(player_id: int) -> int:
    """Retrieve the current team ID of a player from the database."""
    with get_connection() as conn: 
        with conn.cursor() as cursor:
    
            cursor.execute("SELECT current_team_id FROM nba_players WHERE id = %s", (player_id,))
            result = cursor.fetchone()
            
            return result[0] if result else None
        
def get_prev_team_id(player_id: int) -> int:
    """Retrieve the previous team ID of a player from the database."""
    with get_connection() as conn: 
        with conn.cursor() as cursor:
    
            cursor.execute("SELECT prev_team_id FROM nba_players WHERE id = %s", (player_id,))
            result = cursor.fetchone()
            
            return result[0] if result else None

def update_prev_team_id(player_id: int, prev_team_id: int):
    """Updates a player's prev_team_id in the database."""
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            
            update_query = sql.SQL("""
                UPDATE nba_players 
                SET prev_team_id = %s
                WHERE id = %s
            """)
            
            cursor.execute(update_query, (prev_team_id, player_id))
            conn.commit()