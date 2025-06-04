from backend.db.queries.players import get_total_games_played, get_total_games_played_for_team
from backend.db.queries.revenge_games import check_first_revenge_game
from backend.db.queries.teams import get_prev_team_id
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
) -> float:
    total_games = get_total_games_played(player_id)
    games_with_opponent = get_total_games_played_for_team(player_id, opponent_team_id)
    is_first_time = check_first_revenge_game(player_id, opponent_team_id)
    
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

    # 5. The drama and storylines 
    if player_name in notable_revenge_narratives and opponent_team_id in notable_revenge_narratives[player_name]:
        score += 2

    # Capped at 10
    return round(min(score, 10.0), 1)

print(calculate_venge_score(332, "Jalen Brunson", 7))