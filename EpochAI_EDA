import pandas as pd
from pathlib import Path

DATA_DIR = Path("C:\\Users\\attho\\OneDrive\\Desktop\\College\\ACM ATLAS\\data_centers")   # change to your actual path

centers = pd.read_csv(DATA_DIR / "data_centers.csv")
timelines = pd.read_csv(DATA_DIR / "data_center_timelines.csv")
chips = pd.read_csv(DATA_DIR / "data_center_chip_quantities.csv")
chillers = pd.read_csv(DATA_DIR / "data_center_chillers.csv")
cooling = pd.read_csv(DATA_DIR / "data_center_cooling_towers.csv")
chip_types = pd.read_csv(DATA_DIR / "chip_types.csv")

#inspects the csvs
datasets = {
    "centers": centers,
    "timelines": timelines,
    "chips": chips,
    "chillers": chillers,
    "cooling": cooling,
    "chip_types": chip_types
}

for name, df in datasets.items():
    print(f"\n{name.upper()}")
    print("Shape:", df.shape)
    print("Columns:")
    print(df.columns.tolist())

# missing value check
def missing_summary(df):
    missing = df.isna().sum()
    percent = (missing / len(df) * 100).round(2)

    return (
        pd.DataFrame({
            "missing_count": missing,
            "missing_percent": percent
        })
        .query("missing_count > 0")
        .sort_values("missing_percent", ascending=False)
    )

for name, df in datasets.items():
    print(f"\n--- {name.upper()} ---")
    print(missing_summary(df))

#relationship between tables 
for name, df in datasets.items():
    print(f"\n--- {name.upper()} ---")
    print(df.head())

for name, df in datasets.items():
    id_cols = [
        col for col in df.columns
        if "id" in col.lower() or "name" in col.lower()
    ]

    print(name, ":", id_cols)

#join verification
center_names = set(centers["Name"].dropna())
timeline_names = set(timelines["Data center"].dropna())
chip_center_names = set(chips["Data center"].dropna())

print("Centers:", len(center_names))
print("Timeline centers:", len(timeline_names))
print("Chip centers:", len(chip_center_names))

print("\nTimeline centers missing from centers:")
print(timeline_names - center_names)

print("\nChip centers missing from centers:")
print(chip_center_names - center_names)

print("\nCenters without timeline records:")
print(center_names - timeline_names)

print("\nCenters without chip records:")
print(center_names - chip_center_names)

#chip type matching 
used_chips = set(chips["Chip type"].dropna())
known_chips = set(chip_types["Name"].dropna())

print("Chip types used:", len(used_chips))
print("Chip types in lookup:", len(known_chips))

print("\nUsed chip types missing from chip_types.csv:")
print(used_chips - known_chips)

#duplicate and cardinality check
print("Unique centers:", centers["Name"].nunique())
print("Center rows:", len(centers))

print("\nTimeline records per center:")
print(timelines["Data center"].value_counts().describe())

print("\nChip records per center:")
print(chips["Data center"].value_counts().describe())

print("\nChip types unique:", chip_types["Name"].nunique())
print("Chip type rows:", len(chip_types))

print("Duplicate center names:",
      centers["Name"].duplicated().sum())

print("Duplicate chip-type names:",
      chip_types["Name"].duplicated().sum())

print("Exact duplicate timeline rows:",
      timelines.duplicated().sum())

print("Exact duplicate chip rows:",
      chips.duplicated().sum())

#specific check on water use
timelines["water_use_missing"] = timelines["Water use (MGD)"].isna()

pd.crosstab(
    timelines["Construction status"],
    timelines["water_use_missing"],
    normalize="index"
)

#chip table combine
chips_enriched = chips.merge(
    chip_types,
    left_on="Chip type",
    right_on="Name",
    how="left",
    validate="many_to_one",
    suffixes=("", "_chip")
)

print("Before:", chips.shape)
print("After:", chips_enriched.shape)

assert len(chips_enriched) == len(chips)

print(
    chips_enriched[
        ["Data center", "Date", "Chip type",
         "Number of Units", "H100e", "Release date"]
    ].head()
)

#temporal eda
timelines["Date"] = pd.to_datetime(
    timelines["Date"],
    errors="coerce"
)

chips_enriched["Date"] = pd.to_datetime(
    chips_enriched["Date"],
    errors="coerce"
)

chips_enriched["Timeline"] = pd.to_datetime(
    chips_enriched["Timeline"],
    errors="coerce"
)

chips_enriched["Release date"] = pd.to_datetime(
    chips_enriched["Release date"],
    errors="coerce"
)

print("Bad timeline dates:",
      timelines["Date"].isna().sum())

print("Bad chip dates:",
      chips_enriched["Date"].isna().sum())

print("Bad chip timeline dates:",
      chips_enriched["Timeline"].isna().sum())

timelines["Year"] = timelines["Date"].dt.year
chips_enriched["Year"] = chips_enriched["Date"].dt.year

