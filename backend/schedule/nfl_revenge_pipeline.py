from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["23", "4"],   # Steelers at Bengals (Thursday)
        ["14", "30"],  # Rams at Jaguars (Sunday 9:30 AM)
        ["18", "3"],   # Saints at Bears
        ["15", "5"],   # Dolphins at Browns
        ["13", "12"],  # Raiders at Chiefs
        ["21", "16"],  # Eagles at Vikings
        ["29", "20"],  # Panthers at Jets
        ["17", "10"],  # Patriots at Titans
        ["19", "7"],   # Giants at Broncos
        ["11", "24"],  # Colts at Chargers
        ["9", "22"],   # Packers at Cardinals
        ["28", "6"],   # Commanders at Cowboys
        ["1", "25"],   # Falcons at 49ers (Sunday Night)
        ["27", "8"],   # Buccaneers at Lions (Monday 7 PM)
        ["34", "26"],  # Texans at Seahawks (Monday 10 PM)
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