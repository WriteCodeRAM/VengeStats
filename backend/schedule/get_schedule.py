from typing import List, Tuple
import requests
import datetime
from db.queries.nba.teams import teams

ESPN_NBA_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

# ESPN team ID → our internal NBA team ID (inverted from player_utils.TEAM_ID_TO_ESPN_ID)
ESPN_TEAM_ID_TO_INTERNAL = {
    "1":  1,  "2":  2,  "17": 3,  "30": 4,  "4":  5,
    "5":  6,  "6":  7,  "7":  8,  "8":  9,  "9":  10,
    "10": 11, "11": 12, "12": 13, "13": 14, "29": 15,
    "14": 16, "15": 17, "16": 18, "3":  19, "18": 20,
    "25": 21, "19": 22, "20": 23, "21": 24, "22": 25,
    "23": 26, "24": 27, "28": 28, "26": 29, "27": 30,
}

def get_nba_schedule() -> List[List[int]]:
    """Return today's NBA matchups as [[away_internal_id, home_internal_id], ...]."""
    try:
        resp = requests.get(ESPN_NBA_SCOREBOARD, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Failed to fetch NBA schedule from ESPN: {e}")
        return []

    matchups = []
    for event in data.get("events", []):
        comps = event["competitions"][0]
        competitors = comps["competitors"]
        try:
            away = next(c for c in competitors if c["homeAway"] == "away")
            home = next(c for c in competitors if c["homeAway"] == "home")
            away_id = ESPN_TEAM_ID_TO_INTERNAL.get(away["team"]["id"])
            home_id = ESPN_TEAM_ID_TO_INTERNAL.get(home["team"]["id"])
            if away_id and home_id:
                matchups.append([away_id, home_id])
        except (KeyError, StopIteration):
            continue

    return matchups


def get_team_ids(schedule: List) -> List[Tuple[int, int]]:
    """Legacy helper kept for compatibility. Returns schedule as list of tuples."""
    return [(m[0], m[1]) for m in schedule]
