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
    if opponent:
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


def exclude_former_teams(df, former_teams):
    """
    Exclude games against former teams from the dataframe
    
    Args:
        df: DataFrame with game data including 'Matchup' column
        former_teams: List of team abbreviations to exclude (e.g., ['BOS', 'MIA'])
    
    Returns:
        DataFrame with former team games filtered out
    """
    def is_not_former_team_game(matchup, former_teams_list):
        """
        Check if the game is NOT against any former team
        """
        for team in former_teams_list:
            if ' vs. ' in matchup:
                # Home game: "PLAYER_TEAM vs. OPPONENT_TEAM"
                player_team, opponent_team = matchup.split(' vs. ')
                if opponent_team.strip() == team:
                    return False
            elif ' @ ' in matchup:
                # Away game: "PLAYER_TEAM @ OPPONENT_TEAM"  
                player_team, opponent_team = matchup.split(' @ ')
                if opponent_team.strip() == team:
                    return False
        return True
    
    return df[df['Matchup'].apply(lambda x: is_not_former_team_game(x, former_teams))]


def get_fair_comparison(player_id, former_team, after_date):
    """
    Get revenge games vs non-revenge games for comparison
    
    Returns:
        tuple: (revenge_games_df, non_revenge_games_df)
    """
    # Get revenge games after the date
    revenge_games = get_stats(player_id, opponent=former_team, after_date=after_date)
    
    # Get ALL games after the same date, then exclude revenge games
    all_games = get_stats(player_id, after_date=after_date)
    non_revenge_games = exclude_former_teams(all_games, [former_team])
    
    return revenge_games, non_revenge_games


def compare_stats(revenge_df, regular_df):
    """
    Compare revenge game stats vs regular game stats
    
    Returns:
        dict: Statistical comparison with differences
    """
    if revenge_df.empty or regular_df.empty:
        return {"error": "Insufficient data for comparison"}
    
    revenge_stats = {
        'points': revenge_df['Points'].mean(),
        'rebounds': revenge_df['Rebounds'].mean(),
        'assists': revenge_df['Assists'].mean(),
        'minutes': revenge_df['Minutes'].mean(),
        'games': len(revenge_df)
    }
    
    regular_stats = {
        'points': regular_df['Points'].mean(),
        'rebounds': regular_df['Rebounds'].mean(), 
        'assists': regular_df['Assists'].mean(),
        'minutes': regular_df['Minutes'].mean(),
        'games': len(regular_df)
    }
    
    # Calculate differences (revenge - regular)
    differences = {
        'points_diff': revenge_stats['points'] - regular_stats['points'],
        'rebounds_diff': revenge_stats['rebounds'] - regular_stats['rebounds'],
        'assists_diff': revenge_stats['assists'] - regular_stats['assists'],
        'minutes_diff': revenge_stats['minutes'] - regular_stats['minutes']
    }
    
    return {
        'revenge_stats': revenge_stats,
        'regular_stats': regular_stats,
        'differences': differences
    }