"""
retrain.py  —  Complete Brahmi OCR Model Retraining Script
===========================================================
Dataset  : models/dataset/OCR_Dataset/RecognizerDataset_Handwritten
           models/dataset/OCR_Dataset/RecognizerDataset_Stone
Images   : .tif.tif files, 150x150, binary (mode=1)
Output   : models/MODEL/model.h5          (replaces old model)
           models/MODEL/label_map.json    (index → class name)

Run:
    cd C:/Users/yashd/final_bramhi
    python retrain.py

Requirements:
    pip install tensorflow scikit-learn pillow numpy opencv-python matplotlib
"""

import os, json, time, random
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PIL import Image as PILImage
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# ════════════════════════════════════════════════════════════════════════════
# CONFIG  — change these if needed
# ════════════════════════════════════════════════════════════════════════════
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))

DATASET_DIRS = [
    os.path.join(BASE_DIR, 'models', 'dataset', 'OCR_Dataset', 'RecognizerDataset_Handwritten'),
    os.path.join(BASE_DIR, 'models', 'dataset', 'OCR_Dataset', 'RecognizerDataset_Stone'),
]

OUTPUT_DIR   = os.path.join(BASE_DIR, 'models', 'MODEL')
MODEL_PATH   = os.path.join(OUTPUT_DIR, 'model.h5')
LABEL_PATH   = os.path.join(OUTPUT_DIR, 'label_map.json')
PLOT_PATH    = os.path.join(OUTPUT_DIR, 'training_history.png')

IMG_SIZE     = 64          # upgraded from 32 → better accuracy
BATCH_SIZE   = 64
EPOCHS       = 40
LR           = 1e-3
VAL_SPLIT    = 0.15
TEST_SPLIT   = 0.10
MIN_SAMPLES  = 2           # skip classes with fewer images than this

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("  Brahmi OCR — Model Retraining")
print("=" * 60)
print(f"  Image size : {IMG_SIZE}x{IMG_SIZE}")
print(f"  Batch size : {BATCH_SIZE}")
print(f"  Epochs     : {EPOCHS}")
print(f"  Output     : {MODEL_PATH}")
print("=" * 60)


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — Discover all classes across both dataset folders
# ════════════════════════════════════════════════════════════════════════════
print("\n[1/6] Scanning dataset folders...")

# Collect {class_name: [file_paths]}
class_files = {}

for dataset_dir in DATASET_DIRS:
    if not os.path.isdir(dataset_dir):
        print(f"  WARNING: not found → {dataset_dir}")
        continue

    for class_name in sorted(os.listdir(dataset_dir)):
        class_dir = os.path.join(dataset_dir, class_name)
        if not os.path.isdir(class_dir):
            continue

        files = [
            os.path.join(class_dir, f)
            for f in os.listdir(class_dir)
            if f.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg', '.bmp'))
        ]

        if len(files) < MIN_SAMPLES:
            continue

        if class_name not in class_files:
            class_files[class_name] = []
        class_files[class_name].extend(files)

# Build sorted class list and index mapping
class_names = sorted(class_files.keys())
NUM_CLASSES  = len(class_names)
name_to_idx  = {name: i for i, name in enumerate(class_names)}
idx_to_name  = {i: name for name, i in name_to_idx.items()}

total_images = sum(len(v) for v in class_files.values())
print(f"  Classes found : {NUM_CLASSES}")
print(f"  Total images  : {total_images}")
print(f"  Sample classes: {class_names[:10]} ...")

# Save label map (index → class name)  — used by final.py
with open(LABEL_PATH, 'w', encoding='utf-8') as f:
    json.dump(idx_to_name, f, ensure_ascii=False, indent=2)