print("\nTimeline year distribution:")
print(
    timelines["Year"]
    .value_counts()
    .sort_index()
)

print("\nChip year distribution:")
print(
    chips_enriched["Year"]
    .value_counts()
    .sort_index()
)

#unique facilities per year
facilities_per_year = (
    timelines
    .groupby("Year")["Data center"]
    .nunique()
)

print(facilities_per_year)

#per facility temporal coverage 
temporal_coverage = (
    timelines
    .groupby("Data center")["Date"]
    .agg(
        first_observation="min",
        last_observation="max",
        n_observations="count"
    )
    .reset_index()
)

temporal_coverage["span_years"] = (
    temporal_coverage["last_observation"]
    - temporal_coverage["first_observation"]
).dt.days / 365.25

print(temporal_coverage)

#construction status
print(
    timelines["Construction status"]
    .value_counts(dropna=False)
)

status_by_year = pd.crosstab(
    timelines["Year"],
    timelines["Construction status"]
)

print(status_by_year)

#leakage check 
timeline_sorted = timelines.sort_values(
    ["Data center", "Date"]
)

timeline_sorted[
    ["Data center", "Date",
     "Construction status",
     "Buildings operational",
     "Power (MW)",
     "H100 equivalents"]
].head(30)

LEAKAGE_SUSPECTS = [
    "Current H100 equivalents (from Data center)"
]

#temporal audit
cutoff = pd.Timestamp("2026-10-05")

timelines["is_future"] = timelines["Date"] > cutoff

print(timelines["is_future"].value_counts())

print(
    timelines.loc[
        timelines["is_future"],
        ["Data center", "Date", "Construction status"]
    ]
    .sort_values("Date")
    .head(20)
)

timelines["Year"] = timelines["Date"].dt.year
timelines["is_2023_or_earlier"] = timelines["Date"] <= "2023-12-31"

#audit flag
chips_enriched["temporal_inconsistency"] = (
    chips_enriched["Date"] < chips_enriched["Release date"]
)

#checking to see what datacenters are compatible with 2023
coverage_2023 = (
    timelines
    .groupby("Data center")
    .agg(
        first_date=("Date", "min"),
        last_date=("Date", "max"),
        has_2023_or_earlier=("is_2023_or_earlier", "max")
    )
    .reset_index()
)

print(
    coverage_2023["has_2023_or_earlier"]
    .value_counts()
)

#latest 2023 record
historical_2023 = (
    timelines[
        timelines["Date"] <= pd.Timestamp("2023-12-31")
    ]
    .sort_values("Date")
    .groupby("Data center")
    .tail(1)
)

print("Facilities with a record by end of 2023:")
print(historical_2023["Data center"].nunique())

print(
    historical_2023[
        [
            "Data center",
            "Date",
            "Construction status",
            "Buildings operational",
            "IT power (MW)",
            "Power (MW)"
        ]
    ].sort_values("Date")
)

#checks when facilities first appear
first_records = (
    timelines
    .sort_values("Date")
    .groupby("Data center")
    .first()
    .reset_index()
)

first_records["first_year"] = first_records["Date"].dt.year

print(
    first_records["first_year"]
    .value_counts()
    .sort_index()
)

print(
    first_records[
        ["Data center", "Date", "Construction status"]
    ]
    .sort_values("Date")
    .to_string(index=False)
)

#chip sanity check
chips_enriched["predates_release"] = (
    chips_enriched["Date"] <
    chips_enriched["Release date"]
)

print(
    chips_enriched["predates_release"]
    .value_counts(dropna=False)
)

print(
    chips_enriched.loc[
        chips_enriched["predates_release"] == True,
        [
            "Data center",
            "Chip type",
            "Date",
            "Release date",
            "Number of Units"
        ]
    ].sort_values("Date")
)


#Spatial relavance check
print(centers["Country"].value_counts(dropna=False))

us_centers = centers[
    centers["Country"].eq("United States")
].copy()

print("All Epoch centers:", len(centers))
print("US centers:", len(us_centers))

#attach to timeline
timeline_geo = timelines.merge(
    centers[["Name", "Country"]],
    left_on="Data center",
    right_on="Name",
    how="left",
    validate="many_to_one"
)

assert len(timeline_geo) == len(timelines)

#relavant temporal coverage
us_timeline = timeline_geo.loc[
    timeline_geo["Country"] == "United States"
].copy()

us_timeline["is_operational"] = (
    us_timeline["Buildings operational"] > 0
)

print(
    us_timeline.groupby("Year")["Data center"]
    .nunique()
)

#"operational" status tag diagnostic
us_timeline["is_operational"] = (
    us_timeline["Buildings operational"] > 0
)

operational_by_year = (
    us_timeline
    .groupby("Year")
    .agg(
        facilities=("Data center", "nunique"),
        operational_records=("is_operational", "sum")
    )
)

print(operational_by_year)

operational_facilities = (
    us_timeline[
        us_timeline["is_operational"]
    ]
    .groupby("Year")["Data center"]
    .nunique()
)

print(operational_facilities)