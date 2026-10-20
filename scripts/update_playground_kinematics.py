#!/usr/bin/env python3
"""
Updates Sections 0 through 8 of playground.ipynb for:
- End-to-end training and comparative evaluation of V0, V1, and V2
- Zero-leakage global scaling on elkinematics_train_datasets/
- Strict physical holdout evaluation on elkinematics_val_datasets/
- Side-by-side comparative validation leaderboard, ROC curves, and confusion matrices
"""

import json
import os
import sys

NOTEBOOK_PATH = "playground.ipynb"

with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 0: TOC
c0_md = """# Elkinematics Research and Experimentation Playground

This notebook serves as the central interactive sandbox, training ground, and staging pipeline for the Elkinematics multi-dimensional Specific Learning Disorder (SLD) screening suite.

### Workflow Sections:
1. **Environment and Centralized Configuration** - Load paths and hyperparameters from `scripts/config.py`.
2. **Centralized Model Builder and Architecture Summary** - Inspect V0 (Baseline CNN), V1 (CNN+XAI), and V2 (Bi-LSTM).
3. **Full Kinematic Battery Dataset Profiling** - Census and balance of `elkinematics_train_datasets/` and `elkinematics_val_datasets/`.
4. **Kinematic Feature Extraction** - Extract the 8 standard kinematic features (`delta_x`, `delta_y`, `pressure`, `tiltX`, `tiltY`, `velocity`, `acceleration`, `jerk`) and `latency`.
5. **Zero-Leakage Global Scaling & Multi-Model Input Formatting** - Compute training scalers and prepare tensor inputs for V0, V1, and V2.
6. **End-to-End Model Training Suite** - Train V0, V1, and V2 with early stopping, dynamic learning rate reduction, and comparative loss curves.
7. **Inference & Explainable AI (XAI) Timestep Heatmaps** - Predict risk scores and render stroke-level anomaly heatmaps.
8. **Comparative Validation Leaderboard & Diagnostic Metrics** - Accuracy, Recall, Specificity, F1-Score, ROC-AUC curves, and Confusion Matrices across all iterations.
9. **Multi-Stream Specific Learning Disorder (SLD) Differential Screening** - Rule out or differentiate Motor Dysgraphia, Spatial Dysgraphia, and Dyslexic Dysgraphia.
10. **In-House Isolated Dual-Head Reversal Classifier (DHRC)** - Isolated character recognition and clinical mirror reversal detection.
11. **Interactive Sandbox / Scratchpad** - Free-form scratchpad.
"""

# Cell 1: Section 1 Header
c1_md = "## 1. Environment and Centralized Configuration"

# Cell 2: Section 1 Code
c2_code = """import sys
import os
from pathlib import Path

# Ensure project root and scripts directory are accessible
PROJECT_ROOT = Path(os.getcwd()).resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for p in [str(SCRIPTS_DIR), str(PROJECT_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

import config

print(f"Project Root                : {config.PROJECT_ROOT}")
print(f"Max Timesteps               : {config.MAX_TIMESTEPS} (Resampling: {config.SAMPLING_RATE_HZ} Hz)")
print(f"Kinematic Features          : {config.FEATURES} features + {config.LATENCY_DIM} latency scalar")
print(f"Baseline V0 Features        : {config.V0_FEATURES} features (velocity, dt, pressure)")
print(f"Elkinematics Train Cohort   : {config.ELKINEMATICS_TRAIN_DIR}")
print(f"Elkinematics Val Cohort     : {config.ELKINEMATICS_VAL_DIR}")
print(f"Model V0 Target Path        : {config.MODEL_PATHS['v0']}")
print(f"Model V1 Target Path        : {config.MODEL_PATHS['v1']}")
print(f"Model V2 Target Path        : {config.MODEL_PATHS['v2']}")
print(f"Feature Scalers Target Path : {config.SCALER_PATH}")
"""

