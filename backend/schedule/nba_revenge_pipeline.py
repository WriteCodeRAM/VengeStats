from backend.schedule.get_schedule import get_nba_schedule, get_team_ids
from backend.db.queries.revenge_games import get_revenge_games
from backend.scrapers.injury_scrapers import get_nba_injuries
from backend.db.venge_data import calculate_venge_score
from backend.nba_api.utils.data_fetcher import get_fair_comparison
from backend.nba_api.utils.player_utils import search_player
from backend.db.queries.teams import team_id_to_abbr

def get_daily_revenge_matchups():
    # revenge_games = get_nba_schedule()
    revenge_games = get_revenge_games([[16,10]]) 
    updated_games = get_nba_injuries(revenge_games)
    
    enriched_games = []
    
    for player in updated_games:
        if player[2] == "Out":  # Skip injured players
            continue
            
        nba_api_id = search_player(player[0])["id"]
        former_team_abbr = team_id_to_abbr[player[4]]
        
        revenge_data, nonrevenge_data = get_fair_comparison(nba_api_id, former_team_abbr, player[6])
        revenge_score = calculate_venge_score(player[3], player[0], player[4], revenge_data, nonrevenge_data)
        
        # Calculate W/L record from revenge_data
        wins = len(revenge_data[revenge_data['WL'] == 'W']) if not revenge_data.empty else 0
        losses = len(revenge_data[revenge_data['WL'] == 'L']) if not revenge_data.empty else 0
        total_games = len(revenge_data) if not revenge_data.empty else 0
        
        # Get departure year
        departure_year = player[6].year if player[6] else None
        
        # enriched player data for tweets 
        enriched_player = {
            'name': player[0],
            'former_team_name': player[1],
            'injury_status': player[2],
            'player_id': player[3],
            'opponent_team_id': player[4],
            'venge_score': revenge_score,
            'departure_date': player[6],
            'departure_year': departure_year,
            'wins': wins,
            'losses': losses,
            'total_games': total_games,
            'record': f"{wins}-{losses}",
            'former_team_abbr': former_team_abbr
        }
        
        enriched_games.append(enriched_player)
    
    return enriched_games

# print(get_daily_revenge_matchups())