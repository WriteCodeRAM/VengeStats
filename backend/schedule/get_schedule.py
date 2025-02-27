import requests
from backend.db.teams import teams

def get_nba_schedule():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        games = data.get("events", [])
        
        schedule = []
        for game in games:
            matchup = game.get("shortName", "Unknown vs Unknown")
            schedule.append(matchup)
        
        return schedule
    else:
        print("Failed to fetch NBA schedule")
        return []

def get_team_ids(schedule: list[str]): 
    games = [] 
    for game in schedule: 
        end = game.index(" ")
        away_team = game[:end]  # get away team abbrev
        start = game.index("@") + 2
        home_team = game[start:]  # get home team abbrev

        if away_team in teams and home_team in teams: 
            games.append([teams[away_team], teams[home_team]])

    return games
