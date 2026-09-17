# VengeStats CLAUDE.md

## What VengeStats Is

VengeStats is the **StatMuse of revenge games**, the definitive platform for detecting, scoring, and surfacing revenge narratives across professional sports. Every time a player faces a former team, VengeStats finds it, quantifies it, and tells the story. The goal is to be the #1 revenge platform in the world: if a revenge narrative is forming, VengeStats should know about it before the broadcast does.

The brand voice is confident, sharp, and data-driven. Not sensational, but earned. Think StatMuse meets The Ringer. The product is for sports fans who want the story behind the stat.

---

## Tech Stack

### Backend (Python / FastAPI)
- **FastAPI** : REST API server (`backend/main.py`)
- **PostgreSQL** : primary data store
- **Redis** : caching layer (7-day TTL for matchups, long TTL for player profiles)
- **ESPN APIs** : all live sports data (stats.nba.com is permanently blocked; never use it)
  - NBA rosters: `http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{id}/roster`
  - NBA game logs: `https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{id}/gamelog`
  - NFL: ESPN Data Py library
  - WNBA: ESPN WNBA endpoints (parallel structure to NBA)
- **nba_api** library : only for `players.find_players_by_full_name()` (static lookup); never for stats or game logs
- **Deployed on Railway** (backend) and **Vercel** (frontend)

### Frontend (Next.js / TypeScript)
- **Next.js 14 App Router**
- **Tailwind CSS** : custom design tokens (see Brand section below)
- **shadcn/ui** components (`Card`, `Badge`)
- **`next/image`** : approved CDN domains: `cdn.nba.com`, `a.espncdn.com`

---

## Repository Structure

```
VengeStats/
├── backend/
│   ├── main.py                        # FastAPI app, Redis cache, all routes
│   ├── db/
│   │   ├── venge_data.py              # VengeScore calculation, notable narratives
│   │   └── queries/
│   │       ├── revenge_games.py       # Core NBA/NFL/WNBA revenge detection SQL
│   │       ├── nba/players.py         # NBA player DB ops (unicode-normalized lookups)
│   │       ├── nfl/                   # NFL player/team queries
│   │       └── wnba/players.py        # WNBA player DB ops (partial)
│   ├── schedule/
│   │   ├── nba_revenge_pipeline.py    # NBA daily revenge matchups (hardcoded offseason)
│   │   ├── nfl_revenge_pipeline.py    # NFL weekly revenge matchups (hardcoded offseason)
│   │   └── wnba_revenge_pipeline.py   # WNBA pipeline (skeleton, not wired to API yet)
│   ├── nba_utils/utils/
│   │   ├── player_utils.py            # ESPN athlete ID map, stint fetching via ESPN
│   │   ├── smart_stint_sync.py        # Syncs stints for players flagged needs_stint_refresh
│   │   ├── roster_sync.py             # Syncs NBA rosters from ESPN
│   │   ├── data_fetcher.py            # get_stats() : currently returns empty (ESPN impl pending)
│   │   └── weekly_sync.py             # Orchestrates weekly roster + stint sync
│   ├── nfl_api/                       # NFL data via ESPN Data Py
│   ├── wnba/
│   │   ├── rosters.py                 # WNBA roster fetcher (ESPN-based, written last session)
│   │   └── seeder/                    # DB seed scripts for WNBA teams/players
│   ├── scrapers/injury_scrapers.py    # NBA injury status scraping
│   └── bot/                           # Twitter/X bot (@VengeStats)
└── frontend/vengestats/src/
    ├── app/
    │   ├── page.tsx                   # Homepage
    │   ├── nba/player/[id]/page.tsx   # NBA player profile
    │   └── nfl/player/[id]/page.tsx   # NFL player profile
    └── components/features/
        ├── RevengePlayersList.tsx     # Fetches /matchups, splits NBA/NFL
        ├── HorizontalPlayerScroll.tsx # Horizontal card scroll per league
        └── PlayerCard.tsx             # Individual player card (logo, VengeScore, record)
```

---

## Brand

### Colors (Tailwind tokens)
| Token | Hex | Use |
|---|---|---|
| `venge-red` | `#BE181A` | Primary accent, VengeScore badges ≥ 8 |
| `dark-bg` | `#09153F` | Page background (deep navy) |
| `dark-card` | `#1A1F2E` | Card background |
| `text-primary` | `#FFFFFF` | Headings, player names |
| `text-secondary` | (inferred gray) | Labels, metadata |
| `amber-500` | Tailwind default | VengeScore 6–7 |
| `blue-500` | Tailwind default | VengeScore < 6 |

