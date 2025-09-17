from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["15", "2"],   # Dolphins at Bills (Thursday)
        ["1", "29"],   # Falcons at Panthers
        ["9", "5"],    # Packers at Browns
        ["34", "30"],  # Texans at Jaguars
        ["4", "16"],   # Bengals at Vikings
        ["23", "17"],  # Steelers at Patriots
        ["14", "21"],  # Rams at Eagles
        ["20", "27"],  # Jets at Buccaneers
        ["11", "10"],  # Colts at Titans
        ["13", "28"],  # Raiders at Commanders
        ["7", "24"],   # Broncos at Chargers
        ["18", "26"],  # Saints at Seahawks
        ["6", "3"],    # Cowboys at Bears
        ["22", "25"],  # Cardinals at 49ers
        ["12", "19"],  # Chiefs at Giants (Sunday Night)
        ["8", "33"]    # Lions at Ravens (Monday Night)
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