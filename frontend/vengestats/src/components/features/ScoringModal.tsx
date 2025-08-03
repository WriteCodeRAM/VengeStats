"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";

interface ScoringModalProps {
  children: React.ReactNode;
}

export function ScoringModal({ children }: ScoringModalProps) {
  const [activeTab, setActiveTab] = useState<"nba" | "nfl">("nba");

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="bg-dark-card border-borderDefault text-white max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white mb-4">
            How Venge Scores Work
          </DialogTitle>
        </DialogHeader>

        {/* Tab Nav */}
        <div className="flex mb-6 bg-dark-bg rounded-lg p-1">
          <button
            onClick={() => setActiveTab("nba")}
            className={`flex-1 py-3 px-4 rounded-md text-sm font-semibold transition-all ${
              activeTab === "nba"
                ? "bg-venge-red text-white"
                : "text-text-secondary hover:text-white"
            }`}
          >
            🏀 NBA Scoring
          </button>
          <button
            onClick={() => setActiveTab("nfl")}
            className={`flex-1 py-3 px-4 rounded-md text-sm font-semibold transition-all ${
              activeTab === "nfl"
                ? "bg-venge-red text-white"
                : "text-text-secondary hover:text-white"
            }`}
          >
            🏈 NFL Scoring
          </button>
        </div>

        {/* NBA Content */}
        {activeTab === "nba" && (
          <div className="space-y-6">
            <p className="text-text-secondary">
              NBA Venge Scores range from{" "}
              <span className="text-venge-red font-semibold">1-10</span> and
              measure how compelling a player's revenge game narrative is.
              Higher scores = more revenge potential.
            </p>

            {/* Tenure Impact */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">Tenure Impact</h3>
                <Badge className="bg-blue-500">Up to 3 pts</Badge>
              </div>
              <p className="text-text-secondary text-sm">
                How much of their career did they spend with this team? Players
                who spent 40%+ of their career get maximum points.
              </p>
            </div>

            {/* Former Team Bonus */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">Former Team Bonus</h3>
                <Badge className="bg-venge-red">2.5 pts</Badge>
              </div>
              <p className="text-text-secondary text-sm">
                Playing against your <em>most recent</em> former team gets the
                full bonus.
              </p>
            </div>

            {/* First-Time Revenge */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">First-Time Revenge</h3>
                <Badge className="bg-amber-500">1.5 pts</Badge>
              </div>
              <p className="text-text-secondary text-sm">
                First time facing a former team? Extra narrative juice.
              </p>
            </div>

            {/* All-Star Status */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">All-Star Status</h3>
                <Badge className="bg-indigo-500">1 pt</Badge>
              </div>
              <p className="text-text-secondary text-sm">
                Current All-Stars get extra attention.
              </p>
            </div>

            {/* Notable Narratives */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">Notable Narratives</h3>
                <Badge className="bg-purple-500">2 pts</Badge>
              </div>
              <p className="text-text-secondary text-sm">
                Special storylines (drama, trades, etc.) that make the revenge
                game extra spicy. Ex: Kyrie playing in TD Garden.
              </p>
            </div>

            {/* Performance Boost */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">Performance Boost</h3>
                <Badge className="bg-green-500">Up to 2 pts</Badge>
              </div>
              <p className="text-text-secondary text-sm">
                Do they actually play better against former teams? We compare
                their revenge game stats vs. normal games.
              </p>
            </div>

            {/* Examples */}
            <div className="bg-dark-bg p-4 rounded-lg border border-borderDefault">
              <h4 className="font-semibold mb-2 text-white">
                NBA Example Scores:
              </h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-text-secondary">
                    Role player, first revenge game
                  </span>
                  <span className="text-amber-400">4-5</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">
                    Star player vs former team
                  </span>
                  <span className="text-venge-red">7-8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">
                    LeBron vs Cleveland (hypothetical)
                  </span>
                  <span className="text-red-400">9-10</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* NFL Content */}
        {activeTab === "nfl" && (
          <div className="space-y-6">
            <p className="text-text-secondary">
              NFL Venge Scores range from{" "}
              <span className="text-venge-red font-semibold">1-10</span> and
              measure how compelling a player's revenge game narrative is.
              <strong className="text-amber-400 block mt-2">
                Note: Only skill positions (QB, RB, WR, TE) are tracked for
                revenge games.
              </strong>
            </p>

            {/* Coming Soon Section */}
            <div className="bg-dark-bg p-8 rounded-lg border border-borderDefault text-center">
              <div className="text-6xl mb-4">🏈</div>
              <h3 className="text-2xl font-bold mb-3 text-venge-red">
                NFL Scoring Coming Soon
              </h3>
              <p className="text-text-secondary text-lg mb-4">
                We're working on the NFL revenge scoring algorithm. It will
                focus on skill positions and account for the unique nature of
                football stats.
              </p>
              <div className="text-text-secondary text-sm">
                <strong>Planned positions:</strong> QB, RB, WR, TE
                <br />
                <strong>Key stats:</strong> Touchdowns, yards, receptions,
                completion %
              </div>
            </div>

            <div className="space-y-4 opacity-50">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold">Position Impact</h3>
                  <Badge className="bg-blue-500">TBD</Badge>
                </div>
                <p className="text-text-secondary text-sm">
                  QB revenge games carry more weight than other positions due to
                  visibility and impact.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold">Departure Context</h3>
                  <Badge className="bg-purple-500">TBD</Badge>
                </div>
                <p className="text-text-secondary text-sm">
                  How they left (cut, traded, free agency) affects the revenge
                  narrative.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold">
                    Performance Differential
                  </h3>
                  <Badge className="bg-green-500">TBD</Badge>
                </div>
                <p className="text-text-secondary text-sm">
                  Position-specific stats: QB completion %, RB rushing yards,
                  WR/TE receptions.
                </p>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
