from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 6 — Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    # DET (8), MIA (15), MIN (16), CIN (4) on bye
    matchups = [
        # Thursday Oct 15
        ["26",  "7"],  # SEA @ DEN  (Thursday Night Football)
        # Sunday Oct 18
        ["34", "30"],  # HOU @ JAX  (NFL London)
        [ "3",  "1"],  # CHI @ ATL
        ["33",  "5"],  # BAL @ CLE
        ["10", "11"],  # TEN @ IND
        ["20", "17"],  # NYJ @ NE
        ["18", "19"],  # NO  @ NYG
        ["29", "21"],  # CAR @ PHI
        ["23", "27"],  # PIT @ TB
        ["22", "14"],  # ARI @ LAR
        ["24", "12"],  # LAC @ KC
        [ "2", "13"],  # BUF @ LV
        [ "6",  "9"],  # DAL @ GB
        # Monday Oct 19
        ["28", "25"],  # WSH @ SF  (Monday Night Football)
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