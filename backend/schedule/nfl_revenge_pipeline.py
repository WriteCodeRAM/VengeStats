from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 2 — Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    matchups = [
        # Thursday Sept 17
        [ "8",  "2"],  # DET @ BUF  (Thursday Night Football)
        # Sunday Sept 20
        [ "3",  "1"],  # CAR @ ATL
        ["16", "18"],  # MIN @ CHI
        ["21", "10"],  # PHI @ TEN
        ["23", "17"],  # PIT @ NE
        [ "9", "20"],  # GB  @ NYJ
        [ "5", "27"],  # CLE @ TB
        ["18", "33"],  # NO  @ BAL
        [ "4", "34"],  # CIN @ HOU
        ["30",  "7"],  # JAX @ DEN
        ["13", "24"],  # LV  @ LAC
        ["28",  "6"],  # WSH @ DAL
        ["26", "22"],  # SEA @ ARI
        ["15", "25"],  # MIA @ SF
        ["11", "12"],  # IND @ KC
        # Monday Sept 21
        ["19", "14"],  # NYG @ LAR  (Monday Night Football)
    ]

    revenge_players = get_nfl_revenge_games(matchups)
    
    for player in revenge_players:
        nfl_id = player["nfl_data_id"]
        opp_abbr = NFL_TEAM_ID_TO_ABBR[int(player["opponent_team_id"])]

        # Use departure_year if available; fall back to season_start so we don't
        # default to the current year (which has no data yet)
        departure = player["departure_year"] or player["season_start"] or 2020

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