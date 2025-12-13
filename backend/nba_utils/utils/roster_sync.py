from typing import Set, Tuple, List, Optional
import time
from db.queries.nba.teams import team_id_to_nba_api_id
from db.queries.nba.players import (
    find_player_by_name_globally, 
    move_player_to_team, 
    move_player_to_free_agency,
    insert_new_player,
    get_player_prev_team
)
from db.database import get_connection
from psycopg2 import sql

def mark_player_needs_stint_refresh(player_id: int):
    """Mark that this player's stints need to be resynced"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE nba_players 
                SET needs_stint_refresh = TRUE
                WHERE id = %s
            """, (player_id,))
            conn.commit()

def get_team_roster_from_api(team_id, season='2025-26'):
    """Get current roster using NBA API with automatic season detection"""
    from nba_api.stats.endpoints import CommonTeamRoster
    
    try:
        print(f"Fetching roster for NBA team {team_id} (season: {season})...")
        roster = CommonTeamRoster(team_id=team_id, season=season)
        df = roster.get_data_frames()[0]
        
        players = []
        for _, player in df.iterrows():
            players.append({
                'player_id': player['PLAYER_ID'],
                'first_name': player['PLAYER'].split()[0],
                'last_name': ' '.join(player['PLAYER'].split()[1:]),
                'full_name': player['PLAYER']
            })
        
        print(f"Found {len(players)} players")
        return players
        
    except Exception as e:
        print(f"Error fetching roster: {e}")
        return []

def get_db_roster_set(team_id: int) -> Set[Tuple[int, str, str]]:
    """Get current roster from database as a set for efficient lookups"""
    print(f"Getting DB roster for team {team_id}...")
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT id, first_name, last_name FROM nba_players WHERE current_team_id = %s")
            cursor.execute(query, (team_id,))
            roster_data = cursor.fetchall()
    
    roster_set = set()
    for player in roster_data:
        player_id, first_name, last_name = player[0], player[1], player[2]
        roster_set.add((player_id, first_name.strip(), last_name.strip()))
    
    print(f"Found {len(roster_set)} players in DB roster")
    return roster_set

def find_player_in_set(first_name: str, last_name: str, roster_set: Set[Tuple[int, str, str]]) -> Optional[Tuple[int, str, str]]:
    """Find player in roster set by name with collision detection"""
    first_clean = first_name.strip()
    last_clean = last_name.strip()
    
    matches = []
    for player_tuple in roster_set:
        _, db_first, db_last = player_tuple
        if db_first == first_clean and db_last == last_clean:
            matches.append(player_tuple)
    
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"    WARNING: Multiple players named {first_clean} {last_clean} found!")
        return matches[0]  # return first match as fallback
    

    for player_tuple in roster_set:
        _, db_first, db_last = player_tuple
        if last_clean == db_last and (first_clean in db_first or db_first in first_clean):
            print(f"    Partial match: {first_clean} {last_clean} -> {db_first} {db_last}")
            return player_tuple
    
    return None

def process_api_player(api_player: dict, roster_set: Set[Tuple[int, str, str]], team_id: int) -> bool:
    """Process a single API player"""
    first_name = api_player['first_name']
    last_name = api_player['last_name']
    full_name = api_player['full_name']
    
    print(f"    Processing: {full_name}")
    

    found_player = find_player_in_set(first_name, last_name, roster_set)
    
    if found_player:
        print(f"    Confirmed on roster: {full_name}")
        roster_set.remove(found_player) 
        return True
    else:
        print(f"    Not in DB roster - checking if moved teams: {full_name}")
        handle_new_or_moved_player(api_player, team_id)
        return False

