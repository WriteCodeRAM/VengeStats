import requests
import pandas as pd
from datetime import datetime
from nba_utils.utils.player_utils import ESPN_GAMELOG_URL

_EMPTY_STATS = pd.DataFrame(columns=['WL', 'Date', 'Matchup', 'Points', 'Rebounds', 'Assists', 'Minutes'])

_ESPN_HEADERS = {'User-Agent': 'Mozilla/5.0'}

# ESPN abbreviation -> internal abbreviation where they differ
_ESPN_ABBR_MAP = {
    'GS':  'GSW',
    'NO':  'NOP',
    'NY':  'NYK',
    'SA':  'SAS',
    'WSH': 'WAS',
}


def _normalize_abbr(abbr: str) -> str:
    return _ESPN_ABBR_MAP.get(abbr, abbr)


def _fetch_season_gamelog(espn_athlete_id, season: int, seasontype: int):
    """
    Fetch one season/type from ESPN gamelog.
    Returns (events_meta, stats_by_event_id, labels) where:
      events_meta: dict of eventId -> {gameDate, opponent, atVs, gameResult, team}
      stats_by_event_id: dict of eventId -> stats list
      labels: list of stat label strings
    """
    try:
        r = requests.get(
            ESPN_GAMELOG_URL.format(espn_athlete_id),
            params={
                'region': 'us', 'lang': 'en', 'contentorigin': 'espn',
                'season': season, 'seasontype': seasontype,
            },
            timeout=12,
            headers=_ESPN_HEADERS,
        )
        if r.status_code != 200:
            return {}, {}, []
        data = r.json()
    except Exception:
        return {}, {}, []

    labels = data.get('labels', [])

    # Top-level events: game metadata
    events_meta = {}
    for event_id, ev in data.get('events', {}).items():
        events_meta[event_id] = ev

    # seasonTypes -> categories -> events: per-game stats arrays
    stats_by_event = {}
    for season_type in data.get('seasonTypes', []):
        for category in season_type.get('categories', []):
            for ev in category.get('events', []):
                eid = str(ev.get('eventId', ''))
                if eid and ev.get('stats'):
                    stats_by_event[eid] = ev['stats']

    return events_meta, stats_by_event, labels


def get_stats(espn_athlete_id, opponent=None, after_date=None):
    """
    Fetch full game log for an NBA player from ESPN.
    Returns DataFrame: WL, Date, Matchup, Points, Rebounds, Assists, Minutes.
    Matchup format: "TEAM vs. OPP" (home) or "TEAM @ OPP" (away).
    """
    if not espn_athlete_id:
        return _EMPTY_STATS

    now = datetime.now()
    espn_season_current = now.year if now.month < 10 else now.year + 1

    if after_date is not None:
        after_ts = pd.Timestamp(after_date).tz_localize(None) if getattr(after_date, 'tzinfo', None) is None else pd.Timestamp(after_date).tz_localize(None)
        start_year = after_ts.year
        if after_ts.month < 10:
            start_year -= 1
        start_season = start_year + 1
    else:
        start_season = max(2010, espn_season_current - 12)

    all_meta = {}
    all_stats = {}
    labels = []

    import time
    for season in range(start_season, espn_season_current + 1):
        for seasontype in [2, 3]:
            meta, stats, lbls = _fetch_season_gamelog(espn_athlete_id, season, seasontype)
            all_meta.update(meta)
            all_stats.update(stats)
            if lbls and not labels:
                labels = lbls
            time.sleep(0.3)

    if not all_meta:
        return _EMPTY_STATS

    def _idx(name):
        try:
            return labels.index(name)
        except ValueError:
            return None

    pts_idx = _idx('PTS')
    reb_idx = _idx('REB')
    ast_idx = _idx('AST')
    min_idx = _idx('MIN')

    rows = []
    for event_id, ev in all_meta.items():
        try:
            raw_date = ev.get('gameDate', '')
            game_ts = pd.Timestamp(raw_date).tz_localize(None)

            if after_date is not None and game_ts <= after_ts:
                continue

            player_abbr = _normalize_abbr(ev.get('team', {}).get('abbreviation', ''))
            opp_abbr = _normalize_abbr(ev.get('opponent', {}).get('abbreviation', ''))

            at_vs = ev.get('atVs', 'vs')  # 'vs' = home, '@' = away
            if at_vs == '@':
                matchup = f"{player_abbr} @ {opp_abbr}"
            else:
                matchup = f"{player_abbr} vs. {opp_abbr}"

            # gameResult is 'W' or 'L' directly on the event
            wl = ev.get('gameResult', '')
            if wl not in ('W', 'L'):
                # fall back to score comparison
                try:
                    home_score = int(ev.get('homeTeamScore', 0))
                    away_score = int(ev.get('awayTeamScore', 0))
                    player_team_id = ev.get('team', {}).get('id', '')
                    home_team_id = ev.get('homeTeamId', '')
                    if player_team_id == home_team_id:
                        wl = 'W' if home_score > away_score else 'L'
                    else:
                        wl = 'W' if away_score > home_score else 'L'
                except (TypeError, ValueError):
                    wl = 'L'

            stats_arr = all_stats.get(event_id, [])

            def _stat(idx, default=0.0):
                if idx is None or idx >= len(stats_arr):
                    return default
                try:
                    val = stats_arr[idx]
                    # Some fields like FG are "9-21" — skip those
                    return float(val)
                except (TypeError, ValueError):
                    return default

            rows.append({
                'WL': wl,
                'Date': game_ts,
                'Matchup': matchup,
                'Points': _stat(pts_idx),
                'Rebounds': _stat(reb_idx),
                'Assists': _stat(ast_idx),
                'Minutes': stats_arr[min_idx] if min_idx is not None and min_idx < len(stats_arr) else '0',
            })
        except Exception:
            continue

    if not rows:
        return _EMPTY_STATS

    df = pd.DataFrame(rows).sort_values('Date').reset_index(drop=True)

    if opponent:
        df = df[df['Matchup'].apply(lambda m: _is_opponent_game(m, opponent))]

    return df


