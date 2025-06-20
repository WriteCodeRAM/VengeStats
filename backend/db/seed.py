from backend.db.queries.players import get_player_id, insert_player_team_stint, move_player_to_team
from backend.db.queries.teams import teams, get_current_nba_roster, update_prev_team_id
from backend.scrapers.player_scrapers import get_player_urls, get_player_history
import time

def seed():
    # pass in team abbrev as TEAM, (must be the abbrev bballref uses)
    team = "NOP"
    team_id = teams[team]
    limited = False

    current_roster = get_current_nba_roster(team_id)

    player_urls = get_player_urls(team)

    for i, player_url in enumerate(player_urls):
        if i > 0 and i % 5 == 0:
            if i == 15:
                print(f"Processed {i} players, taking 5 min break...")
                time.sleep(300)  
            else:
                print(f"Processed {i} players, taking 2 min break...")
                time.sleep(120)  
        
        result = get_player_history(player_url)
            
        # if all goes well continue
        first_name, last_name, history, games_played, prev_team_id = result
        player_tuple = (first_name, last_name)

        player_id = get_player_id(first_name, last_name, team_id)

        if prev_team_id == None: 
            prev_team_id = team_id
        update_prev_team_id(player_id, prev_team_id)

        print(f"Processing: {first_name} {last_name}")
        if player_tuple in current_roster:
            print(f"✅ Player {first_name} {last_name} still on {team_id}, removing from roster set.")
            current_roster.remove(player_tuple)
        else:
            print(f"🚨 NEW PLAYER DETECTED: Moving {first_name} {last_name} to {team_id}")
            move_player_to_team(player_id, team_id)  

        for team_abbrev, start_date, end_date in history:
            curr_team_id = teams[team_abbrev]
            gp = games_played.get(team_abbrev, 0)
            insert_player_team_stint(player_id, curr_team_id, start_date, end_date, gp)

    if not limited:
        for removed_player in current_roster:
            first_name, last_name = removed_player
            player_id = get_player_id(first_name,last_name, teams[team])
            move_player_to_team(player_id, 31)
            print(f"Moved {first_name} {last_name} to team 31 (Unassigned)")
    else:
        print("rate limited")

seed()