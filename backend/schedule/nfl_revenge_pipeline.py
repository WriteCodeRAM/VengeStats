from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
    ["14", "26"],  # LAR @ SEA  (TNF)
    ["21", "28"],  # PHI @ WAS
    ["9", "3"],    # GB @ CHI
    ["27", "29"],  # TB @ CAR
    ["2", "5"],    # BUF @ CLE
    ["24", "6"],   # LAC @ DAL
    ["20", "18"],  # NYJ @ NO
    ["16", "19"],  # MIN @ NYG
    ["12", "10"],  # KC @ TEN
    ["4", "15"],   # CIN @ MIA
    ["1", "22"],   # ATL @ ARI
    ["30", "7"],   # JAX @ DEN
    ["23", "8"],   # PIT @ DET
    ["13", "34"],  # LV @ HOU
    ["17", "33"],  # NE @ BAL  (SNF)
    ["25", "11"],  # SF @ IND  (MNF)
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