"""Read-only audit of tonight's NBA slate. Prints every issue that needs a DB fix before the cache refresh.

Usage (from backend/):  python -m scripts.nba_audit [YYYYMMDD]
"""
import sys
from collections import defaultdict

import requests

from db.database import get_connection
from db.queries.nba.teams import team_id_to_abbr
from db.queries.revenge_games import get_nba_revenge_games
from nba_utils.utils.player_utils import TEAM_ID_TO_ESPN_ID, _norm
from schedule.get_schedule import get_nba_schedule

ROSTER_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{}/roster"


def abbr(team_id):
    return team_id_to_abbr.get(team_id, f"#{team_id}")


def audit_rosters(cur, team_ids):
    """Players on tonight's ESPN rosters whose DB current team is wrong."""
    cur.execute("SELECT id, first_name || ' ' || last_name, current_team_id, active FROM nba_players")
    by_name = defaultdict(list)
    for pid, name, team, active in cur.fetchall():
        by_name[_norm(name)].append((pid, name, team, active))

    issues = []
    espn_names = {}
    for tid in team_ids:
        athletes = requests.get(ROSTER_URL.format(TEAM_ID_TO_ESPN_ID[tid]), timeout=10).json().get("athletes", [])
        for a in athletes:
            espn_names[_norm(a["fullName"])] = tid
            rows = by_name.get(_norm(a["fullName"]), [])
            if not rows:
                issues.append(f"MISSING FROM DB: {a['fullName']} is on {abbr(tid)} per ESPN")
            elif len(rows) > 1:
                ids = ", ".join(f"id {r[0]} '{r[1]}' team={abbr(r[2])}" for r in rows)
                issues.append(f"DUPLICATE ROWS: {a['fullName']} ({ids}); ESPN says {abbr(tid)}")
            elif rows[0][2] != tid:
                pid, name, team, _ = rows[0]
                issues.append(f"WRONG CURRENT TEAM: {name} (id {pid}) DB={abbr(team)} ESPN={abbr(tid)}")

    cur.execute("SELECT id, first_name || ' ' || last_name, current_team_id FROM nba_players WHERE current_team_id = ANY(%s)",
                (list(team_ids),))
    for pid, name, team in cur.fetchall():
        if espn_names.get(_norm(name)) is None:
            issues.append(f"NOT ON ESPN ROSTER: {name} (id {pid}) DB={abbr(team)}; moved, waived or retired?")
    return issues


def audit_player(cur, player_id):
    cur.execute("SELECT first_name || ' ' || last_name, current_team_id, prev_team_id FROM nba_players WHERE id=%s", (player_id,))
    name, current, prev = cur.fetchone()
    cur.execute("""SELECT id, team_id, first_game_date, last_game_date, games_played, departure_method, is_current
                   FROM nba_player_team_stints_api WHERE player_id=%s ORDER BY first_game_date""", (player_id,))
    stints = cur.fetchall()

    lines = [f"{name} (id {player_id}) current={abbr(current)} prev={abbr(prev)}"]
    for sid, team, start, end, gp, method, is_cur in stints:
        lines.append(f"    [stint {sid}] {abbr(team):4} {start} -> {end or '...'}  gp={gp:<4} {method or 'NULL':10} {'CURRENT' if is_cur else ''}")

    flags = []
    currents = [s for s in stints if s[6]]
    if len(currents) != 1:
        flags.append(f"{len(currents)} stints marked is_current (expected 1)")
    if stints and stints[-1][1] != current:
        flags.append(f"latest stint is {abbr(stints[-1][1])} but current team is {abbr(current)}: missing stint for current team")
    for sid, team, *_, method, is_cur in stints:
        if not is_cur and not method:
            flags.append(f"NULL departure_method on {abbr(team)} stint {sid}")
    past = [s for s in stints if s[1] != current]
    if past and prev != past[-1][1]:
        flags.append(f"prev_team_id={abbr(prev)} but most recent former team is {abbr(past[-1][1])}")
    lines += [f"    !! {f}" for f in flags]
    return lines, bool(flags)


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else None
    matchups = get_nba_schedule(date)
    if not matchups:
        print("NO NBA GAMES")
        return
    print("SLATE:", ", ".join(f"{abbr(a)} @ {abbr(h)}" for a, h in matchups))
    team_ids = {t for m in matchups for t in m}

    with get_connection() as conn, conn.cursor() as cur:
        print("\n=== ROSTER CHECK (tonight's teams vs ESPN) ===")
        roster_issues = audit_rosters(cur, team_ids)
        print("\n".join(roster_issues) or "clean")

        print("\n=== REVENGE PLAYER HISTORIES ===")
        flagged = 0
        seen = set()
        for row in get_nba_revenge_games(matchups):
            player_id, opponent = row[3], row[4]
            if player_id in seen:
                continue
            seen.add(player_id)
            lines, has_flags = audit_player(cur, player_id)
            flagged += has_flags
            print(f"\n[vs {abbr(opponent)}] " + "\n".join(lines))

    print(f"\nSUMMARY: {len(roster_issues)} roster issues, {flagged}/{len(seen)} revenge players flagged")


if __name__ == "__main__":
    main()
