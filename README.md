
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
 
# ATLAS

Finalized top 4 datasets to use as additional tabular datasets to join with IM3 for feature extraction

Next steps: importing data, geting API key, and joining these data sets with the im3, cleaning and seeing how the data looks like 


The IM3 Open Source Data Center Atlas gives spatial features/structural information for existing and future data centers in the US. 

#Main Attributes/Features


  * id: facility identification number (OpenStreetMap).
  * type: whether it is a point building or campus 
  * ref: external reference numbers or other facility codes.
  * state and state_abb: Full name and two-letter abbreviation of the US state .
  * state_id: Numeric identifier for the state.
  * county and county_id: U.S. county name and ID mapping (facilities across multiple boundary lines).
  * lat and lon: latitude and longitude coordinates for the facility point.
  *facility area: Calculated square footage footprints
    Infrastructure:
    -Transmission Lines: Proximity to high-voltage electric grids and substations.
    -Municipal Water Service Areas: Overlays mapping public water supply boundaries.
    -High-Speed Fiber Density:Areas with fiber service provider accessibility.

#Extra Environmental Features

1. Water Risk
 Water Stress: This looks at how much water is actually being pulled from local supplies compared to what's available (rivers and groundwater).

Drought Severity Risk: mentions how often droughts happen and how long they last, which is important for figuring out how cooling systems will hold up.
Riverine Flood Risk: This is basically checking if a low-lying facility is at risk of getting flooded during bad weather or changing climate.

2. Soil and land climate information:
Soil Permeability Index: Concrete and asphalt block the ground from soaking up water. This measures how much surface area gets sealed up, which increases temperatures (the urban heat island effect) and makes runoff worse.

Land uses: This tracks what the land was used for before construction started (farmland or forested area prior)

3. Energy Demographics
Substation proximity/capacity: This measures how far the facility is from the nearest substation and checks whether the local power grid actually has enough room to handle the load.
### IM3 Open Source Data Center Atlas 
-Contains locations of existing data centers in the US derived from OpenStreetMap.
-Data center data is provided in 3 seperate layers. 
```
Point - includes all data from OSM that has POINT geometry type like coordinates with an exact location. 
Building - data that represents an area or like the shape of a building, usually a bunch of points connected together to outline the building/ area.
Campus - a large area containing many buildings/objects 
```

-Relevant parameters 
```
id - unique identifer 
state - name of state
county - name of US county
operator - name of company, corporation, person in charge of facility
sqft - surface area of facility measured in sqr ft
lat - latititude of data point
lon - longitude of data point
type - represented spatial information ex. point, building, campus
```

### Aqueduct Dataset
-Provide geospatial datasets for evalutating water-related risk by location. 

-Relevant parameters/features
```
water stress - how much available water is already being used . (is there enough water relative to existing demand)
baseline water depletion - how much available water is being consumed. (how much water is being used up)
drought risk - measures when droughts are likely to occur. (Long drought periods could threaten water availability)
groundwater table decline - how quickly groundwater levels are declining. (is groundwater disappearing over time)
riverine flood risk - risk from rivers overflowing. (flooding can threaten nearby buildings, electrical systems, roads, and infrastructure)
```
## EIA Feature Pipeline

`environmental-features/eia_feature_pipeline.ipynb` builds the combined IM3 + EIA dataset.

**Requirements**
- A `.env` file in the repo root containing `EIA_API_KEY=...`
- The raw IM3 data CSV in `Data/`
- The `ATLAS` AWS profile configured (for S3 uploads)

**Run**
Open the notebook and choose Restart → Run All. It can be run from the repo root or from inside `environmental-features/`; paths resolve either way. Outputs are saved to `Data/pipeline/`.

## Training Notes (Hyperparameters are all measured independently)
-Test run folder ending in 851343 testing resnet18

-Test run folder ending in 671400 testing resnet34

-Test run folder ending in 142875 had tensor filenames and metadata Ids had different leading-zero formatting, so
when they were merged they were treated as different IDs and excluded most tensors which left only 68 samples. In result came out
with very poor results in training

-Test run folder ending in 023906 fixed the leading zero formatting issue which allowed 249 tensors across 245 facilities.
the tensor count > facility count because multiple tensor files share the same facility.

-Test run folder ending in 474337 used early stoppage with the patience of 10 where it monitored validation loss and stopped after 21 epoches
because epoch 11 had the lowest validation loss of 1.0159 and an accuracy of roughly 46%.

-Test run folder ending in 586537 used class weighted loss which improved small and large recall while medium recall declined but didn't improve overall accuracy
with 51.4% accuracy.

-Test run folder ending in 930916 runs with class weighted loss but main aspect is that Grad-Cam is implemented and shows a heatmap of why the 
model chose the classification.

