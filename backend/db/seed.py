from backend.db.database import get_connection, get_player_id, insert_player_team_history, get_current_nba_roster, update_prev_team_id, move_player_to_team
from backend.db.teams import teams
from backend.scrapers.player_scrapers import get_player_urls, get_player_history

def seed():
    team = "CLE"
    team_id = teams[team]
    limited = False

    current_roster = get_current_nba_roster(team_id)

    player_urls = get_player_urls(team)

    for player in player_urls: 
        # ✅ Step 3: Scrape player history & retrieve name
        result = get_player_history(player)

        if result[0] == "NEW_PLAYER":
            player_id = get_player_id(result[1], result[2], team_id)
            if (result[1], result[2]) in current_roster:
                current_roster.remove((result[1], result[2]))
            continue
        elif result[0] == "RATE_LIMITED": 
            limited = True 
            continue 
        
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


        for team_abbrev in history:
            old_team_id = teams[team_abbrev]
            insert_player_team_history(player_id, old_team_id, games_played.get(team_abbrev, 0))

    if not limited:
        for removed_player in current_roster:
            first_name, last_name = removed_player
            player_id = get_player_id(first_name,last_name, teams[team])
            move_player_to_team(player_id, 31)
            print(f"Moved {first_name} {last_name} to team 31 (Unassigned)")
    else:
        print("rate limited")

seed()