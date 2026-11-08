### ATLAS Training 

<ins>Baseline</ins>

-The multimodal model baseline is the folder ending in 225909 with the hyperparameters of 
```
Tabular encoder - one hidder layer with 128 units, dropout = 0.1, 64-feature output

Fusion classifer - one linear layer, 640 inputs, 2 logits

Image and DEM encoder - frozen resnet18 and ImageNet weights and frozen pretrained DEM CNNs

Loss - class-weighted cross-entropy, with weights calculated from each folds training labels

Class weights = medium: 1.72-1.75, large: 0.70-0.71 dependent on fold

Optimizer - Adam, learning rate of 0.001 and weight decay of 0

Batch size - 16

Learning-rate scheduler - ReduceLROnPlateau on validation loss, patience 2, factor 0.5

Epoch and early stopping - up to 100 epochs, stops after 7 epochs without lower validation loss and restore best checkpoint

Evaluation and seeds - 5 geographic folds, base seed 42, training seed 43-47

```

## Results

"accuracy": 0.6242774566473989,
"macro_f1": 0.5766986636551854,
"balanced_accuracy": 0.5873983739837398

# Modality comparison
variant,accuracy,macro_f1,balanced_accuracy
image_only | 0.7167630057803468 |0.6836113910349718 | 0.7058536585365853
image_tabular | 0.653179190751445 | 0.6075317604355717 | 0.6195934959349594
image_dem | 0.7225433526011561 | 0.6860254083484574 | 0.7039837398373984
all | 0.6242774566473989 | 0.5766986636551854 | 0.5873983739837398


<ins>Test 1</ins>

-The test ending in 657505 runs on 32 hidden layers instead of 128 on the tabular encoder 

## Results

"accuracy": 0.6416184971098265,
"macro_f1": 0.5868258859784283,
"balanced_accuracy": 0.5936585365853658

# Modality comparison
variant,accuracy,macro_f1,balanced_accuracy
image_only | 0.7283236994219653 | 0.6939205721814418 | 0.7139837398373984
image_tabular | 0.7109826589595376 | 0.6634765017117958 | 0.6721138211382114
image_dem | 0.7167630057803468 | 0.6861881316403213 | 0.7117886178861789
all | 0.6416184971098265 | 0.5868258859784283 | 0.5936585365853658


The biggest improvement was 
Model | Accuracy | Macro-F1 | 
Image + tabular	| 65.3% → 71.1%  |0.608 → 0.663 |
All three |62.4% → 64.2%| 0.577 → 0.587| 

<ins>Test 2</ins>

-The test ending in 906451 uses unweighted cross-entropy loss with 32 hidden layers 

## Results

"accuracy": 0.7167630057803468,
"macro_f1": 0.5829274292742928,
"balanced_accuracy": 0.581219512195122,

# Modality Comparison
variant,accuracy,macro_f1,balanced_accuracy
image_only | 0.7456647398843931 | 0.6595706618962434 | 0.6490243902439025
image_tabular | 0.7052023121387283 | 0.5889587700908456 | 0.5849593495934959
image_dem | 0.7167630057803468 | 0.611663383572312 | 0.604959349593496
all | 0.7167630057803468 | 0.5829274292742928 | 0.581219512195122

The weighted loss is the better choice between unweighted if we want the model to recognize both classes reliably, because it swung too far toward large even though it reduced false Medium predictions.

I've also tried prediction-level late fusion, removing columns lie "type" and "ba_code", changed the tabular dropout to 0.25 to 0.1, and changed the learning rate from 1e-3 to 3e-4, and it performed worse with those implementations so I didn't even send them to s3.