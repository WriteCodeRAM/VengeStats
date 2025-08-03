"use client";

import { useState, useEffect } from "react";
import { HorizontalPlayerScroll } from "./HorizontalPlayerScroll";
import { RevengePlayer } from "@/types/player";

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
        title="NBA Revenge Games 🏀"
        subtitle={`${nbaPlayers.length} players seeking vengeance today`}
        players={nbaPlayers}
      />

      {/* NFL Section */}
      <HorizontalPlayerScroll
        title="NFL Revenge Games 🏈"
        subtitle="Coming soon..."
        players={[]}
      />
    </div>
  );
}