# Cell 3: Section 2 Header
c3_md = """## 2. Centralized Model Builder and Architecture Summary
Centralized architectures compiled from `scripts/model_builder.py` representing three progressive research iterations:
1. **V0 (Baseline 1D-CNN):** Global spatial feature extraction on 3 baseline features (`velocity, dt, pressure`).
2. **V1 (CNN + XAI TimeDistributed):** Dual-input architecture fusing temporal CNN features with static cognitive initiation latency.
3. **V2 (Bi-LSTM Flagship):** Dual-input Bidirectional LSTM processing the full 8 standard kinematic features + latency for fine-grained millisecond anomaly tracking.
"""

# Cell 4: Section 2 Code
c4_code = """from model_builder import build_v0_baseline, build_v1_xai, build_v2_bilstm

print("Compiling Model Iterations from Centralized Model Builder...")
model_v0 = build_v0_baseline(learning_rate=config.LEARNING_RATE)
model_v1 = build_v1_xai(learning_rate=config.LEARNING_RATE)
model_v2 = build_v2_bilstm(learning_rate=config.LEARNING_RATE)

arch_summary = [
    {
        "Iteration": "V0 (Baseline CNN)",
        "Input Shape": f"({config.MAX_TIMESTEPS}, {config.V0_FEATURES})",
        "Output": "Binary Scalar (Sigmoid)",
        "Parameters": f"{model_v0.count_params():,}"
    },
    {
        "Iteration": "V1 (CNN + XAI)",
        "Input Shape": f"[({config.MAX_TIMESTEPS}, {config.V0_FEATURES}), (1,)]",
        "Output": f"TimeDistributed Heatmap ({config.MAX_TIMESTEPS}, 1)",
        "Parameters": f"{model_v1.count_params():,}"
    },
    {
        "Iteration": "V2 (Bi-LSTM Flagship)",
        "Input Shape": f"[({config.MAX_TIMESTEPS}, {config.FEATURES}), (1,)]",
        "Output": f"TimeDistributed Heatmap ({config.MAX_TIMESTEPS}, 1)",
        "Parameters": f"{model_v2.count_params():,}"
    }
]

print("\\n" + "=" * 80)
print(f"{'Iteration':<24} | {'Input Shape':<28} | {'Output':<25} | {'Params':<10}")
print("=" * 80)
for row in arch_summary:
    print(f"{row['Iteration']:<24} | {row['Input Shape']:<28} | {row['Output']:<25} | {row['Parameters']:<10}")
print("=" * 80)
"""

# Cell 5: Section 3 Header
c5_md = """## 3. Data Loading and Discovery
Profiles the physical training and validation cohorts populated by `scripts/setup_training_datasets.py`:
- `elkinematics_train_datasets/`: Complete hierarchical handwriting battery (letters, words, pseudowords, multisyllabic words, standardized sentences).
- `elkinematics_val_datasets/`: Frozen clinical validation holdout.
- Strictly Latin alphabet (zero digits) per DSM-5 Specific Learning Disorder standards.
"""

# Cell 6: Section 3 Code
c6_code = """import glob

train_files = sorted(glob.glob(os.path.join(config.ELKINEMATICS_TRAIN_DIR, "*.csv")))
val_files = sorted(glob.glob(os.path.join(config.ELKINEMATICS_VAL_DIR, "*.csv")))

train_normal = [f for f in train_files if "normal" in os.path.basename(f).lower()]
train_atypical = [f for f in train_files if ("dyslexia" in os.path.basename(f).lower() or "dysgraphia" in os.path.basename(f).lower())]

val_normal = [f for f in val_files if "normal" in os.path.basename(f).lower()]
val_atypical = [f for f in val_files if ("dyslexia" in os.path.basename(f).lower() or "dysgraphia" in os.path.basename(f).lower())]

print("=" * 65)
print("ELKINEMATICS KINEMATIC BATTERY COHORT CENSUS")
print("=" * 65)
print(f"Training Cohort   : {len(train_files):4d} recordings (Normal: {len(train_normal):4d}, Atypical: {len(train_atypical):4d})")
print(f"Validation Cohort : {len(val_files):4d} recordings (Normal: {len(val_normal):4d}, Atypical: {len(val_atypical):4d})")
print(f"Total Cohort Size : {len(train_files) + len(val_files):4d} recordings")
print("=" * 65)

# Visual Distribution Chart
fig, ax = plt.subplots(figsize=(8, 3.5))
categories = ["Training Cohort", "Validation Cohort"]
normal_counts = [len(train_normal), len(val_normal)]
atypical_counts = [len(train_atypical), len(val_atypical)]

x = np.arange(len(categories))
width = 0.35

ax.bar(x - width/2, normal_counts, width, label="Typical / Normal", color="#2b5c8f")
ax.bar(x + width/2, atypical_counts, width, label="Atypical / Dysgraphic", color="#c44e52")

ax.set_ylabel("Number of Recordings")
ax.set_title("Kinematic Battery Dataset Distribution (Strict Physical Holdout)")
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend(frameon=True)
ax.grid(axis="y", linestyle="--", alpha=0.5)

for i in range(len(categories)):
    ax.text(x[i] - width/2, normal_counts[i] + 15, str(normal_counts[i]), ha="center", fontsize=9, fontweight="bold")
    ax.text(x[i] + width/2, atypical_counts[i] + 15, str(atypical_counts[i]), ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.show()
"""

