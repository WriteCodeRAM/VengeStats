from fastapi import FastAPI
from backend.schedule.nba_revenge_pipeline import get_daily_revenge_matchups
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    revenge_games = get_daily_revenge_matchups()
    return {"nba_revenge_matchups": revenge_games, "nfl_revenge_matchups": "Coming Soon..."}