from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["25", "14"],  # 49ers at Rams (Thursday)
        ["16", "5"],   # Vikings at Browns (Sunday 9:30 AM)
        ["34", "33"],  # Texans at Ravens
        ["15", "29"],  # Dolphins at Panthers
        ["13", "11"],  # Raiders at Colts
        ["19", "18"],  # Giants at Saints
        ["6", "20"],   # Cowboys at Jets
        ["7", "21"],   # Broncos at Eagles
        ["10", "22"],  # Titans at Cardinals
        ["27", "26"],  # Buccaneers at Seahawks
        ["8", "4"],    # Lions at Bengals
        ["28", "24"],  # Commanders at Chargers
        ["17", "2"],   # Patriots at Bills (Sunday Night)
        ["12", "30"]   # Chiefs at Jaguars (Monday Night)
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
        if nfl_id == '00-0035100': 
            venge_score += 2
        player["revenge_score"] = venge_score
        player["differentials"] = differentials

    return revenge_players