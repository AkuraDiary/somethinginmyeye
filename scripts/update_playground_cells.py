#!/usr/bin/env python3
"""
Updates Section 10 of playground.ipynb to implement the localized Dual-Head Reversal Classifier (DHRC)
pipeline consuming dhrc_train_datasets/ and dhrc_val_datasets/ with 52 Latin classes and dynamic training.
"""

import json
import os
import sys

NOTEBOOK_PATH = "playground.ipynb"

with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Markdown Header (Cell 19)
c19_md = """## 10. In-House Dual-Head Reversal Classifier (DHRC): Ingestion, Training & Evaluation

This section trains and evaluates the in-house **Dual-Head Reversal Classifier (DHRC)** directly from the dedicated local partitioned repositories:
- **Training Cohort:** `dhrc_train_datasets/` (902 raw isolated Latin letter samples: 443 Typical, 459 Atypical).
- **Validation Holdout:** `dhrc_val_datasets/` (198 raw isolated Latin letter samples: 130 Typical, 68 Atypical).
- **Zero-Digit Invariant:** Evaluates strictly the 52-letter Latin alphabet (`a-z`, `A-Z`). Numerals are completely eliminated under DSM-5 SLD guidelines.
- **Dual-Task Objectives:**
  1. **Head 1 (`char_output`):** Softmax across 52 classes for canonical character identification.
  2. **Head 2 (`reversal_output`):** Sigmoid probability ($p_{\\text{rev}} \\ge 0.50$) detecting clinical mirror reversals and inversions.
"""

# Code: Ingest Local Partitioned Tablet Datasets (Cell 20)
c20_code = """import os
import sys
import glob
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional

# Ensure scripts directory is on sys.path
SCRIPT_DIR = os.path.abspath("scripts")
PROJECT_ROOT = os.path.abspath(".")
for p in [SCRIPT_DIR, PROJECT_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

from config import (
    DHRC_TRAIN_DIR,
    DHRC_VAL_DIR,
    DHRC_VOCABULARY,
    DHRC_CHAR_TO_IDX,
    DHRC_SEQ_LEN,
    DHRC_FEATURES,
    DHRC_NUM_CLASSES
)

# -----------------------------------------------------------------------------
# 1. LATIN ALPHABET VOCABULARY (52 CLASSES: a-z, A-Z)
# -----------------------------------------------------------------------------
VOCABULARY = DHRC_VOCABULARY
CHAR_TO_IDX = DHRC_CHAR_TO_IDX

# Chiral reversal transformation maps
HORIZONTAL_REVERSIBLE_CHARS = {
    'b': 'd', 'd': 'b',
    'p': 'q', 'q': 'p',
    'B': 'B_rev', 'D': 'D_rev', 'E': 'E_rev', 'F': 'F_rev',
    'J': 'J_rev', 'K': 'K_rev', 'L': 'L_rev', 'N': 'N_rev',
    'P': 'P_rev', 'R': 'R_rev', 'S': 'S_rev', 'Z': 'Z_rev',
    'c': 'c_rev', 'e': 'e_rev', 's': 's_rev', 'z': 'z_rev'
}

ROTATIONAL_REVERSIBLE_CHARS = {
    'm': 'w', 'w': 'm',
    'u': 'n', 'n': 'u',
    'M': 'W', 'W': 'M'
}

# -----------------------------------------------------------------------------
# 2. LOCAL TABLET SAMPLE LOADER
# -----------------------------------------------------------------------------
def load_tablet_samples_from_dir(dataset_dir: str) -> List[Dict[str, Any]]:
    \"\"\"
    Reads tablet CSV recordings and segments them into stroke point lists:
    {'label': char, 'sample_id': filename, 'strokes': [[(x, y), ...]], 'is_atypical': bool}
    \"\"\"
    samples = []
    csv_files = sorted(glob.glob(os.path.join(dataset_dir, "*.csv")))
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        if len(parts) < 4:
            continue
            
        # Extract label and mode
        mode = parts[1].lower()
        if parts[-1].isdigit() and parts[-2].isdigit():
            lbl = "_".join(parts[2:-3])
        elif parts[-1].isdigit():
            lbl = "_".join(parts[2:-2])
        else:
            lbl = parts[2]
            
        if len(lbl) != 1 or lbl not in CHAR_TO_IDX:
            continue
            
        try:
            df = pd.read_csv(filepath)
            if 'x' not in df.columns or 'y' not in df.columns:
                continue
                
            touching = df['touching'].values if 'touching' in df.columns else np.ones(len(df))
            time_vals = df['time'].values if 'time' in df.columns else np.arange(len(df))
            
            strokes = []
            curr_stroke = []
            for i in range(len(df)):
                if touching[i] == 1:
                    if curr_stroke and i > 0 and (time_vals[i] - time_vals[i-1]) > 80.0:
                        if len(curr_stroke) >= 2:
                            strokes.append(curr_stroke)
                        curr_stroke = []
                    curr_stroke.append((float(df['x'].iloc[i]), float(df['y'].iloc[i])))
                else:
                    if len(curr_stroke) >= 2:
                        strokes.append(curr_stroke)
                    curr_stroke = []
            if len(curr_stroke) >= 2:
                strokes.append(curr_stroke)
                
            if strokes:
                samples.append({
                    'label': lbl,
                    'sample_id': filename,
                    'source': os.path.basename(dataset_dir),
                    'strokes': strokes,
                    'is_atypical': ("dyslexia" in mode or "dysgraphia" in mode)
                })
        except Exception:
            continue
            
    return samples

print("Loading local partitioned cohorts...")
train_samples = load_tablet_samples_from_dir(DHRC_TRAIN_DIR)
val_samples = load_tablet_samples_from_dir(DHRC_VAL_DIR)

train_typ = sum(1 for s in train_samples if not s['is_atypical'])
train_atyp = sum(1 for s in train_samples if s['is_atypical'])
val_typ = sum(1 for s in val_samples if not s['is_atypical'])
val_atyp = sum(1 for s in val_samples if s['is_atypical'])

print(f"Loaded {len(train_samples)} training samples from '{DHRC_TRAIN_DIR}':")
print(f"  -> Typical (Normal): {train_typ} | Atypical (SLD/Dyslexia): {train_atyp}")
print(f"Loaded {len(val_samples)} validation holdout samples from '{DHRC_VAL_DIR}':")
print(f"  -> Typical (Normal): {val_typ} | Atypical (SLD/Dyslexia): {val_atyp}")
print(f"Vocabulary size: {len(VOCABULARY)} Latin classes (strictly zero digits).")
"""

