# ATLAS — Environmental Data Integration & Baseline Research

ATLAS is an ACM Research project investigating multimodal approaches to data center classification using facility information, satellite imagery, terrain data, and environmental/infrastructure features.

This repository contains research notebooks and supporting scripts for dataset exploration, preprocessing, feature integration, baseline modeling, and evaluation.

## 1. Repository Structure

| Directory | Contents |
|---|---|
| `usgs/` | USGS 3DEP acquisition, preprocessing, terrain analysis, and S3 publication |
| `wri/` | WRI Aqueduct 4.0 EDA, facility-level feature extraction, dataset merging, validation, and publication |
| `epoch/` | Preliminary Epoch AI dataset exploration |
| `tabular_baseline/` | IM3/EIA baseline experiments, leakage-aware ATLAS/WRI modeling, evaluation, explainability, and publication utilities |

Shared preprocessing code and other team-owned components remain outside these research-specific directories.

**Execution convention:** Run notebooks with the ATLAS repository root as the working directory. Several notebooks use relative paths such as `Data/processed/` and `outputs/`. Moving notebooks into subdirectories does not automatically update those paths.

Data files, trained models, generated outputs, and large raster artifacts are stored locally or in AWS S3 rather than committed to GitHub.

## 2. Data Sources

### IM3 — Open Source Data Center Atlas

IM3 provides the core facility registry, including facility identifiers, geographic locations, estimated building area, and spatial representations.

Facility IDs and coordinates are used to align imagery, terrain, environmental indicators, and infrastructure data.

Important considerations:
- `sqft` is used to derive the current experimental Small/Medium/Large target.
- `type` describes spatial representation (point, building, or campus), not the intended operational data center category.
- `type`, facility identity, coordinates, and other proxy variables require leakage and shortcut-learning checks.
- The current size-classification experiment does not establish Edge/Colocation/Hyperscale classification.

### EIA — Energy and Infrastructure Features

EIA-derived variables provide energy and infrastructure context for the tabular modeling experiments.

These features are evaluated alongside WRI indicators to determine their contribution to classification performance.

### WRI Aqueduct 4.0

WRI Aqueduct provides geographic water-risk indicators describing surrounding environmental conditions, not facility-specific water consumption.

The implemented workflow includes:
- Extraction and integration of 13 facility-level water-risk indicators.
- Validation of feature ranges, missingness, identifiers, and joins.
- Integration with IM3/EIA tabular records.
- Raw and normalized feature representations.
- Validation and publication workflows for generated datasets.

WRI indicators are contextual features. They should not be interpreted as direct measurements of data center water usage or environmental impact.

### USGS 3DEP

USGS 3DEP provides elevation and terrain information through geospatial raster data.

The implemented workflow includes:
- Facility-location-based DEM acquisition and extraction.
- GeoTIFF processing and exploratory analysis.
- Facility-level raster organization and acquisition validation.
- S3 publication of generated terrain artifacts.

USGS terrain data is intended for later integration into the multimodal model.

### Epoch AI

Preliminary dataset exploration is included in `epoch/`. This is exploratory work and is not part of the finalized tabular baseline.

## 3. Tabular Baseline Experiments

### Original IM3/EIA Baseline — v1

Initial experiments evaluated the predictive signal available from IM3 and EIA-derived tabular features.

The selected tuned Random Forest achieved the following results under the original held-out evaluation:

| Metric | Result |
|---|---:|
| Macro-F1 | 0.5676 |
| Balanced accuracy | 0.5622 |
| Accuracy | 68.79% |

These experiments established an initial tabular reference point, but subsequent analysis identified limitations involving geographic generalization and potential leakage.

The v1 artifacts are stored under:

`artifacts/baseline/im3_eia_tabular_v1/`

### Leakage-Aware ATLAS/WRI Baseline — v3

The revised experiment incorporates EIA and WRI features and uses a spatially separated evaluation protocol.

Key design decisions:
- Three-class footprint-derived Small/Medium/Large classification.
- 43 raw tabular inputs: 32 EIA and 11 WRI.
- Exclusion of IM3 `type` as a potentially target-related proxy.
- Spatial group-disjoint development/test split using a 250-meter grouping threshold.
- Spatial and state-grouped cross-validation.
- Random Forest, XGBoost, and CatBoost model comparisons.
- Final class-weighted XGBoost selection and held-out evaluation.

**Final held-out evaluation (161 facilities):**

| Metric | Result |
|---|---:|
| Macro-F1 | 0.4298 |
| Balanced accuracy | 0.5137 |
| Accuracy | 50.93% |

The development set contains 986 facilities.

The lower v3 score should not be interpreted as a direct model regression against v1: the experiments use different evaluation protocols, and the v3 approach is designed to reduce spatial leakage.

**Explainability and feature-family analysis**

SHAP attribution was approximately 76.3% EIA and 23.7% WRI by absolute attribution magnitude. This describes model reliance, not causal influence.

WRI ablation produced mixed results, with no consistent improvement across spatial and state-grouped validation.

**Limitations**

- Geographic transferability remains challenging.
- Minority-class performance is limited.
- The classification labels are derived from facility footprint, not verified operational categories.
- Additional external validation and multimodal experiments are required.

Published artifacts:

`artifacts/baseline/atlas_wri_v3/`

The S3 publication contains 13 artifacts covering the selected model, held-out evaluation, spatial split protocol, cross-validation, SHAP analysis, and WRI ablation.

