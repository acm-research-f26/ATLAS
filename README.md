# ATLAS

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

### Build Night 3 Notes
- Code to display the images works fine but display won't work because it breaks at rgb thumbnail creation since I only have read access and not write access in google cloud

## Tabular data -> Satellite Imagery Pipeline
```
IM3 GeoPackage
      │
      │ Select a row
      ▼
CoreSite DC1
      │
      │ geometry.x / geometry.y or lon/lat 
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
Sentinel-2 ImageCollection
      │
      │ filterBounds(region)
      │ filterDate(...)
      │ cloud < 10%
      ▼
Possible satellite images
      │
      │ sort newest → oldest
      ▼
One Sentinel-2 image
      │
      ▼
Spectral bands
      │
      ├──── B2 = Blue
      ├──── B3 = Green
      ├──── B4 = Red
      ├──── B8 = NIR
      └──── B11 = SWIR
             │
             │
       For visual image:
             │
             ▼
         B4 + B3 + B2
        Red  Green Blue
             │
             ▼
         RGB composite
             │
             │ visualization:
             │ min = 0
             │ max = 3000
             ▼
     Earth Engine renders
        RGB thumbnail
             │
             │ getThumbURL()
             ▼
        Image URL
             │
             │ requests.get()
             ▼
        Image bytes
             │
             │ PIL.Image.open()
             ▼
       Python image object
             │
             │ plt.imshow()
             ▼
     Image of Data Center
```