# Code: Visualizer (Cell 21)
c21_code = """import matplotlib.pyplot as plt
import matplotlib.cm as cm

def get_sample_bounding_box(strokes: List[List[Tuple[float, float]]]) -> Tuple[float, float, float, float]:
    all_x = [pt[0] for stroke in strokes for pt in stroke]
    all_y = [pt[1] for stroke in strokes for pt in stroke]
    if not all_x or not all_y:
        return 0.0, 1.0, 0.0, 1.0
    return min(all_x), max(all_x), min(all_y), max(all_y)

def plot_strokes_with_trajectory(ax, strokes, title, color_map="Blues"):
    \"\"\"
    Plots a multi-stroke character trajectory with progressive color gradients
    and directional arrows to visually inspect authentic vs. reversed kinematics.
    \"\"\"
    cmap = plt.get_cmap(color_map)
    min_x, max_x, min_y, max_y = get_sample_bounding_box(strokes)
    total_pts = sum(len(s) for s in strokes)
    pt_counter = 0
    
    for s_idx, stroke in enumerate(strokes):
        if not stroke:
            continue
        xs = [pt[0] for pt in stroke]
        ys = [pt[1] for pt in stroke]
        
        for i in range(len(stroke) - 1):
            t = (pt_counter + i) / max(total_pts - 1, 1)
            ax.plot(
                [xs[i], xs[i+1]], 
                [ys[i], ys[i+1]], 
                color=cmap(0.35 + 0.65 * t), 
                linewidth=2.8, 
                solid_capstyle='round'
            )
            
            # Directional arrow near stroke midpoint
            if len(stroke) >= 4 and i == len(stroke) // 2:
                dx = xs[i+1] - xs[i]
                dy = ys[i+1] - ys[i]
                ax.annotate(
                    '', 
                    xy=(xs[i+1], ys[i+1]), 
                    xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="->", color=cmap(0.85), lw=1.5)
                )
        pt_counter += len(stroke)
        
    margin_x = max((max_x - min_x) * 0.15, 0.05)
    margin_y = max((max_y - min_y) * 0.15, 0.05)
    ax.set_xlim(min_x - margin_x, max_x + margin_x)
    ax.set_ylim(max_y + margin_y, min_y - margin_y)  # Invert Y to match screen coordinates
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(title, fontsize=11, fontweight='bold', pad=8)
    ax.axis('off')

# Find representative samples for visual inspection
sample_norm = next((s for s in train_samples if s['label'] == 'b' and not s['is_atypical']), train_samples[0])
sample_atyp = next((s for s in train_samples if s['label'] == 'b' and s['is_atypical']), train_samples[1])

# Generate synthetic mirror
min_x, max_x, _, _ = get_sample_bounding_box(sample_norm['strokes'])
mirrored_strokes = [[(min_x + max_x - pt[0], pt[1]) for pt in stroke] for stroke in sample_norm['strokes']]

fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
plot_strokes_with_trajectory(axes[0], sample_norm['strokes'], f"Authentic Normal '{sample_norm['label']}' (y_rev=0.0)", "Greens")
plot_strokes_with_trajectory(axes[1], sample_atyp['strokes'], f"Authentic Clinical Dyslexic '{sample_atyp['label']}' (y_rev=1.0)", "Reds")
plot_strokes_with_trajectory(axes[2], mirrored_strokes, f"Synthetically Mirrored '{sample_norm['label']}' (y_rev=1.0)", "Purples")
plt.tight_layout()
plt.show()
"""

