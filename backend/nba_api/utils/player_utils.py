import pandas as pd
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLog
from backend.db.queries.players import insert_api_player_stint, get_player_id
from backend.db.queries.teams import teams
from datetime import datetime

def search_player(name): 
    player = players.find_players_by_full_name(name)
    if not player: 
        return "Player not found"
    return player[0]

def get_seasons_from_date(after_date):
    """
    Generate list of NBA seasons from the given date to current season
    """
    if isinstance(after_date, str):
        after_date = pd.to_datetime(after_date)
    
    start_year = after_date.year
    current_year = datetime.now().year
    
    # NBA season starts in October, so if we're before October, we're still in the previous season
    if datetime.now().month < 10:
        current_year -= 1
    
    # If the date is before October, it's part of the previous NBA season
    if after_date.month < 10:
        start_year -= 1
    
    seasons = []
    for year in range(start_year, current_year + 1):
        next_year = str(year + 1)[-2:]  # Get last 2 digits
        seasons.append(f"{year}-{next_year}")
    
    return seasons

def extract_player_team_from_matchup(matchup):
    """
    Extract the player's team from matchup string
    Examples: "LAL vs. BOS" -> "LAL", "LAL @ BOS" -> "LAL"
    """
    if ' vs. ' in matchup:
        return matchup.split(' vs. ')[0].strip()
    elif ' @ ' in matchup:
        return matchup.split(' @ ')[0].strip()
    else:
        return None

def process_single_player_api(player_name, current_team_abbr):
    """
    Process a single player using NBA API and populate the new table
    """
    print(f"🏀 PROCESSING SINGLE PLAYER: {player_name}")
    print("=" * 50)
   
    player_info = search_player(player_name)
    if player_info == "Player not found":
        print(f"❌ Could not find {player_name} in NBA API")
        return
    
    # Get internal team ID from abbreviation
    internal_team_id = teams.get(current_team_abbr.upper())
    if not internal_team_id:
        print(f"❌ Unknown team abbreviation: {current_team_abbr}")
        return
    
    print(f"✅ Found player: {player_info['full_name']}, NBA API ID: {player_info['id']}")
    print(f"✅ Current team: {current_team_abbr} (Internal ID: {internal_team_id})")
    
    try:
        # Parse player name for database
        name_parts = player_name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Get or create player in your DB
        db_player_id = get_player_id(first_name, last_name, internal_team_id)
        print(f"📊 Database Player ID: {db_player_id}")
        
        # Get stint history
        stints = get_player_stints_from_nba_api(player_info['id'], player_info['full_name'])
        
        if not stints:
            print("⚠️  No stint data found")
            return
        
        # Insert each stint
        stints_inserted = 0
        print(f"💾 Inserting {len(stints)} stints into database:")
        
        for j, stint in enumerate(stints, 1):
            # Convert team abbr to your internal team ID
            stint_team_id = teams.get(stint['team'])
            if stint_team_id:
                insert_api_player_stint(
                    db_player_id,
                    stint_team_id, 
                    stint['start_date'],
                    stint['end_date'],
                    stint['games_played'],
                    player_info['id']
                )
                
                status = "CURRENT" if stint['end_date'] is None else "FORMER"
                print(f"  {j}. {stint['team']} ({stint['start_date']} to {stint['end_date'] or 'present'}) - {stint['games_played']} games [{status}]")
                stints_inserted += 1
            else:
                print(f"  ❌ Unknown team abbreviation: {stint['team']}")
        
        print(f"✅ Inserted {stints_inserted}/{len(stints)} stints successfully")
        print(f"📊 Data inserted into: nba_player_team_stints_api")
        
    except Exception as e:
        print(f"❌ Error processing {player_name}: {e}")

