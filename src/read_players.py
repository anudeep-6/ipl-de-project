"""Build dim_player: one row per person, keyed by the Cricsheet registry code.

A few codes appear under two spellings across files (e.g. "NA Saini" and
"Navdeep Saini"). For those we choose the name by hand in name_overrides;
every other code has exactly one name. Any other code with two or more names
is printed as "needs override" so a human decides, never guessed.

Writes the result to data/processed/dim_player.csv (964 rows plus a header).
"""

import csv
import os
import json
from pathlib import Path

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

# Codes with two spellings: the clean name is chosen by hand, never guessed.
name_overrides = {
    "21d4e29b": "Navdeep Saini",
    "12314277": "Arshad Khan",
    "d7423da1": "Salil Arora",
}

# code -> set of names seen for that code across all files
names_by_code = {}
for filename in sorted(os.listdir(raw_dir)):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        for name, code in data["info"]["registry"]["people"].items():
            # First time we see this code: start an empty set for its names.
            if code not in names_by_code:
                names_by_code[code] = set()
            # A set keeps each distinct name once, however many files repeat it.
            names_by_code[code].add(name)

dim_player = []
for code, names in names_by_code.items():
    if code in name_overrides:
        player_name = name_overrides[code]
    else:
        # A set cannot be indexed; sorted() turns it into a list. With one name, [0] is that name.
        player_name = sorted(names)[0]
    dim_player.append({"player_id": code, "player_name": player_name})

print("dim_player rows:", len(dim_player))

# Any code with 2+ names that is not in name_overrides needs a human decision.
unresolved = 0
for code, names in names_by_code.items():
    if len(names) > 1 and code not in name_overrides:
        unresolved += 1
        print("needs override:", code, names)
print("codes needing an override:", unresolved)

# Write dim_player to data\processed (mode "w" replaces the file on every run).
output_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "dim_player.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["player_id", "player_name"])
    for row in dim_player:
        writer.writerow([row["player_id"], row["player_name"]])
print("written to", output_path)