# Cell 7: Section 4 Header
c7_md = """## 4. Kinematic Feature Extraction (8 Kinematic Features & Latency)
Extracts velocity-invariant physical and kinematic derivatives:
- Resamples continuous on-surface strokes to a uniform 60 Hz grid ($\Delta t = 16.67\\text{ ms}$).
- Calculates: $[\\Delta x, \\Delta y, \\text{pressure}, \\text{tiltX}, \\text{tiltY}, \\text{velocity}, \\text{acceleration}, \\text{jerk}]$.
- Preserves prompt-to-first-stroke cognitive latency as a distinct secondary scalar.
"""

# Cell 8: Section 4 Code
c8_code = """from universal_pipeline import extract_universal_features

# Inspect feature extraction on a benchmark sample
test_sample = train_files[0] if train_files else os.path.join(config.SAMPLE_DIR, "sample_normal.csv")
sample_df = pd.read_csv(test_sample)

features_matrix = extract_universal_features(sample_df, resample=True)
print(f"Sample File           : {os.path.basename(test_sample)}")
print(f"Raw Trajectory Events : {len(sample_df)} points")
print(f"Resampled Matrix      : {features_matrix.shape} (Timesteps x Features)")
print(f"Feature Columns (8+1) : {config.FEATURE_NAMES + ['dt']}")

# Display feature statistics
features_df = pd.DataFrame(features_matrix, columns=config.FEATURE_NAMES + ["dt"])
display(features_df.describe().T[["mean", "std", "min", "max"]])
"""

# Cell 9: Section 5 Header
c9_md = """## 5. Zero-Leakage Global Scaling & Multi-Model Input Formatting
Transforms raw kinematic sequences with strict physical separation:
1. **Fit Scalers on Training Cohort Only:** Computes global Z-score parameters ($\mu, \sigma$) across `elkinematics_train_datasets/` and saves to `models/feature_scalers.npz`.
2. **Transform Validation Cohort with Frozen Scalers:** Normalizes `elkinematics_val_datasets/` without computing statistics, completely eliminating data leakage.
3. **Format Model Input Tensors:**
   - **V0:** `X_v0 = [velocity, dt, pressure]` $\\rightarrow$ shape `(N, 500, 3)`, target shape `(N, 1)`.
   - **V1:** `[X_v1_seq, X_v1_lat]` $\\rightarrow$ shapes `(N, 500, 3)` and `(N, 1)`, target shape `(N, 500, 1)`.
   - **V2:** `[X_v2_seq, X_v2_lat]` $\\rightarrow$ shapes `(N, 500, 8)` and `(N, 1)`, target shape `(N, 500, 1)`.
"""

