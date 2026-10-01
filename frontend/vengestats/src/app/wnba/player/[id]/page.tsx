"use client";
import { useState, useEffect } from "react";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface CareerStint {
  team_abbr: string;
  team_full_name: string;
  start_year: number;
  end_year: number | null;
  games_played: number;
  is_current: boolean;
}

interface WNBAPlayerProfileData {
  player_id: number;
  name: string;
  espn_athlete_id: string | null;
  current_team_name: string;
  current_team_abbr: string;
  former_team_name: string;
  former_team_abbr: string;
  opponent_team_id: number;
  venge_score: number;
  departure_method: string | null;
  games_for_former: number;
  career_games: number;
  departure_date: string | null;
  history: CareerStint[];
}

export default function WNBAPlayerProfilePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [player, setPlayer] = useState<WNBAPlayerProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState<string | null>(null);

  useEffect(() => {
    const resolveParams = async () => {
      const resolved = await params;
      setPlayerId(resolved.id);
    };
    resolveParams();
  }, [params]);

  useEffect(() => {
    if (!playerId) return;
    const fetchPlayer = async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      try {
        setLoading(true);
        const res = await fetch(`${apiUrl}/wnba/player/${playerId}`);
        if (!res.ok) throw new Error("Player not found");
        setPlayer(await res.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch player");
      } finally {
        setLoading(false);
      }
    };
    fetchPlayer();
  }, [playerId]);

  if (loading) {
    return (
      <div className="bg-dark-bg min-h-screen flex justify-center items-center">
        <div className="text-text-secondary">Loading player profile...</div>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="bg-dark-bg min-h-screen flex justify-center items-center">
        <div className="text-venge-red">Error: {error || "Player not found"}</div>
      </div>
    );
  }

  const getVengeScoreBg = (score: number) => {
    if (score >= 8) return "bg-venge-red";
    if (score >= 6) return "bg-amber-500";
    return "bg-blue-500";
  };

  const logoUrl = (abbr: string) =>
    `https://a.espncdn.com/i/teamlogos/wnba/500/${abbr.toLowerCase()}.png`;

  const headshotUrl = player.espn_athlete_id
    ? `https://a.espncdn.com/i/headshots/wnba/players/full/${player.espn_athlete_id}.png`
    : null;

  const departureYear = player.departure_date
    ? new Date(player.departure_date).getFullYear()
    : null;

  return (
    <div className="bg-dark-bg min-h-screen">
      <div className="max-w-4xl mx-auto px-4 py-8">

        {/* Back link */}
        <a
          href="/"
          className="text-text-secondary hover:text-white text-sm mb-6 inline-block"
        >
          ← Back to Revenge Games
        </a>

        {/* Hero card */}
        <Card className="bg-dark-card border-borderDefault mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">

              {/* Headshot */}
              <div className="w-24 h-24 rounded-full bg-gray-700 overflow-hidden shrink-0 flex items-center justify-center">
                {headshotUrl ? (
                  <Image
                    src={headshotUrl}
                    alt={player.name}
                    width={96}
                    height={96}
                    className="object-cover w-full h-full"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                ) : (
                  <span className="text-white text-2xl font-bold">
                    {player.name.split(" ").map((n) => n[0]).join("")}
                  </span>
                )}
              </div>

              {/* Name + matchup */}
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-1">{player.name}</h1>
                <div className="flex items-center gap-2 mb-3">
                  <Image
                    src={logoUrl(player.current_team_abbr)}
                    alt={player.current_team_name}
                    width={28}
                    height={28}
                    className="rounded-sm"
                  />
                  <span className="text-text-secondary text-sm">vs</span>
                  <Image
                    src={logoUrl(player.former_team_abbr)}
                    alt={player.former_team_name}
                    width={28}
                    height={28}
                    className="rounded-sm"
                  />
                  <span className="text-text-secondary text-sm">
                    {player.current_team_name} vs {player.former_team_name}
                  </span>
                </div>

                {player.departure_method && (
                  <Badge className="bg-gray-700 text-gray-200 text-xs mr-2">
                    {player.departure_method}
                    {departureYear ? ` · ${departureYear}` : ""}
                  </Badge>
                )}
              </div>

              {/* VengeScore */}
              <div className="text-center shrink-0">
                <div className={`${getVengeScoreBg(player.venge_score)} rounded-xl px-6 py-4`}>
                  <div className="text-white text-4xl font-black">{player.venge_score}</div>
                  <div className="text-white text-xs font-semibold tracking-widest mt-1">VENGESCORE</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <Card className="bg-dark-card border-borderDefault">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-white">{player.games_for_former}</div>
              <div className="text-xs text-text-secondary uppercase tracking-wide mt-1">
                Games with {player.former_team_abbr}
              </div>
            </CardContent>
          </Card>
          <Card className="bg-dark-card border-borderDefault">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-white">{player.career_games}</div>
              <div className="text-xs text-text-secondary uppercase tracking-wide mt-1">Career Games</div>
            </CardContent>
          </Card>
          <Card className="bg-dark-card border-borderDefault col-span-2 md:col-span-1">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-white">
                {player.career_games > 0
                  ? `${Math.round((player.games_for_former / player.career_games) * 100)}%`
                  : "—"}
              </div>
              <div className="text-xs text-text-secondary uppercase tracking-wide mt-1">
                Career Spent with {player.former_team_abbr}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Career timeline */}
        {player.history && player.history.length > 0 && (
          <Card className="bg-dark-card border-borderDefault">
            <CardContent className="p-6">
              <h2 className="text-white font-semibold text-lg mb-4">Career Timeline</h2>

              {/* Desktop */}
              <div className="hidden md:flex items-center gap-2 flex-wrap">
                {player.history.map((stint, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="flex flex-col items-center gap-1">
                      <Image
                        src={logoUrl(stint.team_abbr)}
                        alt={stint.team_abbr}
                        width={40}
                        height={40}
                        className={`rounded-sm ${stint.is_current ? "ring-2 ring-venge-red" : ""}`}
                      />
                      <span className="text-text-secondary text-xs">
                        {stint.start_year}
                        {stint.end_year && stint.end_year !== stint.start_year
                          ? `–${stint.end_year}`
                          : ""}
                      </span>
                      <span className="text-text-secondary text-xs">{stint.games_played}g</span>
                    </div>
                    {i < player.history.length - 1 && (
                      <span className="text-text-secondary text-lg">→</span>
                    )}
                  </div>
                ))}
              </div>

              {/* Mobile */}
              <div className="flex md:hidden gap-3 overflow-x-auto pb-2">
                {player.history.map((stint, i) => (
                  <div key={i} className="flex flex-col items-center gap-1 shrink-0">
                    <Image
                      src={logoUrl(stint.team_abbr)}
                      alt={stint.team_abbr}
                      width={32}
                      height={32}
                      className={`rounded-sm ${stint.is_current ? "ring-2 ring-venge-red" : ""}`}
                    />
                    <span className="text-text-secondary text-xs">{stint.start_year}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
