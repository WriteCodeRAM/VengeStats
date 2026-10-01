from db.queries.revenge_games import get_wnba_revenge_games
from db.venge_data import calculate_wnba_venge_score
from db.database import get_connection


def _get_wnba_career_games(player_id: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(SUM(games_played), 0) FROM wnba_player_stints WHERE player_id = %s",
                (player_id,)
            )
            return cursor.fetchone()[0]


def _get_games_for_team(player_id: int, team_id: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(SUM(games_played), 0) FROM wnba_player_stints WHERE player_id = %s AND team_id = %s",
                (player_id, team_id)
            )
            return cursor.fetchone()[0]


def _get_career_history(player_id: int) -> list:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.abbreviation, t.name,
                       EXTRACT(YEAR FROM s.first_game_date)::int,
                       EXTRACT(YEAR FROM s.last_game_date)::int,
                       s.games_played, s.is_current
                FROM wnba_player_stints s
                JOIN wnba_teams t ON t.id = s.team_id
                WHERE s.player_id = %s
                ORDER BY s.first_game_date
            """, (player_id,))
            return [
                {
                    'team_abbr': row[0],
                    'team_full_name': row[1],
                    'start_year': row[2],
                    'end_year': row[3],
                    'games_played': row[4],
                    'is_current': row[5],
                }
                for row in cursor.fetchall()
            ]


def _get_prev_team_id(player_id: int) -> int | None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT prev_team_id FROM wnba_players WHERE id = %s",
                (player_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None


def get_wnba_revenge_matchups():
    # WNBA 2026 Postseason (First Round + Semifinals)
    # Sept 30 - Oct 2, 2026 games pulled from ESPN scoreboard
    # Format: [away_team_id, home_team_id] using internal DB IDs
    matchups = [
        [1, 15],  # ATL @ WSH
        [5, 4],   # GS @ DAL
        [6, 7],   # IND @ LV
        [4, 5],   # DAL @ GS
    ]

    raw_players = get_wnba_revenge_games(matchups)
    enriched = []
    seen_player_ids = set()

    for row in raw_players:
        # row: (player_id, first_name, last_name, current_team_name, former_team_name,
        #        opponent_team_id, most_recent_departure, departure_method,
        #        espn_athlete_id, current_team_abbr, former_team_abbr)
        (player_id, first_name, last_name, current_team_name, former_team_name,
         opponent_team_id, most_recent_departure, departure_method,
         espn_athlete_id, current_team_abbr, former_team_abbr) = row

        name = f"{first_name} {last_name}"
        if player_id in seen_player_ids:
            continue
        seen_player_ids.add(player_id)

        career_games = _get_wnba_career_games(player_id)
        games_for_former = _get_games_for_team(player_id, opponent_team_id)
        prev_team_id = _get_prev_team_id(player_id)
        is_prev_team = (prev_team_id == opponent_team_id)

        venge_score, _ = calculate_wnba_venge_score(
            player_id=player_id,
            player_name=name,
            opponent_team_id=opponent_team_id,
            games_played_for_former=games_for_former,
            total_career_games=career_games,
            is_prev_team=is_prev_team,
            departure_method=departure_method,
        )

        history = _get_career_history(player_id)

        enriched.append({
            'player_id': player_id,
            'name': name,
            'espn_athlete_id': espn_athlete_id,
            'current_team_name': current_team_name,
            'current_team_abbr': current_team_abbr,
            'former_team_name': former_team_name,
            'former_team_abbr': former_team_abbr,
            'opponent_team_id': opponent_team_id,
            'venge_score': venge_score,
            'departure_method': departure_method,
            'games_for_former': games_for_former,
            'career_games': career_games,
            'departure_date': str(most_recent_departure) if most_recent_departure else None,
            'history': history,
        })

    return enriched