# Cell 10: Section 5 Code
c10_code = """from universal_pipeline import (
    load_and_scale_universal,
    load_validation_with_train_scalers,
    get_v0_data,
    get_v1_data,
    get_v2_data
)

# 1. Load and compute global scalers on training data
print("Processing Training Cohort (Computing Global Scalers)...")
X_train_seq_scaled, X_train_lat_scaled, y_train = load_and_scale_universal(
    data_dir=config.ELKINEMATICS_TRAIN_DIR,
    scaler_save_path=config.SCALER_PATH,
    resample=True
)

# 2. Transform validation cohort using frozen training scalers (Strict Hold-Out, Zero Leakage)
print("Processing Validation Cohort (Using Frozen Scalers)...")
X_val_seq_scaled, X_val_lat_scaled, y_val = load_validation_with_train_scalers(
    data_dir=config.ELKINEMATICS_VAL_DIR,
    scaler_path=config.SCALER_PATH,
    resample=True
)

# 3. Format inputs for V0 Baseline (3 features: velocity, dt, pressure)
X_train_v0, y_train_v0 = get_v0_data(X_train_seq_scaled, y_train)
X_val_v0, y_val_v0 = get_v0_data(X_val_seq_scaled, y_val)

# 4. Format inputs for V1 (3 features + Latency, TimeDistributed target)
[X_train_v1_seq, X_train_v1_lat], y_train_v1_td = get_v1_data(X_train_seq_scaled, X_train_lat_scaled, y_train)
[X_val_v1_seq, X_val_v1_lat], y_val_v1_td = get_v1_data(X_val_seq_scaled, X_val_lat_scaled, y_val)

# 5. Format inputs for V2 Flagship (8 standard features + Latency, TimeDistributed target)
[X_train_v2_seq, X_train_v2_lat], y_train_v2_td = get_v2_data(X_train_seq_scaled, X_train_lat_scaled, y_train)
[X_val_v2_seq, X_val_v2_lat], y_val_v2_td = get_v2_data(X_val_seq_scaled, X_val_lat_scaled, y_val)

print("\\n" + "=" * 65)
print("FORMATTED MULTI-MODEL INPUT TENSORS")
print("=" * 65)
print(f"V0 Train Input : {X_train_v0.shape} | Target: {y_train_v0.shape}")
print(f"V0 Val Input   : {X_val_v0.shape} | Target: {y_val_v0.shape}")
print("-" * 65)
print(f"V1 Train Seq   : {X_train_v1_seq.shape} | Lat: {X_train_v1_lat.shape} | Target: {y_train_v1_td.shape}")
print(f"V1 Val Seq     : {X_val_v1_seq.shape} | Lat: {X_val_v1_lat.shape} | Target: {y_val_v1_td.shape}")
print("-" * 65)
print(f"V2 Train Seq   : {X_train_v2_seq.shape} | Lat: {X_train_v2_lat.shape} | Target: {y_train_v2_td.shape}")
print(f"V2 Val Seq     : {X_val_v2_seq.shape} | Lat: {X_val_v2_lat.shape} | Target: {y_val_v2_td.shape}")
print("=" * 65)
"""

# Cell 11: Section 6 Header
c11_md = """## 6. End-to-End Model Training Suite (V0 Baseline, V1 CNN+XAI, V2 Bi-LSTM)
Trains all three model generations sequentially using dynamic regularization:
- **Optimization:** Adam optimizer with initial learning rate $\eta = 10^{-3}$.
- **Callbacks:**
  - `EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)`: Halts training on convergence and restores optimal weights.
  - `ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)`: Dynamically shrinks step size upon plateau.
- **Model Checkpointing:** Saves trained binaries to `models/elkinematic.keras`, `models/elkinematicV1.keras`, and `models/elkinematicV2.keras`.
"""

