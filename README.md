![ACM Research Banner Light](https://github.com/ACM-Research/paperImplementations/assets/108421238/467a89e3-72db-41d7-9a25-51d2c589bfd9)

---
# ATLAS - Characterizing Data Center Development using Multimodal Data Fusion

## 📌 Project Summary
ATLAS investigates whether publicly available satellite imagery, terrain elevation, regional environmental and infrastructure indicators can jointly characterize the scale of U.S. data centers. We developed and evaluated a multimodal classification framework that combines National Agriculture Imagery Program (NAIP) imagery, USGS 3D Elevation Program (3DEP) terrain data, tabular features derived from IM3, the U.S. Energy Information Administration (EIA), and WRI Aqueduct. The final experiment classifies facilities as **Medium** or **Large**, based on footprint-derived size labels, using **173 facilities** evaluated across five geographic folds.

## 🎯 Motivation
Growing demand for AI training and inference has accelerated data center development, while public facility-level operational data remains limited. Understanding where facilities are built and how their scale relates to surrounding infrastructure and environmental conditions is important for future research on energy and water demand. ATLAS explores whether widely available geospatial and contextual data can provide a scalable starting point for facility profiling without requiring manual inspection of every site.

## 🧩 Novelty
- **Multimodal Data Integration:** Combines high-resolution NAIP satellite imagery, USGS 3DEP terrain data, and EIA/WRI infrastructure and environmental indicators to characterize data center facilities using complementary visual and non-visual information.
- **Modality-Specific Feature Extraction:** Employs separate neural network encoders for satellite imagery (ResNet-18), terrain (SmallCNN), and tabular features (MLP), integrating their learned representations through feature-level fusion.
- **Modality ablation:** Evaluates image-only, image-plus-tabular, image-plus-terrain, and three-modality configurations to measure whether added information improves prediction.
- **Geographically separated evaluation:** Uses five geographic folds to assess performance on held-out facilities rather than relying solely on random splits.
- **Explainable predictions:** Uses Grad-CAM to visualize influential satellite image regions and Integrated Gradients for tabular and terrain attribution, helping identify potential reliance on surrounding scene context and regional indicators.

## 🧠 Methodology
1. **Dataset:** The 2025 IM3 Atlas dataset supplied the facility registry, geographic coordinates, and footprint information for **1,147 U.S. data centers** in the initial cohort. Records were spatially deduplicated to **317** facilities. The USGS–NAIP alignment workflow produced **180** paired terrain records; after filtering and exclusion of the Small class, **173 Medium and Large facilities** were used in the final multimodal evaluation. Data modalities included:
   - **NAIP:** Satellite imagery capturing building footprints and surrounding land cover.
   - **USGS 3DEP:** Elevation rasters providing local terrain context.
   - **IM3/EIA/WRI:** Facility, regional energy/infrastructure, and Aqueduct water-risk information. WRI indicators describe regional water risk, not measured facility water consumption.

2. **Architecture:** Three modality-specific encoders produce **64-dimensional representations**:
   - **NAIP imagery:** Pretrained ResNet-18.
   - **USGS terrain:** SmallCNN.
   - **Tabular features:** Multilayer perceptron (MLP).
   - **Fusion:** Trainable modality projections and normalization yield three 64-dimensional embeddings, concatenated into a **192-dimensional vector** and passed to a linear classifier with two output logits (Medium and Large). The pretrained image and terrain backbones remain frozen during the final training configuration.

3. **Evaluation:** Models were trained using class-weighted cross-entropy, AdamW with weight decay, training-only image augmentation, learning-rate scheduling, and early stopping. The best checkpoint within each fold was selected by validation loss. Five geographic folds yielded one held-out prediction per facility (**n = 173**). The final comparison tests four modality combinations under this evaluation protocol.

4. **Metrics:** Macro-F1 averages the two classes' F1 scores, balanced accuracy averages class recall, and accuracy measures the proportion of correct predictions.

   | Model | Macro-F1 ↑ | Balanced Accuracy ↑ | Accuracy ↑ |
   |---|---:|---:|---:|
   | **Image Only (Baseline)** | **0.704** | **0.738** | **0.728** |
   | Image + Tabular | 0.688 | 0.726 | 0.711 |
   | Image + Terrain | 0.648 | 0.660 | 0.694 |
   | Image + Tabular + Terrain | 0.596 | 0.623 | 0.624 |

#### Additional Methodology:
- **Interpretability:** Grad-CAM and Integrated Gradients were examined on model predictions. In an illustrated incorrect prediction, image attention included vegetation, access roads, and nearby development, while strong tabular attributions involved regional balancing-authority indicators; terrain attributions were comparatively diffuse.
- **Earlier baselines:** Separate three-class tabular and terrain experiments informed the research pipeline, but their datasets, labels, and evaluation protocols differ from the final two-class multimodal study. Their scores should not be compared directly with the table above.

## 🌍 Impact
The final ablation found that **NAIP imagery alone performed best on Macro-F1 and accuracy** for the evaluated Medium/Large classification task. Adding tabular and terrain features did not improve these scores, and the full three-modality model performed worse. These findings suggest that coarse regional indicators and terrain information can dilute useful local visual signal under the tested fusion design. They also demonstrate the value of evaluating added modalities rather than assuming that more data always improves a model.

ATLAS is an early investigation of **footprint-derived facility scale**, not a validated method for estimating actual energy or water use, identifying previously unknown facilities, or distinguishing operational categories such as Edge, Colocation, and Hyperscale. The small evaluation cohort, class imbalance, geographic transferability, and remaining image-to-terrain registration uncertainty limit generalization.


#### Future Work

- Expand and diversify the facility dataset, including more geographic regions and underrepresented size classes.
- Verify historical NAIP footprints and improve pixel-level image-to-DEM registration.
- Investigate fine-tuning visual encoders and adaptive fusion approaches, such as cross-attention, to better combine local and regional information.
- Evaluate against external geographic holdouts and develop independently validated operational facility labels.


**Additional Sources:**

- IM3 Open Source Data Center Atlas (2025), Pacific Northwest National Laboratory.
- USDA National Agriculture Imagery Program (NAIP).
- USGS 3D Elevation Program (3DEP).
- U.S. Energy Information Administration (EIA).
- World Resources Institute (WRI), Aqueduct 4.0.
- Zhou, Y., Tan, Y., Wen, Q., Wang, W., Li, L., & Li, Z. (2023). *Deep Multimodal Fusion Model for Building Structural Type Recognition Using Multisource Remote Sensing Images and Building-Related Knowledge*. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 16, 9646–9660. https://doi.org/10.1109/JSTARS.2023.3323484
- Suel, E., Bhatt, S., Brauer, M., Flaxman, S., & Ezzati, M. (2021). *Multimodal deep learning from satellite and street-level imagery for measuring income, overcrowding, and environmental deprivation in urban areas*. Remote Sensing of Environment, 257, 112339. https://doi.org/10.1016/j.rse.2021.112339
