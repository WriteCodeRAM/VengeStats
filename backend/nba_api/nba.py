from nba_api.stats.endpoints import PlayerGameLog
from nba_api.stats.static import players
import pandas as pd

def search_player(name): 
    player = players.find_players_by_full_name(name)
    if not player: 
        return "Player not found"
    return player[0]

# print(search_player("LeBron James"))

def get_stats(player_id): 
    gamelog = PlayerGameLog(player_id=player_id, season='2016-25')
    df = gamelog.get_data_frames()[0]

    df_selected = df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'MIN']]
    df_selected.columns = ['Date', 'Matchup', 'Points', 'Rebounds', 'Assists', 'Minutes']

    return df_selected

pid = search_player("Jimmy Butler")["id"]
# print(pid)
print(get_stats(pid))
