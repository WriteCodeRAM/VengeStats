from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["16", "24"],  # Vikings at Chargers (Thu)
        ["15", "1"],   # Dolphins at Falcons
        ["3", "33"],   # Bears at Ravens
        ["2", "29"],   # Bills at Panthers
        ["20", "4"],   # Jets at Bengals
        ["25", "34"],  # 49ers at Texans
        ["5", "17"],   # Browns at Patriots
        ["19", "21"],  # Giants at Eagles
        ["27", "18"],  # Buccaneers at Saints
        ["6", "7"],    # Cowboys at Broncos
        ["10", "11"],  # Titans at Colts
        ["9", "23"],   # Packers at Steelers (SNF)
        ["28", "12"],  # Commanders at Chiefs (MNF)
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