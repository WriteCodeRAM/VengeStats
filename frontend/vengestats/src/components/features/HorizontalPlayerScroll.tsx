"use client";

import { PlayerCard } from "./PlayerCard";
import { RevengePlayer } from "@/types/player";

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
            <div key={`${player.player_id}`} className="flex-shrink-0 w-80">
              {console.log("HorizontalPlayerScroll passing player:", player)}
              <PlayerCard
                player={{
                  name: player.name,
                  former_team_name: player.former_team_name,
                  former_team_abbr: player.former_team_abbr,
                  player_id: player.player_id,
                  nba_api_id: player.nba_api_id,
                  nfl_data_id: player.nfl_data_id,
                  injury_status: player.injury_status,
                  venge_score: player.venge_score,
                  record: player.record,
                  total_revenge_games: player.total_revenge_games,
                  current_team_name: player.current_team_name,
                  league: player.league,
                }}
              />
            </div>
          ))}
        </div>

        <div className="absolute top-0 right-0 h-full w-12 bg-gradient-to-l from-dark-bg to-transparent pointer-events-none" />
      </div>
    </div>
  );
}
