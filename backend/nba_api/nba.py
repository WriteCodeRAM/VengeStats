from backend.nba_api.utils.player_utils import search_player
from backend.nba_api.utils.data_fetcher import get_stats

if __name__ == "__main__":
    # Find Player 
    player_info = search_player("Kyrie Irving")
    if player_info != "Player not found":
        pid = player_info["id"]
        print(f"Found player: {player_info['full_name']}, ID: {pid}")
        
        # This will find games where BOS is the OPPONENT
        df = get_stats(pid, opponent="BOS", after_date="2019-05-08")

        # Get averages directly
        print(df)
        avg_points = df['Points'].mean()
        avg_rebounds = df['Rebounds'].mean() 
        avg_assists = df['Assists'].mean()
        avg_minutes = df['Minutes'].mean()

        print(f"Averages: {avg_points:.1f} PTS, {avg_rebounds:.1f} REB, {avg_assists:.1f} AST")
    else:
        print("Player not found")