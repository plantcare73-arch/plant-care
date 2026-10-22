# Machine Learning Models Directory

This directory stores trained deep learning model weights for the AI Plant Care diagnostic engine.

## Model Specifications

- **Target Architecture**: MobileNetV2 (Transfer Learning from ImageNet) + Custom Dense Classifier
- **Input Dimensions**: `(224, 224, 3)` RGB normalized to `[0.0, 1.0]`
- **Classes**: 38 plant disease & healthy leaf categories from the PlantVillage dataset
- **Primary Production File**: `models/plant_disease_model.h5`
- **Fallback Filename**: `models/model_weights.h5`

## Training Your Own Model

A training pipeline is provided in `scripts/train_model.py`. It handles data loading, augmentation, transfer learning with fine-tuning, evaluation, and exporting accuracy/loss curves and confusion matrices:

```bash
# 1. Download the PlantVillage dataset (color images)
# 2. Train the CNN model:
python scripts/train_model.py --data path/to/PlantVillage/color --epochs 30 --batch 64
```

The script will automatically output:
- `models/plant_disease_model.h5` — Model weights ready for production inference
- `models/training_history.png` — Loss and accuracy convergence graphs
- `models/confusion_matrix.png` — Per-class confusion matrix
- `models/classification_report.txt` — Precision, recall, and F1 scores per class

## Demo Mode Fallback

If no `.h5` file is present in this directory, the application gracefully operates in **Demo Mode**, generating structured synthetic predictions with realistic confidence scores, severity assessments, and full treatment plans. This ensures that the application, UI, and workflows can be evaluated and demonstrated even without downloading multi-hundred-megabyte weights.
