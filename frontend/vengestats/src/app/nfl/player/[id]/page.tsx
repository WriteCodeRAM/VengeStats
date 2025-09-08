"use client";
import { useState, useEffect } from "react";

interface NFLPlayerProfileData {
  player_id: number;
  name: string;
  nfl_data_id: string;
  display_name: string;
  current_team_id: string;
  position: string;
  usage_tier: string;
  years_exp: number;
  draft_team: string;
  pro_bowl_selections: number;
  all_pro_selections: number;
  former_team_name: string;
  former_team_abbr: string;
  opponent_team_id: string;
  current_team_name: string;
  current_team_abbr: string;
  season_start: number;
  departure_year: number;
  total_games_played_for_team: number;
  injury_status: string;
  revenge_score: number;
  record: string;
  total_revenge_games: number;
  league: string;
  differentials?: {
    revenge_stats: any;
    regular_stats: any;
    differences: any;
  };
  history?: Array<{
    team_abbr: string;
    team_full_name: string;
    start_year: number;
    end_year?: number;
    games_played: number;
  }>;
}

export default function NFLPlayerProfilePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [player, setPlayer] = useState<NFLPlayerProfileData>();
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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      try {
        setLoading(true);
        const response = await fetch(`${apiUrl}/nfl/player/${playerId}`);

        if (!response.ok) {
          throw new Error("Player not found");
        }

        const playerData = await response.json();
        setPlayer(playerData);
      } catch (err) {
        console.error("Failed to fetch NFL player:", err);
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
    if (!player.injury_status || player.injury_status === "Healthy") {
      return { text: "Active", color: "text-green-400", icon: "✓" };
    } else {
      return {
        text: player.injury_status,
        color: "text-amber-400",
        icon: "⚠️",
      };
    }
  };

  const getPositionColor = (position: string) => {
    switch (position) {
      case "QB":
        return "text-purple-400";
      case "RB":
        return "text-green-400";
      case "WR":
        return "text-blue-400";
      case "TE":
        return "text-orange-400";
      default:
        return "text-gray-400";
    }
  };

  const getUsageTierBadge = (tier: string) => {
    const colors = {
      STARTER: "bg-green-900/30 text-green-400",
      ROTATIONAL: "bg-yellow-900/30 text-yellow-400",
      BACKUP: "bg-gray-900/30 text-gray-400",
      INACTIVE: "bg-red-900/30 text-red-400",
    };
    return colors[tier] || "bg-gray-900/30 text-gray-400";
  };

  // Check if we have regular stats (check if values are actually numbers, not null)
  const hasRegularStats =
    player.differentials &&
    player.differentials.regular_stats &&
    player.differentials.regular_stats.games > 0 &&
    typeof player.differentials.regular_stats.games === "number";

  // Check if we have sufficient revenge data (check if values are numbers, not null)
  const hasRevengeStats =
    player.differentials &&
    player.total_revenge_games >= 1 &&
    player.differentials.revenge_stats &&
    player.differentials.revenge_stats.games > 0 &&
    typeof player.differentials.revenge_stats.games === "number";

  const status = getPlayerStatus();

  // Get position-specific stat labels
  const getStatLabels = (position: string) => {
    switch (position) {
      case "QB":
        return {
          stat1: { label: "Passing Yards", key: "passing_yards" },
          stat2: { label: "Passing TDs", key: "passing_tds" },
          stat3: { label: "Completions", key: "completions" },
          stat4: { label: "Interceptions", key: "interceptions" },
          stat5: { label: "Fantasy Points", key: "fantasy_points" },
          diff1: { label: "PASSING YDS", key: "passing_yards_diff" },
          diff2: { label: "PASSING TDS", key: "passing_tds_diff" },
          diff3: { label: "COMPLETIONS", key: "completions_diff" },
          diff4: { label: "INTERCEPTIONS", key: "interceptions_diff" },
        };
      case "RB":
        return {
          stat1: { label: "Rushing Yards", key: "rushing_yards" },
          stat2: { label: "Rushing TDs", key: "rushing_tds" },
          stat3: { label: "Carries", key: "carries" },
          stat4: { label: "Receiving Yards", key: "receiving_yards" },
          stat5: { label: "Fantasy Points", key: "fantasy_points" },
          diff1: { label: "RUSHING YDS", key: "rushing_yards_diff" },
          diff2: { label: "RUSHING TDS", key: "rushing_tds_diff" },
          diff3: { label: "CARRIES", key: "carries_diff" },
          diff4: { label: "REC YARDS", key: "receiving_yards_diff" },
        };
      case "WR":
      case "TE":
        return {
          stat1: { label: "Receiving Yards", key: "receiving_yards" },
          stat2: { label: "Receiving TDs", key: "receiving_tds" },
          stat3: { label: "Receptions", key: "receptions" },
          stat4: { label: "Targets", key: "targets" },
          stat5: { label: "Fantasy Points", key: "fantasy_points" },
          diff1: { label: "REC YARDS", key: "receiving_yards_diff" },
          diff2: { label: "REC TDS", key: "receiving_tds_diff" },
          diff3: { label: "RECEPTIONS", key: "receptions_diff" },
          diff4: { label: "TARGETS", key: "targets_diff" },
        };
      default:
        return {
          stat1: { label: "Fantasy Points", key: "fantasy_points" },
          stat2: { label: "Games", key: "games" },
          stat3: { label: "Games", key: "games" },
          stat4: { label: "Games", key: "games" },
          stat5: { label: "Fantasy Points", key: "fantasy_points" },
          diff1: { label: "FANTASY PTS", key: "fantasy_points_diff" },
          diff2: { label: "GAMES", key: "games_diff" },
          diff3: { label: "GAMES", key: "games_diff" },
          diff4: { label: "GAMES", key: "games_diff" },
        };
    }
  };

  const statLabels = getStatLabels(player.position);

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
                <div className="absolute inset-0 w-full h-full flex items-center justify-center text-white font-semibold text-5xl bg-gray-600 rounded-full">
                  {player.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
              </div>
            </div>

            {/* Center: Player Name + Career Timeline */}
            <div className="col-span-6 text-center">
              <div className="flex items-center justify-center gap-4 mb-2">
                <h1 className="text-6xl font-bold">{player.name}</h1>
                <div className="flex flex-col gap-2">
                  <span
                    className={`${getPositionColor(
                      player.position
                    )} text-2xl font-bold`}
                  >
                    {player.position}
                  </span>
                  <span
                    className={`px-3 py-1 rounded-lg text-sm font-semibold ${getUsageTierBadge(
                      player.usage_tier
                    )}`}
                  >
                    {player.usage_tier}
                  </span>
                </div>
              </div>

              {/* NFL Accolades */}
              <div className="flex items-center justify-center gap-4 mb-6">
                {player.pro_bowl_selections > 0 && (
                  <div className="bg-blue-900/30 text-blue-400 px-3 py-1 rounded-lg text-sm">
                    {player.pro_bowl_selections}x Pro Bowl
                  </div>
                )}
                {player.all_pro_selections > 0 && (
                  <div className="bg-yellow-900/30 text-yellow-400 px-3 py-1 rounded-lg text-sm">
                    {player.all_pro_selections}x All-Pro
                  </div>
                )}
                <div className="bg-gray-900/30 text-gray-400 px-3 py-1 rounded-lg text-sm">
                  {player.years_exp} Years
                </div>
              </div>

              {/* Career Timeline */}
              <div className="mb-6">
                <div className="text-text-secondary text-sm font-semibold mb-3">
                  CAREER TIMELINE
                </div>

                {/* Desktop Timeline */}
                <div className="flex items-center gap-3 justify-center overflow-x-auto">
                  {player.history && player.history.length > 0 ? (
                    player.history.map((stint, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div
                          className={`px-4 py-3 rounded-xl text-center min-w-20 ${
                            index === 0
                              ? "bg-purple-600" // First team (draft team)
                              : index === player.history.length - 1
                              ? "bg-blue-600" // Current team
                              : "bg-gray-600" // Former teams
                          }`}
                        >
                          <div className="font-semibold">{stint[0]}</div>
                          <div className="text-xs text-gray-300">
                            {stint[1]}
                            {stint[2] && stint[2] !== stint[1]
                              ? `-${stint[2]}`
                              : ""}
                          </div>
                          <div className="text-xs text-gray-300">
                            {stint.games_played}
                          </div>
                        </div>
                        {index < player.history.length - 1 && (
                          <div className="text-text-secondary">→</div>
                        )}
                      </div>
                    ))
                  ) : (
                    // Fallback to original timeline if no history data
                    <>
                      {player.draft_team && (
                        <>
                          <div className="bg-purple-600 px-4 py-3 rounded-xl text-center min-w-20">
                            <div className="font-semibold">
                              {player.draft_team}
                            </div>
                            <div className="text-xs text-gray-300">Drafted</div>
                          </div>
                          <div className="text-text-secondary">→</div>
                        </>
                      )}
                      <div className="bg-gray-600 px-4 py-3 rounded-xl text-center min-w-20">
                        <div className="font-semibold">
                          {player.former_team_abbr}
                        </div>
                        <div className="text-xs text-gray-300">
                          {player.season_start}-{player.departure_year}
                        </div>
                      </div>
                      <div className="text-text-secondary">→</div>
                      <div className="bg-blue-600 px-4 py-3 rounded-xl text-center min-w-20">
                        <div className="font-semibold">
                          {player.current_team_abbr}
                        </div>
                        <div className="text-xs text-gray-300">Current</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Right: Venge Score */}
            <div className="col-span-3 flex justify-end">
              <div className="relative group cursor-help">
                <div className="bg-venge-red text-white px-6 py-4 rounded-2xl text-center min-w-32">
                  <div className="text-3xl font-bold">
                    {player.revenge_score}
                  </div>
                  <div className="text-sm opacity-90">VENGE SCORE</div>
                </div>
              </div>
            </div>
          </div>

          {/* Mobile Layout */}
          <div className="md:hidden space-y-6">
            {/* Top: Player Image + Venge Score */}
            <div className="flex items-center justify-between">
              <div className="w-24 h-24 bg-gray-600 rounded-full overflow-hidden border-4 border-venge-red relative">
                <div className="absolute inset-0 w-full h-full flex items-center justify-center text-white font-semibold text-2xl bg-gray-600 rounded-full">
                  {player.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
              </div>

              <div className="bg-venge-red text-white px-4 py-3 rounded-xl text-center">
                <div className="text-2xl font-bold">{player.revenge_score}</div>
                <div className="text-xs opacity-90">VENGE SCORE</div>
              </div>
            </div>

            {/* Middle: Player Name + Position */}
            <div className="text-center">
              <h1 className="text-3xl md:text-4xl font-bold mb-2">
                {player.name}
              </h1>
              <div className="flex items-center justify-center gap-3">
                <span
                  className={`${getPositionColor(
                    player.position
                  )} text-xl font-bold`}
                >
                  {player.position}
                </span>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${getUsageTierBadge(
                    player.usage_tier
                  )}`}
                >
                  {player.usage_tier}
                </span>
              </div>
            </div>

            {/* Bottom: Simplified Timeline */}
            <div className="flex items-center gap-3 justify-center">
              {player.history && player.history.length > 0 ? (
                <>
                  <div
                    className={`px-3 py-2 rounded-lg text-center min-w-16 ${
                      player.history.length === 1
                        ? "bg-blue-600"
                        : "bg-gray-600"
                    }`}
                  >
                    <div className="font-semibold text-sm">
                      {player.history.length > 1
                        ? player.former_team_abbr
                        : player.history[0].team_abbr}
                    </div>
                    <div className="text-xs text-gray-300">
                      {player.history.length > 1 ? "Former" : "Current"}
                    </div>
                  </div>
                  {player.history.length > 1 && (
                    <>
                      <div className="text-text-secondary text-sm">→</div>
                      <div className="bg-blue-600 px-3 py-2 rounded-lg text-center min-w-16">
                        <div className="font-semibold text-sm">
                          {player.current_team_abbr}
                        </div>
                        <div className="text-xs text-gray-300">Current</div>
                      </div>
                    </>
                  )}
                </>
              ) : (
                // Original fallback
                <>
                  <div className="bg-gray-600 px-3 py-2 rounded-lg text-center min-w-16">
                    <div className="font-semibold text-sm">
                      {player.former_team_abbr}
                    </div>
                    <div className="text-xs text-gray-300">Former</div>
                  </div>
                  <div className="text-text-secondary text-sm">→</div>
                  <div className="bg-blue-600 px-3 py-2 rounded-lg text-center min-w-16">
                    <div className="font-semibold text-sm">
                      {player.current_team_abbr}
                    </div>
                    <div className="text-xs text-gray-300">Current</div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Bottom Section: Status + Revenge Game Info */}
          <div className="mt-6 pt-6 border-t border-borderDefault flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div className={`${status.color} flex items-center gap-2`}>
              <span>{status.icon}</span>
              <span>{status.text}</span>
            </div>

            <div className="text-text-secondary text-sm">
              {player.total_revenge_games > 0
                ? `${player.total_revenge_games + 1}${getOrdinalSuffix(
                    player.total_revenge_games + 1
                  )} revenge game against ${player.former_team_name}`
                : `First revenge game against ${player.former_team_name}`}
            </div>
          </div>
        </div>

        {/* Stats Section - Show if we have regular stats */}
        {hasRegularStats ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 mb-8">
              {/* Revenge Games Section */}
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
                    {player.total_revenge_games}{" "}
                    {player.total_revenge_games > 1 ? "games" : "game"}
                  </span>
                </div>

                {hasRevengeStats ? (
                  <div className="space-y-4">
                    <StatRow
                      label={statLabels.stat1.label}
                      value={
                        player.differentials.revenge_stats[
                          statLabels.stat1.key
                        ]?.toFixed(1) || "0.0"
                      }
                      color="text-venge-red"
                    />
                    <StatRow
                      label={statLabels.stat2.label}
                      value={
                        player.differentials.revenge_stats[
                          statLabels.stat2.key
                        ]?.toFixed(1) || "0.0"
                      }
                      color="text-venge-red"
                    />
                    <StatRow
                      label={statLabels.stat3.label}
                      value={
                        player.differentials.revenge_stats[
                          statLabels.stat3.key
                        ]?.toFixed(1) || "0.0"
                      }
                      color="text-venge-red"
                    />
                    {statLabels.stat4.key !== statLabels.stat3.key && (
                      <StatRow
                        label={statLabels.stat4.label}
                        value={
                          player.differentials.revenge_stats[
                            statLabels.stat4.key
                          ]?.toFixed(1) || "0.0"
                        }
                        color="text-venge-red"
                      />
                    )}
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
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-3">⚠️</div>
                    <div className="text-text-secondary text-lg font-medium mb-2">
                      Not Enough Revenge Data
                    </div>
                    <div className="text-text-secondary text-sm opacity-75">
                      More games needed for detailed stats
                    </div>
                  </div>
                )}
              </div>

              {/* Regular Games Section */}
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
                    label={statLabels.stat1.label}
                    value={
                      player.differentials.regular_stats[
                        statLabels.stat1.key
                      ]?.toFixed(1) || "0.0"
                    }
                    color="text-blue-400"
                  />
                  <StatRow
                    label={statLabels.stat2.label}
                    value={
                      player.differentials.regular_stats[
                        statLabels.stat2.key
                      ]?.toFixed(1) || "0.0"
                    }
                    color="text-blue-400"
                  />
                  <StatRow
                    label={statLabels.stat3.label}
                    value={
                      player.differentials.regular_stats[
                        statLabels.stat3.key
                      ]?.toFixed(1) || "0.0"
                    }
                    color="text-blue-400"
                  />
                  {statLabels.stat4.key !== statLabels.stat3.key && (
                    <StatRow
                      label={statLabels.stat4.label}
                      value={
                        player.differentials.regular_stats[
                          statLabels.stat4.key
                        ]?.toFixed(1) || "0.0"
                      }
                      color="text-blue-400"
                    />
                  )}
                  <StatRow
                    label="Games Played"
                    value={
                      player.differentials.regular_stats.games?.toString() ||
                      "0"
                    }
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

              {hasRevengeStats ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                  <DifferentialItem
                    label={statLabels.diff1.label}
                    value={
                      player.differentials.differences[statLabels.diff1.key] ||
                      0
                    }
                  />
                  <DifferentialItem
                    label={statLabels.diff2.label}
                    value={
                      player.differentials.differences[statLabels.diff2.key] ||
                      0
                    }
                  />
                  <DifferentialItem
                    label={statLabels.diff3.label}
                    value={
                      player.differentials.differences[statLabels.diff3.key] ||
                      0
                    }
                  />
                  <DifferentialItem
                    label={statLabels.diff4.label}
                    value={
                      player.differentials.differences[statLabels.diff4.key] ||
                      0
                    }
                  />
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-3">📊</div>
                  <div className="text-text-secondary text-lg font-medium mb-2">
                    Insufficient Revenge Data
                  </div>
                  <div className="text-text-secondary text-sm opacity-75 mb-4">
                    Cannot calculate performance differentials without
                    sufficient revenge game data
                  </div>
                  <div className="text-text-secondary text-sm">
                    Current revenge games:{" "}
                    <span className="text-white font-semibold">
                      {player.total_revenge_games}
                    </span>{" "}
                    | Regular games:{" "}
                    <span className="text-white font-semibold">
                      {player.differentials.regular_stats?.games || 0}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          /* No Data Available */
          <div className="bg-dark-card border border-borderDefault rounded-2xl p-8 md:p-12 text-center">
            <div className="text-4xl md:text-6xl mb-4">🏈</div>
            <h3 className="text-xl md:text-2xl font-bold mb-3 text-venge-red">
              No Statistical Data Available
            </h3>
            <p className="text-text-secondary text-base md:text-lg mb-4">
              No game data found for {player.name} since {player.departure_year}
              .
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
