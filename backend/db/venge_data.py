from backend.db.queries.players import get_total_games_played, get_total_games_played_for_team
from backend.db.queries.revenge_games import check_first_revenge_game
from backend.db.queries.teams import get_prev_team_id
from backend.nba_api.utils.data_fetcher import compare_stats

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
    "Kevin Durant": [10, 21],           # GSW, OKC
    "Kyrie Irving": [2],                # BOS
    "LeBron James": [6, 16],            # CLE, MIA
    "Jimmy Butler": [18, 23, 16],       # MIN, PHI, MIA
    "Paul George": [12],                # IND
    "Chris Paul": [11, 13],             # HOU, LAC
    "James Harden": [11, 23],           # HOU, PHI
    "Ben Simmons": [23],                # PHI
    "Russell Westbrook": [21, 14],      # OKC, LAL
    "Jrue Holiday": [17],               # MIL
    "Marcus Smart": [2],                # BOS
    "Luka Dončić": [7]                  # DAL
}

def calculate_venge_score(
    player_id: int,
    player_name: str,
    opponent_team_id: int,
    revenge_games_data=None,
    non_revenge_games_data=None
) -> float:
    """
    Calculate comprehensive venge score from 1-10
    
    Args:
        player_id: Internal player ID
        player_name: Player's full name
        opponent_team_id: Internal opponent team ID  
        nba_api_player_id: NBA API player ID (for stats lookup)
        opponent_team_abbr: Team abbreviation for NBA API
        departure_date: When player left the team (YYYY-MM-DD)
    """
    total_games = get_total_games_played(player_id)
    games_with_opponent = get_total_games_played_for_team(player_id, opponent_team_id)
    is_first_time = check_first_revenge_game(player_id, opponent_team_id)

    print(f"{player_name}: total games = {total_games}, games played for opps = {games_with_opponent}")
    
    score = 0
    
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

    # 2. FORMER TEAM BONUS (2.5 points) 
    last_team_id = get_prev_team_id(player_id)
    if last_team_id == opponent_team_id:
        score += 2.5

    # 3. FIRST-TIME REVENGE (1.5 points)
    if is_first_time:
        score += 1.5

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
        # recall the api 
        print("error: need to recall nba_api")

    # Ensure minimum score of 1 and cap at 10
    final_score = max(1.0, min(score, 10.0))
    return round(final_score, 1)

def get_venge_score_breakdown(
    player_id: int,
    player_name: str, 
    opponent_team_id: int,
    nba_api_player_id: int = None,
    opponent_team_abbr: str = None,
    departure_date: str = None
) -> dict:
    """
    Get detailed breakdown of venge score components
    """
    total_games = get_total_games_played(player_id)
    games_with_opponent = get_total_games_played_for_team(player_id, opponent_team_id)
    is_first_time = check_first_revenge_game(player_id, opponent_team_id)
    
    breakdown = {
        "tenure_score": 0,
        "former_team_bonus": 0,
        "first_time_bonus": 0,
        "all_star_bonus": 0,
        "narrative_bonus": 0,
        "performance_bonus": 0,
        "total_score": 0
    }
    
    
    final_score = calculate_venge_score(
        player_id, player_name, opponent_team_id,
        nba_api_player_id, opponent_team_abbr, departure_date
    )
    
    breakdown["total_score"] = final_score
    return breakdown