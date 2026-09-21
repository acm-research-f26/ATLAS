#ATLAS

IM3 Open Source Data Center Atlas Dataset
The IM3 Open Source Data Center Atlas provides spatial features/structural baselines for existing and projected data centers in the US. 

#Main Attributes/Features
Spatial Identifiers and Metadata:
  * `id`: Unique facility identification number (OpenStreetMap).
  * `type`: Categorization of spatial representation geometry (`point`, `building`, or `campus`).
  * `ref`: External reference numbers or secondary facility codes.
Geographic Boundaries:
  * `state` & `state_abb`: Full name and two-letter abbreviation of the U.S. state.
  * `state_id`: Numerical identifier for the state.
  * `county` & `county_id`: U.S. county name and ID mapping (handles facilities across multiple boundary lines via duplicated rows).
  * `lat` & `lon`: Latitude and longitude coordinates representing the facility/centroid point.
Physical/Structural Dimensions:
`facility area`: Calculated square footage footprints (available across building and campus footprint layers).
  Contextual Infrastructure Overlays:
    -Transmission Lines: Proximity to high-voltage electric grids and substations.
    -Municipal Water Service Areas: Overlays mapping public water supply boundaries.
    -High-Speed Fiber Density:Areas with fiber service provider accessibility.

#Extra Ecological and Environmental Features

1. Water Risk
Baseline Water Stress: This looks at how much water is actually being pulled from local supplies compared to what's available (from rivers and groundwater).

Drought Severity Risk: We look at how often droughts happen and how long they last, which is super important for figuring out how cooling systems (like closed-loop vs. open-loop towers) will hold up.
Riverine & Coastal Flood Risk: This is basically checking if a low-lying facility is at risk of getting flooded during bad weather or changing climate patterns..

3. Soil, Land-Cover, and Microclimate Dynamics
Soil Permeability & Sealing Index: Concrete and asphalt block the ground from soaking up water. This measures how much surface area gets "sealed" up, which increases up local temperatures (the urban heat island effect) and makes runoff worse.

Land-Use Conversion Metrics: This tracks what the land was used for before construction started—like whether we're taking over farmland or cutting into forested areas.

3. Energy Demographics & Grid Carbon Intensity
Substation Proximity & Capacity Constraints: This measures how far the facility is from the nearest electrical substation and checks whether the local power grid actually has enough room to handle the load.


