"""
CNN Model Training Pipeline for Plant Disease Detection.

This script trains a Convolutional Neural Network (CNN) on the PlantVillage
dataset to classify 38 categories of plant leaf diseases and healthy leaves.

Dataset: PlantVillage Dataset (https://github.com/spMohanty/PlantVillage-Dataset)
         ~54,000 images across 38 classes of diseased and healthy plant leaves.

Architecture: Transfer Learning with MobileNetV2 (ImageNet pre-trained)
              + Custom classification head with dropout regularization.

Usage:
    python scripts/train_model.py                          # Train with defaults
    python scripts/train_model.py --epochs 30 --batch 64   # Custom parameters
    python scripts/train_model.py --data /path/to/dataset   # Custom dataset path

Output:
    - models/plant_disease_model.h5   (Trained Keras model weights)
    - models/training_history.png     (Accuracy & Loss curves)
    - models/confusion_matrix.png     (Per-class confusion matrix)
    - models/classification_report.txt (Precision, Recall, F1 per class)

Author: Bhuvaneswari.SA
Project: AI Plant Care — Final Year Project
"""

import os
import sys
import argparse
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for servers without display
import matplotlib.pyplot as plt
from datetime import datetime

# Suppress TensorFlow verbose logging during training
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# ============================================================================
# 1. CONFIGURATION
# ============================================================================

# 38 class labels matching the PlantVillage dataset directory structure.
# These MUST match the order used during training for correct inference.
CLASS_LABELS = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]

IMG_SIZE = 224          # Input resolution for MobileNetV2
CHANNELS = 3            # RGB
NUM_CLASSES = len(CLASS_LABELS)  # 38


# ============================================================================
# 2. DATA LOADING & AUGMENTATION
# ============================================================================

