from backend.nba_api.utils.player_utils import search_player
from backend.nba_api.utils.data_fetcher import get_fair_comparison, compare_stats
from backend.db.venge_data import calculate_venge_score
from backend.db.queries.nba.players import get_player_id
from backend.db.queries.nba.teams import teams
import time

def test_player_revenge_scoring(player_name: str, former_team_abbr: str, departure_date: str, current_team_abbr: str):
    """
    Test the new revenge scoring system with a specific player 
    """
    print(f"\n{'='*60}")
    print(f"TESTING REVENGE SCORING: {player_name} vs {former_team_abbr}")
    print(f"{'='*60}")
    
    # Find player in NBA API
    player_info = search_player(player_name)
    if player_info == "Player not found":
        print(f"❌ Could not find {player_name} in NBA API")
        return
    
    nba_api_player_id = player_info["id"]
    print(f"✅ Found player: {player_info['full_name']}, NBA API ID: {nba_api_player_id}")
    
    # Parse player name for database lookup
    name_parts = player_name.split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
    
    # Get team IDs from teams mapping
    current_team_id = teams.get(current_team_abbr) 
    former_team_id = teams.get(former_team_abbr)
    
    if not former_team_id:
        print(f"❌ Unknown team abbreviation: {former_team_abbr}")
        return
    
    print(f"🏀 Team IDs: Current={current_team_id} ({current_team_abbr}), Former={former_team_id} ({former_team_abbr})")
    
    # Get or create player in database
    try:
        db_player_id = get_player_id(first_name, last_name, current_team_id)
        print(f"📊 Database Player ID: {db_player_id}")
    except Exception as e:
        print(f"❌ Error getting player from database: {e}")
        return
    
    print(f"\n📊 PERFORMANCE ANALYSIS:")
    print("-" * 40)
    
    try:
        # Get revenge vs regular game comparison
        revenge_games, non_revenge_games = get_fair_comparison(
            player_id=nba_api_player_id,
            former_team=former_team_abbr,
            after_date=departure_date
        )
        
        print(f"Revenge games found: {len(revenge_games)}")
        print(f"Non-revenge games found: {len(non_revenge_games)}")
        if len(revenge_games) >= 1:  # Show revenge games even if not enough for comparison
            print(f"\n🎯 REVENGE GAMES vs {former_team_abbr}:")
            for _, game in revenge_games.iterrows():
                print(f"   {game['Date'].strftime('%Y-%m-%d')}: {game['WL']} {game['Matchup']} - {game['Points']}pts, {game['Rebounds']}reb, {game['Assists']}ast")
        if len(revenge_games) >= 2 and len(non_revenge_games) >= 5:
            comparison = compare_stats(revenge_games, non_revenge_games)
            
            if "error" not in comparison:
                revenge = comparison['revenge_stats']
                regular = comparison['regular_stats']
                diffs = comparison['differences']
                
                print(f"\n📈 STAT COMPARISON:")
                print(f"   Revenge avg: {revenge['points']:.1f} PTS, {revenge['rebounds']:.1f} REB, {revenge['assists']:.1f} AST")
                print(f"   Regular avg: {regular['points']:.1f} PTS, {regular['rebounds']:.1f} REB, {regular['assists']:.1f} AST")
                
                print(f"\n🔥 REVENGE BOOST:")
                print(f"   Points: {diffs['points_diff']:+.1f}")
                print(f"   Rebounds: {diffs['rebounds_diff']:+.1f}")
                print(f"   Assists: {diffs['assists_diff']:+.1f}")
                
                # Calculate weighted revenge factor
                revenge_factor = (
                    diffs['points_diff'] * 1.0 +
                    diffs['rebounds_diff'] * 0.5 +
                    diffs['assists_diff'] * 0.7
                )
                print(f"   Weighted Revenge Factor: {revenge_factor:.2f}")
                
                # Show what performance score this would get
                if revenge_factor >= 5:
                    perf_score = 2.0
                    level = "🔥🔥🔥 ELITE"
                elif revenge_factor >= 3:
                    perf_score = 1.5  
                    level = "🔥🔥 STRONG"
                elif revenge_factor >= 1:
                    perf_score = 1.0
                    level = "🔥 MILD"
                elif revenge_factor >= 0:
                    perf_score = 0.5
                    level = "📈 SLIGHT"
                else:
                    perf_score = 0.0
                    level = "😐 NONE"
                
                print(f"   Performance Level: {level} (+{perf_score} points)")
                
        else:
            print("ℹ️  Insufficient data for statistical comparison")
            print(f"   Need: 2+ revenge games, 5+ regular games")
            print(f"   Have: {len(revenge_games)} revenge, {len(non_revenge_games)} regular")
            
    except Exception as e:
        print(f"❌ Error in performance analysis: {e}")
    
    print(f"\n🏆 VENGE SCORE CALCULATION:")
    print("-" * 40)
    
    # Calculate the full venge score with performance component
    try:
        final_score = calculate_venge_score(
        player_id=db_player_id,
        player_name=player_name,
        opponent_team_id=former_team_id,
        revenge_games_data=revenge_games,      
        non_revenge_games_data=non_revenge_games  
    )
        
        print(f"🎯 FINAL VENGE SCORE: {final_score}/10")
        
        # Show what this means
        if final_score >= 9:
            print("   Level: 🔥🔥🔥 LEGENDARY REVENGE GAME")
        elif final_score >= 7:
            print("   Level: 🔥🔥 HIGH REVENGE POTENTIAL")
        elif final_score >= 5:
            print("   Level: 🔥 SOLID REVENGE GAME")
        elif final_score >= 3:
            print("   Level: 📈 MILD REVENGE STORYLINE")
        else:
            print("   Level: 😐 LOW REVENGE FACTOR")
    except Exception as e:
        print(f"❌ Error calculating venge score: {e}")
        print(f"   This might be due to missing database setup or API issues")
    

if __name__ == "__main__":
    print("🏀 VENGESTATS REVENGE SCORING TEST")
    print("Testing new performance-based scoring system with real database...")
    
    # Test cases - players with known revenge narratives
    # Format: (player_name, former_team_abbr, departure_date, current_team_abbr)
    test_cases = [
        # ("Kyrie Irving", "BOS", "2019-05-08", "DAL"),   # Kyrie vs Celtics
        # ("Luka Dončić", "DAL", "2025-01-30", "LAL"),   # Luka vs Mavs
        # ("Kevin Durant", "GSW", "2019-07-07", "PHO"),   # KD vs Warriors  
        # ("Kevin Durant", "OKC", "2016-05-30", "PHO"),   # KD vs OKC  
        # ("LeBron James", "CLE", "2010-05-13", "MIA"),   # LeBron vs Heat
        # ("Jimmy Butler", "MIN", "2018-11-12", "GSW"),   # Jimmy vs Wolves
        # ("Jimmy Butler", "CHI", "2017-04-28", "GSW"),   # Jimmy vs MIA
        # ("Paul George", "IND", "2017-07-06", "PHI"),    # PG vs Pacers
    ]
    
    for player_name, former_team_abbr, departure_date, current_team_abbr in test_cases:
        try:
            time.sleep(5)
            test_player_revenge_scoring(player_name, former_team_abbr, departure_date, current_team_abbr)
        except Exception as e:
            print(f"❌ Error testing {player_name}: {e}")
        
        print("\n" + "="*60 + "\n")