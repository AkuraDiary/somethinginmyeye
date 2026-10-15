"""
Appends Dual-Head Feature Extraction, Tensor Construction, and Model Training cells
to Section 11 of playground.ipynb.
"""
import json
import os

NOTEBOOK_PATH = "playground.ipynb"

cell_md_prep = """### 11.2 Dual-Head Kinematic Feature Extraction & Dataset Tensor Construction

This stage converts raw stroke sequences into fixed-size $(64, 8)$ kinematic tensors:
1. **Equidistant Arc-Length Resampling ($T=64$):** Normalizes trajectories into a $[0, 1]$ bounding box while preserving authentic aspect ratios and pen-lift transitions.
2. **Kinematic Feature Channels ($F=8$):**
   $[\Delta x, \Delta y, \cos\\theta, \sin\\theta, \Delta\\theta, a_x, a_y, \\text{pen\\_state}]$.
3. **Data Augmentation:** Horizontal mirror reflection and $180^\\circ$ rotational inversion across all 62 alphanumeric classes (`a-z`, `A-Z`, `0-9`).
"""

cell_code_prep = """import os
import random
import numpy as np
from sklearn.model_selection import train_test_split
from typing import List, Dict, Tuple, Any

# Alphanumeric canonical vocabulary: 62 classes
VOCABULARY = (
    [chr(i) for i in range(ord('a'), ord('z') + 1)] +
    [chr(i) for i in range(ord('A'), ord('Z') + 1)] +
    [str(d) for d in range(10)]
)
CHAR_TO_IDX = {ch: idx for idx, ch in enumerate(VOCABULARY)}

def resample_and_normalize_sample(
    sample: Dict[str, Any], 
    target_len: int = 64
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

print("Building training dataset tensors across 62 alphanumeric classes...")
valid_samples = [s for s in ujipen_samples if s['label'] in CHAR_TO_IDX]

X_all, y_char_all, y_rev_all = [], [], []
for s in valid_samples:
    lbl = s['label']
    c_idx = CHAR_TO_IDX[lbl]
    
    # 1. Authentic Standard Sample (y_rev = 0.0)
    res_auth = resample_and_normalize_sample(s)
    X_all.append(extract_reversal_kinematic_features(res_auth))
    y_char_all.append(c_idx)
    y_rev_all.append(0.0)

    # 2. Horizontal Reflection Augmentation (y_rev = 1.0)
    if lbl in HORIZONTAL_REVERSIBLE_CHARS:
        mir = mirror_sample_horizontal(s)
        res_mir = resample_and_normalize_sample(mir)
        X_all.append(extract_reversal_kinematic_features(res_mir))
        y_char_all.append(c_idx)
        y_rev_all.append(1.0)

    # 3. Rotational 180-degree Inversion Augmentation (y_rev = 1.0)
    if lbl in ROTATIONAL_REVERSIBLE_CHARS or lbl in {'6', '9'}:
        rot = rotate_sample_180(s)
        res_rot = resample_and_normalize_sample(rot)
        X_all.append(extract_reversal_kinematic_features(res_rot))
        y_char_all.append(c_idx)
        y_rev_all.append(1.0)

X_all = np.array(X_all, dtype=np.float32)
y_char_all = np.array(y_char_all, dtype=np.int32)
y_rev_all = np.array(y_rev_all, dtype=np.float32).reshape(-1, 1)

# Stratified 80/20 train/validation split
indices = np.arange(len(X_all))
train_idx, val_idx = train_test_split(indices, test_size=0.20, random_state=42, stratify=y_rev_all)

X_train, X_val = X_all[train_idx], X_all[val_idx]
y_char_train, y_char_val = y_char_all[train_idx], y_char_all[val_idx]
y_rev_train, y_rev_val = y_rev_all[train_idx], y_rev_all[val_idx]

print(f"Dataset constructed successfully:")
print(f"  Training set:   X={X_train.shape}, y_char={y_char_train.shape}, y_rev={y_rev_train.shape}")
print(f"  Validation set: X={X_val.shape}, y_char={y_char_val.shape}, y_rev={y_rev_val.shape}")
print(f"  Reversal distribution: {np.mean(y_rev_all)*100:.1f}% reversed, {(1-np.mean(y_rev_all))*100:.1f}% authentic")
"""

cell_md_train = """### 11.3 Dual-Head Model Architecture Compilation & Training

The architecture uses a compact shared feature extractor followed by two specialized heads:
- **Shared Backbone:** Conv1D (32 filters, $k=5$) $\\to$ BatchNorm $\\to$ MaxPool $\\to$ Conv1D (64 filters, $k=3$) $\\to$ BatchNorm $\\to$ MaxPool $\\to$ Bidirectional GRU (32 units) $\\to$ GlobalAveragePooling1D $\\to$ Dense(64, ReLU) + Dropout(0.3).
- **Head 1 (`char_output`):** Dense(62, Softmax) predicting canonical character identity.
- **Head 2 (`reversal_output`):** Dense(1, Sigmoid) predicting clinical reversal probability.
- **Total parameters:** ~35,000 (~136 KB), fully compatible with browser ONNX runtime.
"""

