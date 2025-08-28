from typing import List, Tuple
import requests
from backend.db.queries.nba.teams import teams

def get_nba_schedule() -> List[str]: 
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        games = data.get("events", [])
        
        schedule = [game.get("shortName", "Unknown vs Unknown") for game in games]
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