print(f"  Label map saved → {LABEL_PATH}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — Load and preprocess all images
# ════════════════════════════════════════════════════════════════════════════
print(f"\n[2/6] Loading {total_images} images (this may take a few minutes)...")

def load_and_preprocess(path):
    """
    Load any image format → uint8 grayscale → 64x64 float32.
    Output format: WHITE ink on BLACK background, values 0.0–1.0.
    """
    try:
        pil = PILImage.open(path)

        # Handle 1-bit binary TIF (dataset format)
        if pil.mode == '1':
            arr = np.array(pil, dtype=np.uint8) * 255
        else:
            arr = np.array(pil.convert('L'), dtype=np.uint8)

        # Ensure white background, black ink
        if arr.mean() < 128:
            arr = 255 - arr

        # Scale up 2x before thresholding (preserves stroke detail)
        h, w = arr.shape
        up = cv2.resize(arr, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

        # Otsu threshold → clean binary
        blur = cv2.GaussianBlur(up, (3, 3), 0)
        _, binary = cv2.threshold(blur, 0, 255,
                                  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Resize to target size
        img = cv2.resize(binary, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)

        # Re-threshold after resize (removes gray aliasing)
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        # Ensure WHITE ink on BLACK background
        if img.mean() > 128:
            img = 255 - img

        # Normalize to 0.0–1.0
        return img.astype(np.float32) / 255.0

    except Exception as e:
        return None


X = []   # images
y = []   # labels

for class_name, files in class_files.items():
    label = name_to_idx[class_name]
    loaded = 0
    for path in files:
        img = load_and_preprocess(path)
        if img is not None:
            X.append(img)
            y.append(label)
            loaded += 1
    if loaded == 0:
        print(f"  WARNING: 0 images loaded for class '{class_name}'")

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)

# Add channel dimension: (N, 64, 64) → (N, 64, 64, 1)
X = np.expand_dims(X, axis=-1)

print(f"  Loaded: X={X.shape}  y={y.shape}")
print(f"  Pixel range: {X.min():.2f} – {X.max():.2f}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — Split into train / validation / test
# ════════════════════════════════════════════════════════════════════════════
print("\n[3/6] Splitting data...")

X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=TEST_SPLIT, random_state=SEED, stratify=y)

val_ratio = VAL_SPLIT / (1.0 - TEST_SPLIT)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=val_ratio, random_state=SEED, stratify=y_temp)

print(f"  Train : {len(X_train)}")
print(f"  Val   : {len(X_val)}")
print(f"  Test  : {len(X_test)}")

# Compute class weights to handle imbalanced classes
class_weights_arr = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = {i: w for i, w in enumerate(class_weights_arr)}


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — Build model  (CNN + BatchNorm + Dropout)
# ════════════════════════════════════════════════════════════════════════════
print("\n[4/6] Building model...")

def build_model(num_classes, img_size=64):
    """
    Deep CNN with:
    - BatchNormalization after each Conv block (stable training)
    - Dropout (reduce overfitting)
    - GlobalAveragePooling (fewer params than Flatten)
    - L2 regularization on Dense layers
    """
    reg = keras.regularizers.l2(1e-4)

    inputs = keras.Input(shape=(img_size, img_size, 1))

    # Block 1
    x = layers.Conv2D(32, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(32, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.25)(x)

    # Block 2
    x = layers.Conv2D(64, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(64, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.25)(x)

    # Block 3
    x = layers.Conv2D(128, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(128, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.30)(x)

    # Block 4
    x = layers.Conv2D(256, 3, padding='same', activation='relu',
                      kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.30)(x)

    # Head
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512, activation='relu', kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.50)(x)
    x = layers.Dense(256, activation='relu', kernel_regularizer=reg)(x)
    x = layers.Dropout(0.40)(x)

    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = keras.Model(inputs, outputs)
    return model


model = build_model(NUM_CLASSES, IMG_SIZE)
model.summary()

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LR),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)


# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — Data Augmentation + Training
# ════════════════════════════════════════════════════════════════════════════
print("\n[5/6] Training...")

# Data augmentation (only on training data)
data_augmentation = keras.Sequential([
    layers.RandomRotation(0.08),           # ±8% rotation
    layers.RandomTranslation(0.08, 0.08),  # shift up/down/left/right
    layers.RandomZoom(0.08),               # slight zoom
], name='augmentation')

# Custom augmented dataset
def make_dataset(X, y, augment=False, batch_size=BATCH_SIZE):
    ds = tf.data.Dataset.from_tensor_slices((X, y))
    if augment:
        ds = ds.shuffle(len(X), seed=SEED)
        ds = ds.map(
            lambda img, lbl: (data_augmentation(img, training=True), lbl),
            num_parallel_calls=tf.data.AUTOTUNE
        )
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(X_train, y_train, augment=True)
val_ds   = make_dataset(X_val,   y_val,   augment=False)

# Callbacks
cb_list = [
    # Save best model automatically
    callbacks.ModelCheckpoint(
        MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    # Reduce LR when val_loss plateaus
    callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1
    ),
    # Stop early if no improvement for 15 epochs
    callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    callbacks.TensorBoard(
        log_dir=os.path.join(OUTPUT_DIR, 'logs'),
        histogram_freq=0
    )
]

start = time.time()

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    class_weight=class_weight_dict,
    callbacks=cb_list,
    verbose=1
)

