from backend.db.database import get_connection, get_player_id, insert_player_team_history
from backend.db.teams import teams
from backend.scrapers.scrapers import get_player_urls, get_player_history



def seed(): 
    player_urls = get_player_urls("WAS")

    for player in player_urls: 

        first_name, last_name, history = get_player_history(player)
        player_id = get_player_id(first_name, last_name)
        print(first_name, last_name)
        for item in history: 
            team_id = teams[item]
            insert_player_team_history(player_id, team_id)

seed()