def get_player_stints_from_nba_api(player_id, player_name):
    """
    Get player's COMPLETE career stint history from NBA API game logs
    Handles multiple stints with same team (like LeBron's Cleveland stints)
    """
    print(f"    🔍 Analyzing {player_name} (full career)...")
    
    # Get current year for season calculation
    current_year = datetime.now().year
    if datetime.now().month < 10:  # Before October = previous season
        current_year -= 1
    
    # Get ALL seasons for this player's career
    seasons = []
    consecutive_empty = 0
    
    # Start from 1996 (covers all current players) and work backwards from current year
    for i in range(30):  # Max 30 seasons back (covers 1996 to present)
        year = current_year - i
        next_year = year + 1
        season = f"{year}-{str(next_year)[-2:]}"
        
        try:
            # Quick check if player has data for this season
            gamelog = PlayerGameLog(player_id=player_id, season=season)
            df = gamelog.get_data_frames()[0]
            
            if not df.empty:
                seasons.append(season)
                consecutive_empty = 0  # Reset counter
                print(f"      📅 Found data for {season}")
            else:
                consecutive_empty += 1
                
            time.sleep(5)  # 5 seconds between season checks
            
            # If we hit 3 consecutive seasons with no data, player likely wasn't in league yet
            if consecutive_empty >= 3 and i > 5:
                print(f"      ⏹️  No data found for 3+ consecutive seasons, stopping search")
                break
                
        except Exception as e:
            consecutive_empty += 1
            # If we hit too many errors early on, player might not exist in older seasons
            if consecutive_empty >= 3 and i > 5:
                break
            continue
    
    # Reverse to get chronological order (oldest to newest)
    seasons.reverse()
    
    if not seasons:
        print(f"    ⚠️  No seasons found for {player_name}")
        return []
    
    print(f"    📊 Found {len(seasons)} seasons of data: {seasons[0]} to {seasons[-1]}")
    
    all_games = []
    
    # Now fetch all the game data for found seasons (regular season + playoffs)
    for i, season in enumerate(seasons, 1):
        try:
            print(f"      📥 Fetching {season} ({i}/{len(seasons)})...")
            
            season_games = []
            
            # Get regular season games
            try:
                reg_gamelog = PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Regular Season')
                reg_df = reg_gamelog.get_data_frames()[0]
                if not reg_df.empty:
                    season_games.append(reg_df)
                    print(f"        📊 Regular season: {len(reg_df)} games")
            except Exception as e:
                print(f"        ⚠️  No regular season data: {e}")
            
            time.sleep(5)  # 5 seconds between reg season and playoffs
            
            # Get playoff games
            try:
                playoff_gamelog = PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Playoffs')
                playoff_df = playoff_gamelog.get_data_frames()[0]
                if not playoff_df.empty:
                    season_games.append(playoff_df)
                    print(f"        🏆 Playoffs: {len(playoff_df)} games")
            except Exception as e:
                # Playoffs are optional - many players/seasons don't have them
                pass
            
            # Combine regular season + playoffs for this season
            if season_games:
                combined_season = pd.concat(season_games, ignore_index=True)
                all_games.append(combined_season)
                total_games = len(combined_season)
                print(f"        ✅ Total {season}: {total_games} games")
            else:
                print(f"        ❌ No data found for {season}")
                
            time.sleep(3)  # 3 seconds between seasons
            
            # Extra break for veterans with many seasons to prevent API overload
            if i > 10:  # After 10+ seasons, take longer breaks
                print(f"        ⏰ Long career detected, taking 10-second break after season {i}...")
                time.sleep(10)  # 10 seconds for veterans mid-career
            
        except Exception as e:
            print(f"      ❌ Error fetching {season}: {e}")
            continue
    
    if not all_games:
        print(f"    ⚠️  No game data found")
        return []
    
    # Combine and sort by date
    combined_df = pd.concat(all_games, ignore_index=True)
    combined_df['GAME_DATE'] = pd.to_datetime(combined_df['GAME_DATE'], errors='coerce')
    combined_df = combined_df.sort_values('GAME_DATE')
    
    # Detect team changes (allowing for multiple stints with same team)
    stints = []
    current_team = None
    stint_start = None
    stint_games = 0
    prev_game_date = None
    
    for _, game in combined_df.iterrows():
        team = extract_player_team_from_matchup(game['MATCHUP'])
        game_date = game['GAME_DATE'].date()
        
        if current_team != team:
            # End previous stint
            if current_team is not None:
                stints.append({
                    'team': current_team,
                    'start_date': stint_start,
                    'end_date': prev_game_date,
                    'games_played': stint_games
                })
            
            # Start new stint
            current_team = team
            stint_start = game_date
            stint_games = 1
        else:
            stint_games += 1
        
        prev_game_date = game_date
    
    # Add final stint (current team, no end date)
    if current_team is not None:
        stints.append({
            'team': current_team,
            'start_date': stint_start,
            'end_date': None,  # Current stint
            'games_played': stint_games
        })
    
    # Log multiple stints for same team
    team_counts = {}
    for stint in stints:
        team_counts[stint['team']] = team_counts.get(stint['team'], 0) + 1
    
    multiple_stint_teams = [team for team, count in team_counts.items() if count > 1]
    if multiple_stint_teams:
        print(f"    🔄 Multiple stints detected: {', '.join(multiple_stint_teams)}")
    
    print(f"    📊 Found {len(stints)} total stints")
    return stints