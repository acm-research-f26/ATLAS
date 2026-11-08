# ATLAS Training

These multimodal experiments classify facilities as **Medium** or **Large**. The tables report held-out results across five geographic folds.

## Baseline — 128 tabular hidden units

**Run** · `linear-weighted-20261105-060320-225909`

| Setting | Value |
| --- | --- |
| Tabular encoder | One hidden layer with 128 units, dropout 0.1, and 64 output features |
| Image and DEM encoders | Frozen ImageNet ResNet-18 and frozen pretrained DEM CNNs |
| Fusion classifier | One linear layer with 640 inputs and two output logits |
| Loss | Class-weighted cross-entropy with weights calculated from each fold's training labels |
| Class weights | Medium 1.72–1.75 and Large 0.70–0.71, depending on the fold |
| Optimizer | Adam with learning rate `1e-3` and weight decay 0 |
| Batch size | 16 |
| Learning rate scheduler | `ReduceLROnPlateau` on validation loss with patience 2 and factor 0.5 |
| Epoch limit and early stopping | Up to 100 epochs. Stop after 7 epochs without lower validation loss and restore the best checkpoint. |
| Evaluation and seeds | Five geographic folds, base seed 42, and training seeds 43–47 |

### Held-out results

| Modality | Accuracy | Macro-F1 | Balanced accuracy |
| --- | ---: | ---: | ---: |
| Image only | 71.7% | 0.684 | 70.6% |
| Image + tabular | 65.3% | 0.608 | 62.0% |
| Image + DEM | 72.3% | 0.686 | 70.4% |
| **All three** | 62.4% | 0.577 | 58.7% |

## Experiment 1 — 32 tabular hidden units

**Run** · `linear-weighted-20261108-184912-657505`

Reduced the tabular hidden width from 128 to 32 and used class-weighted cross-entropy.

### Held-out results

| Modality | Accuracy | Macro-F1 | Balanced accuracy |
| --- | ---: | ---: | ---: |
| Image only | 72.8% | 0.694 | 71.4% |
| Image + tabular | 71.1% | 0.663 | 67.2% |
| Image + DEM | 71.7% | 0.686 | 71.2% |
| **All three** | 64.2% | 0.587 | 59.4% |

Image + tabular saw the largest improvement over the baseline. Accuracy rose from 65.3% to 71.1% and macro-F1 rose from 0.608 to 0.663. With all three modalities, accuracy rose from 62.4% to 64.2% and macro-F1 rose from 0.577 to 0.587.

## Experiment 2 — Unweighted cross-entropy

**Run** · `linear-weighted-20261108-200357-906451`

Used unweighted cross-entropy with the 32-unit tabular encoder.

### Held-out results

| Modality | Accuracy | Macro-F1 | Balanced accuracy |
| --- | ---: | ---: | ---: |
| Image only | 74.6% | 0.660 | 64.9% |
| Image + tabular | 70.5% | 0.589 | 58.5% |
| Image + DEM | 71.7% | 0.612 | 60.5% |
| **All three** | 71.7% | 0.583 | 58.1% |

With all three modalities, unweighted loss increased accuracy from 64.2% to 71.7%, while macro-F1 fell from 0.587 to 0.583 and balanced accuracy fell from 59.4% to 58.1%. The model made fewer false Medium predictions and missed more Medium facilities. The weighted run gave a better balance between the two classes.

## Other experiments

Additional experiments included prediction-level late fusion, removing `type` and `ba_code`, increasing tabular dropout from 0.10 to 0.25, and lowering the learning rate from `1e-3` to `3e-4` but didn't push them to s3 because they either performed significantly worse or no improvements at all.