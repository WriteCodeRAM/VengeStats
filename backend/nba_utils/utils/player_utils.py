import unicodedata
import requests
import time
from datetime import datetime, timedelta
from nba_api.stats.static import players
from db.queries.nba.teams import team_id_to_abbr

ESPN_GAMELOG_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{}/gamelog"
ESPN_ROSTER_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{}/roster"

# Internal team ID → ESPN team ID (same as roster_sync.py)
TEAM_ID_TO_ESPN_ID = {
    1: 1,  2: 2,  3: 17, 4: 30, 5: 4,  6: 5,  7: 6,  8: 7,  9: 8,  10: 9,
    11: 10, 12: 11, 13: 12, 14: 13, 15: 29, 16: 14, 17: 15, 18: 16, 19: 3,
    20: 18, 21: 25, 22: 19, 23: 20, 24: 21, 25: 22, 26: 23, 27: 24, 28: 28,
    29: 26, 30: 27,
}
ESPN_ID_TO_TEAM_ID = {v: k for k, v in TEAM_ID_TO_ESPN_ID.items()}


def search_player(name):
    player = players.find_players_by_full_name(name)
    if not player:
        return None
    return player[0]


def get_seasons_from_date(after_date):
    import pandas as pd
    if isinstance(after_date, str):
        after_date = pd.to_datetime(after_date)
    start_year = after_date.year
    current_year = datetime.now().year
    if datetime.now().month < 10:
        current_year -= 1
    if after_date.month < 10:
        start_year -= 1
    seasons = []
    for year in range(start_year, current_year + 1):
        next_year = str(year + 1)[-2:]
        seasons.append(f"{year}-{next_year}")
    return seasons


def extract_player_team_from_matchup(matchup):
    if ' vs. ' in matchup:
        return matchup.split(' vs. ')[0].strip()
    elif ' @ ' in matchup:
        return matchup.split(' @ ')[0].strip()
    return None


def get_player_stints_from_nba_api(player_id, player_name, current_team_abbr=None):
    """Legacy shim — redirects to ESPN-based implementation."""
    return []


def _norm(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()


def build_espn_athlete_id_map() -> dict:
    """Fetch all 30 ESPN rosters and return {normalized_full_name: espn_athlete_id}."""
    name_to_id = {}
    for internal_id, espn_team_id in TEAM_ID_TO_ESPN_ID.items():
        try:
            r = requests.get(ESPN_ROSTER_URL.format(espn_team_id), timeout=15)
            r.raise_for_status()
            for athlete in r.json().get('athletes', []):
                full_name = athlete.get('displayName') or athlete.get('fullName', '')
                athlete_id = athlete.get('id')
                if full_name and athlete_id:
                    name_to_id[_norm(full_name)] = athlete_id
            time.sleep(0.3)
        except Exception as e:
            print(f"  Warning: could not fetch ESPN roster for team {internal_id}: {e}")
    print(f"  ESPN athlete ID map built: {len(name_to_id)} players")
    return name_to_id


def _fetch_espn_season_games(espn_athlete_id: str, espn_season: int) -> dict:
    """Fetch all games for one season (regular + playoffs) from ESPN, keyed by event ID."""
    games = {}
    for seasontype in [2, 3]:  # 2=regular, 3=playoffs
        try:
            r = requests.get(
                ESPN_GAMELOG_URL.format(espn_athlete_id),
                params={
                    'region': 'us', 'lang': 'en', 'contentorigin': 'espn',
                    'season': espn_season, 'seasontype': seasontype,
                },
                timeout=12,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            if r.status_code == 200:
                for event_id, event in r.json().get('events', {}).items():
                    games[event_id] = event
        except Exception:
            pass
    return games


def get_player_stints_from_espn(espn_athlete_id: str, player_name: str, current_team_id: int = None):
    """
    Build complete career stint history from ESPN game logs.
    Returns list of {team, start_date, end_date, games_played} dicts.
    team is our internal abbreviation (e.g. 'GSW').
    """
    print(f"    Analyzing {player_name} via ESPN (id={espn_athlete_id})...")

    now = datetime.now()
    # ESPN uses end-year convention: 2026 = 2025-26 season
    espn_season_current = now.year if now.month < 10 else now.year + 1

    all_games = {}
    consecutive_empty = 0

    for i in range(25):
        season = espn_season_current - i
        if season < 2002:
            break

        season_games = _fetch_espn_season_games(espn_athlete_id, season)

        if season_games:
            all_games.update(season_games)
            consecutive_empty = 0
            print(f"      Season {season-1}-{str(season)[-2:]}: {len(season_games)} games")
        else:
            consecutive_empty += 1
            if consecutive_empty >= 3 and i > 3:
                print(f"      3 consecutive empty seasons — stopping")
                break

        time.sleep(0.4)

    if not all_games:
        print(f"    No game data found for {player_name}")
        return []

    # Sort chronologically
    sorted_games = sorted(all_games.values(), key=lambda e: e['gameDate'])
    print(f"    Total games found: {len(sorted_games)}")

    # Detect stints: consecutive games on the same ESPN team
    stints = []
    current_espn_team_id = None
    stint_start = None
    stint_games = 0
    last_date = None

    for event in sorted_games:
        try:
            espn_team_id = int(event['team']['id'])
            game_date = datetime.fromisoformat(
                event['gameDate'].replace('Z', '+00:00')
            ).date()
        except (KeyError, ValueError):
            continue

        if espn_team_id != current_espn_team_id:
            if current_espn_team_id is not None:
                stints.append({
                    'espn_team_id': current_espn_team_id,
                    'start_date': stint_start,
                    'end_date': last_date,
                    'games_played': stint_games,
                })
            current_espn_team_id = espn_team_id
            stint_start = game_date
            stint_games = 1
        else:
            stint_games += 1

        last_date = game_date

    if current_espn_team_id is not None:
        stints.append({
            'espn_team_id': current_espn_team_id,
            'start_date': stint_start,
            'end_date': None,
            'games_played': stint_games,
        })

    # If player was recently traded and hasn't played yet for new team, add a 0-game stint
    if current_team_id and stints:
        expected_espn_id = TEAM_ID_TO_ESPN_ID.get(current_team_id)
        if expected_espn_id and stints[-1]['espn_team_id'] != expected_espn_id:
            print(f"    Recent move detected — adding 0-game stint for current team")
            stints[-1]['end_date'] = last_date
            stints.append({
                'espn_team_id': expected_espn_id,
                'start_date': last_date + timedelta(days=1) if last_date else None,
                'end_date': None,
                'games_played': 0,
            })

    # Convert ESPN team IDs → our abbreviations
    result = []
    for stint in stints:
        internal_tid = ESPN_ID_TO_TEAM_ID.get(stint['espn_team_id'])
        if internal_tid:
            result.append({
                'team': team_id_to_abbr.get(internal_tid, '???'),
                'start_date': stint['start_date'],
                'end_date': stint['end_date'],
                'games_played': stint['games_played'],
            })
        else:
            print(f"    Unknown ESPN team ID {stint['espn_team_id']} — skipping stint")

    return result
