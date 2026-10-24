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

## Tabular data -> Satellite Imagery Pipeline
```
IM3 GeoPackage
      │
      │ Select a row
      ▼
Geopandas
      │
      │ 
      ▼
ee.Geometry.Point([lon, lat])
      │
      │ buffer(1000)
      ▼
1 km area around data center
      │
      │
      ▼
Google Earth Engine
      │
      │ Search:
      │ COPERNICUS/S2_SR_HARMONIZED
      ▼
NAIP image collection
      │
      │ filterBounds(region)
      │ filterDate(...)
      ▼
Possible satellite images
      │
      │ sort newest → oldest
      ▼
Recent image
      │
      ▼
VLM filter 
      |
      |
      ▼
Accept/Reject
      |
      |
      ▼
Import into Temp Folder






