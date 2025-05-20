from typing import TypedDict, Optional

class NBARevengeGame(TypedDict):
    player_name: str
    opponent_team: str
    status: Optional[str]  # "Out", "Active", or None