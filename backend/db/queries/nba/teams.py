from db.database import get_connection
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

team_id_to_abbr = {
    1: "ATL", 2: "BOS", 3: "BKN", 4: "CHA", 5: "CHI", 6: "CLE", 
    7: "DAL", 8: "DEN", 9: "DET", 10: "GSW", 11: "HOU", 12: "IND",
    13: "LAC", 14: "LAL", 15: "MEM", 16: "MIA", 17: "MIL", 18: "MIN",
    19: "NOP", 20: "NYK", 21: "OKC", 22: "ORL", 23: "PHI", 24: "PHX",
    25: "POR", 26: "SAC", 27: "SAS", 28: "TOR", 29: "UTA", 30: "WAS"
}

team_id_to_full_name = {
    1: "Atlanta Hawks", 2: "Boston Celtics", 3: "Brooklyn Nets", 4: "Charlotte Hornets", 5: "Chicago Bulls",
    6: "Cleveland Cavaliers", 7: "Dallas Mavericks", 8: "Denver Nuggets", 9: "Detroit Pistons", 10: "Golden State Warriors", 
    11: "Houston Rockets", 12: "Indiana Pacers", 13: "LA Clippers", 14: "Los Angeles Lakers", 15: "Memphis Grizzlies",
    16: "Miami Heat", 17: "Milwaukee Bucks", 18: "Minnesota Timberwolves", 19: "New Orleans Pelicans", 20: "New York Knicks",
    21: "Oklahoma City Thunder", 22: "Orlando Magic", 23: "Philadelphia 76ers", 24: "Phoenix Suns", 25: "Portland Trail Blazers",
    26: "Sacramento Kings", 27: "San Antonio Spurs", 28: "Toronto Raptors",  29: "Utah Jazz", 30: "Washington Wizards"
}

# team mapping (1-30) to NBA API IDs
team_id_to_nba_api_id = {
    1: 1610612737,   # ATL
    2: 1610612738,   # BOS
    3: 1610612751,   # BRK/BKN
    4: 1610612766,   # CHA
    5: 1610612741,   # CHI
    6: 1610612739,   # CLE
    7: 1610612742,   # DAL
    8: 1610612743,   # DEN
    9: 1610612765,   # DET
    10: 1610612744,  # GSW
    11: 1610612745,  # HOU
    12: 1610612754,  # IND
    13: 1610612746,  # LAC
    14: 1610612747,  # LAL
    15: 1610612763,  # MEM
    16: 1610612748,  # MIA
    17: 1610612749,  # MIL
    18: 1610612750,  # MIN
    19: 1610612740,  # NOP
    20: 1610612752,  # NYK
    21: 1610612760,  # OKC
    22: 1610612753,  # ORL
    23: 1610612755,  # PHI
    24: 1610612756,  # PHX
    25: 1610612757,  # POR
    26: 1610612758,  # SAC
    27: 1610612759,  # SAS
    28: 1610612761,  # TOR
    29: 1610612762,  # UTA
    30: 1610612764,  # WAS
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