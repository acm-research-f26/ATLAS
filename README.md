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


