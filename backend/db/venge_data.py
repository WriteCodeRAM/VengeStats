from db.queries.nba.players import get_total_games_played, get_total_games_played_for_team
from db.queries.revenge_games import check_first_revenge_game
from db.queries.nba.teams import get_prev_team_id
from nba_utils.utils.data_fetcher import compare_stats
import numpy as np
import pandas as pd

# All-Star Selections for 2024-2025 Season
all_stars = {
    "LeBron James", "Jaylen Brown", "Stephen Curry", "Kevin Durant", "James Harden",
    "Kyrie Irving", "Damian Lillard", "Jayson Tatum", "Nikola Jokic", "Shai Gilgeous-Alexander",
    "Donovan Mitchell", "Pascal Siakam", "Karl-Anthony Towns", "Alperen Sengun",
    "Victor Wembanyama", "Trae Young", "Anthony Edwards", "Jalen Brunson", "Cade Cunningham",
    "Darius Garland", "Tyler Herro", "Jaren Jackson Jr.", "Evan Mobley", "Jalen Williams"
}

# Players with strong revenge narratives (long tenure, messy exits, emotional returns)
notable_revenge_narratives = {
    "Kevin Durant": {10, 21},           # GSW, OKC
    "Kyrie Irving": {2},                # BOS
    "LeBron James": {6, 16},            # CLE, MIA
    "Jimmy Butler": {18, 23, 16},       # MIN, PHI, MIA
    "Paul George": {12},                # IND
    "Chris Paul": {11, 13},             # HOU, LAC
    "James Harden": {11, 23},           # HOU, PHI
    "Ben Simmons": {23},                # PHI
    "Russell Westbrook": {21, 14},      # OKC, LAL
    "Jrue Holiday": {17},               # MIL
    "Marcus Smart": {2},                # BOS
    "Luka Dončić": {7}                  # DAL
}

def convert_numpy_to_python(obj):
    """Recursively convert numpy types to Python types"""
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'item'):  # numpy scalar fallback
        return obj.item()
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    else:
        return obj