### Typography
- Font: **Sora** (Google Fonts)
- Style: clean, modern, confident. No fluff.

### Logo
- `/public/logo.png` is the primary brand mark
- Team logos: local `/public/nba_logos/{abbreviation}.png` for NBA; ESPN CDN `https://a.espncdn.com/i/teamlogos/nfl/500/{abbr}.png` for NFL; WNBA should use ESPN CDN `https://a.espncdn.com/i/teamlogos/wnba/500/{abbr}.png`

### Voice / Copy
- Section labels: `"NBA Revenge Games 🏀"`, `"NFL Revenge Games 🏈"`
- Off-season placeholder text: matches pattern `"NFL Revenge Game Tracking Will Return September, 9, 2026!"`
- Keep it punchy. Revenge is personal, write like it is.

---

## VengeScore

Scored 1–10. Higher = more compelling revenge narrative.

| Factor | Max Points |
|---|---|
| Tenure ratio (games with former team / career games) | 3.0 |
| Former team bonus (last team before current) | 1.5 |
| First-time revenge game | 1.0 |
| All-Star status | 1.0 |
| Notable revenge narrative (hand-curated list) | 2.0 |
| Departure method modifier (Traded/Waived/Cut) | varies |

Source: `backend/db/venge_data.py`

Notable narratives and All-Star lists in `venge_data.py` must be updated each season. Notable narratives are a dict of `{player_name: {set of opponent team IDs}}`.

---

## Data Sources & Rules

### What works
- **ESPN APIs** : rosters, game logs, schedules for NBA/NFL/WNBA. Always prefer ESPN.
- **ESPN Data Py** : NFL player/team data
- **nba_api static helpers** : `players.find_players_by_full_name()` only

### What is permanently dead
- **stats.nba.com** : completely blocked (curl exit 28, no response). `data_fetcher.get_stats()` returns an empty DataFrame stub. Do not attempt to revive it. The path forward is an ESPN-based stats implementation.

### ID systems
- **NBA internal team IDs** (1–30): our system. Mapped to ESPN team IDs in `TEAM_ID_TO_ESPN_ID` in `player_utils.py`.
- **NFL team IDs**: match ESPN IDs directly. Always stored/passed as **strings** (`"17"` not `17`).
- **ESPN season year convention**: end-year (`2026` = 2025–26 season). Season type 2 = regular, 3 = playoffs.
- **prev_team_id**: critical field on `nba_players`. Drives revenge detection. Source of truth is `nba_player_team_stints_api`; always cross-reference stints when something looks wrong.

---

## League Implementation Status

| League | Rosters | Stints | Stats | Revenge Detection | Pipeline | Frontend |
|---|---|---|---|---|---|---|
| NBA | ESPN ✅ | ESPN ✅ | ❌ (stub) | ✅ | ✅ | ✅ |
| NFL | ESPN Data Py ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WNBA | ESPN ✅ (written) | ❌ | ❌ | ❌ | Skeleton | ❌ |

### WNBA Next Steps
WNBA work was started but paused. The roster fetcher exists (`backend/wnba/rosters.py`) and uses ESPN, but the seeder still calls `stats.nba.com` (broken). To complete WNBA:
1. Replace seeder `stats.nba.com` calls with ESPN WNBA endpoints (mirror NBA ESPN pattern)
2. Build `wnba_player_team_stints_api` table + sync logic
3. Wire `wnba_revenge_pipeline.py` to actual DB queries (currently a skeleton)
4. Add WNBA section to frontend (`RevengePlayersList`, player profile page)
5. Add WNBA team logos (ESPN CDN: `https://a.espncdn.com/i/teamlogos/wnba/500/{abbr}.png`)
6. Update `main.py` to include WNBA matchups in `/matchups` response

---

## Season Calendar (reference)

| League | Season Start | Offseason |
|---|---|---|
| NBA | Mid-October | June–October |
| NFL | Early September | February–August |
| WNBA | Mid-May | October–April |

During offseason, matchups are **hardcoded** in the pipeline files to showcase the product. Update them before each season opens with the real opening-week slate fetched from ESPN scoreboard API.

### Update cadence (in-season)
- **NFL**: Update matchups every **Tuesday** for the upcoming week's slate. Hardcode all 16 games in `nfl_revenge_pipeline.py`, commit, push, then hit `POST /cron/refresh-cache/{CACHE_KEY}` to regenerate.
- **NBA**: Update matchups every **night at midnight**. During the season the matchups should reflect that day's games. Hit the cache refresh endpoint nightly.
- **Cache refresh endpoint**: `POST https://vengestats-production.up.railway.app/cron/refresh-cache/{CACHE_KEY}` (key is in Railway env vars)