# Cell 12: Section 6 Code
c12_code = """import os
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

os.makedirs(config.MODEL_DIR, exist_ok=True)

# Helper function to generate standardized callbacks
def get_callbacks(model_name: str):
    return [
        EarlyStopping(
            monitor="val_loss",
            patience=config.EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=config.REDUCE_LR_PATIENCE,
            min_lr=config.MIN_LR,
            verbose=1
        )
    ]

# -----------------------------------------------------------------------------
# 1. TRAIN MODEL V0 (BASELINE 1D-CNN)
# -----------------------------------------------------------------------------
print("\\n" + "=" * 65)
print("TRAINING ITERATION 1: MODEL V0 (BASELINE 1D-CNN)")
print("=" * 65)
model_v0 = build_v0_baseline(learning_rate=config.LEARNING_RATE)
history_v0 = model_v0.fit(
    X_train_v0, y_train_v0,
    validation_data=(X_val_v0, y_val_v0),
    epochs=config.EPOCHS,
    batch_size=config.BATCH_SIZE,
    callbacks=get_callbacks("V0"),
    verbose=1
)
model_v0.save(config.MODEL_PATHS["v0"])
print(f"Saved Model V0 weights to: {config.MODEL_PATHS['v0']}")

# -----------------------------------------------------------------------------
# 2. TRAIN MODEL V1 (CNN + XAI TIMEDISTRIBUTED)
# -----------------------------------------------------------------------------
print("\\n" + "=" * 65)
print("TRAINING ITERATION 2: MODEL V1 (CNN + XAI TIMEDISTRIBUTED)")
print("=" * 65)
model_v1 = build_v1_xai(learning_rate=config.LEARNING_RATE)
history_v1 = model_v1.fit(
    [X_train_v1_seq, X_train_v1_lat], y_train_v1_td,
    validation_data=([X_val_v1_seq, X_val_v1_lat], y_val_v1_td),
    epochs=config.EPOCHS,
    batch_size=config.BATCH_SIZE,
    callbacks=get_callbacks("V1"),
    verbose=1
)
model_v1.save(config.MODEL_PATHS["v1"])
print(f"Saved Model V1 weights to: {config.MODEL_PATHS['v1']}")

# -----------------------------------------------------------------------------
# 3. TRAIN MODEL V2 (FLAGSHIP BI-LSTM + 8 KINEMATIC FEATURES)
# -----------------------------------------------------------------------------
print("\\n" + "=" * 65)
print("TRAINING ITERATION 3: MODEL V2 (FLAGSHIP BI-LSTM)")
print("=" * 65)
model_v2 = build_v2_bilstm(learning_rate=config.LEARNING_RATE)
history_v2 = model_v2.fit(
    [X_train_v2_seq, X_train_v2_lat], y_train_v2_td,
    validation_data=([X_val_v2_seq, X_val_v2_lat], y_val_v2_td),
    epochs=config.EPOCHS,
    batch_size=config.BATCH_SIZE,
    callbacks=get_callbacks("V2"),
    verbose=1
)
model_v2.save(config.MODEL_PATHS["v2"])
print(f"Saved Model V2 weights to: {config.MODEL_PATHS['v2']}")

# -----------------------------------------------------------------------------
# 4. PLOT COMPARATIVE TRAINING DYNAMICS
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 4.5), sharey=True)

for ax, hist, title, color in zip(
    axes,
    [history_v0, history_v1, history_v2],
    ["V0: Baseline 1D-CNN", "V1: CNN + XAI", "V2: Flagship Bi-LSTM"],
    ["#1f77b4", "#ff7f0e", "#2ca02c"]
):
    ax.plot(hist.history["loss"], label="Train Loss", color=color, linewidth=2)
    ax.plot(hist.history["val_loss"], label="Val Loss", color=color, linestyle="--", linewidth=2)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Binary Crossentropy Loss")
    ax.legend(frameon=True)
    ax.grid(True, linestyle=":", alpha=0.6)

plt.suptitle("Comparative Training Dynamics across Architectural Iterations", fontsize=14, y=1.02)
plt.tight_layout()
plt.show()
"""

# Cell 13: Section 7 Header
c13_md = """## 7. Inference and Explainable AI (XAI) Heatmap Inspection
Loads production trained Model V2 and demonstrates millisecond-resolution Explainable AI (XAI) risk heatmap generation:
- Displays point-by-point dysgraphic anomaly risk across the handwriting trajectory.
- Contrasts typical smooth kinematic rhythm against atypical motor tremors and stalls.
"""

