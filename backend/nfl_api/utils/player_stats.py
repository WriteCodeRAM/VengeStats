import nfl_data_py as nfl
import pandas as pd
from datetime import datetime

def get_nfl_stats(player_id, opponent_team_abbr=None, after_season=None):
    """
    Get NFL player game stats filtered by opponent and season using nfl_data_py
    
    Args:
        player_id: nfl_data_py player ID (gsis_id)
        opponent_team_abbr: Team abbreviation to filter by as OPPONENT (e.g., 'KC', 'MIA')
        after_season: Season year to start from (e.g., 2022)
    """
    if after_season:
        seasons = list(range(after_season, datetime.now().year + 1))
    else:
        # Default to current season
        current_year = datetime.now().year
        seasons = [current_year]
    
    all_games = []
    
    for season in seasons:
        try:
            print(f"Fetching NFL data for season {season}...")
            
            # Get weekly stats for the season
            weekly_stats = nfl.import_weekly_data([season], columns=[
                'player_id', 'player_name', 'recent_team', 'opponent_team',
                'week', 'season', 'position', 'fantasy_points', 'fantasy_points_ppr',
                'receiving_yards', 'receiving_tds', 'receptions', 'targets',
                'rushing_yards', 'rushing_tds', 'carries',
                'passing_yards', 'passing_tds', 'completions', 'attempts', 'interceptions'
            ])
            
            # Filter for specific player
            player_stats = weekly_stats[weekly_stats['player_id'] == player_id]
            
            if not player_stats.empty:
                all_games.append(player_stats)
                
        except Exception as e:
            print(f"Error fetching season {season}: {e}")
            continue
    
    if not all_games:
        return pd.DataFrame()
    
    # Combine all seasons
    df_combined = pd.concat(all_games, ignore_index=True)
    
    # Filter by opponent if provided
    if opponent_team_abbr:
        print(f"Filtering for opponent: {opponent_team_abbr}")
        before_filter = len(df_combined)
        df_combined = df_combined[df_combined['opponent_team'] == opponent_team_abbr]
        after_filter = len(df_combined)
        print(f"Games before filter: {before_filter}, after filter: {after_filter}")
        
        # Debug: Print the actual games found
        if not df_combined.empty:
            print("Revenge games found:")
            for _, game in df_combined.iterrows():
                print(f"  Season {game['season']}, Week {game['week']}: {game['recent_team']} vs {game['opponent_team']}")
    
    return df_combined.sort_values(['season', 'week'])

# print(get_nfl_stats('00-0033040', 'KC', 2021)) 

def get_nfl_fair_comparison(player_id: str, former_team_abbr: str, after_season: int):
    """
    Get revenge games vs non-revenge games for NFL comparison
    """
    # Fetch ALL games after departure season
    all_games = get_nfl_stats(player_id, after_season=after_season)
    
    if all_games.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Split the data
    revenge_games = all_games[all_games['opponent_team'] == former_team_abbr]
    non_revenge_games = all_games[all_games['opponent_team'] != former_team_abbr]
    
    return revenge_games, non_revenge_games

