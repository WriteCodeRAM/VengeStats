export interface NBAPlayerStats {
  points: number;
  rebounds: number;
  assists: number;
  minutes: number;
  games: number;
}

export interface NBADifferentials {
  revenge_stats: NBAPlayerStats;
  regular_stats: NBAPlayerStats;
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

export interface NBARevengePlayer {
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

export interface NFLRevengePlayer {
  player_id: number;
  nfl_data_id: string;
  name: string;
  position: string;
  former_team_abbr: string;
  former_team_name: string;
  current_team_name: string;
  current_team_abbr?: string;
  record: string;
  total_revenge_games: number;
  games_played: number;
  venge_score: number;
  league: string;
  // legacy / profile-only fields
  player_name?: string;
  display_name?: string;
  current_team_id?: number;
  usage_tier?: string;
  years_exp?: number | null;
  draft_team?: string | null;
  pro_bowl_selections?: number | null;
  all_pro_selections?: number | null;
  former_team_id?: number;
  season_start?: number;
  departure_year?: number;
  total_games_played_for_team?: number;
  injury_status?: string | null;
}

// Minimal shared shape for all leagues -- used by HorizontalPlayerScroll / PlayerCard
export interface RevengePlayer {
  player_id: number;
  name: string;
  former_team_abbr: string;
  former_team_name: string;
  current_team_name: string;
  current_team_abbr?: string;
  venge_score: number;
  league: string;
  // NBA / NFL only
  nba_api_id?: number;
  nfl_data_id?: string;
  injury_status?: string | null;
  record?: string;
  total_revenge_games?: number;
}

export interface WNBARevengePlayer {
  player_id: number;
  name: string;
  espn_athlete_id: string | null;
  current_team_name: string;
  current_team_abbr: string;
  former_team_name: string;
  former_team_abbr: string;
  venge_score: number;
  departure_method: string | null;
  games_for_former: number;
  league: string;
}

export interface PlayerProfileData extends NBARevengePlayer {
  departure_date: string;
  departure_year: number;
  total_games: number;
  wins: number;
  losses: number;
  differentials: NBADifferentials | null;
  history: CareerStint[];
}