def calculate_nba_venge_score(
    player_id: int,
    player_name: str,
    opponent_team_id: int,
    revenge_games_data=None,
    non_revenge_games_data=None, 
    departure_method=None
) -> float:
    """
    Calculate comprehensive venge score from 1-10
    
    Args:
        player_id: Internal player ID
        player_name: Player's full name
        opponent_team_id: Internal opponent team ID  
        nba_api_player_id: NBA API player ID (for stats lookup)
        opponent_team_abbr: Team abbreviation for NBA API
        departure_method: (Traded, Waived, Free Agency)
    """
    total_games = get_total_games_played(player_id)
    games_with_opponent = get_total_games_played_for_team(player_id, opponent_team_id)
    is_first_time = check_first_revenge_game(player_id, opponent_team_id)
    comparison = None
    
    score = 1
    
    if total_games > 0:
        tenure_ratio = games_with_opponent / total_games  # 0.0 to 1.0
    else:
        tenure_ratio = 0

    # 1. TENURE IMPACT (0-3 points)
    if tenure_ratio > 0:
        if tenure_ratio >= 0.4:  # Spent 40%+ of career there
            tenure_score = 2.5 + (tenure_ratio - 0.4) * 0.83  # 2.5-3 points
        elif tenure_ratio >= 0.2:  # 20-40% of career
            tenure_score = 1.5 + (tenure_ratio - 0.2) * 5  # 1.5-2.5 points  
        elif tenure_ratio >= 0.1:  # 10-20% of career 
            tenure_score = 0.75 + (tenure_ratio - 0.1) * 7.5  # 0.75-1.5 points
        else:  # Less than 10% 
            tenure_score = tenure_ratio * 7.5  # 0-0.75 points
        
        score += tenure_score

    # 2. FORMER TEAM BONUS (1.5 points) 
    last_team_id = get_prev_team_id(player_id)
    if last_team_id == opponent_team_id:
        score += 1.5

    # 3. FIRST-TIME REVENGE (1 point)
    if is_first_time:
        score += 1

    # 4. ALL-STAR STATUS (1 point)
    if player_name in all_stars:
        score += 1

    # 5. NOTABLE REVENGE NARRATIVES (2 points)
    if player_name in notable_revenge_narratives and opponent_team_id in notable_revenge_narratives[player_name]:
        score += 2

    # 6. PERFORMANCE-BASED REVENGE FACTOR (0-2 points)
    if revenge_games_data is not None and non_revenge_games_data is not None:
        # Need minimum games for reliable comparison
        if len(revenge_games_data) >= 2 and len(non_revenge_games_data) >= 5:
            comparison = compare_stats(revenge_games_data, non_revenge_games_data)
            
            if "error" not in comparison:
                diffs = comparison['differences']
                
                # Calculate weighted revenge factor
                revenge_factor = (
                    diffs['points_diff'] * 1.0 +
                    diffs['rebounds_diff'] * 0.5 +
                    diffs['assists_diff'] * 0.7
                )
                
                # Convert to 0-2 point scale
                if revenge_factor >= 5:
                    performance_score = 2.0
                elif revenge_factor >= 3:
                    performance_score = 1.5
                elif revenge_factor >= 1:
                    performance_score = 1.0
                elif revenge_factor >= 0:
                    performance_score = 0.5
                else:
                    performance_score = 0.0
                
                score += performance_score
                print(f"Performance boost: +{performance_score:.1f} points")
    else: 
        print("error: need to recall nba_api")
    #7 DEPARTURE METHOD
    if departure_method in ['RELEASED', 'WAIVED', 'TRADED', 'TRADE']: 
        score += 1
    elif departure_method == 'F/A': 
        score += 0.5
    else: 
        score += 0.2
    # ensure minimum score of 1 and cap at 10
    final_score = max(1.0, min(score, 10.0))
    # return score and differentials
    return [round(final_score, 1), convert_numpy_to_python(comparison)]

