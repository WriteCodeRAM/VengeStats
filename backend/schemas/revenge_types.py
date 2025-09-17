from typing import List, Dict, Any, TypedDict, Optional, Union
from datetime import datetime

class NFLRevengePlayer(TypedDict):
    player_id: int
    name: str  
    nfl_data_id: str
    display_name: str
    current_team_id: int
    position: str
    usage_tier: str
    years_exp: Optional[int]
    draft_team: Optional[str]
    pro_bowl_selections: Optional[int]
    all_pro_selections: Optional[int]
    former_team_name: str
    former_team_abbr: str  
    opponent_team_id: int
    current_team_name: str 
    current_team_abbr: str  
    season_start: int
    departure_year: int
    departure_method: str
    total_games_played_for_team: int
    
    # PlayerCard interface fields
    injury_status: str
    revenge_score: Optional[float]
    record: str
    total_revenge_games: int
    league: str

    
class NBARevengePlayer(TypedDict):
    player_name: str          
    former_team_name: str      
    injury_status: Optional[str]  
    player_id: int            
    opponent_team_id: int     
    revenge_score: Optional[float]  
    departure_date: str        


class EnrichedNBARevengePlayer(NBARevengePlayer):
    name: str                  # Alias for player_name
    former_team_abbr: str      # Team abbreviation
    current_team_name: str     # Current team full name
    current_team_abbr: str     # Current team abbreviation
    nba_api_id: str           # NBA API player ID
    venge_score: Optional[float]  # Calculated revenge score
    departure_year: int        # Year they left the team
    total_games: int          # Total games played against former team
    wins: int                 # Wins against former team
    losses: int               # Losses against former team
    total_revenge_games: int  # Total revenge games played
    record: str               # Win-loss record as string (e.g., "3-2")
    differentials: Optional[Dict[str, Any]]  # Performance differentials
    history: List[Dict[str, Any]]  # Game history   


class NBARevengeGame(TypedDict):
    player_name: str
    opponent_team: str
    status: Optional[str]  # "Out", "Active", or None
    player_id: int
    opponent_team_id: int
    revenge_score: int