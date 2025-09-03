from db.database import get_connection 

def insert_nfl_player(nfl_data_player_id, first_name, last_name, display_name, 
                     current_team_id, position, years_exp=0, usage_tier='INACTIVE', 
                     draft_round=None, draft_number=None, draft_team=None, 
                     pro_bowl_selections=0, all_pro_selections=0, is_active=True):
    """
    Insert or update NFL player with all venge scoring fields
    Returns the player's DB ID
    """
    with get_connection() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(
                """
                INSERT INTO nfl_players (
                    nfl_data_py_player_id, first_name, last_name, display_name, 
                    current_team_id, position, years_exp, usage_tier,
                    draft_round, draft_number, draft_team, pro_bowl_selections, 
                    all_pro_selections, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (nfl_data_py_player_id) 
                DO UPDATE SET 
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    display_name = EXCLUDED.display_name,
                    current_team_id = EXCLUDED.current_team_id,
                    position = EXCLUDED.position,
                    years_exp = EXCLUDED.years_exp,
                    usage_tier = EXCLUDED.usage_tier,
                    draft_round = EXCLUDED.draft_round,
                    draft_number = EXCLUDED.draft_number,
                    draft_team = EXCLUDED.draft_team,
                    pro_bowl_selections = EXCLUDED.pro_bowl_selections,
                    all_pro_selections = EXCLUDED.all_pro_selections,
                    is_active = EXCLUDED.is_active,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (nfl_data_player_id, first_name, last_name, display_name, current_team_id, 
                 position, years_exp, usage_tier, draft_round, draft_number, draft_team, 
                 pro_bowl_selections, all_pro_selections, is_active)
            )
            player_db_id = cursor.fetchone()[0]
            return player_db_id

def insert_nfl_player_stint(player_id, team_id, season_start, season_end, 
                           games_played, is_current_stint=False):
    """
    Insert or update player stint (unchanged from before)
    """
    with get_connection() as conn:
        with conn.cursor() as cursor: 
            cursor.execute(
                """
                INSERT INTO nfl_player_stints (player_id, team_id, season_start, season_end, games_played, is_current_stint)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, team_id, season_start) 
                DO UPDATE SET 
                    season_end = EXCLUDED.season_end,
                    games_played = EXCLUDED.games_played,
                    is_current_stint = EXCLUDED.is_current_stint,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (player_id, team_id, season_start, season_end, games_played, is_current_stint)
            )

def get_nfl_player_db_id(nfl_data_player_id):
    """
    Get the DB ID for a player using their nfl-data-py ID
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM nfl_players 
                WHERE nfl_data_py_player_id = %s
                """,
                (nfl_data_player_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

def get_existing_player_info(nfl_data_player_id):
    """
    Get existing player info to check if processing needed
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, current_team_id, usage_tier, is_active, updated_at
                FROM nfl_players 
                WHERE nfl_data_py_player_id = %s
                """,
                (nfl_data_player_id,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'current_team_id': result[1], 
                    'usage_tier': result[2],
                    'is_active': result[3],
                    'updated_at': result[4]
                }
            return None