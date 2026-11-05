"""Build bridge_wicket_fielder: one row per fielder involved in one wicket (11,266 rows).

Why a bridge table: a wicket has 0 to 3 fielders (bowled and lbw have none, a catch
or stumping has one, a run out can have up to three). A list cannot sit in one
fact_delivery cell, and repeating the delivery row per fielder would change its grain
and double count runs.

Grain: one row = one fielder on one wicket.
Key: match_id + innings_number + delivery_seq + fielder_id. The first three columns
are the foreign key back to fact_delivery; fielder_id tells apart the fielders of
one wicket.

Columns:
  fielder_id    : registry code of the fielder (name -> code, per-match registry).
                  A name missing from the registry is flagged UNMAPPED, never guessed.
  is_substitute : True when the fielder was a substitute, not in the playing XI.
                  Cricsheet only writes the key for substitutes, so absent means False.

Reconciliation checks at the end must all pass before the rows are used.
"""

import csv
import json
import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
raw_dir = base_dir / "data" / "raw"
output_path = base_dir / "data" / "processed" / "bridge_wicket_fielder.csv"

fielder_rows = []
# Keys (match_id, innings_number, delivery_seq) of every delivery that has a wicket,
# used at the end to check that no fielder row points at a delivery without a wicket.
wicket_keys = set()

# sorted() keeps the row order the same on every run.
for filename in sorted(os.listdir(raw_dir)):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        # The name -> code registry is per match, so it is loaded inside the file loop.
        people = data["info"]["registry"]["people"]
        match_id = filename.replace(".json", "")
        innings_number = 0
        for innings in data["innings"]:
            innings_number += 1
            # Same counter as read_deliveries.py (every ball, wides and no-balls included),
            # so the keys join to fact_delivery.
            delivery_seq = 0
            for over in innings["overs"]:
                for delivery in over["deliveries"]:
                    delivery_seq += 1
                    if "wickets" in delivery:
                        wicket_keys.add((match_id, innings_number, delivery_seq))
                    for wicket in delivery.get("wickets", []):
                        # Bowled, lbw etc. have no "fielders" key, so default to an empty list.
                        for fielder in wicket.get("fielders", []):
                            fielder_rows.append({
                                "match_id": match_id,
                                "innings_number": innings_number,
                                "delivery_seq": delivery_seq,
                                "fielder_id": people.get(fielder["name"], "UNMAPPED"),
                                # Only substitutes carry the "substitute" key (value True).
                                "is_substitute": fielder.get("substitute", False)
                            })

# Reconciliation. Expected:
# - 11,266 rows (9,321 catches + 388 stumpings + 1,557 from run outs)
# - 227 substitute rows
# - 0 UNMAPPED fielder_id
# - 11,266 unique keys, 0 duplicates
# - 14,705 wicket deliveries (same as fact_delivery), 0 orphan fielder rows
print("total rows", len(fielder_rows))
print(fielder_rows[0])

substitute_count = 0
unmapped_count = 0
seen_keys = set()
duplicate_count = 0
orphans = 0

for row in fielder_rows:
    key = (row["match_id"], row["innings_number"], row["delivery_seq"], row["fielder_id"])
    delivery_key = (row["match_id"], row["innings_number"], row["delivery_seq"])
    if row["is_substitute"]:
        substitute_count += 1
    if row["fielder_id"] == "UNMAPPED":
        unmapped_count += 1
    if key in seen_keys:
        duplicate_count += 1
    seen_keys.add(key)
    if delivery_key not in wicket_keys:
        orphans += 1

print("substitute rows:", substitute_count)
print("UNMAPPED fielder_id:", unmapped_count)
print("unique keys, duplicates:", len(seen_keys), duplicate_count)
print("wicket deliveries:", len(wicket_keys))
print("orphan fielder rows:", orphans)

columns = ["match_id", "innings_number", "delivery_seq", "fielder_id", "is_substitute"]

# Creates data\processed if it does not exist yet.
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    for row in fielder_rows:
        writer.writerow([row[column] for column in columns])

print("written to", output_path)