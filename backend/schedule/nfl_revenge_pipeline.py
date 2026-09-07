from db.queries.revenge_games import get_nfl_revenge_games
from db.venge_data import calculate_nfl_venge_score
from db.queries.nfl.teams import NFL_TEAM_ID_TO_ABBR
from nfl_api.utils.player_stats import get_all_nfl_player_data

def get_weekly_revenge_matchups(): 

    # NFL 2026 Week 1 — Full slate
    # Format: [away_team_id, home_team_id]  (IDs match ESPN/NFL Data Py)
    matchups = [
        # Thursday Sept 9
        ["17", "26"],  # NE @ SEA  (Thursday Night opener)
        # Saturday Sept 10
        ["25", "14"],  # SF @ LAR
        # Sunday Sept 13
        ["27",  "4"],  # TB  @ CIN
        ["18",  "8"],  # NO  @ DET
        ["20", "10"],  # NYJ @ TEN
        ["33", "11"],  # BAL @ IND
        [ "1", "23"],  # ATL @ PIT
        [ "3", "29"],  # CHI @ CAR
        [ "5", "30"],  # CLE @ JAX
        [ "2", "34"],  # BUF @ HOU
        ["15", "13"],  # MIA @ LV
        [ "9", "16"],  # GB  @ MIN
        ["28", "21"],  # WSH @ PHI
        ["22", "24"],  # ARI @ LAC
        [ "6", "19"],  # DAL @ NYG
        # Monday Sept 14
        [ "7", "12"],  # DEN @ KC  (Monday Night Football)
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