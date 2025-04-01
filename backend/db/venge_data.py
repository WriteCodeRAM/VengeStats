# All-Star Selections for 2024-2025 Season
all_stars = {
    "LeBron James", "Jaylen Brown", "Stephen Curry", "Kevin Durant", "James Harden",
    "Kyrie Irving", "Damian Lillard", "Jayson Tatum", "Nikola Jokic", "Shai Gilgeous-Alexander",
    "Donovan Mitchell", "Pascal Siakam", "Karl-Anthony Towns", "Alperen Sengun",
    "Victor Wembanyama", "Trae Young", "Anthony Edwards", "Jalen Brunson", "Cade Cunningham",
    "Darius Garland", "Tyler Herro", "Jaren Jackson Jr.", "Evan Mobley", "Jalen Williams"
}

# Players with strong revenge narratives (long tenure, messy exits, emotional returns)
revenge_narratives = {
    "Kevin Durant": ["GSW", "OKC"],
    "Kyrie Irving": ["BOS"],
    "LeBron James": ["CLE", "MIA"],
    "Jimmy Butler": ["MIN", "PHI", "MIA"],
    "Paul George": ["IND"],
    "Chris Paul": ["HOU", "LAC"],
    "James Harden": ["HOU","PHI"],
    "Ben Simmons": ["PHI"],
    "Russell Westbrook": ["OKC", "LAL"],
    "Jrue Holiday": ["MIL"],
    "Marcus Smart": ["BOS"],
}

# Venge Score / Formula here 
# updated revege games will return the following data ['James Johnson', 'Minnesota Timberwolves', None]
# can we use this to help weith scoring 
# lookup player name in db, get id, check first game table, check histories, check for name in revenge narratives / all stars. generate score
# 
def calculate_venge_score():  
