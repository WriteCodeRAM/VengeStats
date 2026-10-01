"""
Builds wnba_player_stints for all active players using ESPN WNBA gamelogs.

Fetches seasons 2022-2026 per player, groups consecutive games by team
into stints with first_game_date, last_game_date, and games_played.
Preserves any manually set departure_method values.

Run with: PYTHONPATH=. python3 wnba/stint_sync.py [--dry-run]
"""
import sys
import os
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_connection

ESPN_GAMELOG_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/wnba/athletes/{}/gamelog"
_HEADERS = {'User-Agent': 'Mozilla/5.0'}
SEASONS = [2022, 2023, 2024, 2025, 2026]


def get_espn_team_id_map():
    """Returns {espn_id_str: internal_db_id} for all wnba_teams."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT espn_id, id FROM wnba_teams")
            return {row[0]: row[1] for row in cursor.fetchall()}


def get_all_players():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, first_name, last_name, espn_athlete_id
                FROM wnba_players
                WHERE espn_athlete_id IS NOT NULL
                ORDER BY id
            """)
            return cursor.fetchall()


def fetch_gamelog(espn_athlete_id, season):
    url = ESPN_GAMELOG_URL.format(espn_athlete_id)
    try:
        r = requests.get(url, headers=_HEADERS, params={'season': season}, timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()
        events = data.get('events', {})
        games = []
        for event in events.values():
            team = event.get('team', {})
            espn_team_id = team.get('id')
            game_date_str = event.get('gameDate', '')
            if not espn_team_id or not game_date_str:
                continue
            try:
                game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00')).date()
            except Exception:
                continue
            games.append({
                'espn_team_id': str(espn_team_id),
                'date': game_date,
                'result': event.get('gameResult', ''),
            })
        games.sort(key=lambda g: g['date'])
        return games
    except Exception as e:
        print(f"    fetch error: {e}")
        return []


def build_stints(all_games, espn_team_map):
    """
    Groups consecutive games by team into stints.
    Returns [{team_id, first_game_date, last_game_date, games_played, is_current}]
    """
    if not all_games:
        return []

    stints = []
    current = None

    for game in all_games:
        team_id = espn_team_map.get(game['espn_team_id'])
        if not team_id:
            continue

        if current is None or current['team_id'] != team_id:
            if current is not None:
                stints.append(current)
            current = {
                'team_id': team_id,
                'first_game_date': game['date'],
                'last_game_date': game['date'],
                'games_played': 1,
            }
        else:
            current['last_game_date'] = game['date']
            current['games_played'] += 1

    if current is not None:
        stints.append(current)

    # Mark the most recent stint as current
    if stints:
        stints[-1]['is_current'] = True
    for s in stints[:-1]:
        s['is_current'] = False

    return stints


def get_existing_departure_methods(player_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT team_id, departure_method FROM wnba_player_stints
                WHERE player_id = %s AND departure_method IS NOT NULL
            """, (player_id,))
            return {row[0]: row[1] for row in cursor.fetchall()}


def save_stints(player_id, stints, departure_methods, dry_run=False):
    if dry_run:
        return

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM wnba_player_stints WHERE player_id = %s", (player_id,))
            for stint in stints:
                departure = departure_methods.get(stint['team_id'])
                cursor.execute("""
                    INSERT INTO wnba_player_stints
                        (player_id, team_id, first_game_date, last_game_date,
                         games_played, departure_method, is_current)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id, team_id, first_game_date)
                    DO UPDATE SET
                        last_game_date   = EXCLUDED.last_game_date,
                        games_played     = EXCLUDED.games_played,
                        is_current       = EXCLUDED.is_current,
                        departure_method = COALESCE(wnba_player_stints.departure_method, EXCLUDED.departure_method),
                        updated_at       = CURRENT_TIMESTAMP
                """, (
                    player_id,
                    stint['team_id'],
                    stint['first_game_date'],
                    stint['last_game_date'],
                    stint['games_played'],
                    departure,
                    stint['is_current'],
                ))
            conn.commit()


def sync_all(dry_run=False):
    espn_team_map = get_espn_team_id_map()
    players = get_all_players()

    print(f"Syncing stints for {len(players)} players across seasons {SEASONS[0]}-{SEASONS[-1]}...")
    if dry_run:
        print("DRY RUN -- no DB writes\n")

    stats = {'ok': 0, 'no_data': 0, 'errors': 0}

    for i, (db_id, first, last, espn_id) in enumerate(players, 1):
        name = f"{first} {last}"
        try:
            all_games = []
            for season in SEASONS:
                games = fetch_gamelog(espn_id, season)
                all_games.extend(games)
                time.sleep(0.15)

            if not all_games:
                print(f"  [{i}/{len(players)}] NO DATA  {name}")
                stats['no_data'] += 1
                continue

            stints = build_stints(all_games, espn_team_map)

            if not stints:
                print(f"  [{i}/{len(players)}] NO STINTS {name}")
                stats['no_data'] += 1
                continue

            stint_summary = " -> ".join(
                f"{s['first_game_date'].year}:{espn_team_map.get(s['team_id'], '?')}"
                for s in stints
            )
            # Get team abbrs for readable output
            team_abbrs = get_team_abbrs()
            readable = " -> ".join(
                f"{team_abbrs.get(s['team_id'], s['team_id'])}({s['games_played']}g)"
                for s in stints
            )
            print(f"  [{i}/{len(players)}] {name}: {readable}")

            departure_methods = get_existing_departure_methods(db_id)
            save_stints(db_id, stints, departure_methods, dry_run)
            stats['ok'] += 1

        except Exception as e:
            print(f"  [{i}/{len(players)}] ERROR {name}: {e}")
            stats['errors'] += 1

    print(f"\nDone. ok={stats['ok']}  no_data={stats['no_data']}  errors={stats['errors']}")


_team_abbr_cache = None

def get_team_abbrs():
    global _team_abbr_cache
    if _team_abbr_cache is None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, abbreviation FROM wnba_teams")
                _team_abbr_cache = {row[0]: row[1] for row in cursor.fetchall()}
    return _team_abbr_cache


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sync_all(dry_run=dry_run)
