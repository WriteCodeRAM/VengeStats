from backend.schedule.nba_revenge_pipeline import get_daily_revenge_matchups
from backend.schedule.nfl_revenge_pipeline import get_weekly_revenge_matchups
from backend.db.venge_data import convert_numpy_to_python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# bootleg cache for now upgrade to redis soon
cache = {"nba_revenge_matchups": None, "nfl_revenge_matchups": None} 
nba_player_profiles_cache = {}
nfl_player_profiles_cache = {} 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Yo"}

@app.get("/matchups")
async def matchups():
    if not cache["nba_revenge_matchups"]: 
        nba_revenge_games = get_daily_revenge_matchups()

        
        # lightweight data for home page
        lightweight_nba_games = []
        for player in nba_revenge_games:
            lightweight_nba_games.append({
                "player_id": player["player_id"],
                "name": player["name"],
                "former_team_abbr": player["former_team_abbr"], 
                "former_team_name": player["former_team_name"],
                "current_team_name": player["current_team_abbr"],
                "nba_api_id": player["nba_api_id"],
                "venge_score": player["venge_score"],
                "injury_status": player["injury_status"],
                "record": player["record"],
                "total_revenge_games": player["total_revenge_games"], 
                "league": "nba"
            })
            nba_player_profiles_cache[player["player_id"]] = player

        cache["nba_revenge_matchups"] = lightweight_nba_games

    if not cache["nfl_revenge_matchups"]:
        
        lightweight_nfl_games = [] 
        nfl_revenge_games = get_weekly_revenge_matchups() 

        for player in nfl_revenge_games: 
            lightweight_nfl_games.append({ 
                "player_id": player["player_id"],
                "current_team_name": player["current_team_abbr"], 
                "record": player["record"],
                "nfl_data_id": player["nfl_data_id"],
                "name": player["name"], 
                "position": player["position"], 
                "former_team_abbr": player["former_team_abbr"], 
                "games_played": player["total_games_played_for_team"], 
                "total_revenge_games": player["total_revenge_games"],
                "venge_score": player["revenge_score"], 
                "league": "nfl"
            })

            # clean numpy types before caching
            cleaned_player = convert_numpy_to_python(player)
            nfl_player_profiles_cache[player["player_id"]] = cleaned_player
            
        cache["nfl_revenge_matchups"] = lightweight_nfl_games
        print(nfl_player_profiles_cache)

    return cache

@app.get("/nba/player/{player_id}")
async def get_nba_player_profile(player_id: int):
    if player_id in nba_player_profiles_cache:
        return nba_player_profiles_cache[player_id]
    raise HTTPException(status_code=404, detail="Player not found") 

@app.get("/nfl/player/{player_id}")
async def get_nfl_player_profile(player_id: int):
    if player_id in nfl_player_profiles_cache:
        return nfl_player_profiles_cache[player_id]
    raise HTTPException(status_code=404, detail="Player not found") 