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

    url = f"{base_url}{player_url}"

    time.sleep(1)  # Add a delay before each request
    page = session.get(url, headers=headers)
    page.encoding = "utf-8"  # Ensure UTF-8 encoding
    
    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the correct table with id "per_game_stats"
    table = soup.find('table', {'id': 'per_game_stats'})
    player_name = soup.find('h1').text.strip()
    # Convert HTML entities, 
    # stops breaking when encounter foreign names with accents (Porzingis, Nurkić)
    player_name = html.unescape(player_name) 
    player_name = unicodedata.normalize("NFKC", player_name)  # Normalize Unicode


    # LARRY NANCE JR. just broke me
    name_parts = player_name.split(" ")
    
    first_name = name_parts[0]
    last_name = None
    last_name = " ".join(name_parts[1:])

    if table:
    # Find all 'td' elements under the "Team" column
        team_cells = table.find_all('td', {'data-stat': 'team_name_abbr'})

    # Extract team names from anchor tags inside the team column
        for cell in team_cells:
            a_tag = cell.find('a')
            if a_tag:
                history.add(a_tag.text)  # Get the text of the team link (e.g., 'ATL')

    return (first_name, last_name, history)
