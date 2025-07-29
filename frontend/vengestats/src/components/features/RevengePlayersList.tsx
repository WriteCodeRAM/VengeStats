"use client";

import { useState, useEffect } from "react";
import { HorizontalPlayerScroll } from "./HorizontalPlayerScroll";

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

export function RevengePlayersList() {
  const [nbaPlayers, setNbaPlayers] = useState<RevengePlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:8000/matchups");

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("API Response:", data);

        const nbaPlayers = data.nba_revenge_matchups || [];
        const sortedPlayers = nbaPlayers.sort(
          (a: RevengePlayer, b: RevengePlayer) => b.venge_score - a.venge_score
        );

        setNbaPlayers(sortedPlayers);
      } catch (err) {
        console.error("Failed to fetch players:", err);
        setError(
          err instanceof Error ? err.message : "Failed to fetch players"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-text-secondary">Loading revenge games...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-venge-red">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      {/* NBA Section */}
      <HorizontalPlayerScroll
        title="NBA Revenge Games"
        subtitle={`${nbaPlayers.length} players seeking vengeance today`}
        players={nbaPlayers}
      />

      {/* NFL Section - Coming Soon */}
      <HorizontalPlayerScroll
        title="NFL Revenge Games"
        subtitle="Coming soon..."
        players={[]} // Empty for now
      />
    </div>
  );
}
