from backend.db.database import get_connection

NFL_TEAM_ID_TO_ABBR = {
    1: 'ATL', 2: 'BUF', 3: 'CHI', 4: 'CIN', 5: 'CLE', 6: 'DAL', 7: 'DEN', 
    8: 'DET', 9: 'GB', 10: 'TEN', 11: 'IND', 12: 'KC', 13: 'LV', 14: 'LAR', 
    15: 'MIA', 16: 'MIN', 17: 'NE', 18: 'NO', 19: 'NYG', 20: 'NYJ', 21: 'PHI', 
    22: 'ARI', 23: 'PIT', 24: 'LAC', 25: 'SF', 26: 'SEA', 27: 'TB', 28: 'WAS', 
    29: 'CAR', 30: 'JAX', 33: 'BAL', 34: 'HOU'
}

NFL_TEAM_ABBR_TO_ID = {
    'ATL': 1, 'BUF': 2, 'CHI': 3, 'CIN': 4, 'CLE': 5, 'DAL': 6, 'DEN': 7,
    'DET': 8, 'GB': 9, 'TEN': 10, 'IND': 11, 'KC': 12, 'LV': 13, 'LAR': 14,
    'MIA': 15, 'MIN': 16, 'NE': 17, 'NO': 18, 'NYG': 19, 'NYJ': 20, 'PHI': 21,
    'ARI': 22, 'PIT': 23, 'LAC': 24, 'SF': 25, 'SEA': 26, 'TB': 27, 'WAS': 28,
    'CAR': 29, 'JAX': 30, 'BAL': 33, 'HOU': 34
}

def get_current_db_roster(team_id):
    """
    Get current database roster for a team
    Returns dict of {nfl_data_py_player_id: db_player_id}
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT nfl_data_py_player_id, id 
                FROM nfl_players 
                WHERE current_team_id = %s 
                AND is_active = true
                AND position IN ('QB', 'RB', 'WR', 'TE')
                """,
                (team_id,)
            )
            return {row[0]: row[1] for row in cursor.fetchall()}

def move_player_to_free_agency(nfl_data_player_id, from_team_id):
    """
    Move player to free agency team (35) and mark as inactive
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Get player name before moving
            cursor.execute(
                """
                SELECT display_name, position, usage_tier
                FROM nfl_players 
                WHERE nfl_data_py_player_id = %s
                """,
                (nfl_data_player_id,)
            )
            player_info = cursor.fetchone()
            
            if player_info:
                player_name, position, usage_tier = player_info
                print(f"  MOVED TO FREE AGENCY: {player_name} ({position}) - Usage: {usage_tier}")
            else:
                print(f"  MOVED TO FREE AGENCY: Player ID {nfl_data_player_id} (unknown name)")
            
            cursor.execute(
                """
                UPDATE nfl_players 
                SET current_team_id = 35,
                    is_active = false,
                    updated_at = CURRENT_TIMESTAMP
                WHERE nfl_data_py_player_id = %s
                """,
                (nfl_data_player_id,)
            )
            
            cursor.execute(
                """
                UPDATE nfl_player_stints 
                SET is_current_stint = false,
                    updated_at = CURRENT_TIMESTAMP
                WHERE player_id = (
                    SELECT id FROM nfl_players 
                    WHERE nfl_data_py_player_id = %s
                ) 
                AND team_id = %s 
                AND is_current_stint = true
                """,
                (nfl_data_player_id, from_team_id)
            )
        conn.commit()