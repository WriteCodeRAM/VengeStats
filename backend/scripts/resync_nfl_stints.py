"""
Rebuilds nfl_player_stints for all active players using nfl-data-py weekly rosters.

Why: the original seeder used seasonal rosters (one entry per season) with a
dedup bug that collapsed multiple stints at the same team. Weekly rosters catch
mid-season trades and give accurate games_played counts.

Safe to re-run: preserves manually set departure_method values.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nfl_data_py as nfl
import pandas as pd
from db.database import get_connection

# nfl-data-py uses 'LA' for Rams; everything else matches ESPN
ABBR_NORMALIZE = {'LA': 'LAR'}

TEAM_ABBR_TO_ID = {
    'ARI': '22', 'ATL': '1',  'BAL': '33', 'BUF': '2',  'CAR': '29', 'CHI': '3',
    'CIN': '4',  'CLE': '5',  'DAL': '6',  'DEN': '7',  'DET': '8',  'GB': '9',
    'HOU': '34', 'IND': '11', 'JAX': '30', 'KC': '12',  'LV': '13',  'LAC': '24',
    'LAR': '14', 'MIA': '15', 'MIN': '16', 'NE': '17',  'NO': '18',  'NYG': '19',
    'NYJ': '20', 'PHI': '21', 'PIT': '23', 'SF': '25',  'SEA': '26', 'TB': '27',
    'TEN': '10', 'WSH': '28',
}

def normalize_abbr(abbr):
    return ABBR_NORMALIZE.get(abbr, abbr)


def build_stints(player_rows: pd.DataFrame) -> list:
    """
    Given weekly roster rows for one player, return stints as:
    [{team_abbr, team_id, season_start, season_end, games_played, is_current_stint}]

    Groups consecutive weeks on the same team. Mid-season trades produce
    separate stints. games_played = regular-season weeks on active roster.
    """
    rows = player_rows.sort_values(['season', 'week'])
    stints = []
    current = None

    for _, row in rows.iterrows():
        abbr = normalize_abbr(str(row['team']))
        season = int(row['season'])
        is_active = str(row.get('status', '')).upper() == 'ACT'
        is_reg = str(row.get('game_type', 'REG')).upper() == 'REG'

        if current is None or current['team_abbr'] != abbr:
            if current is not None:
                stints.append(current)
            current = {
                'team_abbr': abbr,
                'season_start': season,
                'season_end': season,
                'games_played': 1 if (is_active and is_reg) else 0,
            }
        else:
            current['season_end'] = season
            if is_active and is_reg:
                current['games_played'] += 1

    if current is not None:
        stints.append(current)

    current_season = 2025
    for stint in stints:
        team_id = TEAM_ABBR_TO_ID.get(stint['team_abbr'])
        stint['team_id'] = team_id
        stint['is_current_stint'] = stint['season_end'] >= current_season

    return [s for s in stints if s['team_id'] is not None]


def get_all_active_players():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, display_name, nfl_data_py_player_id
                FROM nfl_players
                WHERE is_active = true AND nfl_data_py_player_id IS NOT NULL
                ORDER BY id
            """)
            return cursor.fetchall()


def get_existing_departure_methods(player_id):
    """Return {team_id: departure_method} for stints that have one set."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT team_id, departure_method
                FROM nfl_player_stints
                WHERE player_id = %s AND departure_method IS NOT NULL
            """, (player_id,))
            return {row[0]: row[1] for row in cursor.fetchall()}


def delete_player_stints(player_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM nfl_player_stints WHERE player_id = %s", (player_id,))
            conn.commit()


def insert_stint(player_id, stint, departure_methods):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            departure = departure_methods.get(stint['team_id'])
            cursor.execute("""
                INSERT INTO nfl_player_stints
                    (player_id, team_id, season_start, season_end, games_played, is_current_stint, departure_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, team_id, season_start)
                DO UPDATE SET
                    season_end = EXCLUDED.season_end,
                    games_played = EXCLUDED.games_played,
                    is_current_stint = EXCLUDED.is_current_stint,
                    departure_method = COALESCE(nfl_player_stints.departure_method, EXCLUDED.departure_method),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                player_id,
                stint['team_id'],
                stint['season_start'],
                stint['season_end'] if stint['season_end'] != stint['season_start'] else None,
                stint['games_played'],
                stint['is_current_stint'],
                departure,
            ))
            conn.commit()


def resync_all(dry_run=False, player_filter=None):
    print("Loading weekly rosters from nfl-data-py (2010-2025)...")
    seasons = list(range(2010, 2026))
    weekly = nfl.import_weekly_rosters(seasons)
    print(f"Loaded {len(weekly):,} weekly roster rows.")

    players = get_all_active_players()
    if player_filter:
        players = [p for p in players if p[1] in player_filter]

    print(f"\nProcessing {len(players)} active players...\n")

    stats = {'ok': 0, 'no_data': 0, 'errors': 0}

    for db_id, name, nfl_id in players:
        try:
            player_rows = weekly[weekly['player_id'] == nfl_id]

            if player_rows.empty:
                print(f"  NO DATA  {name} ({nfl_id})")
                stats['no_data'] += 1
                continue

            stints = build_stints(player_rows)

            if not stints:
                print(f"  NO STINTS {name} ({nfl_id})")
                stats['no_data'] += 1
                continue

            departure_methods = get_existing_departure_methods(db_id)

            stint_summary = " -> ".join(
                f"{s['team_abbr']}({s['season_start']}-{s['season_end']})" for s in stints
            )
            print(f"  {name}: {stint_summary}")

            if not dry_run:
                delete_player_stints(db_id)
                for stint in stints:
                    insert_stint(db_id, stint, departure_methods)

            stats['ok'] += 1

        except Exception as e:
            print(f"  ERROR {name}: {e}")
            stats['errors'] += 1

    print(f"\nDone. ok={stats['ok']} no_data={stats['no_data']} errors={stats['errors']}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN -- no DB writes\n")
    resync_all(dry_run=dry_run)