---

## Departure Methods

Every player stint in `nfl_player_stints` and `nba_player_team_stints_api` has a `departure_method` field. This field drives the VengeScore modifier and the tweet copy. **Always look up the real departure story before writing it to the DB.**

### How to update
```python
UPDATE nfl_player_stints SET departure_method = 'Released'
WHERE player_id = (SELECT id FROM nfl_players WHERE display_name = 'Player Name')
AND team_id = (SELECT id FROM nfl_teams WHERE team_abbreviation = 'XXX');
```

### Valid values and their meaning
| Value | Meaning | VengeScore impact |
|---|---|---|
| `Released` | Team cut the player, often to sign someone else | +1.0 (most personal) |
| `Traded` | Team traded the player away | +0.8 |
| `Free Agent` | Contract expired, player left on own terms | +0.2 |
| `NULL` | Unknown, needs research | +0.2 (same as FA fallback) |

**Rule**: whenever a player surfaces in a revenge matchup with `departure_method = NULL`, look up the real story (search "[Player] [Team] departure/trade/released/cut") and update the DB before tweeting. Never tweet a departure method you haven't verified.

---

## Running Locally

```bash
# Backend
cd backend
uvicorn main:app --reload --port 8000

# Frontend
cd frontend/vengestats
npm run dev
```

API base: `http://localhost:8000` (set via `NEXT_PUBLIC_API_URL` env var for prod).

### Key env vars (backend)
- `DATABASE_URL` : PostgreSQL connection string
- `REDIS_URL` : Redis connection string (default `redis://localhost:6379`)
- `CACHE_KEY` : secret for cache-clear and cron endpoints
- `PORT` : server port (default 8000)

---

## Architectural Principles

1. **Cache everything.** The `/matchups` endpoint is cached in Redis. Player profiles are cached on first load. Never hit the DB or external APIs on repeat requests.
2. **ESPN is the source of truth.** Any time external sports data is needed, reach for ESPN first.
3. **Revenge detection lives in SQL.** `backend/db/queries/revenge_games.py` contains the core logic. The pipeline files orchestrate and enrich; they don't detect.
4. **The VengeScore is the product.** Every feature decision should ask: does this make the VengeScore more accurate or more compelling?
5. **StatMuse benchmark.** If StatMuse would show a graphic for it, VengeStats should surface it for revenge games. The bar is: instant, visual, shareable.
6. **Notify before the broadcast.** Detection pipelines should run on game-day morning so the site is populated before tip-off/kickoff. Twitter bot fires on the same cadence.

---

## Common Gotchas

- `current_team_name` in the NBA pipeline is the full name (e.g. `"Boston Celtics"`) but NBA logos are keyed by **abbreviation** (e.g. `"BOS"`). The matchup dict has both `current_team_name` and `current_team_abbr`; use `current_team_abbr` for logo lookups.
- NFL player dicts use `'league': 'NFL'` (uppercase). Frontend checks `player.league?.toLowerCase() === "nfl"`.
- NFL team IDs are always strings. If you see an int, convert it.
- `nba_player_team_stints_api` is the career stint table. `nba_players.prev_team_id` is derived from it; if they disagree, the stints table wins.
- `notable_revenge_narratives` in `venge_data.py` uses internal team IDs (not ESPN IDs). Keep this in sync when teams are added.
- Twitter bot lives in `backend/bot/` and posts on `@VengeStats`. Do not run it locally against the production account without intent.

---

## Tweet Format

### NFL Weekly Revenge Tweet
Post the top 2 players by VengeScore only. Skip players with mid scores (under ~6.5) unless the narrative is strong.

```
WEEK {N} NFL REVENGE GAMES 🏈

🔥 {Player Name} ({Current Team}) vs {Former Team} [{Departure Method}] — VengeScore: {X.X}
🔥 {Player Name} ({Current Team}) vs {Former Team} [{Departure Method}] — VengeScore: {X.X}

{One punchy line about the top player's narrative. Make it personal.}

#NFLSunday #NFL vengestats.com
```

**Rules:**
- Departure method must be verified in DB before posting (see Departure Methods section)
- VengeScore stands alone per player, never combined or shown as a ratio
- One narrative line max, focused on the top player
- Use `#TNF` instead of `#NFLSunday` for Thursday Night Football games
- `#MNF` for Monday Night Football

### NBA Nightly Revenge Tweet
Same format, swap NFL emoji for 🏀 and hashtags for `#NBA`.
