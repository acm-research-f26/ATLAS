# ATLAS — Environmental Data Integration & Baseline Research

ATLAS is an ACM Research project investigating multimodal approaches to data center classification using facility information, satellite imagery, terrain data, and environmental/infrastructure features.

This repository contains research notebooks and supporting scripts for dataset exploration, preprocessing, feature integration, baseline modeling, and evaluation.

## 1. Repository Structure

| Directory | Contents |
|---|---|
| `environmental-features/usgs/` | USGS 3DEP acquisition, preprocessing, terrain-feature extraction, and S3 publication |
| `environmental-features/wri/` | WRI Aqueduct 4.0 facility-level 13-score extraction, dataset merging, validation, and publication |
| `environmental-features/epoch/` | Preliminary Epoch AI dataset exploration |
| `models/tabular_baseline/` | IM3/EIA baseline experiments, leakage-aware ATLAS/WRI modeling, evaluation, explainability, and publication utilities |

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

**Completed acquisition and alignment workflows:**
- Historical facility-location-based DEM acquisition, GeoTIFF processing, and S3 publication.
- A unified USGS–NAIP alignment v2 pipeline covering 180 facilities with available NAIP imagery and reconstructed footprint metadata.
- Standardized single-band, float32 DEMs in EPSG:4326 at 1/3 arc-second resolution (1/10800 degree), using a globally anchored target grid.
- Facility-level provenance JSON files recording source selection, USGS source URLs, processing configuration, raster geometry, and NAIP metadata references.
- Completed local validation of 180 DEMs and 180 provenance files, including raster-grid consistency, source lineage, and facility identifier checks.
- S3 publication and remote verification of all 360 DEM/provenance objects and the associated manifest.

**Final v2 S3 locations:**

| Artifact | S3 prefix or key |
|---|---|
| Aligned DEMs (180) | `usgs/naip_aligned_v2/dem/` |
| Provenance JSONs (180) | `usgs/naip_aligned_v2/provenance/` |
| Alignment manifest | `usgs/processed/usgs_naip_alignment_manifest_v2.parquet` |

All paths above are relative to `s3://atlas-acm-research-f26/`.

**Reproducible notebook:** `environmental-features/usgs/usgs_naip_alignment.ipynb`

The superseded v1 aligned S3 collection was backed up locally and removed from S3. The historical `usgs/raw/` collection and its provenance remain preserved.

**Geospatial limitation:** The NAIP footprints used for alignment were reconstructed from available metadata rather than independently verified against the original historical Google Earth Engine exports. The v2 DEMs follow a consistent geographic grid, but pixel-perfect alignment with the original NAIP PNGs is not established. Historical footprint verification and image-to-DEM registration remain outstanding.

The aligned terrain dataset is ready for downstream preprocessing and multimodal experimentation; integration into a trained multimodal model is not yet complete.

### Epoch AI

Preliminary dataset exploration is included in `environmental-features/epoch/`. This is exploratory work and is not part of the finalized tabular baseline.

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

## USGS Terrain Classification Baselines — Spatial Evaluation

Three terrain-related experiments were completed using the 180-facility USGS–NAIP aligned v2 cohort:

- **Terrain CNN:** A compact, single-channel CNN using standardized USGS 3DEP elevation rasters, with a reusable 64-dimensional terrain embedding.
- **Handcrafted terrain baseline:** Ten interpretable terrain features evaluated using Logistic Regression and Random Forest.
- **Geographic shortcut control:** Latitude/longitude-only Logistic Regression and Random Forest models to assess the predictive contribution of geographic location.

All experiments used the same five geographic-block-disjoint outer folds, based on 2-degree latitude/longitude groups, with out-of-fold predictions for all 180 facilities.

The target was footprint-derived facility size: Small (under 20,000 sqft), Medium (20,000–99,999 sqft), and Large (at least 100,000 sqft). The cohort contained 7 Small, 50 Medium, and 123 Large facilities.

### Pooled out-of-fold results

| Model | Accuracy | Balanced accuracy | Macro-F1 |
|---|---:|---:|---:|
| Handcrafted Random Forest | 0.4000 | 0.3522 | **0.3060** |
| Geographic Logistic Regression | 0.3722 | 0.2765 | 0.2960 |
| USGS Terrain CNN | 0.6333 | 0.3208 | 0.2881 |
| Majority-class baseline | 0.6833 | 0.3333 | 0.2706 |
| Geographic Random Forest | 0.3444 | 0.2590 | 0.2674 |
| Handcrafted Logistic Regression | 0.3222 | 0.3222 | 0.2646 |

The handcrafted Random Forest achieved the highest macro-F1 and balanced accuracy, although absolute performance remained limited. The terrain CNN predicted the majority Large class frequently and did not correctly identify any Small facilities.

The geographic controls indicate that location alone contains some predictive signal, but these experiments do not establish that the terrain CNN learned geographic shortcuts.

### Limitations and interpretation

- The evaluation cohort is small and imbalanced, with only seven Small facilities.
- Results are pooled out-of-fold estimates from five spatial folds, not performance on an independent untouched test cohort.
- The 2-degree geographic blocks prevent groups from crossing folds but do not enforce a geographic separation buffer.
- NAIP footprint reconstruction and exact image-to-DEM registration remain unverified.
- Terrain-only size classification is not equivalent to detecting previously unknown data centers.

These results do not establish a strong standalone terrain classifier. The CNN's 64-dimensional embedding remains available for testing whether terrain adds incremental predictive value in multimodal fusion.

### Reproducibility and publication

Experiment notebooks:

- `models/USGS_CNN_complete.ipynb`
- `models/USGS_Terrain_Baseline.ipynb`
- `models/USGS_Geographic_Control.ipynb`

All 18 experiment artifacts, including five CNN checkpoints, predictions, evaluation metrics, metadata, and handcrafted features, were published to:

`s3://atlas-acm-research-f26/artifacts/usgs_terrain_baselines/v1/`

A separate publication manifest records artifact sizes and SHA-256 checksums. All 18 uploaded artifacts and the manifest were verified by downloading and hashing their S3 contents.

The completed CNN experiment used a maximum of 30 epochs with early stopping. Its published `cnn/experiment_config.json` records the completed experiment configuration.

The geographic-fold manifest must also be available to reproduce the exact evaluation partitions; its separate publication remains outstanding.

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
| Original IM3/EIA tabular baseline | Complete |
| Leakage-aware ATLAS/WRI v3 baseline | Complete |
| SHAP analysis and WRI ablation | Complete |
| USGS 3DEP acquisition and historical S3 publication | Complete |
| USGS terrain-only model input preparation | Complete for 180 aligned DEMs; NAIP image-to-DEM registration remains unverified || USGS terrain CNN, handcrafted baseline, and geographic controls | Complete; five-fold spatial evaluation and S3 publication verified |
| Historical NAIP export footprint verification | Outstanding; reconstructed metadata used |
| USGS/NAIP model input preparation and registration | Outstanding |
| Final v3 artifact publication to S3 | Complete |
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

1. Verify historical NAIP export footprints where possible and validate image-to-DEM registration.
2. Prepare aligned NAIP imagery and USGS terrain tensors for CNN training, including consistent facility IDs and spatial coverage.
3. Implement and test the multimodal training pipeline using imagery, terrain, and EIA/WRI tabular features.
4. Compare imagery-only, terrain-only, tabular-only, and fused models using spatially separated evaluation and feature-family ablation.
5. Investigate operational data center classification labels (Edge, Colocation, Hyperscale) beyond footprint-derived size classes.

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
