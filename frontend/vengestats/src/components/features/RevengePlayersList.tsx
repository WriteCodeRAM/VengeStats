"use client";

import { useState, useEffect } from "react";
import { HorizontalPlayerScroll } from "./HorizontalPlayerScroll";
import { NBARevengePlayer, NFLRevengePlayer } from "@/types/player";

export function RevengePlayersList() {
  const [nbaPlayers, setNBAPlayers] = useState<NBARevengePlayer[]>([]);
  const [nflPlayers, setNFLPlayers] = useState<NFLRevengePlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/matchups`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const nbaPlayers = data.nba_revenge_matchups || [];
        const nflPlayers = data.nfl_revenge_matchups || [];
        const sortedNBAPlayers = nbaPlayers.sort(
          (a: NBARevengePlayer, b: NBARevengePlayer) =>
            b.venge_score - a.venge_score
        );

        const sortedNFLPlayers = nflPlayers.sort(
          (a: NFLRevengePlayer, b: NFLRevengePlayer) =>
            b.venge_score - a.venge_score
        );

        setNBAPlayers(sortedNBAPlayers);
        setNFLPlayers(sortedNFLPlayers);
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
        title="NBA Revenge Games 🏀"
        subtitle={`${nbaPlayers.length} revenge ${
          nbaPlayers.length > 1 || nbaPlayers.length == 0
            ? "matchups"
            : "matchup"
        } in the NBA today`}
        players={nbaPlayers}
      />
      {/* NFL Section */}
      <HorizontalPlayerScroll
        title="NFL Revenge Games 🏈"
        subtitle={`${nflPlayers.length} players seeking vengeance in week 14`}
        players={nflPlayers}
      />
    </div>
  );
}
