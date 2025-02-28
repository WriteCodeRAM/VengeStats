from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.bot.config import USERNAME, PASSWORD
import time

TWEET_TEXT = "selenium test tweet #2"

driver = webdriver.Chrome()

def login_to_twitter():
    """Logs into Twitter and handles popups if any appear."""
    driver.get("https://twitter.com/login")
    time.sleep(3)

    # Enter username
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys(USERNAME)
    username_field.send_keys(Keys.RETURN)
    time.sleep(3)

    # Enter password
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)

    # Handle unexpected popups 
    try:
        dismiss_button = driver.find_element(By.XPATH, "//div[@role='button'][text()='Not now']")
        dismiss_button.click()
        time.sleep(2)
    except:
        print("✅ No popups detected, continuing.")

def post_tweet(tweet: str):
    """Posts a tweet after ensuring elements are loaded."""
    try:
        # wait for the tweet box to appear
        tweet_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
        )
        tweet_box.send_keys(tweet)
        time.sleep(2)

        # press ENTER to post instead of clicking
        tweet_box.send_keys(Keys.COMMAND, Keys.RETURN) 
        time.sleep(3)

        print("✅ Tweet posted successfully!")

    except Exception as e:
        print(f"❌ Error posting tweet: {e}")


if __name__ == "__main__":
    try:
        login_to_twitter() 
        post_tweet(TWEET_TEXT) 
    finally:
        driver.quit()  # close browser