def _is_opponent_game(matchup: str, target_opponent: str) -> bool:
    if ' vs. ' in matchup:
        return matchup.split(' vs. ')[1].strip() == target_opponent
    elif ' @ ' in matchup:
        return matchup.split(' @ ')[1].strip() == target_opponent
    return False


def exclude_former_teams(df, former_teams):
    def _keep(matchup):
        for team in former_teams:
            if _is_opponent_game(matchup, team):
                return False
        return True
    return df[df['Matchup'].apply(_keep)]


def get_fair_comparison(espn_athlete_id, former_team_abbr: str, after_date):
    """
    Split game log into revenge games (vs former_team_abbr) and all other games.
    """
    all_games = get_stats(espn_athlete_id, after_date=after_date)

    revenge_games = all_games[all_games['Matchup'].apply(
        lambda m: _is_opponent_game(m, former_team_abbr)
    )]
    non_revenge_games = exclude_former_teams(all_games, [former_team_abbr])

    return revenge_games, non_revenge_games


def compare_stats(revenge_df, regular_df):
    if revenge_df.empty or regular_df.empty:
        return {"error": "Insufficient data for comparison"}

    def _parse_minutes(series):
        def _m(val):
            try:
                if isinstance(val, str) and ':' in val:
                    return float(val.split(':')[0])
                return float(val)
            except (TypeError, ValueError):
                return 0.0
        return series.apply(_m)

    revenge_stats = {
        'points':   float(revenge_df['Points'].mean()),
        'rebounds': float(revenge_df['Rebounds'].mean()),
        'assists':  float(revenge_df['Assists'].mean()),
        'minutes':  float(_parse_minutes(revenge_df['Minutes']).mean()),
        'games':    len(revenge_df),
    }
    regular_stats = {
        'points':   float(regular_df['Points'].mean()),
        'rebounds': float(regular_df['Rebounds'].mean()),
        'assists':  float(regular_df['Assists'].mean()),
        'minutes':  float(_parse_minutes(regular_df['Minutes']).mean()),
        'games':    len(regular_df),
    }
    differences = {
        'points_diff':   revenge_stats['points']   - regular_stats['points'],
        'rebounds_diff': revenge_stats['rebounds'] - regular_stats['rebounds'],
        'assists_diff':  revenge_stats['assists']  - regular_stats['assists'],
        'minutes_diff':  revenge_stats['minutes']  - regular_stats['minutes'],
    }
    return {
        'revenge_stats': revenge_stats,
        'regular_stats': regular_stats,
        'differences':   differences,
    }
