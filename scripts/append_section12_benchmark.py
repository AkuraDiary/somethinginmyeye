#!/usr/bin/env python3
"""
Appends Section 12 to playground.ipynb:
End-to-End System Benchmark & Multi-Class DHRC Diagnostic Profiling.
Preserves existing cells (0-33) completely.
Strictly zero-emoji compliant.
"""

import json
import os
import sys

NOTEBOOK_PATH = "playground.ipynb"

with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 34: Markdown Documentation & Academic Citations
c34_md = """## 12. End-to-End System Benchmark & Multi-Class DHRC Diagnostic Profiling

This section executes a comprehensive, academic-grade quantitative evaluation of both the **sequential kinematics models (V0, V1, V2)** and the **in-house Dual-Head Reversal Classifier (DHRC)** on pure held-out validation cohorts, providing publication-ready empirical tables for JISEBI 2024 and IEEE reporting standards.

### 12.1 Academic Grounding & Methodological Attributions
In accordance with peer-reviewed literature from relevant venues:
1. **V0 Baseline 1D-CNN (Temporal Feature Pooling):** Pools localized kinematic derivatives (velocity, dt, pressure) across temporal windows without recurrence overhead (Gemelli et al., *DocEng 2023*; Aldehim et al., *J. Disabil. Res.*, 2024).
2. **V1 CNN + XAI (TimeDistributed Pointwise Saliency):** Applies pointwise temporal 1D convolution to isolate motor disturbance anomalies directly along handwriting trajectories (Ghasemzadeh, *JARAC*, 2026; Pamungkas et al., *JISEBI*, 2026).
3. **V2 Bi-LSTM (Bidirectional Temporal Context):** Models long-range sequential dynamics and velocity micro-tremors from both forward and backward stroke directions (Alevizos et al., *ICECCE 2024*; Brescia et al., *Biomed. Signal Process. Control*, 2026; Rangasrinivasan et al., *SN Comput. Sci.*, 2025).
4. **Kinematic & Latency Biomarkers:** Integrates pen pressure, velocity, acceleration, jerk, and cognitive initiation delay (Asselborn et al., *npj Digit. Med.*, 2018; Kunhoth et al., *Biomed. Signal Process. Control*, 2023; Danna et al., *Sensors*, 2021; Germano & Capellini, *Front. Psychol.*, 2023).
5. **Diagnostic Decision Metrics:** Evaluates Sensitivity, Specificity, Precision, F1-Score, Balanced Accuracy, Matthews Correlation Coefficient (MCC), and Precision-Recall AUC (PR-AUC / Average Precision) alongside Brier Score probability calibration (Sathyanarayanan, 2024; Khedr et al., *IEEE AICCONF*, 2026).
"""

