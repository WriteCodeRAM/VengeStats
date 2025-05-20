from backend.schedule.get_schedule import get_nba_schedule, get_team_ids
from backend.db.queries.revenge_games import get_revenge_games
from backend.scrapers.injury_scrapers import get_nba_injuries

def get_daily_revenge_matchups():
    # schedule = get_nba_schedule()
    # team_ids = get_team_ids(schedule)
    revenge_games = get_revenge_games([[1,2], [14,17]])
    updated_games = get_nba_injuries(revenge_games)
    print(updated_games)
    return [game for game in updated_games if game[2] != "Out"]