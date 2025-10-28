from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["33", "15"],  # BAL @ MIA
        ["3", "4"],    # CHI @ CIN
        ["16", "8"],   # MIN @ DET
        ["29", "9"],   # CAR @ GB
        ["24", "10"],  # LAC @ TEN
        ["1", "17"],   # ATL @ NE
        ["25", "19"],  # SF @ NYG
        ["11", "23"],  # IND @ PIT
        ["7", "34"],   # DEN @ HOU
        ["30", "13"],  # JAX @ LV
        ["18", "14"],  # NO @ LAR
        ["12", "2"],   # KC @ BUF
        ["26", "28"],  # SEA @ WAS
        ["22", "6"],   # ARI @ DAL
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