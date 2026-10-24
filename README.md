
# Analysis & data preprocessing of the IM3 Open Source Data Center Atlas
- the IM3 OSM dataset identifies the locations of existing data center facilities across the US, with the intended purpose to help identify areas of concentrated data center devlopment
   - the data comes from a crowd-sourced database called OpenStreetMap(OSM)
## Attributes/Features it includes:
(identification & ownership)
* 'id' : identification number unique for each facility
* 'name' : name of the facility provided by OSM
* 'operator' : the company/corporation/person in charge of the facility
* 'ref' : reference numbers/codes associated w/ the site
(geographic data)
* state information : includes the full state name, two-letter abbreviation ('state_abb'), and numerical state ID (state_id)
* county information : includes the county name ('county') and numerical county ID ('county_id')
(spatial and physical characteristics)
* 'type' : represented spatial information categorized as 'point', 'building', or 'campus'
* 'sqft' : surface area of the facility polygon measured in square feet (available for building and campus types)
* coordinates : latitude ('lat') and longitude ('lon') of the data point

## Data preprocessing and baseline (`preprocessing.ipynb`)
- cleans the raw IM3 Open Source Data Center Atlas (`Data/im3_atlas.csv`, 1,242 rows) and builds the baseline used by the rest of the pipeline
- run with Restart Kernel → Run All; it creates every file below from the raw atlas, then uploads two of them to S3

### Files it creates
* `Data/im3_atlas_cleaned.csv` : 1,147 facilities, 6 columns (`id`, `sqft`, `lat`, `lon`, `type`, `size_class`), used for the plots
* `Data/im3_baseline_5km.csv` : 317 rows, no two rows closer than 5 km
* `Data/im3_baseline_10km.csv` : 251 rows, also merges rows within 0.1° in both lon and lat (closest two rows ~9.5 km apart)
* `Data/im3_baseline.csv` : a copy of the version chosen in `BASELINE_CHOICE` (currently the 5 km file); the file the rest of the team reads
## Data preprocessing steps
the data was preprocessed in Python using the Pandas, NumPy, and GeoPandas libraries
- Deduplication: Duplicate records sharing unique id values were removed to prevent double-counting facilities crossing county lines
- Column removal and imputation: The ref column was dropped, entries missing square footage ('sqft') were filtered out, and missing operator and name fields were filled with 'Unknown'
- Data type correction: Identifiers were converted to integers, physical measurements to float values, and text columns were cleaned of extra whitespace
- Geographic filtering: Coordinates were bounded between 17.0°–72.0° N latitude and -170.0°–-65.0° W longitude to keep offshore U.S. territories like Puerto Rico in 
- Clean data checkpoint: The processed dataset was saved to 'im3_atlas_cleaned.csv' for mapping

### Baseline deduplication
- the baseline is built from the **raw** atlas and keeps the original 13 columns (nothing added): `id`, `state`, `state_abb`, `state_id`, `county`, `county_id`, `operator`, `ref`, `name`, `sqft`, `lon`, `lat`, `type`
- cleaning: leading zeros restored on `id` (10 characters), `state_id` (2) and `county_id` (3); duplicate rows and facilities listed once per county removed; `point` rows (no footprint) dropped; coordinates bounded to the U.S. (17.0°–72.0° N, -170.0°–-65.0° W). This leaves 1,147 facilities
- merging nearby rows: rows are ranked campuses first, then largest `sqft`. Each kept row (a) removes the nearby rows (b), and b's name is appended to a's `name` with " / ". Distance is great-circle (haversine) from lon/lat
- why: the satellite-imagery step (300 m buffer, 3 km minimum distance) should not get repeat images from nearby buildings of the same data center
- to merge less, lower the 5 km distance or set the 0.1° box to `None` in the `VERSIONS` setting

### S3 upload
- the last cell uploads `Data/im3_baseline.csv` and `Data/im3_atlas_cleaned.csv` to `dataset/` in the `atlas-acm-research-f26` bucket
- needs an AWS login first: `aws login --profile ATLAS`

### Things to know
- always read ids as strings: `pd.read_csv(file, dtype={"id": str, "state_id": str, "county_id": str})`, or the leading zeros are lost
- merged rows keep the `id`, location and `sqft` of the kept row only. Removed rows' ids no longer exist, so anything keyed to an old id (like already-downloaded satellite images) will not match
- `operator` is not filled in from merged rows, so a merged `name` can mention a company that `operator` does not
- `name` is the only column that differs from the raw atlas values


## Visualizations made
- Density hexbin map: A hexagonal binning plot was generated to display national data center clusters 
- GeoPandas map overlay: Facility centroids were plotted on top of U.S. geographic boundaries in the WGS84 coordinate reference system 
- State facility rankings:A bar chart was created to rank states by total facility count, led by Virginia, Oregon, Texas, California, and Washington
- Facility size threshold categories: Facilities in the top states were grouped into five size categories based on square footage 
  * micro: under 5,000 sqft
  * small: 5,000- 20,000 sqft
  * medium: 20,000 -100,000 sqft
  * large: 100,000 - 500,000 sqft
  * hyperscale: 500,000+ sqft
 