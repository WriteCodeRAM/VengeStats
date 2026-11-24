from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 12: Full slate (Wed Nov 25 - Mon Nov 30, ET)
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    # No teams on bye
    matchups = [
        # Wednesday Nov 25
        ["9",  "14"],  # GB  @ LAR
        # Thursday Nov 26 (Thanksgiving)
        ["3",   "8"],  # CHI @ DET
        ["21",  "6"],  # PHI @ DAL
        ["12",  "2"],  # KC  @ BUF  (Thursday Night Football)
        # Friday Nov 27
        ["7",  "23"],  # DEN @ PIT
        # Sunday Nov 29
        ["18",  "4"],  # NO  @ CIN
        ["19", "11"],  # NYG @ IND
        ["20", "15"],  # NYJ @ MIA
        ["1",  "16"],  # ATL @ MIN
        ["10", "30"],  # TEN @ JAX
        ["33", "34"],  # BAL @ HOU
        ["17", "24"],  # NE  @ LAC
        ["28", "22"],  # WSH @ ARI
        ["26", "25"],  # SEA @ SF  (Sunday Night Football)
        # Sunday Night Nov 29 / Monday Nov 30
        ["13",  "5"],  # LV  @ CLE
        ["29", "27"],  # CAR @ TB  (Monday Night Football)
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