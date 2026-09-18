# ATLAS

#1.IM3 Open Source Data Center Atlas Dataset
The IM3 Open Source Data Center Atlas provides spatial features and structural baselines for existing and projected data centers across the US. 

#Key Attributes and Features Included in the Dataset:
#Spatial Identifiers and Metadata:
  * `id`: Unique facility identification number (OpenStreetMap).
  * `type`: Categorization of spatial representation geometry (`point`, `building`, or `campus`).
  * `ref`: External reference numbers or secondary facility codes.
#Geographic and Administrative Boundaries:
  * `state` & `state_abb`: Full name and two-letter abbreviation of the U.S. state.
  * `state_id`: Numerical identifier for the state.
  * `county` & `county_id`: U.S. county name and ID mapping (handles facilities across multiple boundary lines via duplicated rows).
  * `lat` & `lon`: Latitude and longitude coordinates representing the facility/centroid point.
#Physical & Structural Dimensions:
`facility area`: Calculated square footage footprints (available across building and campus footprint layers).
  #Contextual Infrastructure Overlays:
    -Transmission Lines: Proximity to high-voltage electric grids and substations.
    -Municipal Water Service Areas: Overlays mapping public water supply boundaries.
    -High-Speed Fiber Density:Areas with fiber service provider accessibility.

# 2. Extra Ecological and Environmental Features

#1. Water Risk & Hydrological Stress (WRI Aqueduct Integration)
Baseline Water Stress: Measures the ratio of total water withdrawals to available renewable surface and groundwater supplies.
Drought Severity Risk: Frequency and duration of anticipated drought conditions affecting closed-loop vs. open-loop evaporative cooling towers.
Riverine & Coastal Flood Risk: Evaluating the physical vulnerability of low-lying data center footprints to extreme weather events and climate shifts.

#2. Soil, Land-Cover, and Microclimate Dynamics
Soil Permeability & Sealing Index: Quantifies the percentage of impermeable surface area introduced by sprawling campus concrete/asphalt and its contribution to local urban heat island (UHI) effects and stormwater runoff.
Land-Use Conversion Metrics: Historical classification of land converted for construction (agricultural land vs. forested land).

#3. Energy Demographics & Grid Carbon Intensity
Substation Proximity & Capacity Constraints: Distance to nearest active electrical substations and local grid headroom limits.
Marginal Grid Carbon Intensity: Regional average carbon profile of the energy mix feeding the facility/

