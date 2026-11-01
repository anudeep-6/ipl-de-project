"""Build one match row per raw Cricsheet file (1,243 matches).

Maps raw team, venue and season spellings to dimension ids through the alias
tables in reference_data.py, then reconciles the result: every row must have a
valid date_key and no "UNMAPPED" values.
"""

import os
import json
from pathlib import Path
from reference_data import venue_alias, team_alias, season_alias, dim_date

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

match_rows = []
for filename in os.listdir(raw_dir):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
            info = data["info"]
            # No-result matches have no winner. Store None (NULL), never a fake
            # value. "UNMAPPED" is reserved for spellings missing from the alias tables.
            winner = info["outcome"].get("winner")
            if winner is None:
                winner_team_id = None
            else:
                winner_team_id = team_alias.get(winner.strip(), "UNMAPPED")
            result = info["outcome"].get("result")
            eliminator = info["outcome"].get("eliminator")
            if eliminator is None:
                eliminator_team_id = None
            else:
                eliminator_team_id = team_alias.get(eliminator.strip(), "UNMAPPED")
            match_row = {
                "match_id": filename.replace(".json", ""),
                "season_id": season_alias.get(str(info.get("season")).strip(), "UNMAPPED"),
                "venue_id": venue_alias.get(info.get("venue", "").strip(), "UNMAPPED"),
                "team1_id": team_alias.get(info["teams"][0].strip(), "UNMAPPED"),
                "team2_id": team_alias.get(info["teams"][1].strip(), "UNMAPPED"),
                "winner_team_id": winner_team_id,
                "result": result,
                "eliminator_team_id": eliminator_team_id,
                # A match can span several days (info["dates"]); use the first one.
                "match_date": info["dates"][0],
                "date_key": int(info["dates"][0].replace("-", ""))
            }
        match_rows.append(match_row)

# Reconciliation: every date must exist in dim_date and no id may be UNMAPPED.
dim_date_keys = set()
for row in dim_date:
    dim_date_keys.add(row["date_key"])

missing = 0
for row in match_rows:
    if row["date_key"] not in dim_date_keys:
        missing += 1
print("date_key missing from dim_date", missing)

check_columns = ["season_id", "venue_id", "team1_id", "team2_id", "winner_team_id", "eliminator_team_id"]

for column in check_columns:
    bad = 0
    for row in match_rows:
        if row[column] == "UNMAPPED":
            bad += 1
    print(column, bad)
print(match_rows[0])
print("total rows", len(match_rows))
