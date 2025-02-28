from backend.schedule.get_schedule import get_nba_schedule, get_team_ids
from backend.db.database import get_revenge_games
from backend.bot.twitter_bot import login_to_twitter, post_tweet, format_revenge_tweet
from backend.scrapers.injury_scrapers import get_nba_injuries
from selenium import webdriver

def run():
    """Main function to fetch NBA revenge games, check injuries, and post tweets."""
    
    # get todays schedule and potential revenge games
    daily_schedule = get_nba_schedule()  
    team_id_list = get_team_ids(daily_schedule)  
    revenge_games = get_revenge_games(team_id_list)

    # injury updates
    updated_revenge_games = get_nba_injuries(revenge_games)
    revenge_games_to_tweet = [game for game in updated_revenge_games if game[2] != "Out"]

    # make bot post tweets
    try:
        driver = webdriver.Chrome() 
        login_to_twitter(driver)  
        
        for game in revenge_games_to_tweet:
            tweet = format_revenge_tweet(game)
            post_tweet(driver, tweet) 

    finally:
        driver.quit() # close browser 

if __name__ == "__main__":
    run()