## 4. Multimodal Integration — Planned Work

The intended multimodal architecture will combine visual and tabular information.

Proposed components:
- NAIP satellite imagery for visual features.
- USGS 3DEP terrain rasters for topographic context.
- EIA and WRI tabular features for infrastructure and environmental context.
- Feature fusion and a classification head for the final prediction.

Potential experiments include a shared image encoder with terrain channels, separate terrain and imagery encoders, and late fusion with tabular features.

These approaches are still under development and are not part of the completed v3 tabular baseline.

## 5. Current Status

| Workstream | Status |
|---|---|
| WRI facility-level feature extraction and validation | Complete |
| WRI integration and publication workflows | Implemented; verify final downstream dataset version |
| USGS 3DEP acquisition and S3 publication | Complete |
| Original IM3/EIA tabular baseline | Complete |
| Leakage-aware ATLAS/WRI v3 baseline | Complete |
| SHAP analysis and WRI ablation | Complete |
| Final v3 artifact publication to S3 | Complete |
| NAIP imagery metadata and geospatial alignment validation | Outstanding |
| USGS/NAIP multimodal input preparation | Outstanding |
| Preliminary CNN/image encoder experiments | Completed; further validation needed |
| Multimodal training entrypoint and fusion experiments | Outstanding |
| Edge/Colocation/Hyperscale label development | Outstanding |


## 6. Research Considerations

The following issues remain important as the project progresses:

**Target leakage and shortcut learning:** Facility footprint, geographic context, spatial representation, and infrastructure proxies may provide predictive shortcuts. Model evaluation should distinguish meaningful generalization from these effects.

**Geographic generalization:** Random splitting may overestimate performance when nearby facilities share environmental and infrastructure characteristics. Spatial and state-grouped evaluation should remain part of future experiments.

**Geospatial alignment:** Satellite imagery and USGS elevation data must be aligned using consistent facility locations, geographic footprints, coordinate reference systems, and raster bounds.

**Temporal alignment:** Imagery, terrain, and tabular datasets may describe different collection periods. Their temporal compatibility should be documented.

**Feature contribution:** Environmental and infrastructure feature families should be assessed using ablation and explainability methods rather than assuming additional inputs always improve performance.

## 7. Next Steps

1. Validate the final facility-aligned multimodal dataset and NAIP metadata.
2. Complete image and terrain preprocessing for model inputs.
3. Implement and test the multimodal training pipeline.
4. Compare imagery-only, tabular-only, and fused models using leakage-aware evaluation.
5. Investigate operational data center classification labels beyond footprint-derived size classes.

---

## 8. Team Pipeline Implementation Notes

### IM3 preprocessing and facility deduplication

The team's `preprocessing.ipynb` is maintained at the repository root.

Starting from `Data/im3_atlas.csv` (1,242 records), the documented workflow produces:

| Output | Description |
|---|---|
| `Data/im3_atlas_cleaned.csv` | 1,147 facilities with six columns for visualization |
| `Data/im3_baseline_5km.csv` | 317 spatially deduplicated records |
| `Data/im3_baseline_10km.csv` | 251 records using an alternative deduplication configuration |
| `Data/im3_baseline.csv` | Selected baseline, currently the 5 km version |

The preprocessing workflow removes duplicate records, filters facilities without usable footprints, validates coordinates, and merges nearby facility records.

For nearby records, campus representations are prioritized, followed by larger footprints. The retained record keeps its own identifier, location, and square footage.

**Facility identifiers:** Read IDs as strings to preserve leading zeros:

`pd.read_csv(file, dtype={"id": str, "state_id": str, "county_id": str})`

IDs from removed or merged facilities may not match previously acquired imagery. Validate identifiers before joining datasets.

The notebook also includes S3 upload steps for the cleaned IM3 datasets. Review the selected baseline configuration before rerunning it.

The 5 km/10 km deduplication configurations are distinct from the 250-meter spatial grouping used for the ATLAS/WRI v3 evaluation.

### EIA feature pipeline

The team's EIA integration notebook is located at `environmental-features/eia_feature_pipeline.ipynb`.

Requirements:
- `EIA_API_KEY` in a repository-root `.env` file.
- Raw IM3 data available under `Data/`.
- Configured AWS `ATLAS` profile for S3 operations.

The notebook generates IM3/EIA features under `Data/pipeline/`. According to the team's documentation, it supports execution from either the repository root or `environmental-features/`.

Do not commit API keys or `.env` files.

### Preliminary vision-model experiments

The team has already conducted preliminary satellite-imagery classification experiments, including:

- ResNet18 and ResNet34 training.
- Correction of leading-zero mismatches between image tensors and facility metadata.
- Early stopping based on validation loss.
- Class-weighted loss experiments.
- Grad-CAM visualization.

The documented identifier correction increased usable imagery to 249 tensors across 245 facilities.

One early-stopping experiment reported approximately 46% validation accuracy, while a separate class-weighted experiment reported 51.4% accuracy. These are historical experiments and are not directly comparable to the leakage-aware v3 tabular results.

Relevant files include:

- `models/train_vision_baseline.py`
- `models/model_training_eval.ipynb`
- `models/local_training_eval.ipynb`
- `models/train_multimodal.ipynb`
- `satellite-imagery/satellite_imagery.ipynb`
- `satellite-imagery/image_to_tensor.ipynb`

Preliminary vision training and Grad-CAM implementation have begun. The integrated multimodal model and its leakage-aware evaluation remain outstanding.
