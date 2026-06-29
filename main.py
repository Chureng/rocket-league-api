import requests
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List

class PlayerStats(BaseModel):
    name: str
    score: int
    rank: Optional[str] = None
    mvp: Optional[bool] = False

class TeamStats(BaseModel):
    goals: int
    players: List[PlayerStats]

class ReplayInfo(BaseModel):
    title: str
    map_name: str
    duration: int
    date: str
    uploader: str
    blue: TeamStats
    orange: TeamStats

load_dotenv()

API_KEY = os.getenv("BALLCHASING_API_KEY")

app = FastAPI()

@app.get("/")
def root():
    return {"mensaje": "Rocket League Stats API funcionando"}

@app.get("/player/{player_name}")
def get_player(player_name: str):
    headers = {"Authorization": API_KEY}
    response = requests.get(
        f"https://ballchasing.com/api/replays?player-name={player_name}&count=10",
        headers=headers
    )
    data = response.json()
    
    replays = []
    for replay in data.get("list", []):
        replays.append(ReplayInfo(
            title=replay["replay_title"],
            map_name=replay["map_name"],
            duration=replay["duration"],
            date=replay["date"],
            uploader=replay["uploader"]["name"],
            blue=TeamStats(
                goals=replay["blue"]["goals"],
                players=[
                    PlayerStats(
                        name=p["name"],
                        score=p["score"],
                        rank=p.get("rank", {}).get("name"),
                        mvp=p.get("mvp", False)
                    ) for p in replay["blue"]["players"]
                ]
            ),
            orange=TeamStats(
                goals=replay["orange"]["goals"],
                players=[
                    PlayerStats(
                        name=p["name"],
                        score=p["score"],
                        rank=p.get("rank", {}).get("name"),
                        mvp=p.get("mvp", False)
                    ) for p in replay["orange"]["players"]
                ]
            )
        ))
    
    return replays