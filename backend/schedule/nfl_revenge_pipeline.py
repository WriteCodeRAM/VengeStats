from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["13", "7"],   # LV @ DEN (Thursday)
        ["1",  "11"],  # ATL @ IND (Berlin)
        ["19", "3"],   # NYG @ CHI
        ["2",  "15"],  # BUF @ MIA
        ["33", "16"],  # BAL @ MIN
        ["5",  "20"],  # CLE @ NYJ
        ["17", "27"],  # NE @ TB
        ["18", "29"],  # NO @ CAR
        ["30", "34"],  # JAX @ HOU
        ["22", "26"],  # ARI @ SEA
        ["14", "25"],  # LAR @ SF
        ["8",  "28"],  # DET @ WAS
        ["23", "24"],  # PIT @ LAC (SNF)
        ["21", "9"],   # PHI @ GB (MNF)
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