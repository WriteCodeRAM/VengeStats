import requests
import os

api_key = os.getenv('SPORTS_BLAZE_API_KEY')
def get_wnba_roster(): 
    url = f"https://api.sportsblaze.com/wnba/v1/rosters/2025.json?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data['teams'])

       


get_wnba_roster() 