from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 
    matchups = [
        ["9", "28"],   # Packers at Commanders (Thursday)
        ["5", "33"],   # Browns at Ravens
        ["30", "4"],   # Jaguars at Bengals
        ["19", "6"],   # Giants at Cowboys
        ["3", "8"],    # Bears at Lions
        ["17", "15"],  # Patriots at Dolphins
        ["25", "18"],  # 49ers at Saints
        ["2", "20"],   # Bills at Jets
        ["26", "23"],  # Seahawks at Steelers
        ["14", "10"],  # Rams at Titans
        ["29", "22"],  # Panthers at Cardinals
        ["7", "11"],   # Broncos at Colts
        ["21", "12"],  # Eagles at Chiefs
        ["1", "16"],   # Falcons at Vikings
        ["27", "34"],  # Buccaneers at Texans (Monday 7PM)
        ["24", "13"]   # Chargers at Raiders (Monday 10PM)
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