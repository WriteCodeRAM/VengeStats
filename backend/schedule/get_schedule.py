from typing import List, Tuple
import requests
import os
import datetime
from db.queries.nba.teams import teams

api_key = os.getenv('SPORTS_BLAZE_API_KEY')
def get_nba_schedule() -> List[str]: 
    date = str(datetime.datetime.now())
    url = f"https://api.sportsblaze.com/nba/v1/schedule/daily/{date[0:10]}.json?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        schedule = []
        games = data.get("games", [])

        for game in games: 
            schedule.append([game['teams']['away']['name'], game['teams']['home']['name']])
        
        return schedule
    else:
        print("Failed to fetch NBA schedule")
        return []

def get_team_ids(schedule: List[str]) -> List[Tuple[int, int]]:
    games = [] 
    for game in schedule: 
        end = game.index(" ")
        away_team = game[:end]
        start = game.index("@") + 2
        home_team = game[start:]

        if away_team in teams and home_team in teams: 
            games.append((teams[away_team], teams[home_team]))

    return games