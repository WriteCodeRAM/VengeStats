import requests
import time
import nfl_data_py as nfl
from db.queries.nfl.players import insert_nfl_player, get_existing_player_info, insert_nfl_player_stint

# Target positions
TARGET_POSITIONS = ['QB', 'RB', 'WR', 'TE']
ESPN_BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/football/nfl"

def get_team_roster(team_id):
    """Get roster for a specific NFL team from ESPN API"""
    url = f"{ESPN_BASE_URL}/teams/{team_id}/roster"
    
    try:
        print(f"📡 Fetching roster for team {team_id}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        team_info = {
            'team_id': data.get('team', {}).get('id'),
            'team_name': data.get('team', {}).get('displayName'),
            'team_abbr': data.get('team', {}).get('abbreviation')
        }
        
        print(f"✅ Got roster for: {team_info['team_name']} ({team_info['team_abbr']})")
        return data, team_info
        
    except requests.RequestException as e:
        print(f"❌ Error fetching roster for team {team_id}: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error processing roster data: {e}")
        return None, None

def extract_target_players(roster_data, team_info):
    """Extract players and determine their active status"""
    if not roster_data or 'athletes' not in roster_data:
        return []
    
    players = []
    
    for position_group in roster_data['athletes']:
        if position_group.get('position') == 'offense':
            for player in position_group.get('items', []):
                position_info = player.get('position', {})
                position_abbr = position_info.get('abbreviation', '')
                
                if position_abbr in TARGET_POSITIONS:
                    # NEW: Check player status from ESPN API
                    player_status = player.get('status', {})
                    status_type = player_status.get('type', 'active').lower()
                    
                    # Determine if player is active
                    is_active = status_type not in ['injured_reserve', 'ir', 'out', 'practice_squad', 'ps', 'suspended']
                    
                    player_data = {
                        'espn_id': player.get('id'),
                        'first_name': player.get('firstName', ''),
                        'last_name': player.get('lastName', ''),
                        'display_name': player.get('displayName', ''),
                        'position': position_abbr,
                        'current_team_id': team_info['team_id'],
                        'current_team_abbr': team_info['team_abbr'],
                        'is_active': is_active  # NEW: Now properly calculated
                    }
                    players.append(player_data)
    
    return players

def find_nfl_data_py_player_id(player_name, position):
    """Find player's nfl-data-py ID by matching name and position"""
    try:
        print(f"    Looking up nfl-data-py ID for {player_name} ({position})...")
        
        current_season = 2025
        rosters = nfl.import_seasonal_rosters([current_season])
        
        # Try exact match first
        matches = rosters[
            (rosters['player_name'] == player_name) & 
            (rosters['position'] == position)
        ]
        
        if not matches.empty:
            player_id = matches.iloc[0]['player_id']
            print(f"    Found exact match: {player_id}")
            return player_id
        
        # Clean the name for suffixes only
        clean_name = player_name.replace(' Sr.', '').replace(' Jr.', '').replace(' III', '').replace(' II', '').replace(' V', '').strip()
        
        # Try without suffix
        matches = rosters[
            (rosters['player_name'] == clean_name) & 
            (rosters['position'] == position)
        ]
        
        if not matches.empty:
            player_id = matches.iloc[0]['player_id']
            matched_name = matches.iloc[0]['player_name']
            print(f"    Found match without suffix: {player_id} ({matched_name})")
            return player_id
        
        # Try last name + position match (safer than first name matching)
        name_parts = clean_name.split()
        if len(name_parts) >= 2:
            last_name = name_parts[-1]
            
            # Only match on exact last name + position
            matches = rosters[
                (rosters['player_name'].str.endswith(last_name, na=False)) &
                (rosters['position'] == position)
            ]
            
            if len(matches) == 1:  # Only if exactly one match
                player_id = matches.iloc[0]['player_id']
                matched_name = matches.iloc[0]['player_name']
                print(f"    Found last name match: {player_id} ({matched_name})")
                return player_id
            elif len(matches) > 1:
                print(f"    Multiple matches for {last_name} ({position}), skipping for safety")
        
        print(f"    No match found for {player_name} ({position})")
        return None
        
    except Exception as e:
        print(f"    Error looking up {player_name}: {e}")
        return None

def calculate_usage_tier(player_id, position, seasons=[2024]):
    """Calculate usage tier based on recent weekly stats"""
    try:
        weekly_stats = nfl.import_weekly_data(seasons)
        player_stats = weekly_stats[weekly_stats['player_id'] == player_id]
        
        if player_stats.empty:
            return 'INACTIVE'
        
        # Calculate average usage based on position
        if position == 'QB':
            usage_col = 'attempts'
            starter_threshold = 20
            rotational_threshold = 10
            backup_threshold = 3
        elif position == 'RB':
            usage_col = 'carries'
            starter_threshold = 12
            rotational_threshold = 6
            backup_threshold = 2
        elif position == 'WR':
            usage_col = 'targets'
            starter_threshold = 6
            rotational_threshold = 3
            backup_threshold = 1
        elif position == 'TE':
            usage_col = 'targets'
            starter_threshold = 4
            rotational_threshold = 2
            backup_threshold = 1
        else:
            return 'INACTIVE'
        
        
        games_with_usage = player_stats[player_stats[usage_col] > 0]
        if games_with_usage.empty:
            return 'INACTIVE'
        
        avg_usage = games_with_usage[usage_col].mean()
        
        # Determine tier
        if avg_usage >= starter_threshold:
            return 'STARTER'
        elif avg_usage >= rotational_threshold:
            return 'ROTATIONAL'
        elif avg_usage >= backup_threshold:
            return 'BACKUP'
        else:
            return 'INACTIVE'
            
    except Exception as e:
        print(f"    ⚠️  Error calculating usage tier: {e}")
        return 'INACTIVE'

