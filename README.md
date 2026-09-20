
# IM3 Open Source Data Center Atlas
- a dataset that identifies the locations of existing data center facilities across the US, with the intended purpose to help identify areas of concentrated data center devlopment

- the data comes from a crowd-sourced database called OpenStreetMap(OSM)
# Attributes/Features it includes:
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
# Ecological features that would be important to consider:
* local resource burden : finding areas where many data centers are crowded together and putting stress on local power and water
    - cleaning script : a step to fix overlapping data so we dont count the same building twice
    - usage math : a way to turn square feet into a guess for how many megawatts and gallons are needed.
    - county totals : adding up all data centers in one county to see the total stress on that area

* predicted water needs : using the location to check local weather (like heat and humidity) to guess how much water each site needs for cooling
    - cooling types : labeling sites as "water-heavy" (high-water demand) or "power-heavy" (high-grid demand)
    - weather match : connecting the site coordinates to local heat and humidity data
    - company check : using the owner name to find their green reports for better efficiency data

