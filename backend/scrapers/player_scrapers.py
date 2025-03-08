from bs4 import BeautifulSoup
from backend.db.database import get_connection
from backend.db.teams import teams 
import requests
import html
import unicodedata
import time 

base_url = "https://www.basketball-reference.com"

session = requests.Session()  # Reuse session to avoid opening/closing new connections
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# pass in team abbreviation 
# (MIA instead of Miami)
def get_player_urls(team: str) -> list[str]: 

    url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
    # we need every a tag (href) thats in the roster table 
    # go to href then totals table and all the a tag (text) under the team column 

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the table by its id 'roster'
    table = soup.find('table', {'id': 'roster'})

    # Find all anchor tags inside the second column (Player column)
    player_links = table.find_all('td', {'data-stat': 'player'})

    # Extract the href attribute from each anchor tag
    player_urls = [a.find('a')['href'] for a in player_links if a.find('a')]

    return player_urls

def get_player_history(player_url: str): 
    history = set()  
    games_played = {} 

    url = f"{base_url}{player_url}"
    time.sleep(1)  
    page = session.get(url, headers=headers)
    page.encoding = "utf-8"  

    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the correct table with id "per_game_stats"
    table = soup.find('table', {'id': 'per_game_stats'})
    if not table:
        return None  # Return None if table is not found

    player_name = soup.find('h1').text.strip()
    first_name = player_name.split(" ")[0] 
    last_name = player_name.split(" ")[1] 


    
    # Extract team history from table
    team_cells = table.find_all('td', {'data-stat': 'team_name_abbr'})
    for cell in team_cells:
        a_tag = cell.find('a')
        if a_tag:
            history.add(a_tag.text) 

    # Extract games played from `tfoot`
    tfoot = table.find('tfoot')
    if tfoot:
        rows = tfoot.find_all('tr')
        for row in rows:
            team_cell = row.find('th') 
            games_cell = row.find('td', {'data-stat': 'games'})  # Games played

            if team_cell and games_cell:
                team_text = team_cell.text.strip()

                
                # Extract the team abbreviation from text like "CLE (11 Yrs)"
                team_abbr = team_text.split()[0] if " " in team_text else team_text
                if not team_abbr.isalpha(): 
                    continue  # Ignore non-team rows

                
                # Convert games played to int
                games = int(games_cell.text.strip()) if games_cell.text.strip().isdigit() else 0
                games_played[team_abbr] = games  # Store team & games played

    return (first_name, last_name, history, games_played)



print(get_player_history("/players/j/jamesle01.html"))