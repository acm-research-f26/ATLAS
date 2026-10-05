# Dataset Review & Additional Feature Ideas

## 1. IM3 Open Source Data Center Atlas

### Purpose
IM3 provides the core facility and spatial information for known U.S.
data centers. Facility locations can be used to retrieve corresponding satellite imagery and integrate additional environmental/contextual data.

### Relevant Parameters

| Parameter | Meaning | Potential Use |
|------|-----------------------------------|--------------------------------------------------------------------------------------------------|
| `id` | Unique facility/record identifier | Primary key for linking datasets and imagery |
| `name` | Facility name when available | Identification and validation |
| `operator` | Organization associated with the facility | Identification/QC; potentially risky as a model input because of shortcut learning |
| `ref` | Reference to source OSM information | Data provenance |
| `sqft` | Estimated facility/building area | Potential measure of physical scale |
| `lat` | Latitude | Imagery retrieval and spatial joins |
| `lon` | Longitude | Imagery retrieval and spatial joins |
| `state` | Facility state | Geographic analysis |
| `state_abb` | State abbreviation | Standardized geographic identification |
| `state_id` | State identifier | Geographic joins |
| `county` | Facility county | County-level contextual joins |
| `county_id` | County identifier | Standardized Census/FEMA/etc. joins |
| `type` | Spatial representation (`point`, `building`, or `campus`) | Describes representation, NOT Edge/Colocation/Hyperscale class |
| `geometry` | POINT or POLYGON spatial geometry | GIS operations, buffers, imagery extraction, spatial joins |

### Important IM3 Considerations

- `type` does not provide the intended Edge/Colocation/Hyperscale labels.
- Latitude/longitude are necessary for spatial joins but may create geographic
  shortcut learning if directly provided to the classifier.
- `operator` may also create shortcut learning if particular operators are
  strongly associated with one target class.
- Missing/incomplete OSM-derived information should be checked during EDA.


## 2. WRI Aqueduct 4.0

### Purpose
Aqueduct provides water-related environmental context for the geographic
areas surrounding data center facilities. These variables can be spatially
joined to IM3 facility locations.

Aqueduct 4.0 provides water-related environmental indicators that can be associated with each data center location. In the initial classification phase, these indicators can be used as contextual features to evaluate whether water conditions contribute additional information when distinguishing between data center types.

### Relevant Parameter Groups

#### Water Quantity / Availability
Potentially relevant indicators include:
- Baseline water stress
- Water depletion
- Interannual variability
- Seasonal variability
- Drought risk

These characterize the availability, demand pressure, and variability of
water resources surrounding a facility.

#### Water Quality
Potential indicators describe water-quality-related risk in the surrounding
area. These may provide environmental context that is distinct from simple
water availability.

#### Flooding / Water-Related Hazards
Aqueduct includes water-related risk information that can complement other
hazard datasets considered later in the project.

#### Future Water Conditions
Aqueduct 4.0 includes future projections centered around:
- 2030
- 2050
- 2080

Future indicators include projected changes in:
- Water supply
- Water demand
- Water stress
- Water depletion
- Water variability

These could potentially be useful for evaluating how the environmental
context of a facility or proposed location may change over time.

### Important Aqueduct Considerations

Aqueduct indicators describe the water-risk context surrounding a data center.
They should NOT be interpreted as measurements of the data center's actual
water consumption or environmental impact.

For example:

    High local water stress ≠ high data-center water consumption

Aqueduct itself notes that composite measures such as overall water risk
cannot be directly measured/validated and are primarily intended as
prioritization tools. Individual indicators may therefore be preferable to
blindly feeding an overall risk score into a model.


## 3. Additional Ecological / Contextual Data to Explore

### Thermal / Climate
Potential features:
- Mean annual temperature
- Seasonal temperature
- Extreme heat frequency
- Land-surface temperature
- Precipitation
- Temperature trends over time

Potential sources:
- NOAA
- USGS Landsat Surface Temperature

### Population / Urbanization
Potential features:
- Population density
- Population within facility buffers
- 5-year / 10-year population growth
- Urban/rural classification
- Developed land percentage
- Impervious surface percentage
- Change in developed land over time

Potential sources:
- U.S. Census Bureau
- NLCD

### Energy / Infrastructure
Potential features:
- Regional generation capacity
- Generation mix
- Renewable share
- Grid region
- Proximity to relevant energy infrastructure

Potential source:
- U.S. EIA

### Natural Hazards
Potential features:
- Wildfire
- Flooding
- Extreme heat
- Severe storms
- Other location-relevant hazards

Potential source:
- FEMA


## 4. Potential Feature Organization

Rather than treating all contextual variables as one group, they could be
organized into interpretable feature families:

1. Water
2. Climate / Thermal
3. Population / Urbanization
4. Energy / Infrastructure
5. Natural Hazards

This organization could support later feature-family ablation experiments and
XAI analysis to investigate which contextual information contributes to
classification beyond satellite imagery.
