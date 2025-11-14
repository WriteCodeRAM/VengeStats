import os
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def refresh_cache():
    base_url = os.getenv('API_BASE_URL')
    cache_key = os.getenv('CACHE_KEY')
    
    if not base_url or not cache_key:
        print(f"Missing environment variables. API_BASE_URL: {base_url}, CACHE_KEY: {bool(cache_key)}")
        sys.exit(1)
    
    print(f"Starting cache refresh at {datetime.now()}")
    
    try:
        print("Step 1: Clearing cache")
        clear_response = requests.get(f"{base_url}/cache/clear/{cache_key}")
        print(f"Cache clear response: {clear_response.json()}")
        print("Step 2: Regenerating matchups...")
        matchups_response = requests.get(f"{base_url}/matchups", timeout=60)  
        
        if matchups_response.status_code == 200:
            data = matchups_response.json()
            print(f"✅ Success! Regenerated {len(data.get('nba_revenge_matchups', []))} NBA and {len(data.get('nfl_revenge_matchups', []))} NFL matchups")
        else:
            print(f"⚠️ Unexpected status: {matchups_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during refresh: {e}")
        sys.exit(1)
    
    print(f"Cache refresh completed at {datetime.now()}")

if __name__ == "__main__":
    refresh_cache()