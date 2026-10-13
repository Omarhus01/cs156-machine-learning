import csv
import os
import time

import requests
from dotenv import load_dotenv

from config import RAW

load_dotenv()
KEY = os.getenv("RIOT_API_KEY")
if not KEY:
    raise SystemExit("RIOT_API_KEY missing. Put it in .env in the repo root.")

MIN_GAP = 1.25  # seconds between calls on one host = 96 calls per 2 minutes
_last_call = {}


def _log(host, url, status):
    path = RAW / f"pull_log_{host}.csv"
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "url", "status"])
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), url, status])


def get(host, path, params=None):
    url = f"https://{host}.api.riotgames.com{path}"
    for attempt in range(4):
        wait = MIN_GAP - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.get(url, params=params, headers={"X-Riot-Token": KEY}, timeout=20)
        except requests.RequestException:
            _last_call[host] = time.time()
            time.sleep(2 ** (attempt + 1))
            continue
        _last_call[host] = time.time()
        _log(host, r.url, r.status_code)

        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 10)))
            continue
        if r.status_code in (401, 403):
            raise SystemExit("401/403: key expired or invalid. Regenerate it and rerun.")
        if r.status_code == 404:
            return None
        if r.status_code >= 500:
            time.sleep(2 ** (attempt + 1))
            continue
        return None
    return None