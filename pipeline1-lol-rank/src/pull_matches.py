"""Step 2: match IDs + full match JSON for one regional host.

Run one process per host, in parallel:
    python src/pull_matches.py --host europe
    python src/pull_matches.py --host americas
    python src/pull_matches.py --host asia
Test first with:  python src/pull_matches.py --host europe --max-players 2
Safe to stop and rerun: finished files are skipped.
"""
import argparse
import csv
import json
import time
from collections import defaultdict

from config import MATCHES_PER_PLAYER, MIN_MATCH_IDS, PLAYERS_PER_TIER, RAW, START_DAYS_AGO
from riot_client import get


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True, choices=["europe", "americas", "asia"])
    ap.add_argument("--max-players", type=int, default=None, help="stop after N players (testing)")
    args = ap.parse_args()

    (RAW / "match_ids").mkdir(parents=True, exist_ok=True)
    (RAW / "matches").mkdir(parents=True, exist_ok=True)
    start = int(time.time()) - START_DAYS_AGO * 86400

    with open(RAW / "players_sampled.csv") as f:
        players = [p for p in csv.DictReader(f) if p["region"] == args.host]

    groups = defaultdict(list)
    for p in players:
        groups[(p["server"], p["tier"])].append(p)

    used_path = RAW / f"used_players_{args.host}.csv"
    used = set()
    if used_path.exists():
        with open(used_path) as f:
            used = {r["puuid"] for r in csv.DictReader(f)}
    done = {g: sum(p["puuid"] in used for p in ps) for g, ps in groups.items()}
    nxt = {g: 0 for g in groups}

    new_file = not used_path.exists()
    used_f = open(used_path, "a", newline="")
    used_w = csv.writer(used_f)
    if new_file:
        used_w.writerow(["server", "tier", "puuid", "n_match_ids"])

    count = 0
    # round robin over server+tier groups so a partial pull stays balanced
    while True:
        progressed = False
        for g, ps in groups.items():
            if done[g] >= PLAYERS_PER_TIER or nxt[g] >= len(ps):
                continue
            p = ps[nxt[g]]
            nxt[g] += 1
            progressed = True
            if p["puuid"] in used:
                continue

            ids_path = RAW / "match_ids" / f"{p['server']}_{p['puuid']}.json"
            if ids_path.exists():
                ids = load_json(ids_path)
            else:
                ids = get(args.host, f"/lol/match/v5/matches/by-puuid/{p['puuid']}/ids",
                          {"queue": 420, "count": MATCHES_PER_PLAYER, "startTime": start}) or []
                with open(ids_path, "w") as f:
                    json.dump(ids, f)
            if len(ids) < MIN_MATCH_IDS:
                continue

            for mid in ids:
                m_path = RAW / "matches" / f"{mid}.json"
                if m_path.exists():
                    continue
                m = get(args.host, f"/lol/match/v5/matches/{mid}")
                if m:
                    with open(m_path, "w") as f:
                        json.dump(m, f)

            used_w.writerow([p["server"], p["tier"], p["puuid"], len(ids)])
            used_f.flush()
            used.add(p["puuid"])
            done[g] += 1
            count += 1
            print(f"[{args.host}] {g[0]} {g[1]}: {done[g]}/{PLAYERS_PER_TIER} players", flush=True)
            if args.max_players and count >= args.max_players:
                used_f.close()
                return
        if not progressed:
            break
    used_f.close()
    short = {f"{s} {t}": n for (s, t), n in done.items() if n < PLAYERS_PER_TIER}
    print("Finished.", "Short groups: " + str(short) if short else "All groups full.")


if __name__ == "__main__":
    main()