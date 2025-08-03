export interface PlayerStats {
  points: number;
  rebounds: number;
  assists: number;
  minutes: number;
  games: number;
}

export interface Differentials {
  revenge_stats: PlayerStats;
  regular_stats: PlayerStats;
  differences: {
    points_diff: number;
    rebounds_diff: number;
    assists_diff: number;
    minutes_diff: number;
  };
}

export interface CareerStint {
  team_abbr: string;
  team_full_name: string;
  start_year: number;
  end_year: number | null;
  games_played: number;
  is_current: boolean;
}

export interface RevengePlayer {
  player_id: number;
  nba_api_id: number;
  name: string;
  former_team_abbr: string;
  former_team_name: string;
  current_team_name: string;
  venge_score: number;
  injury_status: string | null;
  record: string;
  total_revenge_games: number;
  league: string;
}

export interface PlayerProfileData extends RevengePlayer {
  departure_date: string;
  departure_year: number;
  total_games: number;
  wins: number;
  losses: number;
  differentials: Differentials | null;
  history: CareerStint[];
}
