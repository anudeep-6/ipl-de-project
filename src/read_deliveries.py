"""Build one fact_delivery row per ball from the raw Cricsheet files (295,732 rows).

Grain: one row = one delivery. The key is match_id + innings_number + delivery_seq.
delivery_seq is a counter we create (it restarts at 1 in each innings), because
the over.ball label in the raw data can repeat when wides and no-balls are bowled.

Columns:
  is_legal_delivery : False for wides and no-balls, True for every other delivery
                      (leg-byes, byes and wickets are still legal balls).
  runs_*            : additive measures; runs_batter + runs_extras = runs_total.
  is_wicket         : a batter's innings ended on this ball (max one per delivery).
  wicket_kind       : dismissal type, or None when there is no wicket.
  is_bowler_wicket  : the wicket is credited to the bowler (not run outs, retirements
                      or obstructing the field).
  player_out_id     : registry code of the dismissed player, None when there is no
                      wicket. Can be the non-striker (run outs).
  *_id (players)    : registry codes, which identify a person better than a name.
  batting_team_id   : the team batting in this innings (id from team_alias),
                      looked up once per innings.
  over_number       : the over the ball was bowled in, 1-20 (Cricsheet counts
                      from 0, so we add 1).

Reconciliation checks at the end must all pass before the rows are used.
"""

import os
import json
from pathlib import Path
from reference_data import team_alias

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

# Dismissals credited to the bowler. Run outs, retired hurt/out and obstructing
# the field are wickets for the batting side but not wickets taken by the bowler.
bowler_wickets = {"caught", "bowled", "lbw", "caught and bowled", "stumped", "hit wicket"}

delivery_rows = []
bad_batting_team = 0
# Counted in the delivery loop because the row only stores is_legal_delivery,
# not which kind of illegal ball it was (extras is only available here).
wides_count = 0
noballs_count = 0