# Markdown: 10.1 Feature Extraction (Cell 22)
c22_md = """### 10.1 Equidistant Arc-Length Resampling & Chiral Augmentation

1. **Equidistant Arc-Length Parameterization ($T=64$):** Decouples writing geometry from temporal polling rate and motor tremor speed spikes by querying at uniform spatial intervals ($\Delta s$).
2. **8 Kinematic Feature Channels ($F=8$):** $[\Delta x, \Delta y, \cos\\theta, \sin\\theta, \Delta\\theta, d^2x, d^2y, \\text{pen\\_state}]$.
3. **Clinical Augmentation Protocol:**
   - **Training Set ONLY (`dhrc_train_datasets/`):** Horizontally reflects normal chiral letters ($b \\leftrightarrow d, p \\leftrightarrow q, B, D, E, S$, etc.) and rotates invertible letters ($m \\leftrightarrow w, u \\leftrightarrow n$), assigning $y_{\\text{rev}} = 1.0$.
   - **Validation Set (`dhrc_val_datasets/`):** Strictly unaugmented, preserving 100% pure authentic human handwriting.
"""

# Code: Feature Extraction & Tensor Construction (Cell 23)
c23_code = """def resample_and_normalize_sample(
    sample: Dict[str, Any], 
    target_len: int = DHRC_SEQ_LEN
) -> Dict[str, np.ndarray]:
    \"\"\"Resamples stroke trajectories to fixed length T with arc-length equidistant sampling.\"\"\"
    strokes = sample.get('strokes', [])
    if not strokes or sum(len(s) for s in strokes) == 0:
        return {
            'x': np.zeros(target_len, dtype=np.float32),
            'y': np.zeros(target_len, dtype=np.float32),
            'pen_state': np.zeros(target_len, dtype=np.float32)
        }

    raw_x, raw_y, raw_pen = [], [], []
    for s_idx, stroke in enumerate(strokes):
        if not stroke:
            continue
        if s_idx > 0 and len(raw_x) > 0:
            raw_x.append(stroke[0][0])
            raw_y.append(stroke[0][1])
            raw_pen.append(0.0)  # Air-stroke transition
        for pt in stroke:
            raw_x.append(float(pt[0]))
            raw_y.append(float(pt[1]))
            raw_pen.append(1.0)  # On-surface writing

    raw_x = np.array(raw_x, dtype=np.float64)
    raw_y = np.array(raw_y, dtype=np.float64)
    raw_pen = np.array(raw_pen, dtype=np.float64)

    min_x, max_x = np.min(raw_x), np.max(raw_x)
    min_y, max_y = np.min(raw_y), np.max(raw_y)
    scale = max(max_x - min_x, max_y - min_y, 1e-6)

    norm_x = (raw_x - min_x) / scale
    norm_y = (raw_y - min_y) / scale

    dx = np.diff(norm_x)
    dy = np.diff(norm_y)
    step_distances = np.sqrt(dx**2 + dy**2)
    cum_dist = np.empty(len(norm_x), dtype=np.float64)
    cum_dist[0] = 0.0
    cum_dist[1:] = np.cumsum(step_distances)
    total_length = cum_dist[-1]

    if total_length < 1e-6:
        return {
            'x': np.full(target_len, norm_x[0], dtype=np.float32),
            'y': np.full(target_len, norm_y[0], dtype=np.float32),
            'pen_state': np.ones(target_len, dtype=np.float32)
        }

    query_dist = np.linspace(0.0, total_length, target_len)
    res_x = np.interp(query_dist, cum_dist, norm_x).astype(np.float32)
    res_y = np.interp(query_dist, cum_dist, norm_y).astype(np.float32)
    interp_pen = np.interp(query_dist, cum_dist, raw_pen)
    res_pen = (interp_pen >= 0.5).astype(np.float32)

    return {'x': res_x, 'y': res_y, 'pen_state': res_pen}

def extract_reversal_kinematic_features(
    resampled_data: Dict[str, np.ndarray],
    eps: float = 1e-7
) -> np.ndarray:
    \"\"\"Extracts an 8-dimensional kinematic and geometric trajectory feature matrix.\"\"\"
    x = resampled_data['x']
    y = resampled_data['y']
    pen_state = resampled_data['pen_state']
    T = len(x)

    dx = np.empty(T, dtype=np.float32)
    dy = np.empty(T, dtype=np.float32)
    dx[0], dy[0] = 0.0, 0.0
    dx[1:] = np.diff(x)
    dy[1:] = np.diff(y)

    ds = np.sqrt(dx**2 + dy**2) + eps
    cos_theta = dx / ds
    sin_theta = dy / ds

    d_theta = np.zeros(T, dtype=np.float32)
    d_theta[1:] = sin_theta[1:] * cos_theta[:-1] - cos_theta[1:] * sin_theta[:-1]

    d2x = np.zeros(T, dtype=np.float32)
    d2y = np.zeros(T, dtype=np.float32)
    d2x[1:] = np.diff(dx)
    d2y[1:] = np.diff(dy)

    return np.column_stack([
        dx, dy, cos_theta, sin_theta, d_theta, d2x, d2y, pen_state.astype(np.float32)
    ])

# -----------------------------------------------------------------------------
# BUILD TRAINING TENSORS WITH CHIRAL AUGMENTATION (TRAIN ONLY)
# -----------------------------------------------------------------------------
X_train_list, y_char_train_list, y_rev_train_list = [], [], []

for s in train_samples:
    lbl = s['label']
    c_idx = CHAR_TO_IDX[lbl]
    is_atyp = s['is_atypical']
    
    # 1. Authentic sample
    res_auth = resample_and_normalize_sample(s)
    feat_auth = extract_reversal_kinematic_features(res_auth)
    X_train_list.append(feat_auth)
    y_char_train_list.append(c_idx)
    y_rev_train_list.append(1.0 if is_atyp else 0.0)
    
    # 2. Augment Normal Chiral Letters ONLY (Never flip Atypical samples)
    if not is_atyp:
        if lbl in HORIZONTAL_REVERSIBLE_CHARS:
            min_x, max_x, _, _ = get_sample_bounding_box(s['strokes'])
            mir_strokes = [[(min_x + max_x - pt[0], pt[1]) for pt in stroke] for stroke in s['strokes']]
            res_mir = resample_and_normalize_sample({'strokes': mir_strokes})
            X_train_list.append(extract_reversal_kinematic_features(res_mir))
            y_char_train_list.append(c_idx)
            y_rev_train_list.append(1.0)
            
        if lbl in ROTATIONAL_REVERSIBLE_CHARS:
            min_x, max_x, min_y, max_y = get_sample_bounding_box(s['strokes'])
            rot_strokes = [[(min_x + max_x - pt[0], min_y + max_y - pt[1]) for pt in stroke] for stroke in s['strokes']]
            res_rot = resample_and_normalize_sample({'strokes': rot_strokes})
            X_train_list.append(extract_reversal_kinematic_features(res_rot))
            y_char_train_list.append(c_idx)
            y_rev_train_list.append(1.0)

# -----------------------------------------------------------------------------
# BUILD VALIDATION TENSORS (100% PURE AUTHENTIC HOLDOUT, ZERO AUGMENTATION)
# -----------------------------------------------------------------------------
X_val_list, y_char_val_list, y_rev_val_list = [], [], []

for s in val_samples:
    lbl = s['label']
    c_idx = CHAR_TO_IDX[lbl]
    res_val = resample_and_normalize_sample(s)
    X_val_list.append(extract_reversal_kinematic_features(res_val))
    y_char_val_list.append(c_idx)
    y_rev_val_list.append(1.0 if s['is_atypical'] else 0.0)

X_train = np.array(X_train_list, dtype=np.float32)
y_char_train = np.array(y_char_train_list, dtype=np.int32)
y_rev_train = np.array(y_rev_train_list, dtype=np.float32).reshape(-1, 1)

X_val = np.array(X_val_list, dtype=np.float32)
y_char_val = np.array(y_char_val_list, dtype=np.int32)
y_rev_val = np.array(y_rev_val_list, dtype=np.float32).reshape(-1, 1)

print("Tensors constructed successfully:")
print(f"  Training Set:   X={X_train.shape}, y_char={y_char_train.shape}, y_rev={y_rev_train.shape}")
print(f"    -> Authentic (0.0): {np.sum(y_rev_train == 0.0)} | Reversed/Atypical (1.0): {np.sum(y_rev_train == 1.0)}")
print(f"  Validation Set: X={X_val.shape}, y_char={y_char_val.shape}, y_rev={y_rev_val.shape}")
print(f"    -> Authentic (0.0): {np.sum(y_rev_val == 0.0)} | Reversed/Atypical (1.0): {np.sum(y_rev_val == 1.0)}")
"""

