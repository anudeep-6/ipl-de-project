"""Reference (dimension) tables and alias lookups for the IPL project.

These tables are curated by hand, because deciding which raw spellings are the
same venue, team or season is a judgment call, not something code can derive.

Each dimension has two parts:
  dim_*    : id -> the one clean name (or value) we keep
  *_alias  : every raw spelling found in the Cricsheet files -> id

Lookups use alias.get(raw_value.strip(), "UNMAPPED"). A spelling that is not in
an alias table is flagged as "UNMAPPED" for review, never guessed or auto-created.
Reconciliation scripts: read_venues.py, read_teams.py, read_seasons.py, read_matches.py.
"""

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Venues: 36 stadiums, 60 raw spellings
# ---------------------------------------------------------------------------
dim_venue = {
    1: "Eden Gardens",
    2: "Wankhede Stadium",
    3: "Arun Jaitley Stadium",
    4: "M Chinnaswamy Stadium",
    5: "MA Chidambaram Stadium",
    6: "Brabourne Stadium",
    7: "Dr DY Patil Sports Academy",
    8: "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
    9: "Himachal Pradesh Cricket Association Stadium",
    10: "Maharaja Yadavindra Singh International Cricket Stadium",
    11: "Maharashtra Cricket Association Stadium",
    12: "Punjab Cricket Association IS Bindra Stadium",
    13: "Rajiv Gandhi International Stadium",
    14: "Narendra Modi Stadium",
    15: "Sawai Mansingh Stadium",
    16: "Shaheed Veer Narayan Singh International Stadium",
    17: "Sheikh Zayed Stadium",
    18: "Barabati Stadium",
    19: "Barsapara Cricket Stadium",
    20: "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium",
    21: "Buffalo Park",
    22: "De Beers Diamond Oval",
    23: "Dubai International Cricket Stadium",
    24: "Green Park",
    25: "Holkar Cricket Stadium",
    26: "JSCA International Stadium Complex",
    27: "Kingsmead",
    28: "Nehru Stadium",
    29: "New Wanderers Stadium",
    30: "Newlands",
    31: "OUTsurance Oval",
    32: "Saurashtra Cricket Association Stadium",
    33: "Sharjah Cricket Stadium",
    34: "St George's Park",
    35: "SuperSport Park",
    36: "Vidarbha Cricket Association Stadium, Jamtha",
}

# Several spellings differ only by a city suffix or punctuation. The groups below
# that are not obvious were verified online; those are commented.
venue_alias = {
    "Eden Gardens": 1,
    "Eden Gardens, Kolkata": 1,
    "Wankhede Stadium": 2,
    "Wankhede Stadium, Mumbai": 2,
    "Feroz Shah Kotla": 3,                    # same ground as Arun Jaitley Stadium (renamed)
    "Arun Jaitley Stadium": 3,
    "Arun Jaitley Stadium, Delhi": 3,
    "M Chinnaswamy Stadium": 4,
    "M Chinnaswamy Stadium, Bengaluru": 4,
    "M.Chinnaswamy Stadium": 4,               # dot variant; strip() would not fix this
    "MA Chidambaram Stadium": 5,
    "MA Chidambaram Stadium, Chepauk": 5,
    "MA Chidambaram Stadium, Chepauk, Chennai": 5,
    "Brabourne Stadium": 6,
    "Brabourne Stadium, Mumbai": 6,
    "Dr DY Patil Sports Academy": 7,
    "Dr DY Patil Sports Academy, Mumbai": 7,
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": 8,
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam": 8,
    "Himachal Pradesh Cricket Association Stadium": 9,
    "Himachal Pradesh Cricket Association Stadium, Dharamsala": 9,
    # Mullanpur and New Chandigarh are two labels for the same new stadium.
    # It is a separate ground from the Mohali stadium (id 12).
    "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur": 10,
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh": 10,
    "Maharashtra Cricket Association Stadium": 11,
    "Maharashtra Cricket Association Stadium, Pune": 11,
    "Subrata Roy Sahara Stadium": 11,         # earlier name of the same Pune ground
    "Punjab Cricket Association IS Bindra Stadium": 12,
    "Punjab Cricket Association IS Bindra Stadium, Mohali": 12,
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh": 12,
    "Punjab Cricket Association Stadium, Mohali": 12,   # older name of the Mohali ground
    "Rajiv Gandhi International Stadium": 13,
    "Rajiv Gandhi International Stadium, Uppal": 13,
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": 13,
    "Narendra Modi Stadium, Ahmedabad": 14,
    "Sardar Patel Stadium, Motera": 14,       # earlier name of the same ground
    "Sawai Mansingh Stadium": 15,
    "Sawai Mansingh Stadium, Jaipur": 15,
    "Shaheed Veer Narayan Singh International Stadium": 16,
    "Shaheed Veer Narayan Singh International Stadium, Raipur": 16,
    "Sheikh Zayed Stadium": 17,
    "Zayed Cricket Stadium, Abu Dhabi": 17,   # same Abu Dhabi ground under its newer name
    "Barabati Stadium": 18,
    "Barsapara Cricket Stadium, Guwahati": 19,
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": 20,
    "Buffalo Park": 21,
    "De Beers Diamond Oval": 22,
    "Dubai International Cricket Stadium": 23,
    "Green Park": 24,
    "Holkar Cricket Stadium": 25,
    "JSCA International Stadium Complex": 26,
    "Kingsmead": 27,
    "Nehru Stadium": 28,
    "New Wanderers Stadium": 29,
    "Newlands": 30,
    "OUTsurance Oval": 31,
    "Saurashtra Cricket Association Stadium": 32,
    "Sharjah Cricket Stadium": 33,
    "St George's Park": 34,
    "SuperSport Park": 35,
    "Vidarbha Cricket Association Stadium, Jamtha": 36,
}

