from bs4 import BeautifulSoup
from backend.db.queries.teams import teams 
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
    history = [] 
    games_played = {}  

    url = f"{base_url}{player_url}"
    time.sleep(1)  
    page = session.get(url, headers=headers)
    page.encoding = "utf-8"  

    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the correct table
    table = soup.find('table', {'id': 'per_game_stats'})
    if not table:
        # Check if this is a rate limit
        if page.status_code == 429 or "Too Many Requests" in page.text:
            print(f"❌ RATE LIMITED: {url}")
            return ("RATE_LIMITED", None, None)

    # Get & properly format player name
    player_name = soup.find('h1').text.strip()
    player_name = html.unescape(player_name)  # ✅ Convert HTML entities (fix "Ä" issue)
    player_name = unicodedata.normalize("NFKC", player_name)  # ✅ Normalize Unicode

    first_name = player_name.split(" ")[0] 
    last_name = " ".join(player_name.split(" ")[1:])

    # check table again if new player but not limited 
    if not table: 
        return ("NEW_PLAYER", first_name, last_name)

    # extract team history (AVOID consecutive duplicates)
    team_cells = table.find_all('td', {'data-stat': 'team_name_abbr'})
    last_team = None  

    for cell in team_cells:
        a_tag = cell.find('a')
        if a_tag:
            team_abbr = a_tag.text  
            if team_abbr != last_team:  
                history.append(team_abbr)
                last_team = team_abbr

    # extract games played from `tfoot`
    tfoot = table.find('tfoot')
    if tfoot:
        rows = tfoot.find_all('tr')
        for row in rows:
            team_cell = row.find('th')  
            games_cell = row.find('td', {'data-stat': 'games'})  

            if team_cell and games_cell:
                team_text = team_cell.text.strip()
                team_abbr = team_text.split()[0] if " " in team_text else team_text
                if not team_abbr.isalpha(): 
                    continue  

                games = int(games_cell.text.strip()) if games_cell.text.strip().isdigit() else 0
                games_played[team_abbr] = games  

    history_set = set(history)
    # Get prev_team_id from history
    prev_team_id = teams[history[-2]] if len(history) > 1 else None

    return (first_name, last_name, history_set, games_played, prev_team_id)

# print(get_player_history("/players/y/youngtr01.html"))