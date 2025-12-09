from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
    ["1", "27"],   # ATL @ TB (TNF)
    ["5", "3"],    # CLE @ CHI
    ["33", "4"],   # BAL @ CIN
    ["22", "34"],  # ARI @ HOU
    ["20", "30"],  # NYJ @ JAX
    ["24", "12"],  # LAC @ KC
    ["2", "17"],   # BUF @ NE
    ["28", "19"],  # WAS @ NYG
    ["13", "21"],  # LV @ PHI
    ["9", "7"],    # GB @ DEN
    ["8", "14"],   # DET @ LAR
    ["29", "18"],  # CAR @ NO
    ["11", "26"],  # IND @ SEA
    ["10", "25"],  # TEN @ SF
    ["16", "6"],   # MIN @ DAL (SNF)
    ["15", "23"],  # MIA @ PIT (MNF)
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