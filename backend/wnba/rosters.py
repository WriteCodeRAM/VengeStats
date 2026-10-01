"""
WNBA roster sync using ESPN APIs (mirrors NBA roster_sync.py pattern).
"""
import requests
from db.database import get_connection

ESPN_WNBA_ROSTER_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams/{}/roster"
_HEADERS = {'User-Agent': 'Mozilla/5.0'}


def get_all_wnba_teams():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, espn_id, abbreviation, name FROM wnba_teams ORDER BY id")
            return cursor.fetchall()


def get_espn_roster(espn_team_id):
    url = ESPN_WNBA_ROSTER_URL.format(espn_team_id)
    r = requests.get(url, headers=_HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"  ESPN returned {r.status_code} for team {espn_team_id}")
        return []
    data = r.json()
    players = []
    for athlete in data.get('athletes', []):
        full_name = athlete.get('fullName', '')
        parts = full_name.split(' ', 1)
        players.append({
            'espn_id': str(athlete.get('id', '')),
            'first_name': parts[0] if parts else '',
            'last_name': parts[1] if len(parts) > 1 else '',
            'full_name': full_name,
        })
    return players


def upsert_player(player, team_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO wnba_players
                    (first_name, last_name, espn_athlete_id, current_team_id, needs_stint_refresh)
                VALUES (%s, %s, %s, %s, TRUE)
                ON CONFLICT (espn_athlete_id) DO UPDATE SET
                    first_name          = EXCLUDED.first_name,
                    last_name           = EXCLUDED.last_name,
                    current_team_id     = EXCLUDED.current_team_id,
                    needs_stint_refresh = TRUE,
                    updated_at          = CURRENT_TIMESTAMP
                RETURNING id, (xmax = 0) AS inserted
            """, (player['first_name'], player['last_name'], player['espn_id'], team_id))
            row = cursor.fetchone()
            conn.commit()
            return row


def sync_team_roster(db_team_id, espn_team_id, team_name):
    print(f"\nSyncing {team_name}...")
    players = get_espn_roster(espn_team_id)
    if not players:
        print(f"  No players returned")
        return 0

    count = 0
    for p in players:
        if not p['espn_id']:
            continue
        result = upsert_player(p, db_team_id)
        if result:
            action = "added" if result[1] else "updated"
            print(f"  {action}: {p['full_name']}")
            count += 1

    print(f"  Done: {count} players synced")
    return count


def sync_all_teams():
    teams = get_all_wnba_teams()
    total = 0
    for db_id, espn_id, abbr, name in teams:
        total += sync_team_roster(db_id, espn_id, name)
    print(f"\nAll teams synced. {total} players total.")
    return total


if __name__ == "__main__":
    sync_all_teams()