# Markdown: 10.2 Model Architecture (Cell 24)
c24_md = """### 10.2 Centralized Architecture Compilation & Dynamic Training

- **Architecture:** Sourced directly from `build_dhrc_model()` in [`scripts/model_builder.py`](file:///Users/asthiseta/Project/somethinginmyeye/scripts/model_builder.py):
  - Shared feature extractor: 2x Conv1D + BatchNorm + MaxPool + Bidirectional GRU (32 units) + GAP + Dense(64, ReLU) + Dropout(0.3).
  - Head 1 (`char_output`): Dense(52, Softmax) predicting canonical Latin character.
  - Head 2 (`reversal_output`): Dense(1, Sigmoid) predicting clinical reversal risk.
- **Dynamic Training Strategy:** Ceiling 50 epochs with `EarlyStopping(monitor='val_reversal_output_auc', mode='max', patience=10, restore_best_weights=True)` and `ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4)`.
"""

# Code: Dynamic Training (Cell 25)
c25_code = """import os
os.environ['KERAS_HOME'] = '/tmp/keras'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from model_builder import build_dhrc_model
from config import (
    DHRC_SEQ_LEN,
    DHRC_FEATURES,
    DHRC_NUM_CLASSES,
    DHRC_EPOCHS,
    DHRC_BATCH_SIZE,
    DHRC_PATIENCE,
    DHRC_REDUCE_LR_PATIENCE,
    DHRC_MODEL_PATH
)

print("Instantiating DHRC model from centralized model_builder...")
reversal_model = build_dhrc_model(
    seq_len=DHRC_SEQ_LEN,
    num_features=DHRC_FEATURES,
    num_classes=DHRC_NUM_CLASSES
)

callbacks = [
    EarlyStopping(
        monitor='val_reversal_output_auc',
        mode='max',
        patience=DHRC_PATIENCE,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=DHRC_REDUCE_LR_PATIENCE,
        min_lr=1e-5,
        verbose=1
    )
]

print(f"Beginning dynamic training (Ceiling: {DHRC_EPOCHS} epochs, Batch Size: {DHRC_BATCH_SIZE})...")
history = reversal_model.fit(
    X_train,
    {'char_output': y_char_train, 'reversal_output': y_rev_train},
    validation_data=(X_val, {'char_output': y_char_val, 'reversal_output': y_rev_val}),
    epochs=DHRC_EPOCHS,
    batch_size=DHRC_BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

# Plot Training Dynamics
fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))

# Character Head Metrics
axes[0].plot(history.history['char_output_accuracy'], label='Train Accuracy', lw=2)
axes[0].plot(history.history['val_char_output_accuracy'], label='Val Accuracy', lw=2, linestyle='--')
axes[0].set_title('Head 1: Character Classification Accuracy (52 Classes)', fontweight='bold')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Accuracy')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Reversal Head Metrics
axes[1].plot(history.history['reversal_output_auc'], label='Train ROC-AUC', lw=2, color='crimson')
axes[1].plot(history.history['val_reversal_output_auc'], label='Val ROC-AUC', lw=2, linestyle='--', color='darkorange')
axes[1].set_title('Head 2: Clinical Reversal Detection ROC-AUC', fontweight='bold')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('ROC-AUC')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
"""