# Cell 35: Code for Kinematics Benchmarking
c35_code = r"""import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from sklearn.metrics import (
    accuracy_score,
    recall_score,
    precision_score,
    f1_score,
    balanced_accuracy_score,
    matthews_corrcoef,
    brier_score_loss,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    auc,
    confusion_matrix
)

# Ensure scripts directory is in sys.path
SCRIPT_DIR = os.path.abspath("scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import config
from universal_pipeline import (
    compute_active_sequence_scores,
    load_validation_with_train_scalers,
    get_v0_data,
    get_v1_data,
    get_v2_data
)

# 1. Ensure validation data and models are loaded
if 'y_val' not in globals() or 'X_val_seq_scaled' not in globals():
    print("Loading validation datasets using precomputed train scalers...")
    X_val_seq_scaled, X_val_lat_scaled, y_val = load_validation_with_train_scalers(config.ELKINEMATICS_VAL_DIR)
    X_val_v0, _ = get_v0_data(X_val_seq_scaled, y_val)
    X_val_v1_seq, X_val_v1_lat, _ = get_v1_data(X_val_seq_scaled, X_val_lat_scaled, y_val)
    X_val_v2_seq, X_val_v2_lat, _ = get_v2_data(X_val_seq_scaled, X_val_lat_scaled, y_val)

if 'eval_v0' not in globals():
    eval_v0 = tf.keras.models.load_model(config.MODEL_PATHS["v0"])
if 'eval_v1' not in globals():
    eval_v1 = tf.keras.models.load_model(config.MODEL_PATHS["v1"])
if 'eval_v2' not in globals():
    eval_v2 = tf.keras.models.load_model(config.MODEL_PATHS["v2"])

# 2. Raw Predictions & Active Masked Scores
preds_v0_raw = eval_v0.predict(X_val_v0, verbose=0)
preds_v1_raw = eval_v1.predict([X_val_v1_seq, X_val_v1_lat], verbose=0)
preds_v2_raw = eval_v2.predict([X_val_v2_seq, X_val_v2_lat], verbose=0)

scores_v0_masked = preds_v0_raw[:, 0]
scores_v1_masked = compute_active_sequence_scores(preds_v1_raw, X_val_seq_scaled, config.SCALER_PATH)
scores_v2_masked = compute_active_sequence_scores(preds_v2_raw, X_val_seq_scaled, config.SCALER_PATH)

# 3. CPU Single-Sample Inference Latency Benchmark (100 iterations)
def benchmark_sample_latency(model, sample_input, iterations=100):
    # Warmup
    for _ in range(5):
        _ = model(sample_input, training=False)
    latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = model(sample_input, training=False)
        latencies.append((time.perf_counter() - t0) * 1000.0)
    return float(np.mean(latencies)), float(np.std(latencies))

sample_v0 = tf.convert_to_tensor(X_val_v0[:1], dtype=tf.float32)
sample_v1 = [tf.convert_to_tensor(X_val_v1_seq[:1], dtype=tf.float32), tf.convert_to_tensor(X_val_v1_lat[:1], dtype=tf.float32)]
sample_v2 = [tf.convert_to_tensor(X_val_v2_seq[:1], dtype=tf.float32), tf.convert_to_tensor(X_val_v2_lat[:1], dtype=tf.float32)]

lat_v0_mean, lat_v0_std = benchmark_sample_latency(eval_v0, sample_v0)
lat_v1_mean, lat_v1_std = benchmark_sample_latency(eval_v1, sample_v1)
lat_v2_mean, lat_v2_std = benchmark_sample_latency(eval_v2, sample_v2)

# 4. Comprehensive Metrics Computation
def evaluate_kinematic_model(model_name, scores, latency_str):
    # ROC and PR curves
    fpr, tpr, threshs_roc = roc_curve(y_val, scores)
    prec_pts, rec_pts, _ = precision_recall_curve(y_val, scores)
    auc_roc = roc_auc_score(y_val, scores)
    auc_pr = auc(rec_pts, prec_pts)
    brier = brier_score_loss(y_val, scores)

    # Optimal Youden threshold
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    opt_thresh = float(threshs_roc[best_idx])

    rows = []
    for mode, tau in [("Default (0.50)", 0.50), ("Calibrated (Youden)", opt_thresh)]:
        b_preds = (scores >= tau).astype(int)
        cm = confusion_matrix(y_val, b_preds)
        tn, fp, fn, tp = cm.ravel()
        sens = recall_score(y_val, b_preds, zero_division=0)
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        prec = precision_score(y_val, b_preds, zero_division=0)
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
        f1 = f1_score(y_val, b_preds, zero_division=0)
        b_acc = balanced_accuracy_score(y_val, b_preds)
        mcc = matthews_corrcoef(y_val, b_preds)

        rows.append({
            "Model": model_name,
            "Mode": mode,
            "Threshold": tau,
            "Accuracy": accuracy_score(y_val, b_preds),
            "Sensitivity": sens,
            "Specificity": spec,
            "Precision": prec,
            "NPV": npv,
            "F1-Score": f1,
            "Balanced Acc": b_acc,
            "MCC": mcc,
            "Brier": brier,
            "ROC-AUC": auc_roc,
            "PR-AUC": auc_pr,
            "Latency": latency_str
        })
    return rows, (fpr, tpr, auc_roc), (rec_pts, prec_pts, auc_pr)

rows_v0, roc_v0, pr_v0 = evaluate_kinematic_model("V0 Baseline CNN", scores_v0_masked, f"{lat_v0_mean:.2f} \u00b1 {lat_v0_std:.2f} ms")
rows_v1, roc_v1, pr_v1 = evaluate_kinematic_model("V1 CNN + XAI", scores_v1_masked, f"{lat_v1_mean:.2f} \u00b1 {lat_v1_std:.2f} ms")
rows_v2, roc_v2, pr_v2 = evaluate_kinematic_model("V2 Bi-LSTM", scores_v2_masked, f"{lat_v2_mean:.2f} \u00b1 {lat_v2_std:.2f} ms")

all_eval_rows = rows_v0 + rows_v1 + rows_v2

# 5. Formatted Tables for JISEBI 2024
print("=" * 130)
print("TABLE 1: KINEMATIC DISCRIMINATION PERFORMANCE & BENCHMARK COMPARISON (JISEBI 2024)")
print("=" * 130)
header_fmt = "{:<16} | {:<18} | {:<5} | {:<7} | {:<7} | {:<7} | {:<7} | {:<7} | {:<6} | {:<7} | {:<7} | {:<12}"
print(header_fmt.format("Model", "Operating Mode", "tau", "Sens", "Spec", "Prec", "F1", "B-Acc", "MCC", "ROC-AUC", "PR-AUC", "CPU Latency"))
print("-" * 130)
row_fmt = "{:<16} | {:<18} | {:<5.2f} | {:<6.2f}% | {:<6.2f}% | {:<6.2f}% | {:<6.2f}% | {:<6.2f}% | {:<6.3f} | {:<7.4f} | {:<7.4f} | {:<12}"
for r in all_eval_rows:
    print(row_fmt.format(
        r["Model"],
        r["Mode"],
        r["Threshold"],
        r["Sensitivity"] * 100.0,
        r["Specificity"] * 100.0,
        r["Precision"] * 100.0,
        r["F1-Score"] * 100.0,
        r["Balanced Acc"] * 100.0,
        r["MCC"],
        r["ROC-AUC"],
        r["PR-AUC"],
        r["Latency"]
    ))
print("=" * 130)

# 6. Multi-Panel Visual Benchmarking Plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
colors = {"V0 Baseline CNN": "#1f77b4", "V1 CNN + XAI": "#ff7f0e", "V2 Bi-LSTM": "#2ca02c"}

# Subplot 1: ROC Curves
for name, (fpr, tpr, roc_score) in [("V0 Baseline CNN", roc_v0), ("V1 CNN + XAI", roc_v1), ("V2 Bi-LSTM", roc_v2)]:
    axes[0].plot(fpr, tpr, color=colors[name], lw=2.2, label=f"{name} (AUC = {roc_score:.3f})")
axes[0].plot([0, 1], [0, 1], "k--", lw=1.2, alpha=0.6)
axes[0].set_xlim([-0.02, 1.02])
axes[0].set_ylim([-0.02, 1.05])
axes[0].set_xlabel("False Positive Rate (1 - Specificity)", fontweight="bold")
axes[0].set_ylabel("True Positive Rate (Sensitivity)", fontweight="bold")
axes[0].set_title("Kinematic Models: ROC Curves", fontweight="bold", pad=10)
axes[0].legend(loc="lower right", frameon=True, fontsize=9)
axes[0].grid(True, alpha=0.3)

# Subplot 2: Precision-Recall Curves
for name, (rec_pts, prec_pts, pr_score) in [("V0 Baseline CNN", pr_v0), ("V1 CNN + XAI", pr_v1), ("V2 Bi-LSTM", pr_v2)]:
    axes[1].plot(rec_pts, prec_pts, color=colors[name], lw=2.2, label=f"{name} (PR-AUC = {pr_score:.3f})")
axes[1].set_xlim([-0.02, 1.02])
axes[1].set_ylim([-0.02, 1.05])
axes[1].set_xlabel("Recall (Sensitivity)", fontweight="bold")
axes[1].set_ylabel("Precision (PPV)", fontweight="bold")
axes[1].set_title("Kinematic Models: Precision-Recall Curves", fontweight="bold", pad=10)
axes[1].legend(loc="lower left", frameon=True, fontsize=9)
axes[1].grid(True, alpha=0.3)

# Subplot 3: Single-Sample Latency Comparison
model_names = ["V0 Baseline CNN", "V1 CNN + XAI", "V2 Bi-LSTM"]
lat_means = [lat_v0_mean, lat_v1_mean, lat_v2_mean]
lat_stds = [lat_v0_std, lat_v1_std, lat_v2_std]
bar_colors = [colors[m] for m in model_names]

bars = axes[2].bar(model_names, lat_means, yerr=lat_stds, capsize=5, color=bar_colors, alpha=0.85, edgecolor="black")
axes[2].set_ylabel("Inference Latency (ms / sample)", fontweight="bold")
axes[2].set_title("Single-Sample CPU Latency Benchmark", fontweight="bold", pad=10)
axes[2].grid(axis="y", alpha=0.3)
for bar, m_val in zip(bars, lat_means):
    axes[2].text(bar.get_x() + bar.get_width() / 2.0, m_val + 0.3, f"{m_val:.2f} ms", ha="center", va="bottom", fontweight="bold")

plt.tight_layout()
plt.show()
"""

