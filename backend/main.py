import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import redis
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schedule.nba_revenge_pipeline import get_daily_revenge_matchups
from cron.refresh_cache import refresh_cache
from schedule.nfl_revenge_pipeline import get_weekly_revenge_matchups
from db.venge_data import convert_numpy_to_python

app = FastAPI()

# Redis connection - lazy loading
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            print(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://venge-stats-isop1u499-randal-michels-projects.vercel.app",
        "https://vengestats.com",
        "https://www.vengestats.com",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_from_cache(key):
    """Get data from Redis cache"""
    try:
        client = get_redis_client()
        if not client:
            return None
        data = client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis get error: {e}")
        return None

def set_in_cache(key, data, expiry=3600):  
    """Set data in Redis cache with expiry"""
    try:
        client = get_redis_client()
        if not client:
            return
        client.setex(key, expiry, json.dumps(data, default=str))
    except Exception as e:
        print(f"Redis set error: {e}")

@app.get("/matchups")
async def matchups():
    cached_matchups = get_from_cache("all_matchups")
    if cached_matchups:
        print("Returning cached matchups")
        return cached_matchups
    
    print("Generating fresh matchups...")
    
    # generate NBA matchups
    nba_revenge_games = get_daily_revenge_matchups()
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
        # Cache NBA player profiles until October 21 
        cleaned_player = convert_numpy_to_python(player)
        set_in_cache(f"nba_player_{player['player_id']}", cleaned_player, 4233600)

    # generate NFL matchups  
    nfl_revenge_games = get_weekly_revenge_matchups()
    lightweight_nfl_games = []
    
    for player in nfl_revenge_games: 
        lightweight_nfl_games.append({ 
            "player_id": player["player_id"],
            "current_team_name": player["current_team_abbr"], 
            "record": player["record"],
            "nfl_data_id": player["nfl_data_id"],
            "name": player["name"], 
            "position": player["position"], 
            "former_team_abbr": player["former_team_abbr"], 
            "former_team_name": player["former_team_name"],
            "games_played": player["total_games_played_for_team"], 
            "total_revenge_games": player["total_revenge_games"],
            "venge_score": player["revenge_score"], 
            "league": "nfl"
        })
        # Cache NFL player profiles for 1 week (604800 seconds)
        cleaned_player = convert_numpy_to_python(player)
        set_in_cache(f"nfl_player_{player['player_id']}", cleaned_player, 604800)

    matchups_data = {
        "nba_revenge_matchups": lightweight_nba_games,
        "nfl_revenge_matchups": lightweight_nfl_games
    }
    
    # NBA data stays static until October 21st anyways
    set_in_cache("all_matchups", matchups_data, 604800)
    
    return matchups_data

@app.get("/nba/player/{player_id}")
async def get_nba_player_profile(player_id: int):
    cached_player = get_from_cache(f"nba_player_{player_id}")
    if cached_player:
        return cached_player
    
    raise HTTPException(status_code=404, detail="Player not found") 

@app.get("/nfl/player/{player_id}")
async def get_nfl_player_profile(player_id: int):
    cached_player = get_from_cache(f"nfl_player_{player_id}")
    if cached_player:
        return cached_player
        
    raise HTTPException(status_code=404, detail="Player not found")

@app.get("/cache/clear/{cache_key}")
async def clear_cache(cache_key: str):
    expected_key = os.getenv('CACHE_KEY')
    
    if not expected_key or cache_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        client = get_redis_client()
        if client:
            client.flushall()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        return {"error": f"Failed to clear cache: {e}"}

@app.get("/cache/status")
async def cache_status():
    """Check cache status"""
    try:
        client = get_redis_client()
        if not client:
            return {"connected": False, "error": "Redis client not available"}
        info = client.info()
        keys = client.keys("*")
        return {
            "connected": True,
            "total_keys": len(keys),
            "memory_usage": info.get("used_memory_human", "Unknown"),
            "keys": keys[:20] 
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

@app.get("/cron/refresh-cache/{cache_key}")
async def cron_refresh(cache_key):
    expected_key = os.getenv('CACHE_KEY')
    if not expected_key or cache_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    refresh_cache()
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)