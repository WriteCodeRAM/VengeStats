from typing import TypedDict, Optional

class NBARevengeGame(TypedDict):
    player_name: str
    opponent_team: str
    status: Optional[str]  # "Out", "Active", or None
    player_id: int
    opponent_team_id: int
    revenge_score: int