"use client";

import { PlayerCard } from "./PlayerCard";

interface RevengePlayer {
  name: string;
  former_team_name: string;
  former_team_abbr: string;
  injury_status: string;
  venge_score: number;
  departure_date: string;
  departure_year: number;
  record: string;
  total_revenge_games: number;
  player_id: number;
  opponent_team_id: number;
  total_games: number;
  wins: number;
  losses: number;
}

interface HorizontalPlayerScrollProps {
  title: string;
  players: RevengePlayer[];
  subtitle?: string;
}

export function HorizontalPlayerScroll({
  title,
  players,
  subtitle,
}: HorizontalPlayerScrollProps) {
  if (players.length === 0) {
    return (
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          {subtitle && (
            <p className="text-text-secondary text-sm mt-1">{subtitle}</p>
          )}
        </div>
        <div className="text-text-secondary py-8">No revenge games found</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {subtitle && (
          <p className="text-text-secondary text-sm mt-1">{subtitle}</p>
        )}
      </div>

      {/* Horizontal Scrolling Container */}
      <div className="relative">
        <div className="flex gap-6 overflow-x-auto scrollbar-hide pb-4">
          {players.map((player) => (
            <div
              key={`${player.player_id}-${player.opponent_team_id}`}
              className="flex-shrink-0 w-80"
            >
              <PlayerCard
                player={{
                  name: player.name,
                  former_team_name: player.former_team_name,
                  former_team_abbr: player.former_team_abbr,
                  injury_status: player.injury_status,
                  venge_score: player.venge_score,
                  departure_date: player.departure_date,
                  departure_year: player.departure_year,
                  record: player.record,
                  total_revenge_games: player.total_revenge_games,
                  current_team: "TBD",
                }}
              />
            </div>
          ))}
        </div>

        {/* Fade effect on right edge */}
        <div className="absolute top-0 right-0 h-full w-12 bg-gradient-to-l from-dark-bg to-transparent pointer-events-none" />
      </div>
    </div>
  );
}
