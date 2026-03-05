"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { PlayerProfileData } from "@/types/player";

export default function PlayerProfilePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [player, setPlayer] = useState<PlayerProfileData>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState<string | null>(null);

  useEffect(() => {
    const resolveParams = async () => {
      const resolvedParams = await params;
      setPlayerId(resolvedParams.id);
    };
    resolveParams();
  }, [params]);

  useEffect(() => {
    if (!playerId) return;

    const fetchPlayer = async () => {
      try {
        setLoading(true);
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/nba/player/${playerId}`);

        if (!response.ok) {
          throw new Error("Player not found");
        }

        const playerData = await response.json();
        setPlayer(playerData);
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
      <div className="bg-dark-bg min-h-screen">
        <div className="flex justify-center items-center py-12">
          <div className="text-text-secondary">Loading player profile...</div>
        </div>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="bg-dark-bg min-h-screen">
        <div className="flex justify-center items-center py-12">
          <div className="text-venge-red">
            Error: {error || "Player not found"}
          </div>
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

  const getVengeScoreBg = (score: number) => {
    if (score >= 8) return "bg-venge-red";
    if (score >= 6) return "bg-amber-500";
    return "bg-blue-500";
  };

  const filteredHistory = player.history?.filter(
    (stint, index, arr) =>
      index === 0 || stint.team_abbr !== arr[index - 1].team_abbr,
  );

  const status = getPlayerStatus();
  const hasStats = player.differentials && player.total_revenge_games >= 2;

  return (
    <div className="bg-dark-bg min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Main Player Banner */}
        <div className="bg-gradient-to-br from-dark-card to-dark-hover border border-borderDefault rounded-2xl p-4 md:p-8 mb-8 text-white">
          {/* Desktop Layout */}
          <div className="hidden md:grid grid-cols-12 gap-8 items-start">
            {/* Left: Player Image */}
            <div className="col-span-3">
              <div className="w-48 h-48 bg-gray-600 rounded-full overflow-hidden border-4 border-venge-red relative">
                <Image
                  src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.nba_api_id}.png`}
                  alt={player.name}
                  width={192}
                  height={192}
                  className="w-full h-full object-cover object-top"
                  onError={(e) => {
                    e.target.style.display = "none";
                    e.target.nextSibling.style.display = "flex";
                  }}
                />
                <div
                  className="absolute inset-0 w-full h-full flex items-center justify-center text-white font-semibold text-5xl bg-gray-600 rounded-full"
                  style={{ display: "none" }}
                >
                  {player.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
              </div>
            </div>

            {/* Center: Player Name + Career Timeline */}
            <div className="col-span-6 text-center">
              <h1 className="text-6xl font-bold mb-6">{player.name}</h1>

              {/* Career Timeline */}
              <div className="mb-6">
                <div className="text-text-secondary text-sm font-semibold mb-3">
                  CAREER TIMELINE
                </div>

                <div
                  className={`flex items-center gap-4 ${
                    filteredHistory && filteredHistory.length > 4
                      ? "justify-start overflow-x-auto pb-2 max-w-lg mx-auto scrollbar-hide"
                      : "justify-center"
                  }`}
                >
                  {filteredHistory && filteredHistory.length > 0 ? (
                    filteredHistory.map((stint, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-4 flex-shrink-0"
                      >
                        <div className="relative group cursor-pointer">
                          <div className="font-semibold">
                            <Image
                              src={`/nba_logos/${stint.team_abbr}.png`}
                              alt="team logo"
                              width={50}
                              height={50}
                            />
                          </div>
                        </div>

                        {/* Arrow between teams */}
                        {index < filteredHistory.length - 1 && (
                          <div className="text-text-secondary flex-shrink-0">
                            →
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    // Fallback
                    <div className="flex items-center gap-4">
                      <div className="bg-gray-600 px-4 py-3 rounded-xl text-center min-w-20">
                        <div className="font-semibold">
                          {player.former_team_abbr}
                        </div>
                        <div className="text-xs text-gray-300">Former</div>
                      </div>
                      <div className="text-text-secondary">→</div>
                      <div className="bg-blue-600 px-4 py-3 rounded-xl text-center min-w-20">
                        <div className="font-semibold">Current</div>
                        <div className="text-xs text-gray-300">Now</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right: Venge Score */}
            <div className="col-span-3 flex justify-end">
              <div className="relative group cursor-help">
                <div
                  className={`${getVengeScoreBg(player.venge_score)} text-white px-6 py-4 rounded-2xl text-center min-w-32`}
                >
                  <div className="text-3xl font-bold">{player.venge_score}</div>
                  <div className="text-sm opacity-90">VENGE SCORE</div>
                </div>

                {/* Score breakdown tooltip */}
                <div className="absolute top-full right-0 mt-2 w-80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10 pointer-events-none">
                  <div className="bg-dark-bg border border-borderDefault rounded-lg p-4">
                    <div className="text-sm font-semibold mb-3">
                      Score Breakdown:
                    </div>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-text-secondary">
                          Tenure Impact:
                        </span>
                        <span>2.1 pts</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-secondary">
                          Former Team Bonus:
                        </span>
                        <span>2.5 pts</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-secondary">
                          Performance Boost:
                        </span>
                        <span>1.8 pts</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-secondary">
                          All-Star Status:
                        </span>
                        <span>1.0 pts</span>
                      </div>
                      <div className="border-t border-borderDefault pt-2 mt-2">
                        <div className="flex justify-between font-semibold">
                          <span>Total Score:</span>
                          <span className="text-venge-red">
                            {player.venge_score}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="absolute top-0 right-8 transform -translate-y-1 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-borderDefault"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Mobile Layout */}
          <div className="md:hidden space-y-6">
            {/* Top: Player Image + Venge Score */}
            <div className="flex items-center flex-col gap-1 justify-between">
              <div className="w-24 h-24 bg-gray-600 rounded-full overflow-hidden border-4 border-venge-red relative">
                <Image
                  src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.nba_api_id}.png`}
                  alt={player.name}
                  width={96}
                  height={96}
                  className="w-full h-full object-cover object-top"
                  onError={(e) => {
                    e.target.style.display = "none";
                    e.target.nextSibling.style.display = "flex";
                  }}
                />
                <div
                  className="absolute inset-0 w-full h-full flex items-center justify-center text-white font-semibold text-2xl bg-gray-600 rounded-full"
                  style={{ display: "none" }}
                >
                  {player.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
              </div>

              <div
                className={`${getVengeScoreBg(player.venge_score)} text-white px-3 py-2 rounded-xl text-center`}
              >
                <div className="text-2xl font-bold">{player.venge_score}</div>
                <div className="text-xs opacity-90">VENGE SCORE</div>
              </div>
            </div>

            {/* Middle: Player Name */}
            <div className="text-center">
              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                {player.name}
              </h1>
            </div>

            {/* Bottom: Career Timeline */}
            <div>
              <div className="text-text-secondary text-sm font-semibold mb-3 text-center">
                CAREER TIMELINE
              </div>
              <div
                className={`flex items-center gap-3 overflow-x-auto pb-2 scrollbar-hide ${
                  player.history && player.history.length < 4
                    ? "justify-center"
                    : ""
                }`}
              >
                {player.history && player.history.length > 0 ? (
                  player.history.map((stint, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-3 flex-shrink-0"
                    >
                      <div className="relative group cursor-pointer">
                        <div>
                          <div className="font-semibold text-sm">
                            <Image
                              src={`/nba_logos/${stint.team_abbr}.png`}
                              alt={`${stint.team_abbr} logo`}
                              width={50}
                              height={50}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Arrow between teams */}
                      {index < player.history.length - 1 && (
                        <div className="text-text-secondary flex-shrink-0 text-sm">
                          →
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  // Mobile fallback
                  <></>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Section: Injury Status + Revenge Game Info */}
          <div className="mt-6 pt-6 border-t text-center items-center border-borderDefault flex flex-col md:flex-row md:justify-between md:items-center gap-4 ">
            <div className={`${status.color} flex items-center gap-2`}>
              <span>{status.icon}</span>
              <span>{status.text}</span>
            </div>

            <div className="text-text-secondary text-sm">
              {player.total_revenge_games > 0
                ? `${player.total_revenge_games + 1}${getOrdinalSuffix(
                    player.total_revenge_games + 1,
                  )} revenge game against ${player.former_team_name}`
                : `First revenge game against ${player.former_team_name}`}
            </div>
          </div>
        </div>

        {/* Stats Comparison Section */}
        {hasStats ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 mb-8">
              <div className="bg-dark-card border border-borderDefault rounded-2xl p-6 md:p-8">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                  <div>
                    <h3 className="text-xl md:text-2xl font-bold text-venge-red">
                      Revenge Games
                    </h3>
                    <p className="text-text-secondary text-xs mt-1">
                      vs {player.former_team_abbr} since {player.departure_year}
                    </p>
                  </div>
                  <span className="bg-red-900/30 text-venge-red px-3 py-1 rounded-lg text-sm font-semibold">
                    {player.total_revenge_games} games
                  </span>
                </div>
                <div className="space-y-4">
                  <StatRow
                    label="Points Per Game"
                    value={player.differentials.revenge_stats.points.toFixed(1)}
                    color="text-venge-red"
                  />
                  <StatRow
                    label="Rebounds Per Game"
                    value={player.differentials.revenge_stats.rebounds.toFixed(
                      1,
                    )}
                    color="text-venge-red"
                  />
                  <StatRow
                    label="Assists Per Game"
                    value={player.differentials.revenge_stats.assists.toFixed(
                      1,
                    )}
                    color="text-venge-red"
                  />
                  <StatRow
                    label="Minutes Per Game"
                    value={player.differentials.revenge_stats.minutes.toFixed(
                      1,
                    )}
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

              <div className="bg-dark-card border border-borderDefault rounded-2xl p-6 md:p-8">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                  <div>
                    <h3 className="text-xl md:text-2xl font-bold text-blue-400">
                      Regular Games
                    </h3>
                    <p className="text-text-secondary text-xs mt-1">
                      All other games since {player.departure_year}
                    </p>
                  </div>
                  <span className="bg-blue-900/30 text-blue-400 px-3 py-1 rounded-lg text-sm font-semibold">
                    vs All Other Teams
                  </span>
                </div>

                <div className="space-y-4">
                  <StatRow
                    label="Points Per Game"
                    value={player.differentials.regular_stats.points.toFixed(1)}
                    color="text-blue-400"
                  />
                  <StatRow
                    label="Rebounds Per Game"
                    value={player.differentials.regular_stats.rebounds.toFixed(
                      1,
                    )}
                    color="text-blue-400"
                  />
                  <StatRow
                    label="Assists Per Game"
                    value={player.differentials.regular_stats.assists.toFixed(
                      1,
                    )}
                    color="text-blue-400"
                  />
                  <StatRow
                    label="Minutes Per Game"
                    value={player.differentials.regular_stats.minutes.toFixed(
                      1,
                    )}
                    color="text-blue-400"
                  />
                  <StatRow
                    label="Games Played"
                    value={player.differentials.regular_stats.games.toString()}
                    color="text-blue-400"
                  />
                </div>
              </div>
            </div>

            {/* Revenge Boost Section */}
            <div className="bg-dark-bg border border-borderDefault rounded-2xl p-6 md:p-8">
              <h3 className="text-xl md:text-2xl font-bold text-center mb-6 text-venge-red">
                Revenge Game Boost
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                <DifferentialItem
                  label="POINTS"
                  value={player.differentials.differences.points_diff}
                />
                <DifferentialItem
                  label="REBOUNDS"
                  value={player.differentials.differences.rebounds_diff}
                />
                <DifferentialItem
                  label="ASSISTS"
                  value={player.differentials.differences.assists_diff}
                />
                <DifferentialItem
                  label="MINUTES"
                  value={player.differentials.differences.minutes_diff}
                />
              </div>
            </div>
          </>
        ) : (
          /* Not Enough Data Section */
          <div className="bg-dark-card border border-borderDefault rounded-2xl p-8 md:p-12 text-center">
            <div className="text-4xl md:text-6xl mb-4">📊</div>
            <h3 className="text-xl md:text-2xl font-bold mb-3 text-venge-red">
              Not Enough Revenge Data
            </h3>
            <p className="text-text-secondary text-base md:text-lg mb-4">
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
    </div>
  );
}

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
      <span className="text-text-secondary font-medium text-sm md:text-base">
        {label}
      </span>
      <span className={`text-lg md:text-xl font-bold ${color}`}>{value}</span>
    </div>
  );
}

function DifferentialItem({ label, value }: { label: string; value: number }) {
  const isPositive = value > 0;
  const isNegative = value < 0;

  return (
    <div className="text-center p-3 md:p-4 bg-dark-card rounded-xl">
      <div
        className={`text-2xl md:text-3xl font-bold mb-1 ${
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
      <div className="text-text-secondary text-xs md:text-sm font-semibold">
        {label}
      </div>
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
