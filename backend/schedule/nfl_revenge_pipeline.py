from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 11: Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    # ATL (1), CLE (5), GB (9), LAR (14), NE (17), SEA (26) on bye
    matchups = [
        # Thursday Nov 19
        ["11", "34"],  # IND @ HOU  (Thursday Night Football)
        # Sunday Nov 22
        ["15",  "2"],  # MIA @ BUF
        ["18",  "3"],  # NO  @ CHI
        ["10",  "6"],  # TEN @ DAL
        ["27",  "8"],  # TB  @ DET
        ["22", "12"],  # ARI @ KC
        ["23", "21"],  # PIT @ PHI
        ["33", "29"],  # BAL @ CAR
        ["20", "24"],  # NYJ @ LAC
        ["13",  "7"],  # LV  @ DEN
        ["30", "19"],  # JAX @ NYG
        # Sunday Night Nov 22
        ["16", "25"],  # MIN @ SF  (Sunday Night Football)
        # Monday Nov 23
        [ "4", "28"],  # CIN @ WSH  (Monday Night Football)
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