elapsed = time.time() - start
print(f"\n  Training complete in {elapsed/60:.1f} minutes")


# ════════════════════════════════════════════════════════════════════════════
# STEP 6 — Evaluate on test set + save plots
# ════════════════════════════════════════════════════════════════════════════
print("\n[6/6] Evaluating on test set...")

test_ds = make_dataset(X_test, y_test, augment=False)
test_loss, test_acc = model.evaluate(test_ds, verbose=0)
print(f"\n  ✅ Test Accuracy : {test_acc*100:.2f}%")
print(f"  ✅ Test Loss     : {test_loss:.4f}")

# Per-class accuracy on test set
print("\n  Top-10 most confused classes:")
preds      = model.predict(test_ds, verbose=0)
pred_labels = np.argmax(preds, axis=1)
correct    = (pred_labels == y_test)

per_class_acc = {}
for i in range(NUM_CLASSES):
    mask = (y_test == i)
    if mask.sum() > 0:
        per_class_acc[idx_to_name[i]] = correct[mask].mean()

worst = sorted(per_class_acc.items(), key=lambda x: x[1])[:10]
for name, acc in worst:
    print(f"    {name:20s}  {acc*100:.1f}%")

# Plot training history
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history.history['accuracy'],     label='Train Acc')
ax1.plot(history.history['val_accuracy'], label='Val Acc')
ax1.set_title('Accuracy'); ax1.legend(); ax1.set_xlabel('Epoch')

ax2.plot(history.history['loss'],     label='Train Loss')
ax2.plot(history.history['val_loss'], label='Val Loss')
ax2.set_title('Loss'); ax2.legend(); ax2.set_xlabel('Epoch')

plt.suptitle(f'Brahmi OCR — Final Test Accuracy: {test_acc*100:.2f}%')
plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150)
print(f"\n  Training plot saved → {PLOT_PATH}")

# Final summary
print("\n" + "=" * 60)
print("  RETRAINING COMPLETE")
print("=" * 60)
print(f"  Model saved   : {MODEL_PATH}")
print(f"  Label map     : {LABEL_PATH}")
print(f"  Classes       : {NUM_CLASSES}")
print(f"  Test accuracy : {test_acc*100:.2f}%")
print(f"  Training time : {elapsed/60:.1f} min")
print("=" * 60)
print("""
  NEXT STEP: Update final.py to use the new label map.
  Add this to the top of final.py:

    import json
    with open('models/MODEL/label_map.json') as f:
        _map = json.load(f)
    NUM_TO_NAME = {int(k): v for k, v in _map.items()}
""")
