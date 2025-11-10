from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
    ["20", "17"],  # NYJ @ NE
    ["28", "15"],  # WAS @ MIA
    ["29", "1"],   # CAR @ ATL
    ["27", "2"],   # TB @ BUF
    ["34", "10"],  # HOU @ TEN
    ["3", "16"],   # CHI @ MIN
    ["9", "19"],   # GB @ NYG
    ["4", "23"],   # CIN @ PIT
    ["24", "30"],  # LAC @ JAX
    ["26", "14"],  # SEA @ LAR
    ["25", "22"],  # SF @ ARI
    ["33", "5"],   # BAL @ CLE
    ["12", "7"],   # KC @ DEN
    ["8", "21"],   # DET @ PHI
    ["6", "13"],   # DAL @ LV
]

    revenge_players = get_nfl_revenge_games(matchups)
    
    for player in revenge_players: 
        nfl_id = player["nfl_data_id"]
        opp_abbr = NFL_TEAM_ID_TO_ABBR[int(player["opponent_team_id"])]
        departure = player["departure_year"]
        
        revenge_games_df, non_revenge_games_df, wins, losses, total_revenge_games = get_all_nfl_player_data(
            nfl_id, opp_abbr, departure
        )
            
        player["record"] = f"{wins}-{losses}"
        player["total_revenge_games"] = total_revenge_games
        
        # Calculate venge score with the data we already have
        venge_score, differentials = calculate_nfl_venge_score(
            player, revenge_games_df, non_revenge_games_df
        )
        
        player["revenge_score"] = venge_score
        player["differentials"] = differentials

    return revenge_players