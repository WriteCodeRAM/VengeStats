from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 8: Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    # NO (18), NYG (19), SF (25), HOU (34) on bye
    matchups = [
        # Thursday Oct 29
        ["29",  "9"],  # CAR @ GB  (Thursday Night Football)
        # Sunday Nov 1
        ["33",  "2"],  # BAL @ BUF
        ["10",  "4"],  # TEN @ CIN
        ["22",  "6"],  # ARI @ DAL
        ["16",  "8"],  # MIN @ DET
        ["13", "20"],  # LV  @ NYJ
        [ "5", "23"],  # CLE @ PIT
        [ "1", "27"],  # ATL @ TB
        ["11", "30"],  # IND @ JAX
        ["24", "14"],  # LAC @ LAR
        ["12",  "7"],  # KC  @ DEN
        ["17", "15"],  # NE  @ MIA
        # Sunday Night Nov 1
        ["21", "28"],  # PHI @ WSH  (Sunday Night Football)
        # Monday Nov 2
        [ "3", "26"],  # CHI @ SEA  (Monday Night Football)
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