# ---------------------------------------------------------------------------
# Teams: 15 franchises, 19 raw spellings
# ---------------------------------------------------------------------------
# Renames and spelling variants of one franchise share an id. Different
# franchises stay separate even when they share a city or a name:
#   - Deccan Chargers (terminated) and Sunrisers Hyderabad are different franchises.
#   - Gujarat Lions and Gujarat Titans are different franchises.
#   - Pune Warriors and Rising Pune Supergiant are different franchises.
dim_team = {
    1: "Chennai Super Kings",
    2: "Deccan Chargers",
    3: "Delhi Capitals",
    4: "Gujarat Lions",
    5: "Gujarat Titans",
    6: "Punjab Kings",
    7: "Kochi Tuskers Kerala",
    8: "Kolkata Knight Riders",
    9: "Lucknow Super Giants",
    10: "Mumbai Indians",
    11: "Pune Warriors",
    12: "Rajasthan Royals",
    13: "Rising Pune Supergiant",
    14: "Royal Challengers Bengaluru",
    15: "Sunrisers Hyderabad",
}

team_alias = {
    "Chennai Super Kings": 1,
    "Deccan Chargers": 2,
    "Delhi Capitals": 3,
    "Delhi Daredevils": 3,                    # renamed to Delhi Capitals
    "Gujarat Lions": 4,
    "Gujarat Titans": 5,
    "Kings XI Punjab": 6,                     # renamed to Punjab Kings
    "Punjab Kings": 6,
    "Kochi Tuskers Kerala": 7,
    "Kolkata Knight Riders": 8,
    "Lucknow Super Giants": 9,
    "Mumbai Indians": 10,
    "Pune Warriors": 11,
    "Rajasthan Royals": 12,
    "Rising Pune Supergiant": 13,
    "Rising Pune Supergiants": 13,            # spelling variant of the same team
    "Royal Challengers Bangalore": 14,        # city renamed Bengaluru
    "Royal Challengers Bengaluru": 14,
    "Sunrisers Hyderabad": 15,
}

# ---------------------------------------------------------------------------
# Seasons: 19 seasons (2008-2026), 19 raw labels
# ---------------------------------------------------------------------------
dim_season = {
    1: 2008,  2: 2009,  3: 2010,  4: 2011,  5: 2012,
    6: 2013,  7: 2014,  8: 2015,  9: 2016,  10: 2017,
    11: 2018, 12: 2019, 13: 2020, 14: 2021, 15: 2022,
    16: 2023, 17: 2024, 18: 2025, 19: 2026,
}

# Raw labels are text keys (the files mix 2012 and "2012", so always str() the
# value before lookup). Split-year labels map to the season they belong to:
# "2007/08" -> 2008, "2009/10" -> 2010, "2020/21" -> 2020.
season_alias = {
    "2007/08": 1,
    "2009": 2,
    "2009/10": 3,
    "2011": 4,
    "2012": 5,
    "2013": 6,
    "2014": 7,
    "2015": 8,
    "2016": 9,
    "2017": 10,
    "2018": 11,
    "2019": 12,
    "2020/21": 13,
    "2021": 14,
    "2022": 15,
    "2023": 16,
    "2024": 17,
    "2025": 18,
    "2026": 19,
}

# ---------------------------------------------------------------------------
# Dates: one row per calendar day, generated (not hand-written)
# ---------------------------------------------------------------------------
# Range = first match date to last match date in the raw data. A match's
# date_key (YYYYMMDD) must exist here; read_matches.py checks that.
# For a new season, extend the end date.
day = datetime.strptime("2008-04-18", "%Y-%m-%d")
end = datetime.strptime("2026-05-31", "%Y-%m-%d")

dim_date = []
while day <= end:
    row = {
        "date_key": int(day.strftime("%Y%m%d")),   # smart integer key, e.g. 20170405
        "full_date": day.strftime("%Y-%m-%d"),
        "year": day.year,
        "month": day.month,
        "day": day.day,
        "weekday_name": day.strftime("%A"),
        "is_weekend": day.weekday() >= 5,          # Saturday = 5, Sunday = 6
    }
    dim_date.append(row)
    day = day + timedelta(days=1)