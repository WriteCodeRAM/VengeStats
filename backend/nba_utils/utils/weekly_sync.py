from nba_utils.utils.roster_sync import sync_all_teams
from nba_utils.utils.smart_stint_sync import sync_stints_for_changed_players
import time

def run_db_sync():
    """Run full db sync process"""
    
    print("🏀 STARTING DB NBA SYNC")
    print("=" * 50)
    
    # Step 1: Sync rosters (this flags players needing stint updates)
    print("\n📋 STEP 1: Syncing team rosters...")
    roster_results = sync_all_teams()
    
    print("\n⏳ Waiting 30 seconds before stint sync...")
    time.sleep(30)
    
    # Step 2: Sync stints only for flagged players
    print("\n📊 STEP 2: Syncing player stints...")
    stint_results = sync_stints_for_changed_players()
    
    print("\n" + "=" * 50)
    print("🎉 DB SYNC COMPLETE!")
    
    return {
        "roster_sync": roster_results,
        "stint_sync": stint_results
    }