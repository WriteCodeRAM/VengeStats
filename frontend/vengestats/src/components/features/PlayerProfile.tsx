"use client";

import { useState, useEffect } from "react";

interface PlayerStats {
  points: number;
  rebounds: number;
  assists: number;
  minutes: number;
  games: number;
}

interface Differentials {
  revenge_stats: PlayerStats;
  regular_stats: PlayerStats;
  differences: {
    points_diff: number;
    rebounds_diff: number;
    assists_diff: number;
    minutes_diff: number;
  };
}

interface PlayerData {
  name: string;
  former_team_name: string;
  former_team_abbr: string;
  injury_status: string | null;
  venge_score: number;
  departure_date: string;
  departure_year: number;
  record: string;
  total_revenge_games: number;
  player_id: number;
  current_team?: string; // You'll add this later
  differentials: Differentials | null;
}

interface PlayerProfileProps {
  playerId: string;
}

export function PlayerProfile({ playerId }: PlayerProfileProps) {
  const [player, setPlayer] = useState<PlayerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayer = async () => {
      try {
        setLoading(true);
        // You'll need a specific endpoint for individual players
        // For now, let's assume you filter from the existing matchups endpoint
        const response = await fetch("http://localhost:8000/matchups");

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const foundPlayer = data.nba_revenge_matchups.find(
          (p: PlayerData) => p.player_id.toString() === playerId
        );

        if (!foundPlayer) {
          throw new Error("Player not found");
        }

        setPlayer(foundPlayer);
      } catch (err) {
        console.error("Failed to fetch player:", err);
        setError(err instanceof Error ? err.message : "Failed to fetch player");
      } finally {
        setLoading(false);
      }
    };

    fetchPlayer();
  }, [playerId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-text-secondary">Loading player profile...</div>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-venge-red">
          Error: {error || "Player not found"}
        </div>
      </div>
    );
  }

  const getPlayerStatus = () => {
    if (!player.injury_status) {
      return { text: "Active", color: "text-green-400", icon: "✓" };
    } else {
      return {
        text: player.injury_status,
        color: "text-amber-400",
        icon: "⚠️",
      };
    }
  };

  const status = getPlayerStatus();
  const hasStats = player.differentials && player.total_revenge_games >= 2;

  return (
    <div className="space-y-8">
      {/* Game Context */}
      <div className="bg-dark-card border border-borderDefault rounded-2xl p-6 text-center">
        <div className="text-2xl font-bold mb-2">
          {player.current_team || "TBD"} vs {player.former_team_abbr} • Tonight
        </div>
        <div className="text-text-secondary">
          {player.name}'s{" "}
          {player.total_revenge_games > 0
            ? `${player.total_revenge_games}${getOrdinalSuffix(
                player.total_revenge_games
              )}`
            : "first"}{" "}
          revenge game against {player.former_team_name}
        </div>
      </div>

      {/* Player Banner */}
      <div className="bg-gradient-to-br from-dark-card to-dark-hover border border-borderDefault rounded-2xl p-8">
        <div className="flex items-center gap-8 mb-8">
          <div className="w-32 h-32 bg-gray-600 rounded-full flex items-center justify-center text-4xl font-bold border-4 border-venge-red">
            {player.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </div>
          <div className="flex-1">
            <h1 className="text-5xl font-bold mb-3">{player.name}</h1>
            <div className="flex gap-6 text-text-secondary text-lg mb-4">
              <span>{player.current_team || "Free Agent"}</span>
              <span>•</span>
              <span>Forward</span>{" "}
              {/* You might want to add position to your API */}
            </div>
            <div className="bg-venge-red text-white px-4 py-2 rounded-lg inline-block text-xl font-bold">
              Venge Score: {player.venge_score}
            </div>
          </div>
        </div>

        {/* Career Timeline - Simplified for now */}
        <div>
          <div className="text-text-secondary text-sm font-semibold mb-3">
            CAREER TIMELINE
          </div>
          <div className="flex items-center gap-4">
            <div className="bg-gray-600 px-4 py-3 rounded-xl text-center min-w-20">
              <div className="font-semibold">{player.former_team_abbr}</div>
              <div className="text-xs text-text-secondary">
                Left {player.departure_year}
              </div>
            </div>
            <div className="text-text-secondary">→</div>
            <div className="bg-blue-600 px-4 py-3 rounded-xl text-center min-w-20">
              <div className="font-semibold">{player.current_team || "FA"}</div>
              <div className="text-xs text-text-secondary">Current</div>
            </div>
          </div>
        </div>

        {/* Player Status */}
        <div className="mt-6 pt-6 border-t border-borderDefault">
          <span className={`${status.color} flex items-center gap-2`}>
            <span>{status.icon}</span>
            <span>{status.text}</span>
          </span>
        </div>
      </div>

      {/* Stats Section */}
      {hasStats ? (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Revenge Games Stats */}
            <div className="bg-dark-card border border-borderDefault rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-venge-red">
                  Revenge Games
                </h3>
                <span className="bg-red-900/30 text-venge-red px-3 py-1 rounded-lg text-sm font-semibold">
                  vs {player.former_team_abbr}
                </span>
              </div>

              <div className="space-y-4">
                <StatRow
                  label="Points Per Game"
                  value={player.differentials!.revenge_stats.points.toFixed(1)}
                  color="text-venge-red"
                />
                <StatRow
                  label="Rebounds Per Game"
                  value={player.differentials!.revenge_stats.rebounds.toFixed(
                    1
                  )}
                  color="text-venge-red"
                />
                <StatRow
                  label="Assists Per Game"
                  value={player.differentials!.revenge_stats.assists.toFixed(1)}
                  color="text-venge-red"
                />
                <StatRow
                  label="Minutes Per Game"
                  value={player.differentials!.revenge_stats.minutes.toFixed(1)}
                  color="text-venge-red"
                />
                <StatRow
                  label="Record"
                  value={player.record}
                  color="text-venge-red"
                />
                <StatRow
                  label="Total Games"
                  value={player.total_revenge_games.toString()}
                  color="text-venge-red"
                />
              </div>
            </div>

            {/* Regular Games Stats */}
            <div className="bg-dark-card border border-borderDefault rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-blue-400">
                  Regular Games
                </h3>
                <span className="bg-blue-900/30 text-blue-400 px-3 py-1 rounded-lg text-sm font-semibold">
                  All Other Games
                </span>
              </div>

              <div className="space-y-4">
                <StatRow
                  label="Points Per Game"
                  value={player.differentials!.regular_stats.points.toFixed(1)}
                  color="text-blue-400"
                />
                <StatRow
                  label="Rebounds Per Game"
                  value={player.differentials!.regular_stats.rebounds.toFixed(
                    1
                  )}
                  color="text-blue-400"
                />
                <StatRow
                  label="Assists Per Game"
                  value={player.differentials!.regular_stats.assists.toFixed(1)}
                  color="text-blue-400"
                />
                <StatRow
                  label="Minutes Per Game"
                  value={player.differentials!.regular_stats.minutes.toFixed(1)}
                  color="text-blue-400"
                />
                <StatRow
                  label="Games Played"
                  value={player.differentials!.regular_stats.games.toString()}
                  color="text-blue-400"
                />
              </div>
            </div>
          </div>

          {/* Revenge Boost Section */}
          <div className="bg-dark-bg border border-borderDefault rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-center mb-6">
              Revenge Game Boost
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <DifferentialItem
                label="POINTS"
                value={player.differentials!.differences.points_diff}
              />
              <DifferentialItem
                label="REBOUNDS"
                value={player.differentials!.differences.rebounds_diff}
              />
              <DifferentialItem
                label="ASSISTS"
                value={player.differentials!.differences.assists_diff}
              />
              <DifferentialItem
                label="MINUTES"
                value={player.differentials!.differences.minutes_diff}
              />
            </div>
          </div>
        </>
      ) : (
        /* Not Enough Data Section */
        <div className="bg-dark-card border border-borderDefault rounded-2xl p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-2xl font-bold mb-3">Not Enough Revenge Data</h3>
          <p className="text-text-secondary text-lg mb-4">
            {player.name} needs at least 2 revenge games for statistical
            analysis.
          </p>
          <div className="text-text-secondary">
            Current revenge games:{" "}
            <span className="text-white font-semibold">
              {player.total_revenge_games}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components
function StatRow({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="flex justify-between items-center py-3 border-b border-borderDefault last:border-b-0">
      <span className="text-text-secondary font-medium">{label}</span>
      <span className={`text-xl font-bold ${color}`}>{value}</span>
    </div>
  );
}

function DifferentialItem({ label, value }: { label: string; value: number }) {
  const isPositive = value > 0;
  const isNegative = value < 0;

  return (
    <div className="text-center p-4 bg-dark-card rounded-xl">
      <div
        className={`text-3xl font-bold mb-1 ${
          isPositive
            ? "text-green-400"
            : isNegative
            ? "text-red-400"
            : "text-text-secondary"
        }`}
      >
        {isPositive ? "+" : ""}
        {value.toFixed(1)}
      </div>
      <div className="text-text-secondary text-sm font-semibold">{label}</div>
    </div>
  );
}

function getOrdinalSuffix(num: number): string {
  const j = num % 10;
  const k = num % 100;
  if (j === 1 && k !== 11) return "st";
  if (j === 2 && k !== 12) return "nd";
  if (j === 3 && k !== 13) return "rd";
  return "th";
}
