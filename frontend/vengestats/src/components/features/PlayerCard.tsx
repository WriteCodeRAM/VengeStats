import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PlayerCardProps {
  player: {
    name: string;
    former_team_name: string;
    former_team_abbr: string;
    injury_status: string;
    venge_score: number;
    departure_date: string;
    departure_year: number;
    record: string;
    total_revenge_games: number;
    current_team?: string;
  };
}

export function PlayerCard({ player }: PlayerCardProps) {
  const getVengeScoreBg = (score: number) => {
    if (score >= 8) return "bg-venge-red";
    if (score >= 6) return "bg-amber-500";
    return "bg-blue-500";
  };

  return (
    <Card className="bg-dark-card border-borderDefault hover:bg-dark-hover transition-all duration-300 cursor-pointer">
      <CardContent className="p-6">
        {/* Header with team matchup and venge score */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-white font-semibold">
            {player.current_team || "TBD"} vs {player.former_team_abbr}
          </span>
          <Badge
            className={`${getVengeScoreBg(player.venge_score)} text-white`}
          >
            {player.venge_score}/10
          </Badge>
        </div>

        {/* Rest stays the same... */}
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
              Left {player.former_team_name} in {player.departure_year}
            </div>
          </div>
        </div>

        {/* Stats without the venge score since it's in header now */}
        <div className="flex gap-6">
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

        {/* Injury Status */}
        {player.injury_status && player.injury_status !== "Healthy" && (
          <div className="mt-3 pt-3 border-t border-borderDefault">
            <span className="text-amber-400 text-sm">
              ⚠️ {player.injury_status}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
