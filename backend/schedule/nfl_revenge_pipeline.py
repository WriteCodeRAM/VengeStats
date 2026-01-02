from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["29", "27"],  # CAR @ TB   (Sat)
        ["26", "25"],  # SEA @ SF   (Sat)
        ["18", "1"],   # NO @ ATL
        ["5", "4"],    # CLE @ CIN
        ["9", "16"],   # GB @ MIN
        ["6", "20"],   # DAL @ NYJ
        ["10", "30"],  # TEN @ JAX
        ["11", "34"],  # IND @ HOU
        ["20", "2"],   # NYJ @ BUF
        ["8", "3"],    # DET @ CHI
        ["24", "7"],   # LAC @ DEN
        ["12", "13"],  # KC @ LV
        ["22", "14"],  # ARI @ LAR
        ["15", "17"],  # MIA @ NE
        ["28", "21"],  # WAS @ PHI
        ["33", "23"],  # BAL @ PIT  (SNF)
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