def compare_nfl_stats(revenge_df, regular_df, position):
    """
    Compare revenge game stats vs regular game stats for NFL using nfl_data_py columns
    Always return regular stats even when revenge data is insufficient
    """
    # Return error only if we don't have regular game data
    if regular_df.empty:
        return {"error": "No regular game data available"}
    
    # Always calculate regular stats first
    if position == 'QB':
        regular_stats = {
            'passing_yards': regular_df['passing_yards'].mean(),
            'passing_tds': regular_df['passing_tds'].mean(),
            'completions': regular_df['completions'].mean(),
            'attempts': regular_df['attempts'].mean(),
            'interceptions': regular_df['interceptions'].mean(),
            'fantasy_points': regular_df['fantasy_points'].mean(),
            'games': len(regular_df)
        }
        
        # Empty revenge stats structure
        empty_revenge_stats = {
            'passing_yards': None,
            'passing_tds': None,
            'completions': None,
            'attempts': None,
            'interceptions': None,
            'fantasy_points': None,
            'games': 0
        }
        
        empty_differences = {
            'passing_yards_diff': None,
            'passing_tds_diff': None,
            'completions_diff': None,
            'interceptions_diff': None,
            'fantasy_points_diff': None
        }
        
    elif position == 'RB':
        regular_stats = {
            'rushing_yards': regular_df['rushing_yards'].mean(),
            'rushing_tds': regular_df['rushing_tds'].mean(),
            'carries': regular_df['carries'].mean(),
            'receiving_yards': regular_df['receiving_yards'].mean(),
            'receiving_tds': regular_df['receiving_tds'].mean(),
            'receptions': regular_df['receptions'].mean(),
            'fantasy_points': regular_df['fantasy_points_ppr'].mean(),
            'games': len(regular_df)
        }
        
        empty_revenge_stats = {
            'rushing_yards': None,
            'rushing_tds': None,
            'carries': None,
            'receiving_yards': None,
            'receiving_tds': None,
            'receptions': None,
            'fantasy_points': None,
            'games': 0
        }
        
        empty_differences = {
            'rushing_yards_diff': None,
            'rushing_tds_diff': None,
            'carries_diff': None,
            'receiving_yards_diff': None,
            'fantasy_points_diff': None
        }
        
    elif position in ['WR', 'TE']:
        regular_stats = {
            'receiving_yards': regular_df['receiving_yards'].mean(),
            'receiving_tds': regular_df['receiving_tds'].mean(),
            'receptions': regular_df['receptions'].mean(),
            'targets': regular_df['targets'].mean(),
            'fantasy_points': regular_df['fantasy_points_ppr'].mean(),
            'games': len(regular_df)
        }
        
        empty_revenge_stats = {
            'receiving_yards': None,
            'receiving_tds': None,
            'receptions': None,
            'targets': None,
            'fantasy_points': None,
            'games': 0
        }
        
        empty_differences = {
            'receiving_yards_diff': None,
            'receiving_tds_diff': None,
            'receptions_diff': None,
            'targets_diff': None,
            'fantasy_points_diff': None
        }
    
    # If no revenge data, return regular stats with empty revenge structure
    if revenge_df.empty or len(revenge_df) < 1:
        return {
            'revenge_stats': empty_revenge_stats,
            'regular_stats': regular_stats,
            'differences': empty_differences
        }
    
    # If we have both datasets, calculate revenge stats and differences
    if position == 'QB':
        revenge_stats = {
            'passing_yards': revenge_df['passing_yards'].mean(),
            'passing_tds': revenge_df['passing_tds'].mean(),
            'completions': revenge_df['completions'].mean(),
            'attempts': revenge_df['attempts'].mean(),
            'interceptions': revenge_df['interceptions'].mean(),
            'fantasy_points': revenge_df['fantasy_points'].mean(),
            'games': len(revenge_df)
        }
        
        differences = {
            'passing_yards_diff': revenge_stats['passing_yards'] - regular_stats['passing_yards'],
            'passing_tds_diff': revenge_stats['passing_tds'] - regular_stats['passing_tds'],
            'completions_diff': revenge_stats['completions'] - regular_stats['completions'],
            'interceptions_diff': revenge_stats['interceptions'] - regular_stats['interceptions'],
            'fantasy_points_diff': revenge_stats['fantasy_points'] - regular_stats['fantasy_points']
        }
        
    elif position == 'RB':
        revenge_stats = {
            'rushing_yards': revenge_df['rushing_yards'].mean(),
            'rushing_tds': revenge_df['rushing_tds'].mean(),
            'carries': revenge_df['carries'].mean(),
            'receiving_yards': revenge_df['receiving_yards'].mean(),
            'receiving_tds': revenge_df['receiving_tds'].mean(),
            'receptions': revenge_df['receptions'].mean(),
            'fantasy_points': revenge_df['fantasy_points_ppr'].mean(),
            'games': len(revenge_df)
        }
        
        differences = {
            'rushing_yards_diff': revenge_stats['rushing_yards'] - regular_stats['rushing_yards'],
            'rushing_tds_diff': revenge_stats['rushing_tds'] - regular_stats['rushing_tds'],
            'carries_diff': revenge_stats['carries'] - regular_stats['carries'],
            'receiving_yards_diff': revenge_stats['receiving_yards'] - regular_stats['receiving_yards'],
            'fantasy_points_diff': revenge_stats['fantasy_points'] - regular_stats['fantasy_points']
        }
        
    elif position in ['WR', 'TE']:
        revenge_stats = {
            'receiving_yards': revenge_df['receiving_yards'].mean(),
            'receiving_tds': revenge_df['receiving_tds'].mean(),
            'receptions': revenge_df['receptions'].mean(),
            'targets': revenge_df['targets'].mean(),
            'fantasy_points': revenge_df['fantasy_points_ppr'].mean(),
            'games': len(revenge_df)
        }
        
        differences = {
            'receiving_yards_diff': revenge_stats['receiving_yards'] - regular_stats['receiving_yards'],
            'receiving_tds_diff': revenge_stats['receiving_tds'] - regular_stats['receiving_tds'],
            'receptions_diff': revenge_stats['receptions'] - regular_stats['receptions'],
            'targets_diff': revenge_stats['targets'] - regular_stats['targets'],
            'fantasy_points_diff': revenge_stats['fantasy_points'] - regular_stats['fantasy_points']
        }
    
    return {
        'revenge_stats': revenge_stats,
        'regular_stats': regular_stats,
        'differences': differences
    }

