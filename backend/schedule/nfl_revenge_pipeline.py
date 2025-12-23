from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["6", "28"],    # DAL @ WAS
        ["8", "16"],    # DET @ MIN
        ["7", "12"],    # DEN @ KC
        ["34", "24"],   # HOU @ LAC
        ["33", "9"],    # BAL @ GB
        ["26", "29"],   # SEA @ CAR
        ["22", "4"],    # ARI @ CIN
        ["23", "5"],    # PIT @ CLE
        ["30", "11"],   # JAX @ IND
        ["27", "15"],   # TB @ MIA
        ["17", "20"],   # NE @ NYJ
        ["18", "10"],   # NO @ TEN
        ["19", "13"],   # NYG @ LV
        ["21", "2"],    # PHI @ BUF
        ["3", "25"],    # CHI @ SF  (SNF)
        ["14", "1"],    # LAR @ ATL (MNF)
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