# Cell 36: Code for Multi-Class DHRC Benchmark
c36_code = r"""import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    auc,
    confusion_matrix,
    matthews_corrcoef,
    balanced_accuracy_score,
    brier_score_loss,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# 1. Ensure DHRC predictions and validation arrays are available
if 'reversal_model' not in globals() or 'X_val' not in globals():
    import tensorflow as tf
    from config import DHRC_MODEL_PATH, DHRC_VOCABULARY
    reversal_model = tf.keras.models.load_model(DHRC_MODEL_PATH)

VOCAB = DHRC_VOCABULARY if 'DHRC_VOCABULARY' in globals() else [chr(i) for i in range(ord('a'), ord('z')+1)] + [chr(i) for i in range(ord('A'), ord('Z')+1)]

val_preds = reversal_model.predict(X_val, verbose=0)
char_probs = val_preds[0]
rev_probs = val_preds[1].ravel()

char_preds_top1 = np.argmax(char_probs, axis=1)

# 2. Multi-Class Character Recognition (Head 1: 52 Classes)
# Exact Top-1 Accuracy
top1_acc = np.mean(char_preds_top1 == y_char_val) * 100.0

# Case-Insensitive Top-1 Accuracy (matches normalized case)
case_insensitive_correct = sum(
    1 for i in range(len(y_char_val)) if VOCAB[char_preds_top1[i]].lower() == VOCAB[y_char_val[i]].lower()
)
case_insensitive_acc = (case_insensitive_correct / len(y_char_val)) * 100.0

# Top-3 and Top-5 Accuracy
top3_correct = sum(
    1 for i in range(len(y_char_val)) if y_char_val[i] in np.argsort(char_probs[i])[-3:]
)
top3_acc = (top3_correct / len(y_char_val)) * 100.0

top5_correct = sum(
    1 for i in range(len(y_char_val)) if y_char_val[i] in np.argsort(char_probs[i])[-5:]
)
top5_acc = (top5_correct / len(y_char_val)) * 100.0

# Macro and Weighted Averages via classification_report
cls_rep = classification_report(y_char_val, char_preds_top1, labels=list(range(len(VOCAB))), target_names=VOCAB, output_dict=True, zero_division=0)
macro_f1 = cls_rep["macro avg"]["f1-score"] * 100.0
macro_prec = cls_rep["macro avg"]["precision"] * 100.0
macro_rec = cls_rep["macro avg"]["recall"] * 100.0
weighted_f1 = cls_rep["weighted avg"]["f1-score"] * 100.0
weighted_prec = cls_rep["weighted avg"]["precision"] * 100.0
weighted_rec = cls_rep["weighted avg"]["recall"] * 100.0

# 3. Clinical Chiral Grapheme Breakdown & Confusion Analysis
chiral_letters = ["b", "d", "p", "q", "n", "u", "m", "w"]
chiral_stats = []
for ch in chiral_letters:
    if ch in VOCAB and ch in cls_rep:
        chiral_stats.append({
            "Letter": ch,
            "Precision": cls_rep[ch]["precision"] * 100.0,
            "Recall": cls_rep[ch]["recall"] * 100.0,
            "F1-Score": cls_rep[ch]["f1-score"] * 100.0,
            "Support": int(cls_rep[ch]["support"])
        })

# Pairwise Chiral Cross-Confusion (b <-> d, p <-> q)
ch_to_idx = {c: i for i, c in enumerate(VOCAB)}
def get_cross_confusion(ch_a, ch_b):
    idx_a, idx_b = ch_to_idx[ch_a], ch_to_idx[ch_b]
    total_a = np.sum(y_char_val == idx_a)
    mis_a_as_b = np.sum((y_char_val == idx_a) & (char_preds_top1 == idx_b))
    rate = (mis_a_as_b / total_a * 100.0) if total_a > 0 else 0.0
    return total_a, mis_a_as_b, rate

b_total, b_as_d, b_as_d_rate = get_cross_confusion("b", "d")
d_total, d_as_b, d_as_b_rate = get_cross_confusion("d", "b")
p_total, p_as_q, p_as_q_rate = get_cross_confusion("p", "q")
q_total, q_as_p, q_as_p_rate = get_cross_confusion("q", "p")

# Top 10 Most Frequent Misclassification Pairs
confusion_counts = {}
for true_i, pred_i in zip(y_char_val, char_preds_top1):
    if true_i != pred_i:
        pair = (VOCAB[true_i], VOCAB[pred_i])
        confusion_counts[pair] = confusion_counts.get(pair, 0) + 1

top_confusions = sorted(confusion_counts.items(), key=lambda x: x[1], reverse=True)[:10]

# 4. Reversal Detection (Head 2: Binary Mirror Classification)
fpr, tpr, threshs_roc = roc_curve(y_rev_val, rev_probs)
auc_roc_rev = roc_auc_score(y_rev_val, rev_probs)
prec_rev_pts, rec_rev_pts, _ = precision_recall_curve(y_rev_val, rev_probs)
auc_pr_rev = auc(rec_rev_pts, prec_rev_pts)
brier_rev = brier_score_loss(y_rev_val, rev_probs)

opt_idx = np.argmax(tpr - fpr)
opt_thresh_rev = float(threshs_roc[opt_idx])

rev_preds_50 = (rev_probs >= 0.50).astype(int)
rev_preds_opt = (rev_probs >= opt_thresh_rev).astype(int)

sens_50 = recall_score(y_rev_val, rev_preds_50, zero_division=0)
spec_50 = np.sum((y_rev_val == 0) & (rev_preds_50 == 0)) / np.sum(y_rev_val == 0)
prec_50 = precision_score(y_rev_val, rev_preds_50, zero_division=0)
f1_50 = f1_score(y_rev_val, rev_preds_50, zero_division=0)
bacc_50 = balanced_accuracy_score(y_rev_val, rev_preds_50)
mcc_50 = matthews_corrcoef(y_rev_val, rev_preds_50)

sens_opt = recall_score(y_rev_val, rev_preds_opt, zero_division=0)
spec_opt = np.sum((y_rev_val == 0) & (rev_preds_opt == 0)) / np.sum(y_rev_val == 0)
prec_opt = precision_score(y_rev_val, rev_preds_opt, zero_division=0)
f1_opt = f1_score(y_rev_val, rev_preds_opt, zero_division=0)
bacc_opt = balanced_accuracy_score(y_rev_val, rev_preds_opt)
mcc_opt = matthews_corrcoef(y_rev_val, rev_preds_opt)

# Joint Multi-Task Dual-Head Accuracy
joint_correct = np.sum((char_preds_top1 == y_char_val) & (rev_preds_50 == y_rev_val))
joint_acc = (joint_correct / len(y_char_val)) * 100.0

# 5. Formatted Tables
print("=" * 95)
print("TABLE 2: DHRC MULTI-CLASS CHARACTER RECOGNITION (HEAD 1 - 52 CLASSES)")
print("=" * 95)
print(f"  -> Exact Top-1 Accuracy           : {top1_acc:.2f}%")
print(f"  -> Case-Insensitive Top-1 Accuracy: {case_insensitive_acc:.2f}% (Normalizing upper/lowercase)")
print(f"  -> Top-3 Accuracy                 : {top3_acc:.2f}%")
print(f"  -> Top-5 Accuracy                 : {top5_acc:.2f}%")
print(f"  -> Macro-Averaged Precision/Recall: {macro_prec:.2f}% / {macro_rec:.2f}% (Macro-F1: {macro_f1:.2f}%)")
print(f"  -> Weighted Precision/Recall      : {weighted_prec:.2f}% / {weighted_rec:.2f}% (Weighted-F1: {weighted_f1:.2f}%)")
print("-" * 95)
print("CLINICAL CHIRAL GROUPS (LATERAL & VERTICAL CONFUSABLE SUBGROUPS)")
print(f"{'Letter':<8} | {'Precision':<12} | {'Recall':<12} | {'F1-Score':<12} | {'Support':<8}")
print("-" * 65)
for s in chiral_stats:
    print(f"{s['Letter']:<8} | {s['Precision']:<11.2f}% | {s['Recall']:<11.2f}% | {s['F1-Score']:<11.2f}% | {s['Support']:<8}")
print("-" * 65)
print("CHIRAL CROSS-CONFUSION MATRIX (LATERAL FLIP ERRORS)")
print(f"  -> True 'b' misclassified as 'd' : {b_as_d}/{b_total} ({b_as_d_rate:.2f}%)")
print(f"  -> True 'd' misclassified as 'b' : {d_as_b}/{d_total} ({d_as_b_rate:.2f}%)")
print(f"  -> True 'p' misclassified as 'q' : {p_as_q}/{p_total} ({p_as_q_rate:.2f}%)")
print(f"  -> True 'q' misclassified as 'p' : {q_as_p}/{q_total} ({q_as_p_rate:.2f}%)")
print("-" * 95)
print("TOP 10 CONFUSED CHARACTER PAIRS:")
for (tr, pr), count in top_confusions:
    print(f"  -> True '{tr}' -> Predicted '{pr}': {count} occurrences")
print("=" * 95)

print("\n" + "=" * 105)
print("TABLE 3: DHRC CLINICAL REVERSAL DETECTION (HEAD 2 - BINARY MIRROR)")
print("=" * 105)
print(f"{'Operating Point':<20} | {'tau':<6} | {'Sens':<8} | {'Spec':<8} | {'Prec':<8} | {'F1':<8} | {'B-Acc':<8} | {'MCC':<7} | {'ROC-AUC':<8} | {'PR-AUC':<8}")
print("-" * 105)
print(f"{'Default':<20} | {0.50:<6.2f} | {sens_50*100:>7.2f}% | {spec_50*100:>7.2f}% | {prec_50*100:>7.2f}% | {f1_50*100:>7.2f}% | {bacc_50*100:>7.2f}% | {mcc_50:>7.3f} | {auc_roc_rev:>8.4f} | {auc_pr_rev:>8.4f}")
print(f"{'Calibrated (Youden)':<20} | {opt_thresh_rev:<6.2f} | {sens_opt*100:>7.2f}% | {spec_opt*100:>7.2f}% | {prec_opt*100:>7.2f}% | {f1_opt*100:>7.2f}% | {bacc_opt*100:>7.2f}% | {mcc_opt:>7.3f} | {auc_roc_rev:>8.4f} | {auc_pr_rev:>8.4f}")
print("-" * 105)
print(f"Joint Multi-Task Accuracy (Both Character & Reversal Correct): {joint_acc:.2f}% | Brier Score: {brier_rev:.4f}")
print("=" * 105)

# 6. Multi-Panel Visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))

# Subplot 1: Head 1 Top-k and Macro/Weighted Comparison
h1_labels = ["Top-1 Exact", "Top-1 (Folded)", "Top-3", "Top-5", "Macro-F1", "Weighted-F1"]
h1_vals = [top1_acc, case_insensitive_acc, top3_acc, top5_acc, macro_f1, weighted_f1]
h1_bars = axes[0].bar(h1_labels, h1_vals, color=["#3b82f6", "#10b981", "#6366f1", "#8b5cf6", "#f59e0b", "#ec4899"], alpha=0.85, edgecolor="black")
axes[0].set_ylabel("Accuracy / F1 (%)", fontweight="bold")
axes[0].set_ylim([0, 105])
axes[0].set_title("Head 1: 52-Class Recognition Spectrum", fontweight="bold", pad=10)
axes[0].grid(axis="y", alpha=0.3)
axes[0].tick_params(axis="x", rotation=25)
for b, val in zip(h1_bars, h1_vals):
    axes[0].text(b.get_x() + b.get_width() / 2.0, val + 1.2, f"{val:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

# Subplot 2: Head 2 ROC and Precision-Recall Curves
axes[1].plot(fpr, tpr, color="#ef4444", lw=2.2, label=f"ROC (AUC = {auc_roc_rev:.3f})")
axes[1].plot(rec_rev_pts, prec_rev_pts, color="#8b5cf6", lw=2.2, linestyle="--", label=f"PR (AUC = {auc_pr_rev:.3f})")
axes[1].scatter([1 - spec_opt], [sens_opt], color="black", s=80, zorder=5, label=f"Optimal tau* = {opt_thresh_rev:.2f}")
axes[1].plot([0, 1], [0, 1], "k:", lw=1.2, alpha=0.5)
axes[1].set_xlim([-0.02, 1.02])
axes[1].set_ylim([-0.02, 1.05])
axes[1].set_xlabel("FPR / Recall", fontweight="bold")
axes[1].set_ylabel("TPR / Precision", fontweight="bold")
axes[1].set_title("Head 2: Standalone ROC & PR Curves", fontweight="bold", pad=10)
axes[1].legend(loc="lower right", frameon=True, fontsize=8.5)
axes[1].grid(True, alpha=0.3)

# Subplot 3: Chiral Confusion Sub-Matrix (b, d, p, q)
chiral_sub = ["b", "d", "p", "q"]
cm_chiral = np.zeros((4, 4), dtype=int)
for i, c_true in enumerate(chiral_sub):
    for j, c_pred in enumerate(chiral_sub):
        idx_t, idx_p = ch_to_idx[c_true], ch_to_idx[c_pred]
        cm_chiral[i, j] = np.sum((y_char_val == idx_t) & (char_preds_top1 == idx_p))

im = axes[2].imshow(cm_chiral, cmap="Blues", interpolation="nearest")
plt.colorbar(im, ax=axes[2])
axes[2].set_xticks(range(4))
axes[2].set_yticks(range(4))
axes[2].set_xticklabels(chiral_sub, fontsize=11, fontweight="bold")
axes[2].set_yticklabels(chiral_sub, fontsize=11, fontweight="bold")
axes[2].set_xlabel("Predicted Chiral Glyph", fontweight="bold")
axes[2].set_ylabel("True Chiral Glyph", fontweight="bold")
axes[2].set_title("Chiral Confusion Sub-Matrix", fontweight="bold", pad=10)

for i in range(4):
    for j in range(4):
        val = cm_chiral[i, j]
        text_col = "white" if val > cm_chiral.max() / 2 else "black"
        axes[2].text(j, i, str(val), ha="center", va="center", color=text_col, fontsize=12, fontweight="bold")

plt.tight_layout()
plt.show()
"""

# Check if Section 12 already exists to prevent duplicate appends
existing_headers = [
    "".join(cell.get("source", []))
    for cell in nb["cells"]
    if cell.get("cell_type") == "markdown"
]
has_s12 = any("12. End-to-End System Benchmark" in h for h in existing_headers)

if has_s12:
    print("Section 12 already exists in playground.ipynb. Updating in-place...")
    # Find indices
    for idx, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        if "## 12. End-to-End System Benchmark" in src:
            nb["cells"][idx]["source"] = [c34_md]
            nb["cells"][idx+1]["source"] = [c35_code]
            nb["cells"][idx+2]["source"] = [c36_code]
            break
else:
    print(f"Appending Section 12 (3 new cells) to playground.ipynb (current count: {len(nb['cells'])})...")
    cell34 = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [c34_md]
    }
    cell35 = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [c35_code]
    }
    cell36 = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [c36_code]
    }
    nb["cells"].extend([cell34, cell35, cell36])

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Successfully updated playground.ipynb! New cell count: {len(nb['cells'])}")
