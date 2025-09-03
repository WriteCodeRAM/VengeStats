from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 
    matchups = [
    ["6", "21"],    # Dallas Cowboys at Philadelphia Eagles (Thursday)
    ["12", "24"],   # Kansas City Chiefs at Los Angeles Chargers (Friday, Brazil)
    ["19", "28"],   # New York Giants at Washington Commanders (Sunday)
    ["23", "20"],   # Pittsburgh Steelers at New York Jets (Sunday)
    ["15", "11"],   # Miami Dolphins at Indianapolis Colts (Sunday)
    ["22", "18"],   # Arizona Cardinals at New Orleans Saints (Sunday)
    ["29", "30"],   # Carolina Panthers at Jacksonville Jaguars (Sunday)
    ["13", "17"],   # Las Vegas Raiders at New England Patriots (Sunday)
    ["27", "1"],    # Tampa Bay Buccaneers at Atlanta Falcons (Sunday)
    ["4", "5"],     # Cincinnati Bengals at Cleveland Browns (Sunday)
    ["25", "26"],   # San Francisco 49ers at Seattle Seahawks (Sunday)
    ["10", "7"],    # Tennessee Titans at Denver Broncos (Sunday)
    ["14", "34"],   # Los Angeles Rams at Houston Texans (Sunday)
    ["9", "8"],     # Green Bay Packers at Detroit Lions (Sunday)
    ["33", "2"],    # Baltimore Ravens at Buffalo Bills (Sunday Night)
    ["16", "3"]     # Minnesota Vikings at Chicago Bears (Monday Night)
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