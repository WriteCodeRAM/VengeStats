from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 10: Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    # CHI (3), DEN (7), PHI (21), TB (27) on bye
    matchups = [
        # Thursday Nov 12
        ["28", "19"],  # WSH @ NYG  (Thursday Night Football)
        # Sunday Nov 15
        ["17",  "8"],  # NE  @ DET
        ["12",  "1"],  # KC  @ ATL
        ["34",  "5"],  # HOU @ CLE
        ["16",  "9"],  # MIN @ GB
        ["30", "10"],  # JAX @ TEN
        ["15", "11"],  # MIA @ IND
        ["29", "18"],  # CAR @ NO
        [ "2", "20"],  # BUF @ NYJ
        ["26", "13"],  # SEA @ LV
        ["14", "22"],  # LAR @ ARI
        ["25",  "6"],  # SF  @ DAL
        # Sunday Night Nov 15
        ["23",  "4"],  # PIT @ CIN  (Sunday Night Football)
        # Monday Nov 16
        ["24", "33"],  # LAC @ BAL  (Monday Night Football)
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