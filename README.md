
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
## Data preprocessing steps
the data was preprocessed in Python using the Pandas, NumPy, and GeoPandas libraries
- Deduplication: Duplicate records sharing unique id values were removed to prevent double-counting facilities crossing county lines
- Column removal and imputation: The ref column was dropped, entries missing square footage ('sqft') were filtered out, and missing operator and name fields were filled with 'Unknown'
- Data type correction: Identifiers were converted to integers, physical measurements to float values, and text columns were cleaned of extra whitespace
- Geographic filtering: Coordinates were bounded between 17.0°–72.0° N latitude and -170.0°–-65.0° W longitude to keep offshore U.S. territories like Puerto Rico in 
- Clean data checkpoint: The processed dataset was saved to 'im3_atlas_cleaned.csv' for mapping

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
  
