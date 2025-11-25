from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
    ["9", "8"],     # GB @ DET (Thu 1:00 PM)
    ["12", "6"],    # KC @ DAL (Thu 4:30 PM)
    ["4", "33"],    # CIN @ BAL (Thu 8:20 PM)
    ["3", "21"],    # CHI @ PHI (Fri 3:00 PM)
    ["25", "5"],    # SF @ CLE (Sun 1:00 PM)
    ["30", "10"],   # JAX @ TEN (Sun 1:00 PM)
    ["34", "11"],   # HOU @ IND (Sun 1:00 PM)
    ["18", "15"],   # NO @ MIA (Sun 1:00 PM)
    ["1", "19"],    # ATL @ NYG (Sun 1:00 PM)
    ["22", "27"],   # ARI @ TB (Sun 1:00 PM)
    ["14", "29"],   # LAR @ CAR (Sun 1:00 PM)
    ["16", "26"],   # MIN @ SEA (Sun 4:05 PM)
    ["2", "23"],    # BUF @ PIT (Sun 4:25 PM)
    ["13", "24"],   # LV @ LAC (Sun 4:25 PM)
    ["7", "28"],    # DEN @ WAS (Sun 8:20 PM)
    ["20", "17"],   # NYJ @ NE (Mon 8:15 PM)
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