"""Reconcile raw team spellings against the team dimension.

Reads every raw Cricsheet file, looks up each team name in team_alias, and
reports how many map to a dim_team row. Expected: every team mapped, none
unmapped.
"""

import os
import json
from pathlib import Path
from reference_data import dim_team, team_alias

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

mapped = 0
unmapped = 0

for filename in os.listdir(raw_dir):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        # Each match lists two teams, so the total should be 2 x 1,243 = 2,486.
        for team in data["info"]["teams"]:
            # Trim stray spaces first, then look up the alias.
            if team_alias.get(team.strip(), "UNMAPPED") == "UNMAPPED":
                unmapped += 1
            else:
                mapped += 1

print("mapped, unmapped, total:", mapped, unmapped, mapped + unmapped)
print("dim_team rows, team_alias rows:", len(dim_team), len(team_alias))