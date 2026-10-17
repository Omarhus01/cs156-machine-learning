
    # Predicting League of Legends rank from match data
  
The model I wanted to makke is predicting  ranked solo tier (Iron to Challenger, 10 classes) from their recent ranked games. The data comes from the Riot API across four servers: KR, EUW, EUNE and NA. I compared 12 setups with 5-fold cross-validation on 1,088 players, then test the best one once on 273 hidden players.
 
The final model turns each tier into a number, Iron = 0 to Challenger = 9. A random forest of 500 decision trees guesses that number for each player, I average the 500 guesses, and I round to the nearest tier. Treating the tier as a number tells the model that Gold is closer to Platinum than to Challenger, so its misses land near the real tier.
 
## Folder layout
 
- `src/config.py`: pull settings (servers, tiers, players per tier, games per player, days back)
- `src/riot_client.py`: Riot API calls with a rate limit, retries and a call log
- `src/pull_players.py`: samples ranked players per server and tier
- `src/pull_matches.py`: downloads match IDs and match JSON for one regional host
- `notebooks/01_ingest.ipynb`: match JSON to one row per game, all 358 fields
- `notebooks/02_clean.ipynb`: keeps 65 of the 358 fields, flags edge-case games, adds per-minute stats
- `notebooks/03_model.ipynb`: one row per player, 12 runs with 5-fold CV, final test, error analysis
- `data/raw/`: API output, not in the repo
- `data/processed/games_raw.csv`: output of 01
- `data/processed/columns_raw.csv`: type, non-null count and example value of each raw field
- `data/processed/column_dictionary.csv`: meaning and group of each raw field
- `data/processed/games_clean.csv`: output of 02, input of 03
- `figures/`: plots saved by the notebooks
- `requirements.txt`: pinned packages
- `.env`: your API key, not in the repo
## The data
 
- Players: sampled at random per server and tier. Iron to Diamond from divisions I to IV, Master to Challenger from the full apex ladders. Each player needs at least 20 ranked games this season and an active account.
- Games: up to 15 ranked solo games (queue 420) per player from the 45 days before the pull. Players with fewer than 8 games are dropped.
- Size: pulled on Oct 13, 2026. 1,361 players and 19,824 games. The cap is 45 players per server and tier. Master, GM and Challenger reach it (180 players each). Iron to Diamond have 99 to 166.
- Label: the player's tier at pull time. Division and LP are not used.
## Setup
 
Python 3.14.3.
 
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
 
On macOS or Linux, activate with `source venv/bin/activate`.
 
To pull new data, create a `.env` file in this folder with your Riot API key:
 
```
RIOT_API_KEY=your_key
```
 
A development key from developer.riotgames.com expires after 24 hours. The pull scripts stop on a 401 or 403 and ask for a new key.
 
## How to run
 
Run everything from this folder. The scripts use relative paths.
 
To pull new data:
 
```
python src/pull_players.py
python src/pull_matches.py --host asia
python src/pull_matches.py --host europe
python src/pull_matches.py --host americas
```
 
Run the three match pulls at the same time, one terminal per host. The client waits 1.25 seconds between calls on each host to stay under the key's limit of 100 calls per 2 minutes. A pull is safe to stop and rerun: finished files are skipped. Add `--max-players 2` to test a pull first.
 
Then run the notebooks in order, with the venv as the kernel:
 
1. `notebooks/01_ingest.ipynb`
2. `notebooks/02_clean.ipynb`
3. `notebooks/03_model.ipynb`
Every split and model uses seed 156, so 02 and 03 give the same numbers on every run.
 
## Running without a pull
 
`data/raw` is not in the repo. It holds more than 21,000 files, and the pull needs an API key. The four files in `data/processed` are committed, so:
 
- `01_ingest` does not run. It needs `data/raw`.
- `02_clean` runs from `games_raw.csv`.
- `03_model` runs from `games_clean.csv`.
`01_ingest` and `02_clean` download item names from Riot's Data Dragon (patch 16.20.1), so they need internet. `03_model` does not.
 
A new pull samples different players, since the ladder changes every day, so its numbers will differ from mine.
 
## Results
 
Final test on the 273 hidden players. All features is Run 6. Gameplay only is Run 8, which drops summoner level, season games and season win rate.
 
| | Accuracy | Macro F1 | Within one tier | Mean tier error |
|---|---|---|---|---|
| All features | 0.348 | 0.336 | 0.828 | 0.886 |
| Gameplay only | 0.187 | 0.172 | 0.630 | 1.440 |
 
Within one tier is the share of players predicted at most one tier from their real tier. Mean tier error is the average gap in tiers. For scale, guessing Master for everyone gets 0.387 within one tier and 2.70 tiers off in validation.
 
Most of the all-features score comes from the season record (games played and win rate), which is close to how the ladder assigns rank in the first place. Gameplay alone still lands within one tier for 63% of players.
 
Plots are in `figures/`.
 
