from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 3 — Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    matchups = [
        # Friday Sept 25
        [ "1",  "9"],  # ATL @ GB   (Friday Night Football)
        # Sunday Sept 27
        ["24",  "2"],  # LAC @ BUF
        ["29",  "5"],  # CAR @ CLE
        ["20",  "8"],  # NYJ @ DET
        ["34", "11"],  # HOU @ IND
        ["12", "15"],  # KC  @ MIA
        ["10", "19"],  # TEN @ NYG
        [ "4", "23"],  # CIN @ PIT
        ["26", "28"],  # SEA @ WSH
        ["17", "30"],  # NE  @ JAX
        ["22", "25"],  # ARI @ SF
        ["16", "27"],  # MIN @ TB
        ["33",  "6"],  # BAL @ DAL
        ["13", "18"],  # LV  @ NO
        # Sunday Night Sept 27
        ["14",  "7"],  # LAR @ DEN
        # Monday Sept 28... wait, ESPN shows PHI@CHI on Sept 29
        ["21",  "3"],  # PHI @ CHI  (Monday Night Football)
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