from nba_api.stats.static import players
import pandas as pd
from datetime import datetime

def search_player(name): 
    player = players.find_players_by_full_name(name)
    if not player: 
        return "Player not found"
    return player[0]

def get_seasons_from_date(after_date):
    """
    Generate list of NBA seasons from the given date to current season
    """
    if isinstance(after_date, str):
        after_date = pd.to_datetime(after_date)
    
    start_year = after_date.year
    current_year = datetime.now().year
    
    # NBA season starts in October, so if we're before October, we're still in the previous season
    if datetime.now().month < 10:
        current_year -= 1
    
    # If the date is before October, it's part of the previous NBA season
    if after_date.month < 10:
        start_year -= 1
    
    seasons = []
    for year in range(start_year, current_year + 1):
        next_year = str(year + 1)[-2:]  # Get last 2 digits
        seasons.append(f"{year}-{next_year}")
    
    return seasons