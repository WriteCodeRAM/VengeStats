from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 4 — Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    matchups = [
        # Thursday Oct 1
        ["23",  "5"],  # PIT @ CLE  (Thursday Night Football)
        # Sunday Oct 4
        ["11", "28"],  # IND @ WSH
        ["17",  "2"],  # NE  @ BUF
        ["20",  "3"],  # NYJ @ CHI
        ["30",  "4"],  # JAX @ CIN
        ["22", "19"],  # ARI @ NYG
        ["14", "21"],  # LAR @ PHI
        [ "9", "27"],  # GB  @ TB
        ["10", "33"],  # TEN @ BAL
        [ "6", "34"],  # DAL @ HOU
        ["15", "16"],  # MIA @ MIN
        ["12", "13"],  # KC  @ LV
        [ "7", "25"],  # DEN @ SF
        ["24", "26"],  # LAC @ SEA
        # Sunday Night Oct 4
        [ "8", "29"],  # DET @ CAR
        # Monday Oct 6
        [ "1", "18"],  # ATL @ NO  (Monday Night Football)
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