import { PlayerCard } from "@/components/features/PlayerCard";

export default function Home() {
  const samplePlayer = {
    name: "LeBron James",
    former_team_name: "Cleveland Cavaliers",
    former_team_abbr: "CLE",
    injury_status: "Healthy",
    venge_score: 9,
    departure_date: "2018-07-01",
    departure_year: 2018,
    record: "12-4",
    total_revenge_games: 16,
    current_team: "LAL",
    game_time: "8:00 PM ET",
  };

  return (
    <div className="bg-dark-bg min-h-screen p-8">
      <div className="max-w-md">
        <PlayerCard player={samplePlayer} />
      </div>
    </div>
  );
}
