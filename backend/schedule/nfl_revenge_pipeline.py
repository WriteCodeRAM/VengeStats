from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["26", "22"],  # Seahawks at Cardinals (Thursday)
        ["16", "23"],  # Vikings at Steelers (Sunday 9:30 AM)
        ["28", "1"],   # Commanders at Falcons
        ["18", "2"],   # Saints at Bills
        ["5", "8"],    # Browns at Lions
        ["10", "34"],  # Titans at Texans
        ["29", "17"],  # Panthers at Patriots
        ["24", "19"],  # Chargers at Giants
        ["21", "27"],  # Eagles at Buccaneers
        ["11", "14"],  # Colts at Rams
        ["30", "25"],  # Jaguars at 49ers
        ["33", "12"],  # Ravens at Chiefs
        ["3", "13"],   # Bears at Raiders
        ["9", "6"],    # Packers at Cowboys (Sunday Night)
        ["20", "15"],  # Jets at Dolphins (Monday 7:15 PM)
        ["4", "7"]     # Bengals at Broncos (Monday 8:15 PM)
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