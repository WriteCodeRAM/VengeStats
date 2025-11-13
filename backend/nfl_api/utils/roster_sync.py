from nfl_api.utils.player_data import get_team_roster, extract_target_players, find_nfl_data_py_player_id, process_single_player
from db.queries.nfl.teams import get_current_db_roster, move_player_to_free_agency

def sync_team_roster(team_id):
    """
    Sync database roster with ESPN API roster - only moves truly released players
    """
    print(f"SYNCING ROSTER: Team {team_id}")
    
    db_roster = get_current_db_roster(team_id)
    db_player_ids = set(db_roster.keys())
    
    roster_data, team_info = get_team_roster(team_id)
    if not roster_data:
        print(f"Could not fetch API roster for team {team_id}")
        return False
    
    api_players = extract_target_players(roster_data, team_info)
    api_player_ids = set()
    
    for player_data in api_players:
        nfl_data_player_id = find_nfl_data_py_player_id(
            player_data['display_name'], 
            player_data['position']
        )
        
        if nfl_data_player_id:
            api_player_ids.add(nfl_data_player_id)
            process_single_player(player_data)
    
    players_to_move = db_player_ids - api_player_ids
    
    if players_to_move:
        print(f"Moving {len(players_to_move)} players to free agency (team 35)")
        print("REVIEW THESE MOVES - Could be IR/suspended instead of cut:")
        print("-" * 50)
        for nfl_data_player_id in players_to_move:
            move_player_to_free_agency(nfl_data_player_id, team_id)
        print("-" * 50)
    else:
        print("No players moved to free agency")
    
    print(f"Roster sync complete for team {team_id}")
    return True

sync_team_roster("34")