# Code: Model Serialization & ONNX Export (Cell 26)
c26_code = """import tf2onnx
import onnx
import onnxruntime as ort
from config import DHRC_ONNX_PATH, DHRC_MODEL_PATH

# 1. Save Keras Model
os.makedirs(os.path.dirname(DHRC_MODEL_PATH), exist_ok=True)
reversal_model.save(DHRC_MODEL_PATH)
print(f"Trained Keras model saved to: {DHRC_MODEL_PATH}")

# Also keep scratch backup
os.makedirs("scratch", exist_ok=True)
reversal_model.save("scratch/dual_head_reversal_model.keras")

# 2. Export to ONNX for Web Runtime
input_signature = [
    tf.TensorSpec(shape=(None, DHRC_SEQ_LEN, DHRC_FEATURES), dtype=tf.float32, name="trajectory_input")
]

os.makedirs(os.path.dirname(DHRC_ONNX_PATH), exist_ok=True)
onnx_model, _ = tf2onnx.convert.from_keras(
    reversal_model,
    input_signature=input_signature,
    opset=15,
    output_path=DHRC_ONNX_PATH
)

onnx_size_kb = os.path.getsize(DHRC_ONNX_PATH) / 1024.0
print(f"Exported ONNX model to: {DHRC_ONNX_PATH} ({onnx_size_kb:.2f} KB)")

# 3. Numerical Parity Verification
ort_session = ort.InferenceSession(DHRC_ONNX_PATH)
test_input = np.random.randn(4, DHRC_SEQ_LEN, DHRC_FEATURES).astype(np.float32)

keras_preds = reversal_model.predict(test_input, verbose=0)
input_name = ort_session.get_inputs()[0].name
ort_preds = ort_session.run(None, {input_name: test_input})

# Handle output dictionary alignment
if ort_preds[0].shape[-1] == DHRC_NUM_CLASSES:
    ort_char, ort_rev = ort_preds[0], ort_preds[1]
else:
    ort_rev, ort_char = ort_preds[0], ort_preds[1]

diff_char = np.max(np.abs(keras_preds[0] - ort_char))
diff_rev = np.max(np.abs(keras_preds[1] - ort_rev))
print(f"ONNX Parity Difference: Character Max Diff = {diff_char:.2e}, Reversal Max Diff = {diff_rev:.2e}")
assert diff_char < 1e-4 and diff_rev < 1e-4, "ONNX numerical parity check failed!"
print("ONNX numerical parity verified successfully.")
"""