def handle_new_or_moved_player(api_player: dict, new_team_id: int):
    """Handle player not found in current roster - either moved teams or completely new"""
    first_name = api_player['first_name']
    last_name = api_player['last_name']
    full_name = api_player['full_name']
    nba_api_player_id = api_player['player_id']
    
    # search entire db for this player
    player_data = find_player_by_name_globally(first_name, last_name)
    
    if player_data:
        player_id, old_team_id = player_data
        
        # If they're currently on team 31 (free agency), preserve their actual prev_team_id
        if old_team_id == 31:
            actual_prev_team = get_player_prev_team(player_id)
            print(f"    Player moved: {full_name} from Free Agency -> {new_team_id} (actual prev: {actual_prev_team})")
            move_player_to_team(player_id, new_team_id)

        else:
            print(f"    Player moved: {full_name} from team {old_team_id} -> {new_team_id}")
            move_player_to_team(player_id, new_team_id)

        mark_player_needs_stint_refresh(player_id)
        print(f"    Marked for stint refresh: {full_name}")
    else:
        print(f"    New player detected: {full_name} - adding to database")
        new_player_id = insert_new_player(first_name, last_name, new_team_id, nba_api_player_id)
        print(f"    Added {full_name} with ID {new_player_id}")
        mark_player_needs_stint_refresh(new_player_id)
        print(f"    Marked for stint refresh: {full_name}")

def handle_remaining_players(remaining_set: Set[Tuple[int, str, str]], team_id: int):
    """Handle players who moved off team - send them to free agency (team 31)"""
    if not remaining_set:
        print("No players moved off the team")
        return
    
    print(f"{len(remaining_set)} players moved off team {team_id} -> Free Agency:")
    
    for player_id, first_name, last_name in remaining_set:
        print(f"    {first_name} {last_name} -> Team 31 (Free Agency)")
        move_player_to_free_agency(player_id, team_id)

def sync_team_roster(team_id: int) -> dict:
    """Main function: Sync database roster with NBA API for a single team"""
    print(f"\nSYNCING ROSTER FOR TEAM {team_id}")
    print("=" * 50)
    

    db_roster_set = get_db_roster_set(team_id)
    original_count = len(db_roster_set)
    

    nba_api_team_id = team_id_to_nba_api_id.get(team_id)
    if not nba_api_team_id:
        print(f"No NBA API team ID for {team_id}")
        return {"success": False}
    
    api_roster = get_team_roster_from_api(nba_api_team_id)
    
    if not api_roster:
        print("Could not get API roster")
        return {"success": False}
    
    print(f"\nPROCESSING {len(api_roster)} API PLAYERS:")
    print("-" * 30)
    

    confirmed_players = 0
    new_players = 0
    
    for api_player in api_roster:
        if process_api_player(api_player, db_roster_set, team_id):
            confirmed_players += 1
        else:
            new_players += 1
    

    moved_players = len(db_roster_set)
    handle_remaining_players(db_roster_set, team_id)
    

    print(f"\nROSTER SYNC SUMMARY:")
    print(f"   Original DB roster: {original_count} players")
    print(f"   Current API roster: {len(api_roster)} players")
    print(f"   Confirmed players: {confirmed_players}")
    print(f"   New/moved players: {new_players}")
    print(f"   Players moved off: {moved_players}")
    
    return {
        "success": True,
        "original_count": original_count,
        "api_count": len(api_roster),
        "confirmed": confirmed_players,
        "new_players": new_players,
        "moved_off": moved_players
    }

def sync_all_teams():
    """Sync rosters for all teams"""
    from db.queries.nba.teams import teams
    
    results = []
    for team_abbr, team_id in teams.items():
        try:
            result = sync_team_roster(team_id)
            results.append({**result, "team": team_abbr})
            if result["success"]:
                print(f"Team {team_abbr} sync completed")
            else:
                print(f"Team {team_abbr} sync failed")
        except Exception as e:
            print(f"Error syncing {team_abbr}: {e}")
            results.append({"success": False, "team": team_abbr, "error": str(e)})
        
        time.sleep(10)  # rate limit
    
    return results

if __name__ == "__main__":
    sync_team_roster(13)