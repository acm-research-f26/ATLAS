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

-Test run folder ending in 949124 has grad-cam classifications of small, medium, and large when correct and incorrect