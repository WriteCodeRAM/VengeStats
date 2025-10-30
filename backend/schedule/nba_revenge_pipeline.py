from schedule.get_schedule import get_nba_schedule, get_team_ids
from db.queries.revenge_games import get_nba_revenge_games
from scrapers.injury_scrapers import get_nba_injuries
from db.venge_data import calculate_nba_venge_score
from nba_utils.utils.data_fetcher import get_fair_comparison
from nba_utils.utils.player_utils import search_player
from db.queries.nba.teams import team_id_to_abbr, team_id_to_full_name, get_current_team_id
from db.queries.nba.players import get_total_games_played_for_team, get_player_career_history
import time
from typing import List
from schemas.revenge_types import EnrichedNBARevengePlayer

def get_daily_revenge_matchups() -> List[EnrichedNBARevengePlayer]:
    # revenge_games = get_nba_schedule()
    revenge_games = get_nba_revenge_games([
    [22, 4],   # ORL @ CHA
    [10, 17],  # GSW @ MIL
    [30, 21],  # WAS @ OKC
    [16, 27],  # MIA @ SAS
])
    updated_games = get_nba_injuries(revenge_games)
    
    enriched_games = []
    
    # player [0] player name
    # player[1] former team full name
    # player[2] injury status
    # player[3] = db player id 
    # player[4] opponent team id 
    for player in updated_games:
        if player[2] == "Out":  # Skip injured players
            continue

        
        time.sleep(5)
        current_team_id = get_current_team_id(player[3])
        nba_api_id = search_player(player[0])["id"]
        former_team_abbr = team_id_to_abbr[player[4]]
        former_team_name = team_id_to_full_name[player[4]]
        current_team_name = team_id_to_full_name[current_team_id]
        current_team_abrev = team_id_to_abbr[current_team_id]
        
        revenge_data, nonrevenge_data = get_fair_comparison(nba_api_id, former_team_abbr, player[6])
        revenge_score, differentials = calculate_nba_venge_score(player[3], player[0], player[4], revenge_data, nonrevenge_data, player[7])
        


        #player[3] = db player id 
        #player[4] opponent team id 
        # Calculate W/L record from revenge_data
        wins = len(revenge_data[revenge_data['WL'] == 'W']) if not revenge_data.empty else 0
        losses = len(revenge_data[revenge_data['WL'] == 'L']) if not revenge_data.empty else 0
        total_revenge_games = len(revenge_data) if not revenge_data.empty else 0
        total_games_played_for_opp = get_total_games_played_for_team(player[3], player[4])
        # Get departure year
        departure_year = player[6].year if player[6] else None

        # get career history 
        history = get_player_career_history(player[3])
        
        # enriched player data for tweets 
        enriched_player = {
            'name': player[0],
            'former_team_name': player[1],
            'former_team_abbr': former_team_name,
            'current_team_name': current_team_name,
            'current_team_abbr': current_team_abrev,
            'injury_status': player[2],
            'player_id': player[3],
            'nba_api_id': nba_api_id,
            'opponent_team_id': player[4],
            'venge_score': revenge_score,
            'departure_date': player[6],
            'departure_year': departure_year,
            'total_games': total_games_played_for_opp,
            'wins': wins,
            'losses': losses,
            'total_revenge_games': total_revenge_games,
            'record': f"{wins}-{losses}",
            'former_team_abbr': former_team_abbr,
            'differentials': differentials, 
            'history': history
        }
        
        enriched_games.append(enriched_player)
    
    return enriched_games