from nba_api.stats.endpoints import CommonTeamRoster
import time
from backend.db.queries.nba.teams import team_id_to_nba_api_id, teams
from backend.db.queries.nba.players import get_player_id, insert_api_player_stint
from backend.nba_api.utils.player_utils import get_player_stints_from_nba_api

error_log = []

def log_player_error(player_name, team_abbr, error_message):
    error_entry = f"{player_name} ({team_abbr}): {str(error_message)}"
    error_log.append(error_entry)
    print(f"🚨 LOGGED ERROR: {error_entry}")

def get_team_roster_from_api(team_id, season="2025-26"):
    """
    Get current roster using NBA API
    """
    try:
        print(f"  📋 Fetching roster for NBA team {team_id}...")
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
        
        print(f"  ✅ Found {len(players)} players")
        return players
        
    except Exception as e:
        print(f"  ❌ Error fetching roster: {e}")
        return []
    
def process_single_team_api(team_abbr):
    """
    Process a single team using NBA API and populate the new table
    """
    print(f"🏀 PROCESSING SINGLE TEAM: {team_abbr.upper()}")
    print("=" * 50)
    
    # Get internal team ID from abbreviation
    internal_team_id = teams.get(team_abbr.upper())
    if not internal_team_id:
        print(f"❌ Unknown team abbreviation: {team_abbr}") 
        print(f"Available teams: {', '.join(teams.keys())}")
        return
    
    # Get NBA API team ID
    nba_api_team_id = team_id_to_nba_api_id.get(internal_team_id)
    if not nba_api_team_id:
        print(f"❌ No NBA API team ID found for {team_abbr}")
        return
    
    print(f"✅ Found team: {team_abbr} (Internal: {internal_team_id}, NBA API: {nba_api_team_id})")
    
    try:
        # Get roster
        roster = get_team_roster_from_api(nba_api_team_id)
        
        if not roster:
            print(f"❌ No roster data found for {team_abbr}")
            return
        
        print(f"\n📋 ROSTER ({len(roster)} players):")
        for i, player in enumerate(roster, 1):
            print(f"  {i:2d}. {player['full_name']}")
        
        print(f"\n🔍 PROCESSING PLAYER HISTORIES:")
        print("-" * 40)
        
        players_processed = 0
        total_stints_inserted = 0
        
        for i, player in enumerate(roster, 1):
            try:
                print(f"\n{i:2d}/{len(roster)} {player['full_name']}")
                print("  " + "="*30)
                
                # Get or create player in DB
                first_name = player['first_name']
                last_name = player['last_name']
                db_player_id = get_player_id(first_name, last_name, internal_team_id)
                print(f"  📊 Database Player ID: {db_player_id}")
                
                # Get stint history
                stints = get_player_stints_from_nba_api(player['player_id'], player['full_name'], team_abbr)
                
                if not stints:
                    print("  ⚠️  No stint data found")
                    continue
                
                # Insert each stint
                stints_inserted = 0
                print(f"  💾 Inserting {len(stints)} stints into database:")
                
                for j, stint in enumerate(stints, 1):
                    # Convert team abbr to internal team ID
                    stint_team_id = teams.get(stint['team'])
                    if stint_team_id:
                        insert_api_player_stint(
                            db_player_id,
                            stint_team_id, 
                            stint['start_date'],
                            stint['end_date'],
                            stint['games_played'],
                            player['player_id']
                        )
                        
                        status = "CURRENT" if stint['end_date'] is None else "FORMER"
                        print(f"    {j}. {stint['team']} ({stint['start_date']} to {stint['end_date'] or 'present'}) - {stint['games_played']} games [{status}]")
                        stints_inserted += 1
                        total_stints_inserted += 1
                    else:
                        print(f"Unknown team abbreviation: {stint['team']}")
                
                print(f"  ✅ Inserted {stints_inserted}/{len(stints)} stints successfully")
                players_processed += 1
                
                time.sleep(10)  # 10 seconds between players
                
            except Exception as e:
                error_message = str(e)
                log_player_error(player['full_name'], team_abbr, error_message)
                continue
        
        print(f"\n🏁 {team_abbr.upper()} PROCESSING COMPLETE!")
        print("="*50)
        print(f"✅ Players processed: {players_processed}/{len(roster)}")
        print(f"✅ Total stints inserted: {total_stints_inserted}")
        print(f"📊 Data inserted into: nba_player_team_stints_api")
        
    except Exception as e:
        print(f"❌ Error processing {team_abbr}: {e}")


teams_to_process = [
    'NYK'
]

if __name__ == "__main__":

    for i, team in enumerate(teams_to_process, 1):
        print(f"Team {i}/{len(teams_to_process)} - {team}")
        try:
            process_single_team_api(team)
            print(f"✅ {team} completed successfully")
        except Exception as e:
            print(f"❌ {team} failed: {e}")
            
        if i < len(teams_to_process):
            print(f"Taking 3 min break before next team")
            time.sleep(180)
    
    print(f"\nPROCESSING COMPLETE!")
    print(f"\n🚨 PLAYERS WITH ERRORS ({len(error_log)} total):")
    for error in error_log:
        print(f" - {error}")