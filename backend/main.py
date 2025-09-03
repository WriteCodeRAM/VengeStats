import sys
import os
import psycopg2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import redis
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schedule.nba_revenge_pipeline import get_daily_revenge_matchups
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
    allow_origins=["http://localhost:3000"],
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

@app.get("/")
async def root():
    return {"message": "Yo"}

@app.get("/test-db")
async def test_db():
    db_url = os.getenv("DATABASE_URL")
    print("Raw DB URL:", db_url)  # debug 

    try:
        # psycopg2 sometimes prefers 'postgres://' instead of 'postgresql://'
        if db_url and db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgres://", 1)

        conn = psycopg2.connect(db_url)
        with conn.cursor() as cur:
            cur.execute("SELECT NOW();")  
            ts = cur.fetchone()
        conn.close()

        return {"db_status": "connected", "time": str(ts[0])}
    except Exception as e:
        return {"db_status": "failed", "error": str(e)}

@app.get("/matchups")
async def matchups():
    try:
        # Debug database connection
        db_url = os.getenv('DATABASE_URL')
        print(f"DATABASE_URL exists: {db_url is not None}")
        print(f"DATABASE_URL starts with: {db_url[:20] if db_url else 'None'}")
        
        nba_revenge_games = get_daily_revenge_matchups()
        return {"status": "NBA worked", "count": len(nba_revenge_games)}
    except Exception as e:
        print(f"Full error: {e}")
        return {"error": f"NBA pipeline failed: {str(e)}"}

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

@app.get("/cache/clear")
async def clear_cache():
    """Clear all cache - useful for development"""
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)