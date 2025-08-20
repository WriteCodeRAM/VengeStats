import requests
from bs4 import BeautifulSoup
from backend.types.revenge_types import NBARevengeGame
from typing import List

def get_nba_injuries(revenge_games: List[NBARevengeGame]):
    url = "https://www.espn.com/nba/injuries"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    teams = soup.find_all("div", class_="ResponsiveTable")

    # create a lookup set for player names in revenge games
    revenge_players = {game[0] for game in revenge_games}  # just names

    for team in teams:
        rows = team.find_all("tr", class_="Table__TR")
        
        for row in rows[1:]:  # skip header row
            cols = row.find_all("td")
            if len(cols) < 4:
                continue  

            player_name = cols[0].text.strip()
            injury_status = cols[3].text.strip()

            # update revenge_games in place
            for game in revenge_games:
                if game[0] == player_name:  
                    game[2] = injury_status  

    return revenge_games # updated w/ injury status 