# Markdown: 10.3 Evaluation Metrics (Cell 27)
c27_md = """### 10.3 Quantitative Evaluation & Reversal Detection Metrics

Evaluates Head 1 (character accuracy) and Head 2 (reversal discriminability) on the held-out validation cohort (`dhrc_val_datasets/`).
"""

# Code: Quantitative Evaluation & Metrics (Cell 28)
c28_code = """from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

print("Evaluating Dual-Head Model on Pure Validation Set...")
val_preds = reversal_model.predict(X_val, verbose=0)
char_probs = val_preds[0]
rev_probs = val_preds[1].ravel()

# Head 1: Character Classification
char_preds_top1 = np.argmax(char_probs, axis=1)
top1_acc = np.mean(char_preds_top1 == y_char_val) * 100.0

top3_correct = 0
for i in range(len(y_char_val)):
    top3_idx = np.argsort(char_probs[i])[-3:]
    if y_char_val[i] in top3_idx:
        top3_correct += 1
top3_acc = (top3_correct / len(y_char_val)) * 100.0

# Head 2: Reversal Detection
rev_preds = (rev_probs >= 0.50).astype(int)
rev_auc = roc_auc_score(y_rev_val, rev_probs)
cm = confusion_matrix(y_rev_val, rev_preds)

print("=" * 65)
print("             DUAL-HEAD REVERSAL CLASSIFIER EVALUATION             ")
print("=" * 65)
print(f"Head 1 (Character Softmax - 52 Classes):")
print(f"  -> Top-1 Accuracy: {top1_acc:.2f}%")
print(f"  -> Top-3 Accuracy: {top3_acc:.2f}%")
print("-" * 65)
print(f"Head 2 (Clinical Reversal Detection):")
print(f"  -> ROC-AUC Score:  {rev_auc:.4f}")
print(f"  -> Confusion Matrix:\\n{cm}")
print("-" * 65)
print("Reversal Classification Report:")
print(classification_report(y_rev_val, rev_preds, target_names=['Authentic (0)', 'Reversed (1)']))
print("=" * 65)

# Visual Confusion Matrix
fig, ax = plt.subplots(figsize=(5, 4.2))
im = ax.imshow(cm, cmap='Blues', interpolation='nearest')
plt.colorbar(im, ax=ax)
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(['Authentic (0)', 'Reversed (1)'], fontsize=10, fontweight='bold')
ax.set_yticklabels(['Authentic (0)', 'Reversed (1)'], fontsize=10, fontweight='bold')
ax.set_xlabel('Predicted Label', fontweight='bold')
ax.set_ylabel('True Clinical Label', fontweight='bold')
ax.set_title('Reversal Detection Confusion Matrix (Val Holdout)', fontweight='bold', pad=10)

# Annotate values
for i in range(2):
    for j in range(2):
        text_color = "white" if cm[i, j] > cm.max() / 2 else "black"
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=text_color, fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()
"""