cell_code_train = """import os
os.environ['KERAS_HOME'] = '/tmp/keras'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

def build_dual_head_model(
    seq_len: int = 64, 
    num_features: int = 8, 
    num_classes: int = 62
) -> Model:
    \"\"\"Constructs the Dual-Head Reversal & Character Recognition Model.\"\"\"
    inputs = layers.Input(shape=(seq_len, num_features), name='trajectory_input')

    # Stage 1: Local Sub-Stroke Spatial Convolution
    x = layers.Conv1D(32, kernel_size=5, padding='same', activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(2)(x)

    # Stage 2: Curvature & Derivative Pattern Extraction
    x = layers.Conv1D(64, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(2)(x)

    # Stage 3: Bidirectional Temporal Dynamics
    x = layers.Bidirectional(layers.GRU(32, return_sequences=True))(x)
    shared = layers.GlobalAveragePooling1D()(x)
    shared = layers.Dense(64, activation='relu')(shared)
    shared = layers.Dropout(0.3)(shared)

    # Head 1: Canonical Character Identity
    char_out = layers.Dense(num_classes, activation='softmax', name='char_output')(shared)

    # Head 2: Clinical Reversal Indicator
    rev_out = layers.Dense(1, activation='sigmoid', name='reversal_output')(shared)

    model = Model(inputs=inputs, outputs=[char_out, rev_out], name='dual_head_reversal_model')
    return model

print("Compiling Dual-Head Reversal Model...")
reversal_model = build_dual_head_model()

reversal_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss={
        'char_output': 'sparse_categorical_crossentropy',
        'reversal_output': 'binary_crossentropy'
    },
    loss_weights={
        'char_output': 1.0,
        'reversal_output': 1.5
    },
    metrics={
        'char_output': ['accuracy'],
        'reversal_output': ['accuracy', tf.keras.metrics.AUC(name='auc')]
    }
)

callbacks = [
    EarlyStopping(monitor='val_reversal_output_auc', mode='max', patience=5, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-5, verbose=1)
]

print("Starting model training (15 epochs)...")
history = reversal_model.fit(
    X_train,
    {'char_output': y_char_train, 'reversal_output': y_rev_train},
    validation_data=(X_val, {'char_output': y_char_val, 'reversal_output': y_rev_val}),
    epochs=15,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)
print("Training completed.")
"""

cell_md_eval = """### 11.4 Quantitative Evaluation & Reversal Detection Metrics

Evaluates both heads on the validation set, computing:
1. Character classification top-1 accuracy.
2. Clinical reversal detection sensitivity, specificity, F1-score, and ROC-AUC.
"""

cell_code_eval = """from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

print("Evaluating Dual-Head Model on Validation Set...")
val_preds = reversal_model.predict(X_val, verbose=0)
char_preds = np.argmax(val_preds[0], axis=1)
rev_probs = val_preds[1].ravel()
rev_preds = (rev_probs >= 0.5).astype(int)

# 1. Character Identity Accuracy
char_acc = np.mean(char_preds == y_char_val) * 100.0

# 2. Reversal Detection Metrics
rev_auc = roc_auc_score(y_rev_val, rev_probs)
cm = confusion_matrix(y_rev_val, rev_preds)

print(f"\\n--- EVALUATION SUMMARY ---")
print(f"Character Identification Accuracy: {char_acc:.2f}% (across 62 classes)")
print(f"Clinical Reversal Detection ROC-AUC: {rev_auc:.4f}")
print(f"\\nConfusion Matrix (Reversal Detection):")
print(f"  True Authentic  (TN): {cm[0, 0]}  | False Reversal (FP): {cm[0, 1]}")
print(f"  False Authentic (FN): {cm[1, 0]}  | True Reversal  (TP): {cm[1, 1]}")
print(f"\\nDetailed Reversal Classification Report:")
print(classification_report(y_rev_val, rev_preds, target_names=['Authentic', 'Reversed']))
"""

def main():
    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)

    clean_cells = []
    in_dual_head = False
    for cell in nb['cells']:
        if cell.get('cell_type') == 'markdown':
            source_text = "".join(cell.get('source', []))
            if "11.2 Dual-Head Kinematic Feature Extraction" in source_text:
                in_dual_head = True
                continue
            elif in_dual_head and source_text.startswith("## ") and not source_text.startswith("### 11."):
                in_dual_head = False
        if not in_dual_head:
            clean_cells.append(cell)

    cells_to_add = [
        {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in cell_md_prep.splitlines()]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in cell_code_prep.splitlines()]},
        {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in cell_md_train.splitlines()]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in cell_code_train.splitlines()]},
        {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in cell_md_eval.splitlines()]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in cell_code_eval.splitlines()]}
    ]

    clean_cells.extend(cells_to_add)
    nb['cells'] = clean_cells

    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)

    print(f"Successfully added Dual-Head cells to {NOTEBOOK_PATH}. Total cells: {len(nb['cells'])}.")

if __name__ == "__main__":
    main()
