import pandas as pd
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLog
from datetime import datetime, timedelta

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

def get_player_stints_from_nba_api(player_id, player_name, current_team_abbr=None):
   """
   Get player's COMPLETE career stint history from NBA API game logs
   Handles multiple stints with same team and recently traded players with no games yet
   """
   print(f"    Analyzing {player_name} (full career)...")
   
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
               print(f"      Found data for {season}")
           else:
               consecutive_empty += 1
               
           time.sleep(5)  # 5 seconds between season checks
           
           # If we hit 3 consecutive seasons with no data, player likely wasn't in league yet
           if consecutive_empty >= 3 and i > 5:
               print(f"      No data found for 3+ consecutive seasons, stopping search")
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
       print(f"    No seasons found for {player_name}")
       return []
   
   print(f"    Found {len(seasons)} seasons of data: {seasons[0]} to {seasons[-1]}")
   
   all_games = []
   
   # Now fetch all the game data for found seasons (regular season + playoffs)
   for i, season in enumerate(seasons, 1):
       try:
           print(f"      Fetching {season} ({i}/{len(seasons)})...")
           
           season_games = []
           
           # Get regular season games
           try:
               reg_gamelog = PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Regular Season')
               reg_df = reg_gamelog.get_data_frames()[0]
               if not reg_df.empty:
                   season_games.append(reg_df)
                   print(f"        Regular season: {len(reg_df)} games")
           except Exception as e:
               print(f"        No regular season data: {e}")
           
           time.sleep(5)  # 5 seconds between reg season and playoffs
           
           # Get playoff games
           try:
               playoff_gamelog = PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Playoffs')
               playoff_df = playoff_gamelog.get_data_frames()[0]
               if not playoff_df.empty:
                   season_games.append(playoff_df)
                   print(f"        Playoffs: {len(playoff_df)} games")
           except Exception as e:
               # Playoffs are optional - many players/seasons don't have them
               pass
           
           # Combine regular season + playoffs for this season
           if season_games:
               combined_season = pd.concat(season_games, ignore_index=True)
               all_games.append(combined_season)
               total_games = len(combined_season)
               print(f"        Total {season}: {total_games} games")
           else:
               print(f"        No data found for {season}")
               
           time.sleep(3)  # 3 seconds between seasons
           
           # Extra break for veterans with many seasons to prevent API overload
           if i > 10:  # After 10+ seasons, take longer breaks
               print(f"        Long career detected, taking 10-second break after season {i}...")
               time.sleep(10)  # 10 seconds for veterans mid-career
           
       except Exception as e:
           print(f"      Error fetching {season}: {e}")
           continue
   
   if not all_games:
       print(f"    No game data found")
       return []
   
   # Combine and sort by date
   combined_df = pd.concat(all_games, ignore_index=True)
   combined_df['GAME_DATE'] = pd.to_datetime(combined_df['GAME_DATE'], errors='coerce')
   combined_df = combined_df.sort_values('GAME_DATE')
   
   # Detect team changes (allowing for multiple stints with same team)
   stints = []
   current_stint_team = None
   stint_start = None
   stint_games = 0
   prev_game_date = None
   
   for _, game in combined_df.iterrows():
       team = extract_player_team_from_matchup(game['MATCHUP'])
       game_date = game['GAME_DATE'].date()
       
       if current_stint_team != team:
           # End previous stint
           if current_stint_team is not None:
               stints.append({
                   'team': current_stint_team,
                   'start_date': stint_start,
                   'end_date': prev_game_date,
                   'games_played': stint_games
               })
           
           # Start new stint
           current_stint_team = team
           stint_start = game_date
           stint_games = 1
       else:
           stint_games += 1
       
       prev_game_date = game_date
   
   # Add final stint from game logs
   if current_stint_team is not None:
       stints.append({
           'team': current_stint_team,
           'start_date': stint_start,
           'end_date': None,  # This will be updated if player moved recently
           'games_played': stint_games
       })
   
    # Handle recently moved players
   if current_team_abbr and stints:
        last_stint_team = stints[-1]['team']
        
        if last_stint_team != current_team_abbr:
            print(f"    Recent move detected: {last_stint_team} -> {current_team_abbr}")
            
            # Set proper end date for previous stint (their actual last game)
            stints[-1]['end_date'] = prev_game_date  # This is the last game they actually played
            
            # Create new current stint starting day after last game
            next_day = prev_game_date + timedelta(days=1)
            
            stints.append({
                'team': current_team_abbr,
                'start_date': next_day,
                'end_date': None,  # Current stint = no end date
                'games_played': 0
            })
    
   return stints