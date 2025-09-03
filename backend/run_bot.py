from bot.twitter_bot import login_to_twitter, post_tweet, format_revenge_tweet
from schedule.nba_revenge_pipeline import get_daily_revenge_matchups
from selenium import webdriver

def run():
    # get todays schedule and potential revenge games
    revenge_games_to_tweet = get_daily_revenge_matchups()
    
    # print(revenge_games_to_tweet)
    if len(revenge_games_to_tweet):
        try:
            driver = webdriver.Chrome() 
            login_to_twitter(driver)  
            
            for game in revenge_games_to_tweet:
                tweet = format_revenge_tweet(game)
                post_tweet(driver, tweet) 
        finally:
            driver.quit() # close browser 
    else: 
        print("No revenge games today!")

if __name__ == "__main__":
    run()
 