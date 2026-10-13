"""Step 1: sample ranked players per server and tier -> data/raw/players_sampled.csv"""
import csv
import json
import random

from config import (APEX_TIERS, CANDIDATES_APEX, CANDIDATES_PER_DIVISION, DIV_TIERS,
                    DIVISIONS, MIN_SEASON_GAMES, PAGES_PER_DIVISION, RAW, SEED, SERVERS)
from riot_client import get

QUEUE = "RANKED_SOLO_5x5"
COLS = ["server", "region", "tier", "division", "leaguePoints", "wins", "losses",
        "veteran", "freshBlood", "hotStreak", "inactive", "puuid"]


def eligible(e):
    return e.get("puuid") and e["wins"] + e["losses"] >= MIN_SEASON_GAMES and not e.get("inactive")


def save(name, data):
    (RAW / "league").mkdir(parents=True, exist_ok=True)
    with open(RAW / "league" / name, "w") as f:
        json.dump(data, f)


def main():
    random.seed(SEED)
    rows = []
    for server, region in SERVERS.items():
        for tier in DIV_TIERS:
            for div in DIVISIONS:
                pool = []
                for page in range(1, PAGES_PER_DIVISION + 1):
                    data = get(server, f"/lol/league/v4/entries/{QUEUE}/{tier}/{div}", {"page": page}) or []
                    save(f"{server}_{tier}_{div}_p{page}.json", data)
                    pool += [e for e in data if eligible(e)]
                pick = random.sample(pool, min(CANDIDATES_PER_DIVISION, len(pool)))
                rows += [{**e, "server": server, "region": region, "tier": tier, "division": div} for e in pick]
                print(f"{server} {tier} {div}: {len(pool)} eligible, took {len(pick)}")

        for tier in APEX_TIERS:
            data = get(server, f"/lol/league/v4/{tier.lower()}leagues/by-queue/{QUEUE}") or {}
            save(f"{server}_{tier}.json", data)
            pool = [e for e in data.get("entries", []) if eligible(e)]
            pick = random.sample(pool, min(CANDIDATES_APEX, len(pool)))
            rows += [{**e, "server": server, "region": region, "tier": tier, "division": "I"} for e in pick]
            print(f"{server} {tier}: {len(pool)} eligible, took {len(pick)}")

    with open(RAW / "players_sampled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Saved {len(rows)} candidates to {RAW / 'players_sampled.csv'}")


if __name__ == "__main__":
    main()