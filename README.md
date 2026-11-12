![ACM Research Banner Light](https://github.com/ACM-Research/paperImplementations/assets/108421238/467a89e3-72db-41d7-9a25-51d2c589bfd9)

---

# ATLAS: Characterizing Data Center Development using Multimodal Data Fusion

## 📌 Project Summary

ATLAS tests whether public satellite imagery, terrain elevation, and regional
environmental and infrastructure indicators can jointly characterize the scale
of U.S. data centers. The framework combines National Agriculture Imagery
Program (NAIP) imagery, USGS 3D Elevation Program (3DEP) terrain, and tabular
features from IM3, the U.S. Energy Information Administration (EIA), and WRI
Aqueduct. The final experiment classifies **173 facilities** as **Medium** or
**Large** from footprint-derived labels, across five geographic folds.

## 🎯 Motivation

AI training and inference have accelerated data center construction, while
public data on individual facilities remains scarce. Where those facilities
are built, and how their scale relates to nearby infrastructure and
environmental conditions, matters for later research on energy and water
demand. ATLAS asks whether widely available geospatial and contextual data can
profile facilities without inspecting every site by hand.

## 🧩 Novelty

- **Multimodal data integration:** Combines NAIP imagery, USGS 3DEP terrain,
and EIA/WRI infrastructure and environmental indicators.
- **Modality-specific feature extraction:** Encodes imagery with ResNet-18,
terrain with a SmallCNN, and tabular features with an MLP, then fuses those
representations.
- **Modality ablation:** Compares image-only, image-plus-tabular,
image-plus-terrain, and all three modalities.
- **Geographically separated evaluation:** Uses five geographic folds so each
facility is scored on a held-out region, rather than a random split.
- **Explainable predictions:** Applies Grad-CAM to satellite imagery and
Integrated Gradients to tabular and terrain inputs, to check whether
predictions rely on surrounding context and regional indicators.

## 🧠 Methodology

1. **Dataset:** The 2025 IM3 Atlas supplied the registry, coordinates, and

   footprints for **1,147 U.S. data centers**. Spatial deduplication left
      **317** facilities. Aligning USGS terrain with NAIP produced **180** paired
      records. After further filtering and dropping the Small class, the final
      evaluation used **173 Medium and Large facilities**. Imagery, terrain,
      tabular features, and fold assignments are centralized in Amazon S3
      (`atlas-acm-research-f26`).
   - **NAIP:** Satellite imagery of building footprints and surrounding land
     cover.
   - **USGS 3DEP:** Elevation rasters for local terrain.
   - **IM3/EIA/WRI:** Facility attributes, regional energy and infrastructure
     indicators, and Aqueduct water risk. WRI indicators describe regional
     water risk, not measured facility water use.
2. **Architecture:** Three encoders each produce a **64-dimensional**

   representation:
   - **NAIP imagery:** Pretrained ResNet-18.
   - **USGS terrain:** SmallCNN.
   - **Tabular features:** Multilayer perceptron (MLP).

     Trainable projections and normalization keep the three embeddings at 64
     dimensions. They are concatenated into a **192-dimensional vector** and
     passed to a linear classifier with two logits (Medium and Large). The
     pretrained image and terrain backbones stay frozen in the final training
     configuration.
3. **Evaluation:** Models were trained with class-weighted cross-entropy and

   AdamW with weight decay. Image augmentation was applied only to the
      training split, with learning-rate scheduling and early stopping. Each fold
      kept the checkpoint with the lowest validation loss. Five geographic folds
      produced one held-out prediction per facility (**n = 173**). The comparison
      covers four modality combinations under that protocol.
4. **Metrics:** Macro-F1 averages the two class F1 scores. Balanced accuracy

   averages class recall. Accuracy is the share of correct predictions.

| Model | Macro-F1 ↑ | Balanced Accuracy ↑ | Accuracy ↑ |
|---|---:|---:|---:|
| **Image Only (Baseline)** | **0.704** | **0.738** | **0.728** |
| Image + Tabular | 0.688 | 0.726 | 0.711 |
| Image + Terrain | 0.648 | 0.660 | 0.694 |
| Image + Tabular + Terrain | 0.596 | 0.623 | 0.624 |

### Additional Methodology

- **Interpretability:** Grad-CAM and Integrated Gradients were applied to
model predictions. In one illustrated error, image attention fell on
vegetation, access roads, and nearby development. The strongest tabular
attributions were regional balancing-authority indicators. Terrain
attributions were diffuse.
- **Earlier baselines:** Separate three-class tabular and terrain experiments
shaped the pipeline. Their datasets, labels, and evaluation protocols differ
from this two-class study, so those scores should not be compared with the
table above.

## 🌍 Impact

**NAIP imagery alone had the highest Macro-F1 and accuracy** on this
Medium/Large task. Adding tabular features, terrain, or both lowered the
scores, and the three-modality model was weakest. Under this fusion design,
coarse regional indicators and terrain can dilute the local visual signal.
Added modalities need to be tested; more inputs do not automatically help.

ATLAS studies **footprint-derived facility scale**. It is an early
investigation, and it is not a validated method for estimating energy or water
use, finding unknown facilities, or separating operational types such as Edge,
Colocation, and Hyperscale. The small cohort, class imbalance, uncertain
geographic transfer, and remaining image-to-terrain registration error limit
generalization.

### Future Work

- Expand the facility set across more regions and underrepresented size
classes.
- Check historical NAIP footprints and improve pixel-level image-to-DEM
registration.
- Fine-tune the visual encoders and test adaptive fusion, including
cross-attention, so local and regional signals can be combined more
carefully.
- Score models on external geographic holdouts, and develop operational
facility labels that are validated independently.

## 📚 Acknowledgments

### Data Sources

- [IM3 Open Source Data Center Atlas](https://data.msdlive.org/records/65g71-a4731)
(2025). Pacific Northwest National Laboratory.
- [USDA National Agriculture Imagery Program (NAIP)](https://naip-usdaonline.hub.arcgis.com/).
- [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program).
- [U.S. Energy Information Administration (EIA)](https://www.eia.gov/opendata/).
- [World Resources Institute (WRI), Aqueduct 4.0](https://www.wri.org/research/aqueduct-40-updated-decision-relevant-global-water-risk-indicators).

### Selected Papers

- Zhou, Y., Tan, Y., Wen, Q., Wang, W., Li, L., & Li, Z. (2023). *Deep
Multimodal Fusion Model for Building Structural Type Recognition Using
Multisource Remote Sensing Images and Building-Related Knowledge*. IEEE
Journal of Selected Topics in Applied Earth Observations and Remote Sensing,
16, 9646–9660.
[doi.org/10.1109/JSTARS.2023.3323484](https://doi.org/10.1109/JSTARS.2023.3323484)
- Suel, E., Bhatt, S., Brauer, M., Flaxman, S., & Ezzati, M. (2021).  
*Multimodal deep learning from satellite and street-level imagery for*  
*measuring income, overcrowding, and environmental deprivation in urban*  
*areas*. Remote Sensing of Environment, 257, 112339.  
[doi.org/10.1016/j.rse.2021.112339](https://doi.org/10.1016/j.rse.2021.112339)

## 👥 Team

**Undergraduate Researchers:**

- Abhinav Atthota 
- Swati Thirulogachander
- Kevin Lam
- Sajna Bhandari

**Research Lead:** Advay Chandramouli

**Faculty Advisor:** Dr. Weili Wu