def create_data_generators(data_dir, batch_size, validation_split=0.2):
    """
    Create training and validation data generators with augmentation.

    Data Augmentation Strategy (applied ONLY to training set):
    - Random horizontal flip: Leaves can appear in any orientation
    - Random rotation (±20°): Account for varied camera angles in the field
    - Random zoom (±15%): Simulate different distances from the leaf
    - Random brightness shift (±20%): Handle outdoor lighting variation
    - Shear transformation (±10%): Minor perspective distortions

    Normalization:
    - All pixel values rescaled to [0, 1] range (divide by 255)
    - This matches the preprocessing used during inference in the web app
      (see app/ml/preprocessing.py)
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    # Training generator with augmentation
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        validation_split=validation_split,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
    )

    # Validation generator — NO augmentation, only rescaling
    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        validation_split=validation_split,
    )

    print(f"\n📁 Loading dataset from: {data_dir}")
    print(f"   Image size: {IMG_SIZE}x{IMG_SIZE}x{CHANNELS}")
    print(f"   Batch size: {batch_size}")
    print(f"   Validation split: {validation_split * 100}%\n")

    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=42,
    )

    val_generator = val_datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
        seed=42,
    )

    print(f"   Training samples:   {train_generator.samples}")
    print(f"   Validation samples: {val_generator.samples}")
    print(f"   Classes detected:   {len(train_generator.class_indices)}")

    # Verify class order matches our expected labels
    detected_classes = list(train_generator.class_indices.keys())
    if detected_classes != CLASS_LABELS:
        print("\n⚠️  WARNING: Detected class order does not match CLASS_LABELS.")
        print("   This may cause inference mismatches in the web application.")
        print(f"   Expected {NUM_CLASSES} classes, found {len(detected_classes)}.")

    return train_generator, val_generator


# ============================================================================
# 3. MODEL ARCHITECTURE
# ============================================================================

def build_model(learning_rate=0.001):
    """
    Build the CNN model using Transfer Learning with MobileNetV2.

    Architecture Justification:
    - MobileNetV2 is lightweight (~3.4M parameters) and optimized for mobile
      and edge deployment, which aligns with our goal of eventually running
      inference on farmer smartphones via TFLite (see Future Scope, Section 8).
    - Pre-trained on ImageNet (1.4M images, 1000 classes), providing strong
      feature extraction for plant leaf textures, colors, and patterns.
    - We freeze the base convolutional layers and only train the custom
      classification head, reducing training time and preventing overfitting
      on the ~54K PlantVillage images.

    Custom Classification Head:
    - GlobalAveragePooling2D: Reduces 7x7x1280 feature maps to 1280-d vector
    - Dense(512, ReLU): Learns disease-specific feature combinations
    - BatchNormalization: Stabilizes training, allows higher learning rates
    - Dropout(0.3): Regularization to prevent overfitting
    - Dense(256, ReLU): Additional capacity for 38-class discrimination
    - Dropout(0.2): Second regularization layer
    - Dense(38, Softmax): Output probability distribution across all classes
    """
    import tensorflow as tf
    from tensorflow.keras import layers, Model
    from tensorflow.keras.optimizers import Adam

    print("\n🏗️  Building model architecture...")

    # Load MobileNetV2 pre-trained on ImageNet, without the top classifier
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, CHANNELS),
        include_top=False,
        weights='imagenet',
    )

    # Freeze base model layers — we only train the classification head
    base_model.trainable = False

    # Custom classification head
    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, CHANNELS))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)

    model = Model(inputs, outputs, name='plant_disease_cnn')

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    total_params = model.count_params()
    trainable_params = sum(
        tf.keras.backend.count_params(w) for w in model.trainable_weights
    )
    print(f"   Base model:        MobileNetV2 (ImageNet)")
    print(f"   Total parameters:  {total_params:,}")
    print(f"   Trainable params:  {trainable_params:,}")
    print(f"   Frozen params:     {total_params - trainable_params:,}")
    print(f"   Output classes:    {NUM_CLASSES}")

    return model, base_model


def fine_tune_model(model, base_model, learning_rate=0.0001, fine_tune_from=100):
    """
    Unfreeze the top layers of the base model for fine-tuning.

    After initial training with a frozen base, we unfreeze the last N layers
    of MobileNetV2 and continue training with a much lower learning rate.
    This allows the model to adapt the pre-trained features to the specific
    textures and patterns of plant disease symptoms.

    We fine-tune from layer 100 onwards (~30% of MobileNetV2 layers).
    Earlier layers capture universal features (edges, textures) that
    generalize well, while later layers capture more task-specific features.
    """
    from tensorflow.keras.optimizers import Adam

    print(f"\n🔧 Fine-tuning: unfreezing layers from {fine_tune_from} onwards...")

    base_model.trainable = True
    for layer in base_model.layers[:fine_tune_from]:
        layer.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    trainable_count = sum(1 for l in base_model.layers if l.trainable)
    print(f"   Fine-tunable layers: {trainable_count}/{len(base_model.layers)}")

    return model


# ============================================================================
# 4. TRAINING CALLBACKS
# ============================================================================

def get_callbacks(output_dir):
    """
    Configure training callbacks for optimal model selection and early stopping.

    - ModelCheckpoint: Saves the best model (by val_accuracy) to disk.
      Only the best epoch is saved, preventing accidentally using an
      overfitted later epoch.
    - EarlyStopping: Halts training if val_loss doesn't improve for 7 epochs.
      Restores the best weights automatically.
    - ReduceLROnPlateau: Reduces learning rate by 50% if val_loss plateaus
      for 3 epochs. Helps escape shallow local minima.
    """
    from tensorflow.keras.callbacks import (
        ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
    )

    model_path = os.path.join(output_dir, 'plant_disease_model.h5')

    callbacks = [
        ModelCheckpoint(
            filepath=model_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1,
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    return callbacks, model_path


# ============================================================================
# 5. EVALUATION & VISUALIZATION
# ============================================================================

def plot_training_history(history, output_dir):
    """
    Plot and save training/validation accuracy and loss curves.

    These curves are critical for the project report to demonstrate:
    1. The model is learning (decreasing loss, increasing accuracy)
    2. No severe overfitting (train and val curves remain close)
    3. Early stopping triggered at the right epoch
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Accuracy
    ax1.plot(history.history['accuracy'], label='Training Accuracy', linewidth=2)
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
    ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)

    # Loss
    ax2.plot(history.history['loss'], label='Training Loss', linewidth=2)
    ax2.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
    ax2.set_title('Model Loss', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss (Categorical Cross-Entropy)')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, 'training_history.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n📊 Training history plot saved to: {path}")


def evaluate_model(model, val_generator, output_dir):
    """
    Run full evaluation on validation set and generate:
    1. Classification report (precision, recall, F1 per class)
    2. Confusion matrix heatmap
    3. Per-class accuracy breakdown
    """
    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    print("\n📈 Evaluating model on validation set...")

    # Get predictions
    val_generator.reset()
    y_pred_probs = model.predict(val_generator, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = val_generator.classes

    # Use class labels from the generator to ensure consistency
    class_names = list(val_generator.class_indices.keys())

    # Classification Report
    report = classification_report(
        y_true, y_pred,
        target_names=class_names,
        digits=4,
    )
    print("\n" + report)

    report_path = os.path.join(output_dir, 'classification_report.txt')
    with open(report_path, 'w') as f:
        f.write(f"Classification Report — Plant Disease CNN\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 70}\n\n")
        f.write(report)
    print(f"📄 Classification report saved to: {report_path}")

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(20, 18))
    sns.heatmap(
        cm, annot=False, fmt='d', cmap='Blues',
        xticklabels=class_names, yticklabels=class_names, ax=ax,
    )
    ax.set_title('Confusion Matrix — Plant Disease Classification', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted Class', fontsize=12)
    ax.set_ylabel('True Class', fontsize=12)
    plt.xticks(rotation=90, fontsize=6)
    plt.yticks(rotation=0, fontsize=6)
    plt.tight_layout()

    cm_path = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(cm_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 Confusion matrix saved to: {cm_path}")

    # Overall metrics
    overall_accuracy = np.sum(y_pred == y_true) / len(y_true)
    print(f"\n✅ Overall Validation Accuracy: {overall_accuracy:.4f} ({overall_accuracy * 100:.2f}%)")

    return overall_accuracy


# ============================================================================
# 6. MAIN TRAINING PIPELINE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Train the Plant Disease Detection CNN Model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/train_model.py --data dataset/PlantVillage
  python scripts/train_model.py --epochs 30 --batch 64 --lr 0.0005
  python scripts/train_model.py --no-fine-tune
        """
    )
    parser.add_argument(
        '--data', type=str, default='dataset/PlantVillage',
        help='Path to the PlantVillage dataset root directory (default: dataset/PlantVillage)',
    )
    parser.add_argument(
        '--output', type=str, default='models',
        help='Output directory for trained model and artifacts (default: models)',
    )
    parser.add_argument(
        '--epochs', type=int, default=20,
        help='Number of training epochs for initial phase (default: 20)',
    )
    parser.add_argument(
        '--fine-tune-epochs', type=int, default=10,
        help='Number of fine-tuning epochs (default: 10)',
    )
    parser.add_argument(
        '--batch', type=int, default=32,
        help='Batch size (default: 32)',
    )
    parser.add_argument(
        '--lr', type=float, default=0.001,
        help='Initial learning rate (default: 0.001)',
    )
    parser.add_argument(
        '--no-fine-tune', action='store_true',
        help='Skip the fine-tuning phase',
    )
    parser.add_argument(
        '--val-split', type=float, default=0.2,
        help='Validation split ratio (default: 0.2)',
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🌿 AI Plant Care — CNN Training Pipeline")
    print("=" * 70)
    print(f"   Started:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Dataset:    {args.data}")
    print(f"   Output:     {args.output}")
    print(f"   Epochs:     {args.epochs} (initial) + {args.fine_tune_epochs} (fine-tune)")
    print(f"   Batch size: {args.batch}")
    print(f"   LR:         {args.lr}")

    # Validate dataset path
    if not os.path.isdir(args.data):
        print(f"\n❌ ERROR: Dataset directory not found: {args.data}")
        print("   Download the PlantVillage dataset and extract it first.")
        print("   Expected structure:")
        print(f"     {args.data}/")
        print(f"       ├── Apple___Apple_scab/")
        print(f"       ├── Apple___Black_rot/")
        print(f"       ├── ...")
        print(f"       └── Tomato___healthy/")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Import TensorFlow after argument parsing to avoid slow startup on --help
    import tensorflow as tf
    print(f"\n   TensorFlow:  {tf.__version__}")
    print(f"   GPU:         {tf.config.list_physical_devices('GPU') or 'None (CPU mode)'}")

    # ---- Phase 1: Data Loading ----
    train_gen, val_gen = create_data_generators(
        args.data, args.batch, args.val_split
    )

    # ---- Phase 2: Build Model ----
    model, base_model = build_model(learning_rate=args.lr)
    model.summary()

    # ---- Phase 3: Initial Training (frozen base) ----
    print(f"\n{'=' * 70}")
    print(f"🚀 Phase 1: Training classification head ({args.epochs} epochs)")
    print(f"{'=' * 70}")

    callbacks, model_path = get_callbacks(args.output)

    history = model.fit(
        train_gen,
        epochs=args.epochs,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1,
    )

    # ---- Phase 4: Fine-Tuning (optional) ----
    if not args.no_fine_tune and args.fine_tune_epochs > 0:
        print(f"\n{'=' * 70}")
        print(f"🔧 Phase 2: Fine-tuning top layers ({args.fine_tune_epochs} epochs)")
        print(f"{'=' * 70}")

        model = fine_tune_model(model, base_model, learning_rate=args.lr / 10)
        callbacks_ft, _ = get_callbacks(args.output)

        history_ft = model.fit(
            train_gen,
            epochs=args.epochs + args.fine_tune_epochs,
            initial_epoch=len(history.history['accuracy']),
            validation_data=val_gen,
            callbacks=callbacks_ft,
            verbose=1,
        )

        # Merge histories for plotting
        for key in history.history:
            history.history[key].extend(history_ft.history[key])

    # ---- Phase 5: Evaluation ----
    print(f"\n{'=' * 70}")
    print(f"📈 Phase 3: Evaluation & Visualization")
    print(f"{'=' * 70}")

    plot_training_history(history, args.output)
    accuracy = evaluate_model(model, val_gen, args.output)

    # Save training metadata
    metadata = {
        'model_name': 'plant_disease_cnn',
        'model_version': '1.0.0',
        'architecture': 'MobileNetV2 + Custom Head',
        'input_shape': [IMG_SIZE, IMG_SIZE, CHANNELS],
        'num_classes': NUM_CLASSES,
        'class_labels': CLASS_LABELS,
        'dataset': 'PlantVillage',
        'validation_accuracy': float(accuracy),
        'epochs_trained': len(history.history['accuracy']),
        'batch_size': args.batch,
        'initial_lr': args.lr,
        'fine_tuned': not args.no_fine_tune,
        'preprocessing': 'RGB, resize 224x224, normalize [0,1]',
        'trained_at': datetime.now().isoformat(),
    }
    meta_path = os.path.join(args.output, 'training_metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"\n📝 Training metadata saved to: {meta_path}")

    print(f"\n{'=' * 70}")
    print(f"✅ Training complete!")
    print(f"   Model saved to:   {model_path}")
    print(f"   Val accuracy:     {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print(f"   Finished:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
