from backend.schedule.get_schedule import get_nba_schedule, get_team_ids
from backend.db.database import get_revenge_games

def run():
    daily_schedule = get_nba_schedule()  
    team_id_list = get_team_ids(daily_schedule)  
    revenge_games = get_revenge_games(team_id_list)

    for game in revenge_games:
        print(game)  

if __name__ == "__main__":
    run()  
