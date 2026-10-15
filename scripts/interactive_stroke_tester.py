"""
Interactive Stroke Tester for Dual-Head Reversal Model.
Tests arbitrary stroke CSVs or trajectory dictionaries, outputs top character candidates,
reversal confidence score, and renders a diagnostic trajectory plot.
"""
import os
import sys

sys.path.insert(0, 'venv/lib/python3.12/site-packages')
os.environ['KERAS_HOME'] = '/tmp/keras'
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import onnxruntime as ort

MODEL_ONNX_PATH = "scratch/dual_head_reversal.onnx"

VOCABULARY = (
    [chr(i) for i in range(ord('a'), ord('z') + 1)] +
    [chr(i) for i in range(ord('A'), ord('Z') + 1)] +
    [str(d) for d in range(10)]
)

def resample_and_normalize_strokes(strokes, target_len=64):
    if not strokes or sum(len(s) for s in strokes) == 0:
        return {'x': np.zeros(target_len, dtype=np.float32), 'y': np.zeros(target_len, dtype=np.float32), 'pen_state': np.zeros(target_len, dtype=np.float32)}

    raw_x, raw_y, raw_pen = [], [], []
    for s_idx, stroke in enumerate(strokes):
        if not stroke: continue
        if s_idx > 0 and len(raw_x) > 0:
            raw_x.append(stroke[0][0])
            raw_y.append(stroke[0][1])
            raw_pen.append(0.0)
        for pt in stroke:
            raw_x.append(float(pt[0]))
            raw_y.append(float(pt[1]))
            raw_pen.append(1.0)

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
        return {'x': np.full(target_len, norm_x[0], dtype=np.float32), 'y': np.full(target_len, norm_y[0], dtype=np.float32), 'pen_state': np.ones(target_len, dtype=np.float32)}

    query_dist = np.linspace(0.0, total_length, target_len)
    res_x = np.interp(query_dist, cum_dist, norm_x).astype(np.float32)
    res_y = np.interp(query_dist, cum_dist, norm_y).astype(np.float32)
    interp_pen = np.interp(query_dist, cum_dist, raw_pen)
    res_pen = (interp_pen >= 0.5).astype(np.float32)

    return {'x': res_x, 'y': res_y, 'pen_state': res_pen}

def extract_features(resampled_data, eps=1e-7):
    x, y, pen_state = resampled_data['x'], resampled_data['y'], resampled_data['pen_state']
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
    return np.column_stack([dx, dy, cos_theta, sin_theta, d_theta, d2x, d2y, pen_state.astype(np.float32)])

def load_strokes_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    touching = df['touching'].values if 'touching' in df.columns else np.ones(len(df))
    time_vals = df['time'].values if 'time' in df.columns else np.arange(len(df))
    strokes = []
    curr = []
    for i in range(len(df)):
        if touching[i] == 1:
            if curr and i > 0 and (time_vals[i] - time_vals[i-1]) > 80.0:
                if len(curr) >= 2:
                    strokes.append(curr)
                curr = []
            curr.append((float(df['x'].iloc[i]), float(df['y'].iloc[i])))
        else:
            if len(curr) >= 2:
                strokes.append(curr)
            curr = []
    if len(curr) >= 2:
        strokes.append(curr)
    return strokes

def test_stroke_trajectory(strokes, title="Stroke Test", save_plot=None):
    session = ort.InferenceSession(MODEL_ONNX_PATH)
    res = resample_and_normalize_strokes(strokes, target_len=64)
    feats = extract_features(res)
    input_tensor = np.expand_dims(feats, axis=0) # (1, 64, 8)

    input_name = session.get_inputs()[0].name
    ort_outputs = session.run(None, {input_name: input_tensor})

    if ort_outputs[0].shape[-1] == 62:
        char_probs, rev_prob = ort_outputs[0][0], float(ort_outputs[1][0][0])
    else:
        rev_prob, char_probs = float(ort_outputs[0][0][0]), ort_outputs[1][0]

    top3_indices = np.argsort(char_probs)[::-1][:3]
    top3 = [(VOCABULARY[idx], float(char_probs[idx])) for idx in top3_indices]
    is_rev = rev_prob >= 0.50

    print(f"\n--- INFERENCE RESULTS: {title} ---")
    print(f"Top-1 Character: '{top3[0][0]}' ({top3[0][1]*100:.1f}%)")
    print(f"Top-3 Candidates: " + ", ".join([f"'{c}': {p*100:.1f}%" for c, p in top3]))
    print(f"Reversal Probability: {rev_prob*100:.2f}%")
    print(f"Clinical Diagnosis: {'[CLINICAL REVERSAL / INVERSION]' if is_rev else '[AUTHENTIC CANONICAL]'}")

    if save_plot:
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        cmap = plt.get_cmap("coolwarm" if is_rev else "Blues")
        total_pts = sum(len(s) for s in strokes)
        pt_counter = 0
        for s_idx, s in enumerate(strokes):
            xs = [pt[0] for pt in s]
            ys = [pt[1] for pt in s]
            for i in range(len(s) - 1):
                t = (pt_counter + i) / max(total_pts - 1, 1)
                ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]], color=cmap(0.3 + 0.7 * t), lw=3.0)
                if len(s) >= 4 and i == len(s) // 2:
                    ax.annotate('', xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                                arrowprops=dict(arrowstyle="->,head_length=0.4,head_width=0.3", color='red', lw=1.5))
            ax.scatter(xs[0], ys[0], color='green', s=45, zorder=5, label='Start' if s_idx == 0 else "")
            ax.scatter(xs[-1], ys[-1], color='crimson', s=45, marker='s', zorder=5, label='End' if s_idx == 0 else "")
            pt_counter += len(s)
        
        status_str = "REVERSED" if is_rev else "NORMAL"
        ax.set_title(f"Predicted: '{top3[0][0]}' | Status: {status_str} ({rev_prob*100:.1f}%)", fontsize=11, fontweight='bold')
        ax.set_aspect('equal', adjustable='datalim')
        ax.invert_yaxis()
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.legend(loc="upper right", fontsize=8)
        plt.tight_layout()
        plt.savefig(save_plot, dpi=140)
        plt.close()
        print(f"Diagnostic plot saved to: {save_plot}")

    return {
        'top_char': top3[0][0],
        'top3': top3,
        'reversal_prob': rev_prob,
        'is_reversed': is_rev
    }

if __name__ == "__main__":
    # Test on a few real tablet files from datasets
    sample_csvs = [
        ("datasets/Train_normal_C_Seta_1787842835503_1787842835.csv", "Normal C"),
        ("datasets/Train_normal_p_Seta_1788152990113_1788152991.csv", "Normal p"),
        ("datasets/Train_dyslexia_M_Seta_1787878180407_1787878179.csv", "Dyslexia M"),
        ("datasets/Train_dysgraphia_u_Seta_1788154173617_1788154174.csv", "Dysgraphia u")
    ]
    os.makedirs("scratch/test_plots", exist_ok=True)
    for path, desc in sample_csvs:
        if os.path.exists(path):
            stk = load_strokes_from_csv(path)
            plot_file = f"scratch/test_plots/{desc.replace(' ', '_').lower()}.png"
            test_stroke_trajectory(stk, title=f"{desc} ({os.path.basename(path)})", save_plot=plot_file)
