from backend.schedule.nba_revenge_pipeline import get_daily_revenge_matchups
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# bootleg cache for now upgrade to redis soon
cache = {"nba_revenge_matchups": None, "nfl_revenge_matchups": "Coming Soon..."} 
nba_player_profiles_cache = {}

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
        revenge_games = get_daily_revenge_matchups()
        
        # full data in profiles cache
        for player in revenge_games:
            nba_player_profiles_cache[player["player_id"]] = player
        
        # lightweight data for home page
        lightweight_games = []
        for player in revenge_games:
            lightweight_games.append({
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
                "league": "NBA"
            })
        
        cache["nba_revenge_matchups"] = lightweight_games
    
    return cache

@app.get("/nba/player/{player_id}")
async def get_nba_player_profile(player_id: int):
    if player_id in nba_player_profiles_cache:
        return nba_player_profiles_cache[player_id]
    raise HTTPException(status_code=404, detail="Player not found") 