def calculate_nfl_venge_score(
    player_data: dict,
    revenge_games_data=None,
    non_revenge_games_data=None
) -> list:
    from nfl_api.utils.player_stats import compare_nfl_stats

    player_name = player_data['name']
    position = player_data['position']
    usage_tier = player_data['usage_tier']
    pro_bowl_selections = player_data['pro_bowl_selections'] or 0
    all_pro_selections = player_data['all_pro_selections'] or 0
    draft_team = player_data['draft_team']
    opponent_team_id = player_data['opponent_team_id']
    total_games_played_for_team = player_data['total_games_played_for_team']
    most_recent_departure = player_data['departure_year'] or 0
    departure_method = player_data['departure_method']
    
    score = 0
    if departure_method in ['RELEASED', 'WAIVED', 'TRADED', 'TRADE']: 
        score += 1
        print(f'{player_name} was {departure_method}. Adding 1 point')
    elif departure_method == 'F/A': 
        score += 0.5
    else: 
        print('No departure method adding .2 points')
        score += 0.2
    comparison = None

    # 1. TENURE IMPACT (0-3.5 points)
    if total_games_played_for_team:  
        if total_games_played_for_team > 0:
            if total_games_played_for_team >= 48:  # 3+ full seasons
                tenure_score = 3.0 + min((total_games_played_for_team - 48) * 0.02, 0.5)  # 3.0-3.5 points
            elif total_games_played_for_team >= 32:  # 2-3 seasons
                tenure_score = 2.2 + (total_games_played_for_team - 32) * 0.05  # 2.2-3.0 points
            elif total_games_played_for_team >= 16:  # 1-2 seasons  
                tenure_score = 1.3 + (total_games_played_for_team - 16) * 0.056  # 1.3-2.2 points
            else:  # Less than 1 season
                tenure_score = 0.5 + total_games_played_for_team * 0.05  # 0.5-1.3 points
            
            score += tenure_score

    # 2. DRAFT TEAM BONUS (2.5 points) - Facing the team that drafted you
    if draft_team and str(opponent_team_id) in str(draft_team):
        score += 2.5

    # 3. USAGE TIER IMPACT (0-2 points) 
    usage_multipliers = {
        'STARTER': 2.0,     # Increased from 1.5
        'ROTATIONAL': 1.2,  # Increased from 1.0
        'BACKUP': 0.6,      # Increased from 0.5
        'INACTIVE': 0.2     # Increased from 0.0
    }
    score += usage_multipliers.get(usage_tier, 0.8)

    # 4. PRO BOWL/ALL-PRO STATUS (0-2.5 points) - Higher ceiling
    if all_pro_selections >= 3:
        score += 2.5  # Elite players
    elif all_pro_selections > 0:
        score += 2.0  # All-Pro players
    elif pro_bowl_selections >= 3:
        score += 1.5  # Multiple Pro Bowls
    elif pro_bowl_selections > 0:
        score += 1.0  # Pro Bowl players

    # 5. RECENCY BONUS (0-1.5 points) 
    current_year = 2024 
    years_since_departure = current_year - most_recent_departure
    if years_since_departure <= 1:
        score += 1.5  # Left very recently
    elif years_since_departure <= 2:
        score += 1.0  # Left recently
    elif years_since_departure <= 3:
        score += 0.5  # Still relatively recent

    # ALWAYS calculate regular stats if we have non-revenge data
    if non_revenge_games_data is not None and len(non_revenge_games_data) >= 1:
        # Create a comparison structure with just regular stats when revenge data is insufficient
        if revenge_games_data is None or len(revenge_games_data) < 1:
            # Call compare_nfl_stats with empty revenge data to get regular stats
            import pandas as pd
            empty_revenge_df = pd.DataFrame()
            comparison = compare_nfl_stats(empty_revenge_df, non_revenge_games_data, position)
        else:
            # Existing logic for when we have both datasets
            if len(revenge_games_data) >= 1 and len(non_revenge_games_data) >= 3:
                comparison = compare_nfl_stats(revenge_games_data, non_revenge_games_data, position)
                
                if "error" not in comparison:
                    diffs = comparison['differences']
                    
                    # Position-specific revenge factor calculation (same weights)
                    if position == 'QB':
                        revenge_factor = (
                            diffs['passing_yards_diff'] * 0.01 + 
                            diffs['passing_tds_diff'] * 0.5 +     
                            diffs['fantasy_points_diff'] * 0.1 -   
                            diffs['interceptions_diff'] * 0.5     
                        )
                    elif position == 'RB':
                        revenge_factor = (
                            diffs['rushing_yards_diff'] * 0.015 +    
                            diffs['rushing_tds_diff'] * 0.7 +        
                            diffs['receiving_yards_diff'] * 0.02 +   
                            diffs['fantasy_points_diff'] * 0.08      
                        )
                    elif position in ['WR', 'TE']:
                        revenge_factor = (
                            diffs['receiving_yards_diff'] * 0.012 +  
                            diffs['receiving_tds_diff'] * 0.8 +      
                            diffs['receptions_diff'] * 0.2 +         
                            diffs['fantasy_points_diff'] * 0.08      
                        )
                    else:
                        revenge_factor = 0
                    
                    # Expanded 0-3 point scale
                    if revenge_factor >= 4:
                        performance_score = 3.0
                    elif revenge_factor >= 3:
                        performance_score = 2.5
                    elif revenge_factor >= 2:
                        performance_score = 2.0
                    elif revenge_factor >= 1:
                        performance_score = 1.5
                    elif revenge_factor >= 0:
                        performance_score = 0.8
                    else:
                        performance_score = 0.0
                    
                    score += performance_score
                    print(f"Performance boost: +{performance_score:.1f} points (revenge factor: {revenge_factor:.2f})")
    if usage_tier == 'BACKUP' and position == 'QB': score -= 2

    final_score = max(2.0, min(score, 10.0)) 
    
    return [round(final_score, 1), comparison]