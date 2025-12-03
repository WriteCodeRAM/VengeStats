from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
    ["6", "8"],     # DAL @ DET (TNF)
    ["26", "1"],    # SEA @ ATL
    ["4", "2"],     # CIN @ BUF
    ["10", "5"],    # TEN @ CLE
    ["28", "16"],   # WAS @ MIN
    ["15", "20"],   # MIA @ NYJ
    ["18", "27"],   # NO @ TB
    ["11", "30"],   # IND @ JAX
    ["23", "33"],   # PIT @ BAL
    ["7", "13"],    # DEN @ LV
    ["3", "9"],     # CHI @ GB
    ["14", "22"],   # LAR @ ARI
    ["34", "12"],   # HOU @ KC
    ["21", "24"],   # PHI @ LAC (MNF)
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