# Cell 14: Section 7 Code
c14_code = """from universal_pipeline import unified_predict

# Load newly trained production model
prod_model = tf.keras.models.load_model(config.MODEL_PATHS["v2"])

# Find representative normal and atypical test samples
sample_normal_path = os.path.join(config.SAMPLE_DIR, "sample_normal.csv")
if not os.path.exists(sample_normal_path):
    normal_candidates = [f for f in val_files if "normal" in os.path.basename(f).lower()]
    sample_normal_path = normal_candidates[0] if normal_candidates else None

atypical_candidates = [f for f in val_files if ("dyslexia" in os.path.basename(f).lower() or "dysgraphia" in os.path.basename(f).lower())]
sample_atypical_path = atypical_candidates[0] if atypical_candidates else None

samples_to_inspect = []
if sample_normal_path:
    samples_to_inspect.append(("Typical / Normal", sample_normal_path))
if sample_atypical_path:
    samples_to_inspect.append(("Atypical / Dysgraphic", sample_atypical_path))

fig, axes = plt.subplots(len(samples_to_inspect), 1, figsize=(12, 3.5 * len(samples_to_inspect)), squeeze=False)

for idx, (label_type, file_path) in enumerate(samples_to_inspect):
    df_sample = pd.read_csv(file_path)
    score, heatmap = unified_predict(df_sample, prod_model, version="v2", scaler_path=config.SCALER_PATH)
    
    ax = axes[idx, 0]
    effective_len = min(len(df_sample), len(heatmap))
    ax.plot(heatmap[:effective_len], color="#d62728" if score > 0.5 else "#1f77b4", linewidth=2, label="Point Anomaly Risk")
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1.5, label="Diagnostic Threshold (0.50)")
    ax.fill_between(range(effective_len), 0, heatmap[:effective_len], alpha=0.15, color="#d62728" if score > 0.5 else "#1f77b4")
    
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(f"Sample: {os.path.basename(file_path)} [{label_type}] | Composite Risk: {score:.4f} -> {'Atypical / Dysgraphic' if score > 0.5 else 'Typical / Normal'}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Stroke Timestep (Resampled @ 60 Hz)")
    ax.set_ylabel("Dysgraphia Probability")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.show()
"""

# Cell 15: Section 8 Header
c15_md = """## 8. Comparative Validation Leaderboard & Diagnostic Metrics
Evaluates all three models on the strict validation cohort (`elkinematics_val_datasets/`, 340 samples: 223 Typical, 117 Atypical):
- Compares V0 (Baseline CNN), V1 (CNN+XAI), and V2 (Bi-LSTM).
- Computes: Accuracy, Sensitivity (Recall), Specificity, Precision, F1-Score, and ROC-AUC.
- Generates side-by-side ROC curves and Confusion Matrices.
"""

