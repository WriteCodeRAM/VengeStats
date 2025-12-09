from typing import List, Tuple
import time
from db.database import get_connection
from db.queries.nba.teams import teams, team_id_to_abbr
from db.queries.nba.players import insert_api_player_stint
from nba_utils.utils.player_utils import get_player_stints_from_nba_api

def get_players_needing_stint_sync() -> List[Tuple]:
    """Get all players marked as needing stint refresh"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.first_name, p.last_name, p.nba_api_player_id, p.current_team_id
                FROM nba_players p
                WHERE p.needs_stint_refresh = TRUE
                ORDER BY p.current_team_id  -- Group by team for efficiency
            """)
            return cursor.fetchall()

def sync_stints_for_changed_players():
    """Only sync stints for players marked as needing refresh"""
    players_to_sync = get_players_needing_stint_sync()
    if not players_to_sync:
        print("✅ No players need stint sync!")
        return {"success": True, "players_synced": 0}
    
    print(f"Found {len(players_to_sync)} players needing stint sync")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for idx, (player_id, first, last, api_id, team_id) in enumerate(players_to_sync, 1):

        # Skip free agents
        if team_id == 31:
            print(f"\n⏭️  Skipping {first} {last} (Free Agency)")
            # Still mark as synced so we don't keep trying
            mark_player_synced(player_id)
            continue
            
        team_abbr = team_id_to_abbr.get(team_id, "")
        print(f"\n[{idx}/{len(players_to_sync)}] Syncing: {first} {last} ({team_abbr})")

        
        try:
            # Get stints from API
            stints = get_player_stints_from_nba_api(api_id, f"{first} {last}", team_abbr)
            
            if not stints:
                print("  ⚠️  No stints found")
                mark_player_synced(player_id)
                continue
            
            # Insert each stint
            stint_count = 0
            for stint in stints:
                stint_team_id = teams.get(stint['team'])
                if stint_team_id:
                    insert_api_player_stint(
                        player_id,
                        stint_team_id, 
                        stint['start_date'],
                        stint['end_date'],
                        stint['games_played'],
                        api_id
                    )
                    stint_count += 1
            
            # Mark as synced
            mark_player_synced(player_id)
            
            print(f"  ✅ Synced {stint_count} stints")
            success_count += 1


   
            if idx < len(players_to_sync):  # Don't sleep after last player
                if idx % 18 == 0:
                    print(f"  💤 Taking 5-min break after {idx} players...")
                    time.sleep(300)
            else:
                time.sleep(10)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_count += 1
            continue
    
    print("\n" + "=" * 50)
    print(f"STINT SYNC COMPLETE!")
    print(f"✅ Success: {success_count} players")
    print(f"❌ Errors: {error_count} players")
    
    return {
        "success": True,
        "players_synced": success_count,
        "errors": error_count
    }

def mark_player_synced(player_id: int):
    """Mark player as synced"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE nba_players 
                SET needs_stint_refresh = FALSE,
                    stints_last_synced = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (player_id,))
            conn.commit()

if __name__ == "__main__":
    sync_stints_for_changed_players()