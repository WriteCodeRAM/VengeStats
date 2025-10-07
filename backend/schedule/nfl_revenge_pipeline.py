from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    matchups = [
        ["19", "21"],  # Giants at Eagles (Thursday)
        ["20", "7"],   # Jets at Broncos (London Game, Sunday 9:30 AM)
        ["33", "14"],  # Ravens at Rams
        ["29", "6"],   # Panthers at Cowboys
        ["22", "11"],  # Cardinals at Colts
        ["26", "30"],  # Seahawks at Jaguars
        ["15", "24"],  # Dolphins at Chargers
        ["5", "23"],   # Browns at Steelers
        ["18", "17"],  # Saints at Patriots
        ["10", "13"],  # Titans at Raiders (4:05 PM)
        ["25", "27"],  # 49ers at Buccaneers (4:25 PM)
        ["4", "9"],    # Bengals at Packers (4:25 PM)
        ["8", "12"],   # Lions at Chiefs (Sunday Night)
        ["2", "1"]     # Bills at Falcons (Monday Night)
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