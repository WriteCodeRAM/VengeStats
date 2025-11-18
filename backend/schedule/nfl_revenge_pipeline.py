from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = week12_matchups = [
    ["2", "34"],   # BUF @ HOU  (TNF)
    ["20", "33"],  # NYJ @ BAL
    ["23", "3"],   # PIT @ CHI
    ["17", "4"],   # NE @ CIN
    ["19", "8"],   # NYG @ DET
    ["16", "9"],   # MIN @ GB
    ["11", "12"],  # IND @ KC
    ["26", "10"],  # SEA @ TEN
    ["30", "22"],  # JAX @ ARI
    ["5", "13"],   # CLE @ LV
    ["21", "6"],   # PHI @ DAL
    ["1", "18"],   # ATL @ NO
    ["27", "14"],  # TB @ LAR  (SNF)
    ["29", "25"],  # CAR @ SF  (MNF)
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