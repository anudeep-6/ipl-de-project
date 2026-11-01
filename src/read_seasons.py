"""Reconcile raw season labels against the season dimension.

Reads every raw Cricsheet file, looks up its season label in season_alias, and
reports how many matches map to a dim_season row. Expected: every match mapped,
none unmapped.
"""

import os
import json
from pathlib import Path
from reference_data import dim_season, season_alias

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
season_counts = {}

mapped = 0
unmapped = 0

for filename in os.listdir(raw_dir):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        # Raw labels mix numbers (2012) and text ("2012"). Convert to text first
        # so both land on the same alias key, then trim stray spaces.
        season = str(data["info"].get("season", "MISSING"))
        if season_alias.get(season.strip(), "UNMAPPED") == "UNMAPPED":
            unmapped += 1
        else:
            mapped += 1
        season_counts[season] = season_counts.get(season, 0) + 1

print("mapped, unmapped, total:", mapped, unmapped, mapped + unmapped)
print("dim_season rows, season_alias rows:", len(dim_season), len(season_alias))

# Matches per raw season label; the total must equal the number of files (1,243).
for season, n in sorted(season_counts.items()):
    print(repr(season), n)
print("distinct labels, total matches:", len(season_counts), sum(season_counts.values()))