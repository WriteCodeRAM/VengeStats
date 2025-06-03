from backend.schedule.get_schedule import get_nba_schedule, get_team_ids
from backend.db.queries.revenge_games import get_revenge_games
from backend.scrapers.injury_scrapers import get_nba_injuries
from backend.db.venge_data import calculate_venge_score

def get_daily_revenge_matchups():
    # schedule = get_nba_schedule()
    # team_ids = get_team_ids(schedule)
    revenge_games = get_revenge_games([[14,7]])
    updated_games = get_nba_injuries(revenge_games)
    # generate revenge scores for all potential matchups
    for player in updated_games:
        revenge_score = calculate_venge_score(player[3], player[0], player[4])
        player[5] = revenge_score
    
    return [game for game in updated_games if game[2] != "Out"]