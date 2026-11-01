"""Reconcile raw venue spellings against the venue dimension.

Reads every raw Cricsheet file, looks up its venue spelling in venue_alias, and
reports how many matches map to a dim_venue row. Expected: every match mapped,
none unmapped.
"""

import json
import os
from pathlib import Path
from reference_data import dim_venue, venue_alias

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

mapped = 0
unmapped = 0

for filename in os.listdir(raw_dir):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        # Trim first, then look up: strip() only removes spaces at the ends, so
        # spelling differences inside the name need their own alias row.
        # A missing venue becomes "MISSING", which is not an alias, so it is
        # counted as unmapped instead of crashing.
        venue = data["info"].get("venue", "MISSING").strip()
        vid = venue_alias.get(venue, "UNMAPPED")
        if vid == "UNMAPPED":
            unmapped += 1
        else:
            mapped += 1

print("mapped, unmapped, total:", mapped, unmapped, mapped + unmapped)
# 60 spellings collapse into 36 stadiums, so many aliases point to one venue id.
print("dim_venue rows, venue_alias rows:", len(dim_venue), len(venue_alias))