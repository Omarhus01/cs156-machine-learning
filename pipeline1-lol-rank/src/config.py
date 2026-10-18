from pathlib import Path

# platform host -> regional host
SERVERS = {"kr": "asia", "euw1": "europe", "eun1": "europe", "na1": "americas"}

DIV_TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
DIVISIONS = ["I", "II", "III", "IV"]
APEX_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]
TIERS = DIV_TIERS + APEX_TIERS  # index 0..9 = label

PAGES_PER_DIVISION = 2
CANDIDATES_PER_DIVISION = 15   # 60 per tier
CANDIDATES_APEX = 60
PLAYERS_PER_TIER = 45          # stop after 45 good players per server+tier
MIN_SEASON_GAMES = 20
MATCHES_PER_PLAYER = 15
MIN_MATCH_IDS = 8              # skip players with fewer recent ranked games
START_DAYS_AGO = 45            # set to the current split start if you know it

RAW = Path("data/raw")
SEED = 156
