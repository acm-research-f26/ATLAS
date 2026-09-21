#ATLAS

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


