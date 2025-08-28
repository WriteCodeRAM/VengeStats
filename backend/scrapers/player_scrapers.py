from bs4 import BeautifulSoup
from backend.db.queries.nba.teams import teams 
import requests
import html
import unicodedata
import time 
import random

base_url = "https://www.basketball-reference.com"

session = requests.Session()  # Reuse session to avoid opening/closing new connections

# Add random delays
time.sleep(random.uniform(2, 4))  # Random 2-4 second delays

# rotate User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def get_start_date(season_href):

    url = f"https://www.basketball-reference.com{season_href}"
    time.sleep(1)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'id': 'player_game_log_reg'})

    if not table:
        print(f"❌ No table found at {url}")
        return None

    tbody = table.find('tbody')
    if not tbody:
        print(f"❌ No tbody found at {url}")
        return None

    for row in tbody.find_all('tr'):
        date_cell = row.find('td', {'data-stat': 'date'})
        if date_cell:
            a_tag = date_cell.find('a')
            if a_tag:
                date_text = a_tag.text.strip()
                # Basic validation that it looks like a date
                if len(date_text) == 10 and date_text.count('-') == 2:
                    return date_text  # Already in YYYY-MM-DD format!

    print(f"⚠️ No valid game date found for {url}")
    return None

def get_end_date(season_href):
    url = f"https://www.basketball-reference.com{season_href}"
    time.sleep(1)  # to avoid rate limiting
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get both tables
    reg_table = soup.find('table', {'id': 'player_game_log_reg'})
    post_table = soup.find('table', {'id': 'player_game_log_post'})
    
    latest_date = None
    
    # Helper function to get last date from a table
    def get_last_date_from_table(table):
        if not table:
            return None
        
        tbody = table.find('tbody')
        if not tbody:
            return None
        
        rows = tbody.find_all('tr')
        # Go through rows in reverse order to find the last valid date
        for row in reversed(rows):
            date_cell = row.find('td', {'data-stat': 'date'})
            if date_cell:
                a_tag = date_cell.find('a')
                if a_tag:
                    date_text = a_tag.text.strip()
                    # Basic validation that it looks like a date
                    if len(date_text) == 10 and date_text.count('-') == 2:
                        return date_text
        return None
    
    # Get last date from regular season
    reg_last_date = get_last_date_from_table(reg_table)
    
    # Get last date from playoffs (if exists)
    post_last_date = get_last_date_from_table(post_table)
    
    # Determine which is later
    if reg_last_date and post_last_date:
        # Compare dates and return the later one
        if reg_last_date > post_last_date:  # String comparison works for YYYY-MM-DD format
            latest_date = reg_last_date
        else:
            latest_date = post_last_date
    elif reg_last_date:
        latest_date = reg_last_date
    elif post_last_date:
        latest_date = post_last_date
    else:
        print(f"❌ No valid game dates found at {url}")
        return None
    
    return latest_date

# pass in team abbreviation 
# (MIA instead of Miami)
def get_player_urls(team: str) -> list[str]: 

    url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
    # we need every a tag (href) thats in the roster table 
    # go to href then totals table and all the a tag (text) under the team column 
    time.sleep(random.uniform(2, 4))
    headers = {"User-Agent": random.choice(user_agents)}
    page = session.get(url, headers=headers)
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
    time.sleep(random.uniform(2, 4))
    headers = {"User-Agent": random.choice(user_agents)}
    page = session.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    page.encoding = "utf-8"  

    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the correct table
    table = soup.find('table', {'id': 'per_game_stats'})

    # Get & properly format player name
    player_name = soup.find('h1').text.strip()
    player_name = html.unescape(player_name)  # ✅ Convert HTML entities (fix "Ä" issue)
    player_name = unicodedata.normalize("NFKC", player_name)  # ✅ Normalize Unicode

    first_name = player_name.split(" ")[0] 
    last_name = " ".join(player_name.split(" ")[1:])
    if not table:
        # Check if this is a rate limit
        if page.status_code == 429 or "Too Many Requests" in page.text:
            print(f"❌ RATE LIMITED: {url}")
            return ("RATE_LIMITED", None, None)
        else: 
            # NEW PLAYER
            return (first_name, last_name, [], 0, None)

    # Get all rows from tbody to process them in sequence
    tbody = table.find('tbody')
    rows = tbody.find_all('tr') if tbody else []
    
    season_links = []
    
    for row in rows:
        # Get season from th
        year_cell = row.find('th', {'data-stat': 'year_id'})
        team_cell = row.find('td', {'data-stat': 'team_name_abbr'})
        
        if year_cell and team_cell:
            # Check if there's a gamelog link in the year cell
            a_tag_year = year_cell.find('a')
            if a_tag_year and 'gamelog' in a_tag_year['href']:
                season = a_tag_year.text.strip()                   # e.g., "2022-23"
                href = a_tag_year['href'].strip()                  # e.g., "/players/y/youngtr01/gamelog/2023/"
                
                # Get team abbreviation
                a_tag_team = team_cell.find('a')
                if a_tag_team and len(a_tag_team.text) < 4:
                    team_abbr = a_tag_team.text.strip()
                    season_links.append([season, href, team_abbr])
    
    if not season_links:
        print("No valid seasons with game logs found")
        return (first_name, last_name, [], {}, None)
    
    # Process team changes
    curr_team = season_links[0][2] 
    start_date = get_start_date(season_links[0][1]) 

    for i in range(len(season_links)): 
        if season_links[i][2] != curr_team: 
            # print(f"Team change detected: {curr_team} -> {season_links[i][2]}")
            end_date = get_end_date(season_links[i - 1][1])
            history.append((curr_team, start_date, end_date))
            curr_team = season_links[i][2]
            start_date = get_start_date(season_links[i][1])
    
    # Add the curr stint (no end date yet)
    history.append((curr_team, start_date, None))

    # extract games played from tfoot
    tfoot = table.find('tfoot')
    if tfoot:
        rows = tfoot.find_all('tr')
        
        for i, row in enumerate(rows):
            team_cell = row.find('th')  
            games_cell = row.find('td', {'data-stat': 'games'})
            
            if team_cell and games_cell:
                team_text = team_cell.text.strip()
                team_abbr = team_text.split()[0] if " " in team_text else team_text
                
                if not team_abbr.isalpha(): 
                    print(f"Skipping non-alpha team: '{team_abbr}'")
                    continue  

                games = int(games_cell.text.strip()) if games_cell.text.strip().isdigit() else 0
                games_played[team_abbr] = games
                print(f"Added: {team_abbr} = {games} games")

    # Get prev_team_id from history
    prev_team_id = teams[history[-2][0]] if len(history) > 1 else None

    return (first_name, last_name, history, games_played, prev_team_id)