# Markdown: 10.4 Interactive Stroke Tester (Cell 29)
c29_md = """### 10.4 Interactive Stroke Tester & Single-Sample Verification

Inspects individual tablet recordings or live strokes through the trained dual-head model.
"""

# Code: Interactive Single-Sample Inference (Cell 30)
c30_code = """def test_sample_inference(sample: Dict[str, Any], model_instance=reversal_model):
    \"\"\"Evaluates a single sample and plots its trajectory with dual-head prediction results.\"\"\"
    res = resample_and_normalize_sample(sample)
    feats = extract_reversal_kinematic_features(res)
    inp = np.expand_dims(feats, axis=0)
    
    preds = model_instance.predict(inp, verbose=0)
    char_probs = preds[0][0]
    rev_prob = float(preds[1][0][0])
    
    top3_idx = np.argsort(char_probs)[-3:][::-1]
    top3_results = [(VOCABULARY[idx], float(char_probs[idx])) for idx in top3_idx]
    
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    color_map = "Reds" if rev_prob >= 0.50 else "Greens"
    plot_strokes_with_trajectory(ax, sample['strokes'], f"Sample: '{sample.get('label')}'", color_map)
    
    rev_tag = "[REVERSED]" if rev_prob >= 0.50 else "[NORMAL]"
    candidates_str = ", ".join([f"'{c}': {p*100:.1f}%" for c, p in top3_results])
    
    plt.suptitle(
        f"Reversal Prob: {rev_prob*100:.1f}% {rev_tag}\\nTop Candidates: {candidates_str}",
        fontsize=11,
        fontweight='bold',
        y=0.98
    )
    plt.tight_layout()
    plt.show()

# Test on representative holdout samples
test_samples = [s for s in val_samples if s['label'] in ['b', 'd', 'p', 'q', 'S']][:2]
for s in test_samples:
    test_sample_inference(s)
"""

def make_cell(cell_type: str, source_text: str):
    lines = [line + "\n" for line in source_text.split("\n")]
    if lines and lines[-1] == "\n":
        lines[-1] = ""
    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": lines
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell

new_section_cells = [
    make_cell("markdown", c19_md),
    make_cell("code", c20_code),
    make_cell("code", c21_code),
    make_cell("markdown", c22_md),
    make_cell("code", c23_code),
    make_cell("markdown", c24_md),
    make_cell("code", c25_code),
    make_cell("code", c26_code),
    make_cell("markdown", c27_md),
    make_cell("code", c28_code),
    make_cell("markdown", c29_md),
    make_cell("code", c30_code),
]

# Preserve cells before index 19 and cells after index 30 (sandbox/scratchpad)
cells_before = nb["cells"][:19]
cells_after = nb["cells"][31:]

nb["cells"] = cells_before + new_section_cells + cells_after

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Successfully updated {NOTEBOOK_PATH}. New total cell count: {len(nb['cells'])}.")
