"use client";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PlayerCardProps {
  player: {
    name: string;
    player_id: number;
    former_team_abbr: string;
    former_team_name: string;
    injury_status: string;
    venge_score: number;
    record: string;
    total_revenge_games: number;
    current_team_name: string;
    league: string;
  };
}

export function PlayerCard({ player }: PlayerCardProps) {
  const router = useRouter();
  const handleClick = (e: React.MouseEvent) => {
    router.push(`/nba/player/${player.player_id}`);
  };

  const getVengeScoreBg = (score: number) => {
    if (score >= 8) return "bg-venge-red";
    if (score >= 6) return "bg-amber-500";
    return "bg-blue-500";
  };

  const getPlayerStatus = () => {
    if (
      !player.injury_status ||
      player.injury_status.toLowerCase() === "healthy"
    ) {
      return {
        text: "Active",
        color: "text-green-400",
        icon: "✓",
      };
    } else {
      return {
        text: player.injury_status,
        color: "text-amber-400",
        icon: "⚠️",
      };
    }
  };

  const status = getPlayerStatus();

  return (
    <Card
      className="bg-dark-card border-borderDefault hover:bg-dark-hover transition-all duration-300 cursor-pointer"
      onClick={handleClick}
    >
      <CardContent className="p-6">
        {/* Header with team matchup and venge score */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-white font-semibold">
            {player.current_team_name || "TBD"} vs {player.former_team_abbr}
          </span>
          <Badge
            className={`${getVengeScoreBg(player.venge_score)} text-white`}
          >
            {player.venge_score}
          </Badge>
        </div>

        {/* Player Info */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-sm">
              {player.name
                .split(" ")
                .map((n) => n[0])
                .join("")}
            </span>
          </div>
          <div className="flex-1">
            <div className="text-white font-semibold">{player.name}</div>
            <div className="text-text-secondary text-xs">
              Former {player.former_team_name} player
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-6 mb-4">
          <div className="text-center">
            <div className="text-lg font-bold text-text-primary">
              {player.record}
            </div>
            <div className="text-xs text-text-secondary">RECORD</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-text-primary">
              {player.total_revenge_games}
            </div>
            <div className="text-xs text-text-secondary">REVENGE GAMES</div>
          </div>
        </div>

        {/* Player Status */}
        <div className="pt-3 border-t border-borderDefault">
          <span className={`${status.color} text-sm flex items-center gap-1`}>
            <span>{status.icon}</span>
            <span>{status.text}</span>
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
