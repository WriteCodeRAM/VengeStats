from nba_api.stats.endpoints import PlayerGameLog
import pandas as pd
from datetime import datetime
from backend.nba_api.utils.player_utils import get_seasons_from_date

def get_stats(player_id, opponent=None, after_date=None): 
    """
    Get player game stats filtered by opponent and date across multiple seasons
    
    Args:
        player_id: NBA player ID
        opponent: Team abbreviation to filter by as OPPONENT (e.g., 'MIA', 'LAL')
        after_date: Date string in format 'YYYY-MM-DD' or datetime object
    """
    if after_date:
        seasons = get_seasons_from_date(after_date)
    else:
        # Default to current season if no date provided
        current_year = datetime.now().year
        if datetime.now().month < 10:
            current_year -= 1
        next_year = str(current_year + 1)[-2:]
        seasons = [f"{current_year}-{next_year}"]
    
    all_games = []
    
    for season in seasons:
        try:
            print(f"Fetching data for season {season}...")
            gamelog = PlayerGameLog(player_id=player_id, season=season)
            df = gamelog.get_data_frames()[0]
            
            if not df.empty:
                all_games.append(df)
        except Exception as e:
            print(f"Error fetching season {season}: {e}")
            continue
    
    if not all_games:
        return pd.DataFrame(columns=['Date', 'Matchup', 'Points', 'Rebounds', 'Assists', 'Minutes'])
    
    # Combine all seasons
    df_combined = pd.concat(all_games, ignore_index=True)
    
    # Convert GAME_DATE to datetime
    df_combined['GAME_DATE'] = pd.to_datetime(df_combined['GAME_DATE'])
    
    # Select relevant columns
    df_selected = df_combined[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'MIN']]
    df_selected.columns = ['Date', 'Matchup', 'Points', 'Rebounds', 'Assists', 'Minutes']

    # Filter by date if provided
    if after_date:
        after_date = pd.to_datetime(after_date)
        df_selected = df_selected[df_selected['Date'] > after_date]
    
    # Filter by opponent if provided
    # This looks for games where the opponent team is in the matchup but the player is NOT playing for that team
    if opponent:
        # Split the matchup to identify home/away and teams
        def is_opponent_game(matchup, target_opponent):
            """
            Check if target_opponent is the opponent (not the player's team)
            Matchup formats: "TEAM1 vs. TEAM2" (home) or "TEAM1 @ TEAM2" (away)
            """
            if ' vs. ' in matchup:
                # Home game: "PLAYER_TEAM vs. OPPONENT_TEAM"
                player_team, opponent_team = matchup.split(' vs. ')
                return opponent_team.strip() == target_opponent
            elif ' @ ' in matchup:
                # Away game: "PLAYER_TEAM @ OPPONENT_TEAM"  
                player_team, opponent_team = matchup.split(' @ ')
                return opponent_team.strip() == target_opponent
            return False
        
        df_selected = df_selected[df_selected['Matchup'].apply(lambda x: is_opponent_game(x, opponent))]

    return df_selected.sort_values('Date')