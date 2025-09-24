from db.database import get_connection
from typing import List, Tuple
from schemas.revenge_types import NFLRevengePlayer, NBARevengePlayer
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR 

NBA_REVENGE_GAME_QUERY = """
SELECT DISTINCT 
    p.id AS player_id, 
    p.first_name, 
    p.last_name, 
    curr_team.name AS current_team_name,  
    former_team.name AS former_team_name,
    former_team.id AS opponent_team_id,
    pts.last_game_date AS most_recent_departure,
    pts.departure_method
FROM nba_players p
JOIN teams curr_team ON p.current_team_id = curr_team.id
JOIN (
    SELECT DISTINCT ON (player_id, team_id)
        player_id,
        team_id,
        last_game_date,
        departure_method
    FROM nba_player_team_stints_api
    ORDER BY player_id, team_id, last_game_date DESC
) pts ON p.id = pts.player_id AND pts.team_id != p.current_team_id
JOIN teams former_team ON pts.team_id = former_team.id
WHERE 
    (p.current_team_id = %s AND pts.team_id = %s)
    OR 
    (p.current_team_id = %s AND pts.team_id = %s);
"""

NFL_REVENGE_GAME_QUERY =NFL_REVENGE_GAME_QUERY = """
WITH recent_stints AS (
    SELECT 
        pts.*,
        ROW_NUMBER() OVER (PARTITION BY pts.player_id, pts.team_id ORDER BY pts.season_end DESC) as rn
    FROM nfl_player_stints pts
)
SELECT DISTINCT 
    p.id AS player_id, 
    p.nfl_data_py_player_id as nfl_id,
    p.first_name, 
    p.last_name, 
    p.display_name,
    p.current_team_id,
    p.position,
    p.usage_tier,
    p.years_exp,
    p.draft_team,
    p.pro_bowl_selections,
    p.all_pro_selections,
    former_team.team_name AS former_team_name,
    former_team.team_abbreviation AS former_team_abbr,
    former_team.id AS opponent_team_id,
    curr_team.team_name AS current_team_name,
    curr_team.team_abbreviation AS current_team_abbr,
    MAX(pts.season_start) AS season_start,
    MAX(pts.season_end) AS most_recent_departure_season,
    SUM(pts.games_played) AS total_games_played_for_team,
    MAX(CASE WHEN pts.rn = 1 THEN pts.departure_method END) AS departure_method
FROM nfl_players p
JOIN recent_stints pts ON p.id = pts.player_id
JOIN nfl_teams former_team ON pts.team_id = former_team.id
JOIN nfl_teams curr_team ON p.current_team_id = curr_team.id
WHERE 
    p.is_active = true
    AND p.position IN ('QB', 'RB', 'TE', 'WR')
    AND pts.team_id != p.current_team_id  -- Player must have played for a different team
    AND (
        (p.current_team_id = %s AND pts.team_id = %s)
        OR 
        (p.current_team_id = %s AND pts.team_id = %s)
    )
GROUP BY p.id, p.nfl_data_py_player_id, p.first_name, p.last_name, p.display_name, p.current_team_id, 
         p.position, p.usage_tier, p.years_exp, p.draft_team, p.pro_bowl_selections,
         p.all_pro_selections, former_team.team_name, former_team.team_abbreviation, former_team.id,
         curr_team.team_name, curr_team.team_abbreviation;
"""

def get_nfl_player_stint_history(player_id: int) -> List[List[int]]:
    """
    Fetches all stints for a given player from nfl_player_stints table.
    
    Args:
        player_id: The ID of the player to fetch stints for
        
    Returns:
        List of stints in format [[team_id, season_start, season_end], ...]
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT team_id, season_start, season_end
                FROM nfl_player_stints 
                WHERE player_id = %s
                ORDER BY season_start ASC, season_end ASC
            """
            cursor.execute(query, (player_id,))
            stints = cursor.fetchall()
            


            stints = [list(stint) for stint in stints]
            for stint in stints:
                stint[0] = NFL_TEAM_ID_TO_ABBR[int(stint[0])]
            return stints


def get_nfl_revenge_games(schedule: List[List[int]]) -> List[NFLRevengePlayer]:
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            revenge_games = []
            for matchup in schedule:
                away_team, home_team = matchup[0], matchup[1]
                cursor.execute(NFL_REVENGE_GAME_QUERY, (away_team, home_team, home_team, away_team))
                players = cursor.fetchall()  

                for player in players:
                    # Calculate revenge record starting from departure year
                    former_team_abbr = player[13]  # former_team_abbr from query
                    departure_year = player[18]    # departure_year
                    nfl_data_id = player[1]       # nfl_data_id
                    team_history = get_nfl_player_stint_history(player[0])
                    revenge_games.append({
                        'player_id': player[0],
                        'name': f"{player[2]} {player[3]}",
                        'nfl_data_id': nfl_data_id,
                        'display_name': player[4],
                        'current_team_id': player[5],
                        'position': player[6],
                        'usage_tier': player[7],
                        'years_exp': player[8],
                        'draft_team': player[9],
                        'pro_bowl_selections': player[10],
                        'all_pro_selections': player[11],
                        'former_team_name': player[12],
                        'former_team_abbr': former_team_abbr,
                        'opponent_team_id': player[14],
                        'current_team_name': player[15],
                        'current_team_abbr': player[16],
                        'season_start': player[17],
                        'departure_year': departure_year,
                        'departure_method': player[20],
                        'total_games_played_for_team': player[19],
                        'injury_status': 'Healthy',
                        'history': team_history,
                        'league': 'NFL'
                    })
                    
            return revenge_games

def get_nba_revenge_games(schedule: List[Tuple[int, int]]) -> List[NBARevengePlayer]:
    with get_connection() as conn: 
        with conn.cursor() as cursor:
            revenge_games = []
            for away_team, home_team in schedule:  
                cursor.execute(NBA_REVENGE_GAME_QUERY, (away_team, home_team, home_team, away_team))
                players = cursor.fetchall()  
                for player in players:
                    revenge_games.append([
                        f"{player[1]} {player[2]}",  # Full name
                        player[4],                   # Former team name
                        None,                        # Injury status
                        player[0],                   # Player ID
                        player[5],                   # Opponent team ID
                        None,                        # revenge_score placeholder
                        player[6],                   # departure date (most recent stint)
                        player[7]                    # departure method
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