def get_draft_info(player_id):
    """Get draft information for a player"""
    try:
        draft_data = nfl.import_draft_picks([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
        player_draft = draft_data[draft_data['gsis_id'] == player_id]
        
        if not player_draft.empty:
            row = player_draft.iloc[0]
            return (
                int(row.get('round', 0)) if row.get('round') else None,
                int(row.get('pick', 0)) if row.get('pick') else None,
                row.get('team', '') if row.get('team') else None
            )
        return None, None, None
        
    except Exception as e:
        print(f"    ⚠️  Error getting draft info: {e}")
        return None, None, None

def get_accolades(player_id):
    """Get Pro Bowl and All-Pro selections"""
    try:
        draft_data = nfl.import_draft_picks([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
        player_draft = draft_data[draft_data['gsis_id'] == player_id]
        
        if not player_draft.empty:
            row = player_draft.iloc[0]
            return (
                int(row.get('probowls', 0)) if row.get('probowls') else 0,
                int(row.get('allpro', 0)) if row.get('allpro') else 0
            )
        return 0, 0
        
    except Exception as e:
        print(f"    ⚠️  Error getting accolades: {e}")
        return 0, 0

def get_years_experience(player_id):
    """Get years of experience from roster data"""
    try:
        rosters = nfl.import_seasonal_rosters([2024])
        player_data = rosters[rosters['player_id'] == player_id]
        
        if not player_data.empty:
            return int(player_data.iloc[0].get('years_exp', 0))
        return 0
        
    except Exception as e:
        return 0

def get_player_team_history(nfl_data_player_id, player_name):
    """Get player's team history using nfl-data-py"""
    if not nfl_data_player_id:
        return []
    
    try:
        print(f"    📊 Getting team history for {player_name}...")
        
        seasons = list(range(1999, 2025))
        rosters = nfl.import_seasonal_rosters(seasons)
        
        player_history = rosters[rosters['player_id'] == nfl_data_player_id].copy()
        
        if player_history.empty:
            return []
        
        # Group consecutive seasons by team
        player_history = player_history.sort_values('season')
        stints = []
        current_stint = None
        
        for _, row in player_history.iterrows():
            team_abbr = row['team']
            season = row['season']
            
            if current_stint is None or current_stint['team_abbr'] != team_abbr:
                if current_stint is not None:
                    stints.append(current_stint)
                
                current_stint = {
                    'team_abbr': team_abbr,
                    'season_start': season,
                    'season_end': season,
                    'seasons': [season]
                }
            else:
                current_stint['season_end'] = season
                current_stint['seasons'].append(season)
        
        if current_stint is not None:
            stints.append(current_stint)
        
        # Remove duplicate team stints - keep the one with most seasons
        team_stints = {}
        for stint in stints:
            team = stint['team_abbr']
            if team not in team_stints or len(stint['seasons']) > len(team_stints[team]['seasons']):
                team_stints[team] = stint
        
        stints = list(team_stints.values())
        stints.sort(key=lambda x: x['season_start'])
        
        # Convert to final format
        team_mapping = get_team_mapping()
        final_stints = []
        
        for stint in stints:
            team_id = team_mapping.get(stint['team_abbr'])
            if team_id:
                final_stints.append({
                    'team_id': team_id,
                    'team_abbr': stint['team_abbr'],
                    'season_start': stint['season_start'],
                    'season_end': stint['season_end'],
                    'games_played': len(stint['seasons']) * 16,  # Estimate
                    'is_current_stint': stint['season_end'] == 2024
                })
        
        print(f"    📊 Found {len(final_stints)} stints")
        for stint in final_stints:
            years = f"{stint['season_start']}-{stint['season_end']}" if stint['season_start'] != stint['season_end'] else str(stint['season_start'])
            print(f"      - {stint['team_abbr']}: {years}")
        
        return final_stints
        
    except Exception as e:
        print(f"    ❌ Error getting history: {e}")
        return []

def get_team_mapping():
    """Map team abbreviations to ESPN team IDs"""
    return {
        'ARI': '22', 'ATL': '1', 'BAL': '33', 'BUF': '2', 'CAR': '29', 'CHI': '3',
        'CIN': '4', 'CLE': '5', 'DAL': '6', 'DEN': '7', 'DET': '8', 'GB': '9',
        'HOU': '34', 'IND': '11', 'JAX': '30', 'KC': '12', 'LV': '13', 'LAC': '24',
        'LAR': '14', 'MIA': '15', 'MIN': '16', 'NE': '17', 'NO': '18', 'NYG': '19',
        'NYJ': '20', 'PHI': '21', 'PIT': '23', 'SF': '25', 'SEA': '26', 'TB': '27',
        'TEN': '10', 'WAS': '28'
    }

def process_single_player(player_data):
 
    player_name = player_data['display_name']
    position = player_data['position']
    
    print(f"🏈 CHECKING: {player_name} ({position})")
    
    nfl_data_player_id = find_nfl_data_py_player_id(player_name, position)
    if not nfl_data_player_id:
        print(f"    ⚠️  Skipping {player_name} - no nfl-data-py match found")
        return False
    
    existing_player = get_existing_player_info(nfl_data_player_id)
    
    if existing_player:
        # check if anything meaningful changed
        same_team = existing_player['current_team_id'] == player_data['current_team_id']
        same_status = existing_player['is_active'] == player_data['is_active']
        
        if same_team and same_status:
            print(f"    ⏭️  Skipping {player_name} - no changes detected")
            return True
        
        print(f"    🔄 Changes detected for {player_name}")
        if not same_team:
            print(f"      Team change: {existing_player['current_team_id']} -> {player_data['current_team_id']}")
        if not same_status:
            status_change = "active" if player_data['is_active'] else "inactive"
            print(f"      Status change: -> {status_change}")
    else:
        print(f"    ➕ New player detected: {player_name}")
    
    print(f"    📊 Gathering player data...")
    usage_tier = calculate_usage_tier(nfl_data_player_id, position)
    years_exp = get_years_experience(nfl_data_player_id)
    draft_round, draft_number, draft_team = get_draft_info(nfl_data_player_id)
    pro_bowls, all_pros = get_accolades(nfl_data_player_id)
    
    print(f"    📈 Usage tier: {usage_tier}")
    if draft_round:
        print(f"    🎯 Draft: Round {draft_round}, Pick {draft_number} by {draft_team}")
    if pro_bowls > 0:
        print(f"    🏆 Accolades: {pro_bowls} Pro Bowls, {all_pros} All-Pros")
    
    try:
        db_player_id = insert_nfl_player(
            nfl_data_player_id=nfl_data_player_id,
            first_name=player_data['first_name'],
            last_name=player_data['last_name'],
            display_name=player_data['display_name'],
            current_team_id=player_data['current_team_id'],
            position=player_data['position'],
            years_exp=years_exp,
            usage_tier=usage_tier,
            draft_round=draft_round,
            draft_number=draft_number,
            draft_team=draft_team,
            pro_bowl_selections=pro_bowls,
            all_pro_selections=all_pros,
            is_active=player_data['is_active']
        )
        print(f"    ✅ Processed player with DB ID: {db_player_id}")
        
        if not existing_player:
            team_history = get_player_team_history(nfl_data_player_id, player_name)
            if team_history:
                stints_inserted = 0
                for stint in team_history:
                    try:
                        insert_nfl_player_stint(
                            player_id=db_player_id,
                            team_id=stint['team_id'],
                            season_start=stint['season_start'],
                            season_end=stint['season_end'] if stint['season_end'] != stint['season_start'] else None,
                            games_played=stint['games_played'],
                            is_current_stint=stint['is_current_stint']
                        )
                        stints_inserted += 1
                    except Exception as e:
                        print(f"      ❌ Error inserting stint for {stint['team_abbr']}: {e}")
                
                print(f"    📊 Inserted {stints_inserted}/{len(team_history)} stints")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error processing player: {e}")
        return False


def process_team_roster(team_id):
    """Main function: Process entire roster for a team"""
    print(f"🚀 STARTING: Process roster for team {team_id}")
    print("=" * 60)
    

    roster_data, team_info = get_team_roster(team_id)
    if not roster_data:
        print(f"❌ Could not get roster for team {team_id}")
        return False
    

    players = extract_target_players(roster_data, team_info)
    if not players:
        print("❌ No target players found")
        return False
    

    successful_players = 0
    for i, player_data in enumerate(players, 1):
        print(f"\n--- Player {i}/{len(players)} ---")
        if process_single_player(player_data):
            successful_players += 1
        
        time.sleep(2)  
    
    print(f"\n🏆 COMPLETED: {successful_players}/{len(players)} players processed successfully")
    print(f"📊 Team: {team_info['team_name']}")
    return True

# def main():
#     """Test the updated roster processing"""
#     print("=== NFL Roster Processor - New Schema ===")
#     print("🎯 Target positions:", ", ".join(TARGET_POSITIONS))
#     print()
    

#     test_team_id = "34" 
#     success = process_team_roster(test_team_id)
    
#     if success:
#         print("\n✅ Roster processing completed successfully!")
#         print("New fields populated:")
#         print("- usage_tier (STARTER/ROTATIONAL/BACKUP/INACTIVE)")
#         print("- draft info (round, number, team)")
#         print("- accolades (Pro Bowls, All-Pros)")
#         print("- years of experience")
#     else:
#         print("\n❌ Roster processing failed")

# if __name__ == "__main__":
#     main()