# Cell 16: Section 8 Code
c16_code = """from sklearn.metrics import (
    accuracy_score,
    recall_score,
    precision_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    ConfusionMatrixDisplay
)

# Load trained models from disk
eval_v0 = tf.keras.models.load_model(config.MODEL_PATHS["v0"])
eval_v1 = tf.keras.models.load_model(config.MODEL_PATHS["v1"])
eval_v2 = tf.keras.models.load_model(config.MODEL_PATHS["v2"])

# Generate validation predictions
# V0: Scalar output (N, 1)
preds_v0_raw = eval_v0.predict(X_val_v0, verbose=0)
scores_v0 = preds_v0_raw[:, 0]

# V1: TimeDistributed output (N, 500, 1) -> aggregate sequence score
preds_v1_raw = eval_v1.predict([X_val_v1_seq, X_val_v1_lat], verbose=0)
scores_v1 = np.mean(preds_v1_raw[:, :, 0], axis=1)

# V2: TimeDistributed output (N, 500, 1) -> aggregate sequence score
preds_v2_raw = eval_v2.predict([X_val_v2_seq, X_val_v2_lat], verbose=0)
scores_v2 = np.mean(preds_v2_raw[:, :, 0], axis=1)

models_eval_data = [
    ("V0 Baseline CNN", scores_v0, eval_v0),
    ("V1 CNN + XAI", scores_v1, eval_v1),
    ("V2 Bi-LSTM Flagship", scores_v2, eval_v2),
]

# Calculate classification metrics
metrics_table = []
for name, scores, _ in models_eval_data:
    binary_preds = (scores >= config.CLASSIFICATION_THRESHOLD).astype(int)
    cm = confusion_matrix(y_val, binary_preds)
    tn, fp, fn, tp = cm.ravel()
    
    acc = accuracy_score(y_val, binary_preds)
    rec = recall_score(y_val, binary_preds)       # Sensitivity (TPR)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0  # Specificity (TNR)
    prec = precision_score(y_val, binary_preds, zero_division=0)
    f1 = f1_score(y_val, binary_preds, zero_division=0)
    auc = roc_auc_score(y_val, scores)
    
    metrics_table.append({
        "Model": name,
        "Accuracy": acc,
        "Sensitivity": rec,
        "Specificity": spec,
        "Precision": prec,
        "F1-Score": f1,
        "ROC-AUC": auc
    })

# Render Formatted ASCII Leaderboard
print("\\n" + "=" * 90)
print("ELKINEMATICS ARCHITECTURAL PROGRESSION: VALIDATION LEADERBOARD")
print("=" * 90)
print(f"{'Model':<22} | {'Accuracy':<10} | {'Sensitivity':<11} | {'Specificity':<11} | {'Precision':<10} | {'F1-Score':<10} | {'ROC-AUC':<9}")
print("-" * 90)
for m in metrics_table:
    print(
        f"{m['Model']:<22} | "
        f"{m['Accuracy']*100:>9.2f}% | "
        f"{m['Sensitivity']*100:>10.2f}% | "
        f"{m['Specificity']*100:>10.2f}% | "
        f"{m['Precision']*100:>9.2f}% | "
        f"{m['F1-Score']*100:>9.2f}% | "
        f"{m['ROC-AUC']:>9.4f}"
    )
print("=" * 90)

# Multi-Panel Visual Evaluation: ROC Curves & Confusion Matrices
fig = plt.figure(figsize=(18, 5))
gs = fig.add_gridspec(1, 4, width_ratios=[1.2, 1, 1, 1])

# Panel 1: Combined ROC Curves
ax_roc = fig.add_subplot(gs[0, 0])
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
for (name, scores, _), color, m in zip(models_eval_data, colors, metrics_table):
    fpr, tpr, _ = roc_curve(y_val, scores)
    ax_roc.plot(fpr, tpr, label=f"{name} (AUC = {m['ROC-AUC']:.3f})", color=color, linewidth=2)

ax_roc.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1)
ax_roc.set_xlim([-0.02, 1.02])
ax_roc.set_ylim([-0.02, 1.05])
ax_roc.set_xlabel("False Positive Rate (1 - Specificity)")
ax_roc.set_ylabel("True Positive Rate (Sensitivity)")
ax_roc.set_title("Validation ROC Curves Comparison", fontsize=11, fontweight="bold")
ax_roc.legend(loc="lower right", frameon=True, fontsize=9)
ax_roc.grid(True, linestyle=":", alpha=0.6)

# Panels 2-4: Confusion Matrices
for idx, (name, scores, _) in enumerate(models_eval_data):
    ax_cm = fig.add_subplot(gs[0, idx + 1])
    b_preds = (scores >= config.CLASSIFICATION_THRESHOLD).astype(int)
    cm = confusion_matrix(y_val, b_preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Typical", "Atypical"])
    disp.plot(ax=ax_cm, cmap="Blues", colorbar=False)
    ax_cm.set_title(f"{name}\\nConfusion Matrix", fontsize=10, fontweight="bold")

plt.tight_layout()
plt.show()
"""

# Map to notebook cells
def set_cell(idx, ctype, source_text):
    lines = [l + "\n" for l in source_text.splitlines()]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    nb["cells"][idx]["cell_type"] = ctype
    nb["cells"][idx]["source"] = lines
    if ctype == "code":
        nb["cells"][idx]["outputs"] = []
        nb["cells"][idx]["execution_count"] = None

set_cell(0, "markdown", c0_md)
set_cell(1, "markdown", c1_md)
set_cell(2, "code", c2_code)
set_cell(3, "markdown", c3_md)
set_cell(4, "code", c4_code)
set_cell(5, "markdown", c5_md)
set_cell(6, "code", c6_code)
set_cell(7, "markdown", c7_md)
set_cell(8, "code", c8_code)
set_cell(9, "markdown", c9_md)
set_cell(10, "code", c10_code)
set_cell(11, "markdown", c11_md)
set_cell(12, "code", c12_code)
set_cell(13, "markdown", c13_md)
set_cell(14, "code", c14_code)
set_cell(15, "markdown", c15_md)
set_cell(16, "code", c16_code)

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print(f"Successfully updated cells 0-16 in {NOTEBOOK_PATH}")