# sorted() makes the file order, and so the row order, the same on every run.
for filename in sorted(os.listdir(raw_dir)):
    if filename.endswith(".json"):
        with open(os.path.join(raw_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
        # The name -> code registry is per match, so it is loaded inside the file loop.
        people = data["info"]["registry"]["people"]
        match_id = filename.replace(".json", "")
        # The ids of the two teams playing this match, used to validate batting_team_id.
        match_team_ids = {team_alias.get(team.strip(), "UNMAPPED") for team in data["info"]["teams"]}
        innings_number = 0
        for innings in data["innings"]:
            innings_number += 1
            delivery_seq = 0
            # Same for every ball in the innings, so it is looked up once here.
            batting_team_id = team_alias.get(innings["team"].strip(), "UNMAPPED")
            for over in innings["overs"]:
                # Cricsheet numbers overs from 0; we store 1-20 as people say "1st over".
                over_number = over["over"] + 1
                for delivery in over["deliveries"]:
                    delivery_seq += 1
                    # Only wides and no-balls are illegal; the value is the runs, so test the key.
                    extras = delivery.get("extras", {})
                    is_legal_delivery = not ("wides" in extras or "noballs" in extras)
                    runs = delivery["runs"]
                    # At most one wicket per delivery (checked on all files), so take the first.
                    wickets = delivery.get("wickets", [])
                    is_wicket = len(wickets) > 0
                    wicket_kind = wickets[0]["kind"] if is_wicket else None
                    # The dismissed player is not always the batter on strike (run outs).
                    player_out_id = people.get(wickets[0]["player_out"], "UNMAPPED") if is_wicket else None
                    is_bowler_wicket = wicket_kind in bowler_wickets
                    # A name missing from the registry is flagged, never guessed.
                    batter_id = people.get(delivery["batter"], "UNMAPPED")
                    bowler_id = people.get(delivery["bowler"], "UNMAPPED")
                    non_striker_id = people.get(delivery["non_striker"], "UNMAPPED")
                    # Counts deliveries where the batting team is not one of the match's two teams.
                    if batting_team_id not in match_team_ids:
                        bad_batting_team += 1
                    if "wides" in extras:
                        wides_count += 1
                    if "noballs" in extras:
                        noballs_count += 1
                    delivery_rows.append({
                        "match_id": match_id,
                        "innings_number": innings_number,
                        "delivery_seq": delivery_seq,
                        "is_legal_delivery": is_legal_delivery,
                        "runs_batter": runs["batter"],
                        "runs_extras": runs["extras"],
                        "runs_total": runs["total"],
                        "is_wicket": is_wicket,
                        "wicket_kind": wicket_kind,
                        "is_bowler_wicket": is_bowler_wicket,
                        "batter_id": batter_id,
                        "bowler_id": bowler_id,
                        "non_striker_id": non_striker_id,
                        "batting_team_id": batting_team_id,
                        "over_number": over_number,
                        "player_out_id": player_out_id
                    })

# Reconciliation. Expected:
# - 295,732 rows
# - 11,102 illegal deliveries (9,876 wides + 1,226 no-balls)
# - 0 rows where runs do not add up; sums: batter 381,529, extras 20,209, total 401,738
# - 14,705 wickets, 13,482 of them credited to the bowler
# - 14,705 player_out ids, 0 UNMAPPED; 571 dismissals of the non-striker (run outs)
# - 0 UNMAPPED player ids and 0 UNMAPPED batting_team_id
# - 0 rows with a batting team outside the match's two teams
# - over_number between 1 and 20
print("total rows", len(delivery_rows))
print(delivery_rows[0])

illegal = 0
bad_runs = 0
wickets_count = 0
bowler_wickets_count = 0
batting_team_id_unmapped = 0
over_numbers = []
sum_batter = 0
sum_extras = 0
sum_total = 0
player_out_count = 0
player_out_unmapped = 0
out_not_batter = 0
out_non_striker = 0

for row in delivery_rows:
    if not row["is_legal_delivery"]:
        illegal += 1
    if row["runs_batter"] + row["runs_extras"] != row["runs_total"]:
        bad_runs += 1
    if row["is_wicket"]:
        wickets_count += 1
    if row["is_bowler_wicket"]:
        bowler_wickets_count += 1
    if row["batting_team_id"] == "UNMAPPED":
        batting_team_id_unmapped += 1
    if row["player_out_id"] is not None:
        player_out_count += 1
    if row["player_out_id"] == "UNMAPPED":
        player_out_unmapped += 1
    if row["is_wicket"] and row["player_out_id"] == row["non_striker_id"]:
        out_non_striker += 1
    if row["is_wicket"] and row["player_out_id"] != row["batter_id"]:
        out_not_batter += 1
    sum_batter += row["runs_batter"]
    sum_extras += row["runs_extras"]
    sum_total += row["runs_total"]
    over_numbers.append(row["over_number"])

print("illegal deliveries:", illegal)
print("rows where batter + extras != total:", bad_runs)
print("wickets_count:", wickets_count)
print("bowler_wickets_count:", bowler_wickets_count)
print("batting_team_id unmapped:", batting_team_id_unmapped)
print("smallest_over, largest_over:", min(over_numbers), max(over_numbers))
print("sum_batter, sum_extras, sum_total:", sum_batter, sum_extras, sum_total)
print("sum_batter + sum_extras == sum_total:", sum_batter + sum_extras == sum_total)
print("player_out_count:", player_out_count)
print("player_out_unmapped:", player_out_unmapped)
print("out_not_batter:", out_not_batter)
print("out_non_striker:", out_non_striker)
print("out_not_batter == out_non_striker:", out_not_batter == out_non_striker)

for column in ["batter_id", "bowler_id", "non_striker_id"]:
    bad = 0
    for row in delivery_rows:
        if row[column] == "UNMAPPED":
            bad += 1
    print(column, bad)

print("bad_batting_team:", bad_batting_team)
print("wides_count, noballs_count:", wides_count, noballs_count)
print("wides + noballs == illegal:", wides_count + noballs_count == illegal)