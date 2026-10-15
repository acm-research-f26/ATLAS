import pandas as pd

annual = pd.read_csv(
    "C:\\Users\\attho\\OneDrive\\Desktop\\College\\ACM ATLAS\\aqueduct-4-0-water-risk-data\\Aqueduct40_waterrisk_download_Y2023M07D05\\CVS\\Aqueduct40_baseline_annual_y2023m07d05.csv",
    low_memory=False
)

monthly = pd.read_csv(
    "C:\\Users\\attho\\OneDrive\\Desktop\\College\\ACM ATLAS\\aqueduct-4-0-water-risk-data\\Aqueduct40_waterrisk_download_Y2023M07D05\\CVS\\Aqueduct40_baseline_monthly_y2023m07d05.csv",
    low_memory=False
)

future = pd.read_csv(
    "C:\\Users\\attho\\OneDrive\\Desktop\\College\\ACM ATLAS\\aqueduct-4-0-water-risk-data\\Aqueduct40_waterrisk_download_Y2023M07D05\\CVS\\Aqueduct40_future_annual_y2023m07d05.csv",
    low_memory=False
)

print("ANNUAL:", annual.shape)
print("MONTHLY:", monthly.shape)
print("FUTURE:", future.shape)

print("\nANNUAL COLUMNS:")
for col in annual.columns:
    print(col)

# Core annual Aqueduct indicators
core_indicators = [
    "bws",  # baseline water stress
    "bwd",  # baseline water depletion
    "iav",  # interannual variability
    "sev",  # seasonal variability
    "gtd",  # groundwater table decline
    "rfr",  # riverine flood risk
    "cfr",  # coastal flood risk
    "drr",  # drought risk
    "ucw",
    "cep",
    "udw",
    "usa",
    "rri",
]

core_raw = [f"{x}_raw" for x in core_indicators]
core_score = [f"{x}_score" for x in core_indicators]

print("\nCORE INDICATOR SUMMARY")
print(
    annual[core_raw].describe().T[
        ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    ]
)

#looks for missing and suspicious values
print("\nCORE INDICATOR MISSINGNESS")

missing = (
    annual[core_raw]
    .isna()
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print(missing)


print("\nVALUES >= 9999")

for col in core_raw:
    count = (annual[col] >= 9999).sum()
    print(f"{col}: {count}")

#sanity check 
print("\nUNIQUE SCORES / CATEGORIES")

for indicator in core_indicators:
    print(f"\n--- {indicator.upper()} ---")
    print(
        annual[
            [
                f"{indicator}_score",
                f"{indicator}_cat",
                f"{indicator}_label",
            ]
        ]
        .drop_duplicates()
        .sort_values(f"{indicator}_score")
        .head(20)
    )

#qualifies sentinal values
print("\nSENTINEL VALUE COUNTS")

for col in core_raw:
    neg9999 = (annual[col] == -9999).sum()
    pos9999 = (annual[col] == 9999).sum()

    print(
        f"{col:10s} "
        f"-9999: {neg9999:6d} "
        f"9999: {pos9999:6d}"
    )

#compares them with labels 
print("\nSENTINEL LABEL CHECK")

for indicator in core_indicators:

    raw_col = f"{indicator}_raw"
    label_col = f"{indicator}_label"

    sentinel_rows = annual[
        annual[raw_col].isin([-9999, 9999])
    ][[raw_col, label_col]]

    if len(sentinel_rows) > 0:
        print(f"\n--- {indicator.upper()} ---")
        print(sentinel_rows.value_counts())

#makes a US subset
us_annual = annual[
    annual["name_0"] == "United States"
].copy()

print("\nUS SUBSET")
print("Rows:", len(us_annual))
print("States/regions:", us_annual["name_1"].nunique())
print(us_annual["name_1"].value_counts().head(10))

#missingness within the US
print("\nUS CORE INDICATOR VALIDITY")

for indicator in core_indicators:
    raw_col = f"{indicator}_raw"
    label_col = f"{indicator}_label"

    total = len(us_annual)

    no_data = (
        us_annual[label_col] == "No Data"
    ).sum()

    print(
        f"{indicator:5s} "
        f"No Data: {no_data:4d} "
        f"({no_data / total * 100:5.1f}%)"
    )

#looks at electric power aggregate
elp_cols = [
    "w_awr_elp_qan_raw",
    "w_awr_elp_qan_score",
    "w_awr_elp_qan_label",

    "w_awr_elp_qal_raw",
    "w_awr_elp_qal_score",
    "w_awr_elp_qal_label",

    "w_awr_elp_rrr_raw",
    "w_awr_elp_rrr_score",
    "w_awr_elp_rrr_label",

    "w_awr_elp_tot_raw",
    "w_awr_elp_tot_score",
    "w_awr_elp_tot_label",

    "w_awr_elp_tot_weight_fraction"
]

print("\nELECTRIC POWER WATER RISK")
print(us_annual[elp_cols].head())

print("\nELP MISSING / SPECIAL VALUES")
for col in elp_cols:
    if col.endswith("_raw") or col.endswith("_score"):
        print(
            col,
            " -9999:",
            (us_annual[col] == -9999).sum()
        )

#Electric power composite metrics
elp_types = ["qan", "qal", "rrr", "tot"]

print("\nELP COMPOSITE METRICS")

for metric in elp_types:
    print(f"\n--- {metric.upper()} ---")

    cols = [
        f"w_awr_elp_{metric}_raw",
        f"w_awr_elp_{metric}_score",
        f"w_awr_elp_{metric}_cat",
        f"w_awr_elp_{metric}_label",
    ]

    print(us_annual[cols].head(10))

#quaitfies catagories 
print("\nELP CATEGORY DISTRIBUTIONS")

for metric in elp_types:

    label_col = f"w_awr_elp_{metric}_label"

    print(f"\n--- {metric.upper()} ---")

    counts = us_annual[label_col].value_counts(
        dropna=False
    )

    print(counts)

print("\nELP WEIGHT FRACTION")

print(
    us_annual["w_awr_elp_tot_weight_fraction"]
    .describe()
)

#compares elp composites to default composites 
groups = ["qan", "qal", "rrr", "tot"]

print("\nDEFAULT vs ELECTRIC POWER")

for group in groups:

    default_col = f"w_awr_def_{group}_raw"
    elp_col = f"w_awr_elp_{group}_raw"

    valid = us_annual[
        (us_annual[default_col] != -9999) &
        (us_annual[elp_col] != -9999)
    ]

    diff = valid[elp_col] - valid[default_col]

    print(f"\n--- {group.upper()} ---")
    print("N:", len(valid))
    print("Mean default:", valid[default_col].mean())
    print("Mean ELP:", valid[elp_col].mean())
    print("Mean difference:", diff.mean())
    print("Median difference:", diff.median())
    print("Mean absolute difference:", diff.abs().mean())
    print("Correlation:", valid[[default_col, elp_col]].corr().iloc[0, 1])