def calculate_nfl_revenge_record(player_id: str, former_team_abbr: str, after_season: int):
    """
    Calculate win-loss record for NFL revenge games starting from a specific season
    
    Args:
        player_id: nfl_data_py player ID
        former_team_abbr: Former team abbreviation  
        after_season: Season to start calculating from (inclusive)
    """
    try:
        # Get revenge games data from the departure season onward
        revenge_games = get_nfl_stats(player_id, opponent_team_abbr=former_team_abbr, after_season=after_season)
        
        if revenge_games.empty:
            return 0, 0, 0  # wins, losses, total_games
        
        wins = 0
        losses = 0
        
        for _, game in revenge_games.iterrows():
            season = game['season']
            week = game['week']
            team = game['recent_team']
            opponent = game['opponent_team']
            
            try:
                # Get schedule data to determine win/loss
                schedule = nfl.import_schedules([season])
                game_result = schedule[
                    ((schedule['home_team'] == team) & (schedule['away_team'] == opponent) & (schedule['week'] == week)) |
                    ((schedule['away_team'] == team) & (schedule['home_team'] == opponent) & (schedule['week'] == week))
                ]
                
                if not game_result.empty:
                    game_row = game_result.iloc[0]
                    if game_row['home_team'] == team:
                        # Player's team was home
                        if game_row['home_score'] > game_row['away_score']:
                            wins += 1
                        elif game_row['away_score'] > game_row['home_score']:
                            losses += 1
                        # Ties are ignored for now
                    else:
                        # Player's team was away
                        if game_row['away_score'] > game_row['home_score']:
                            wins += 1
                        elif game_row['home_score'] > game_row['away_score']:
                            losses += 1
                        # Ties are ignored for now
                            
            except Exception as e:
                print(f"Error getting game result for week {week}, season {season}: {e}")
                continue
        
        total_games = wins + losses
        return wins, losses, total_games
        
    except Exception as e:
        print(f"Error calculating revenge record for {player_id}: {e}")
        return 0, 0, 0
    
def get_all_nfl_player_data(player_id: str, former_team_abbr: str, after_season: int):
    """
    Get all NFL data for a player in one go - stats, comparisons, and record
    
    Returns:
        tuple: (revenge_games_df, non_revenge_games_df, wins, losses, total_revenge_games)
    """
    try:
        # Fetch ALL games after departure season (single API call)
        all_games = get_nfl_stats(player_id, after_season=after_season)
        
        if all_games.empty:
            return pd.DataFrame(), pd.DataFrame(), 0, 0, 0
        
        # Split the data for comparison
        revenge_games = all_games[all_games['opponent_team'] == former_team_abbr]
        non_revenge_games = all_games[all_games['opponent_team'] != former_team_abbr]
        
        # Calculate win-loss record from revenge games
        wins = 0
        losses = 0
        
        if not revenge_games.empty:
            # Group by season to minimize schedule API calls
            seasons_to_check = revenge_games['season'].unique()
            schedule_cache = {}
            
            for season in seasons_to_check:
                try:
                    schedule_cache[season] = nfl.import_schedules([season])
                except Exception as e:
                    print(f"Error fetching schedule for {season}: {e}")
                    schedule_cache[season] = pd.DataFrame()
            
            # Calculate record
            for _, game in revenge_games.iterrows():
                season = game['season']
                week = game['week']
                team = game['recent_team']
                opponent = game['opponent_team']
                
                if season not in schedule_cache or schedule_cache[season].empty:
                    continue
                
                try:
                    schedule = schedule_cache[season]
                    game_result = schedule[
                        ((schedule['home_team'] == team) & (schedule['away_team'] == opponent) & (schedule['week'] == week)) |
                        ((schedule['away_team'] == team) & (schedule['home_team'] == opponent) & (schedule['week'] == week))
                    ]
                    
                    if not game_result.empty:
                        game_row = game_result.iloc[0]
                        if game_row['home_team'] == team:
                            if game_row['home_score'] > game_row['away_score']:
                                wins += 1
                            elif game_row['away_score'] > game_row['home_score']:
                                losses += 1
                        else:
                            if game_row['away_score'] > game_row['home_score']:
                                wins += 1
                            elif game_row['home_score'] > game_row['away_score']:
                                losses += 1
                                
                except Exception as e:
                    print(f"Error processing game result: {e}")
                    continue
        
        total_revenge_games = wins + losses
        return revenge_games, non_revenge_games, wins, losses, total_revenge_games
        
    except Exception as e:
        print(f"Error getting player data for {player_id}: {e}")
        return pd.DataFrame(), pd.DataFrame(), 0, 0, 0