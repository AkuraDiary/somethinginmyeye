"""
Appends Section 11 (In-House Isolated Reversal Classifier Benchmark & Verification)
to playground.ipynb and executes the visualization pipeline.
"""
import json
import os
import sys

NOTEBOOK_PATH = "playground.ipynb"

section_markdown = """## 11. In-House Isolated Reversal Classifier: Benchmark Dataset & Visual Verification

This section prepares and verifies the isolated character dataset for the in-house reversal and kinematic distortion classifier:
1. **UJIpenchars2 Benchmark Ingestion (`parse_ujipenchars`):** Parses authentic online handwriting trajectories (11,640 samples across 97 character classes, exactly 120 samples per character).
2. **Local Dataset Adapter (`load_local_tablet_samples`):** Converts local tablet recordings from `datasets/` into standard stroke sequences, governed by an explicit on/off switch (`BLEND_LOCAL_SAMPLES = False`).
3. **Synthetic Reflection & Rotation Augmentation:** Generates mirror-reversed twins ($x' = x_{max} - (x - x_{min})$) for horizontal flip letters (`B`, `b`, `d`, `p`, `q`, `E`, `N`, `S`, etc.) and rotational inversions (`m <-> w`, `u <-> n`).
4. **Visual Verification Panel:** Generates multi-panel comparative trajectory plots with stroke direction gradient arrows to verify authentic vs. reversed kinematics prior to model training.
"""

section_code_data = """import os
import glob
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional

# ==============================================================================
# 1. CENTRAL CONFIGURATION & ADAPTER TOGGLE
# ==============================================================================
UJIPEN_PATH = "ujipendatasets/ujipenchars2.txt"
LOCAL_DATASETS_DIR = "datasets"

# Architectural toggle: keep False by default to maintain isolated benchmark integrity
BLEND_LOCAL_SAMPLES = False

# Asymmetric reversible character sets for targeted augmentation
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

# ==============================================================================
# 2. UJIPENCHARS2 BENCHMARK DATASET PARSER
# ==============================================================================
def parse_ujipenchars(filepath: str) -> List[Dict[str, Any]]:
    \"\"\"
    Parses the UJIpenchars2 online handwriting dataset.
    Extracts stroke coordinate sequences [[(x1, y1), (x2, y2), ...], ...] for each word sample.
    \"\"\"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"UJIpenchars dataset file not found at: {filepath}")
        
    samples = []
    current_sample = None
    
    with open(filepath, 'r', encoding='latin1') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            if line.startswith('WORD'):
                parts = line.split()
                label = parts[1]
                sample_id = parts[2] if len(parts) > 2 else ''
                current_sample = {
                    'label': label,
                    'sample_id': sample_id,
                    'source': 'ujipenchars2',
                    'strokes': []
                }
                samples.append(current_sample)
            elif line.startswith('POINTS'):
                if current_sample is None:
                    continue
                if '#' in line:
                    pts_str = line.split('#')[1].strip()
                    nums = [float(val) for val in pts_str.split()]
                    pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
                    current_sample['strokes'].append(pts)
                    
    return samples

# ==============================================================================
# 3. LOCAL TABLET DATASET ADAPTER (ON/OFF SWITCH CONTROLLED)
# ==============================================================================
def load_local_tablet_samples(dataset_dir: str = "datasets") -> List[Dict[str, Any]]:
    \"\"\"
    Adapter reading local tablet recordings from datasets/ and converting them into
    the standardized stroke structure: {'label': char, 'sample_id': path, 'strokes': [...]}.
    \"\"\"
    local_samples = []
    csv_files = glob.glob(os.path.join(dataset_dir, "**", "*.csv"), recursive=True)
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        # Typical naming: Train_normal_C_Seta_... or Train_dyslexia_M_...
        if len(parts) >= 3 and len(parts[2]) == 1:
            label = parts[2]
        else:
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
                local_samples.append({
                    'label': label,
                    'sample_id': filename,
                    'source': 'local_tablet',
                    'strokes': strokes
                })
        except Exception:
            continue
            
    return local_samples

# ==============================================================================
# 4. SYNTHETIC REFLECTION & ROTATION AUGMENTATION
# ==============================================================================
def get_sample_bounding_box(strokes: List[List[Tuple[float, float]]]) -> Tuple[float, float, float, float]:
    \"\"\"Calculates (min_x, max_x, min_y, max_y) across all strokes of a sample.\"\"\"
    all_x = [pt[0] for stroke in strokes for pt in stroke]
    all_y = [pt[1] for stroke in strokes for pt in stroke]
    if not all_x or not all_y:
        return 0.0, 1.0, 0.0, 1.0
    return min(all_x), max(all_x), min(all_y), max(all_y)

def mirror_sample_horizontal(sample: Dict[str, Any], target_label: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Reflects sample coordinates along the horizontal axis:
    x_new = max_x - (x - min_x) = min_x + max_x - x.
    Preserves exact temporal stroke order and point sequencing.
    \"\"\"
    min_x, max_x, _, _ = get_sample_bounding_box(sample['strokes'])
    mirrored_strokes = []
    for stroke in sample['strokes']:
        mirrored_stroke = [(min_x + max_x - pt[0], pt[1]) for pt in stroke]
        mirrored_strokes.append(mirrored_stroke)
        
    lbl = target_label if target_label is not None else sample['label'] + "_rev"
    return {
        'label': lbl,
        'sample_id': sample['sample_id'] + "_mirror_h",
        'source': sample.get('source', '') + "_augmented_mirror",
        'strokes': mirrored_strokes,
        'is_reversal': True
    }

def rotate_sample_180(sample: Dict[str, Any], target_label: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Rotates sample coordinates 180 degrees (inversion for m <-> w, u <-> n):
    x_new = min_x + max_x - x
    y_new = min_y + max_y - y
    \"\"\"
    min_x, max_x, min_y, max_y = get_sample_bounding_box(sample['strokes'])
    rotated_strokes = []
    for stroke in sample['strokes']:
        rotated_stroke = [(min_x + max_x - pt[0], min_y + max_y - pt[1]) for pt in stroke]
        rotated_strokes.append(rotated_stroke)
        
    lbl = target_label if target_label is not None else sample['label'] + "_rot180"
    return {
        'label': lbl,
        'sample_id': sample['sample_id'] + "_rot180",
        'source': sample.get('source', '') + "_augmented_rot180",
        'strokes': rotated_strokes,
        'is_reversal': True
    }

# ==============================================================================
# 5. DATA INGESTION AND ADAPTER VERIFICATION
# ==============================================================================
print("Ingesting UJIpenchars2 benchmark dataset...")
ujipen_samples = parse_ujipenchars(UJIPEN_PATH)
print(f"UJIpenchars2 successfully loaded: {len(ujipen_samples)} character samples across {len(set(s['label'] for s in ujipen_samples))} unique glyphs.")

if BLEND_LOCAL_SAMPLES:
    print(f"Loading local tablet samples from '{LOCAL_DATASETS_DIR}' (BLEND_LOCAL_SAMPLES=True)...")
    local_samples = load_local_tablet_samples(LOCAL_DATASETS_DIR)
    combined_samples = ujipen_samples + local_samples
    print(f"Local samples loaded: {len(local_samples)}. Combined total: {len(combined_samples)}.")
else:
    print("BLEND_LOCAL_SAMPLES is FALSE: Preserving pure UJIpenchars2 isolated benchmark.")
    combined_samples = ujipen_samples
"""

section_code_visualizer = """import matplotlib.pyplot as plt
import matplotlib.cm as cm

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
                if abs(dx) > 1e-4 or abs(dy) > 1e-4:
                    ax.annotate(
                        '', 
                        xy=(xs[i+1], ys[i+1]), 
                        xytext=(xs[i], ys[i]),
                        arrowprops=dict(
                            arrowstyle="->,head_length=0.4,head_width=0.3", 
                            color='red', 
                            lw=1.5
                        )
                    )
        
        ax.scatter(xs[0], ys[0], color='green', s=35, zorder=5, label='Start' if s_idx == 0 else "")
        ax.scatter(xs[-1], ys[-1], color='crimson', s=35, marker='s', zorder=5, label='End' if s_idx == 0 else "")
        pt_counter += len(stroke)
        
    ax.set_title(title, fontsize=10, fontweight='bold', pad=8)
    ax.set_aspect('equal', adjustable='datalim')
    ax.invert_yaxis()  # Canvas coordinate system: y increases downward
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xticks([])
    ax.set_yticks([])

# ==============================================================================
# VISUAL VERIFICATION: MULTI-PANEL SIDE-BY-SIDE PLOT
# ==============================================================================
target_characters = ['B', 'b', 'd', 'E', 'N', 'S', 'm', 'w']
fig, axes = plt.subplots(len(target_characters), 2, figsize=(8.5, 3.2 * len(target_characters)))

print("Rendering visual verification panels (Authentic vs. Synthetic Reversal)...")

for row_idx, char in enumerate(target_characters):
    authentic = next((s for s in ujipen_samples if s['label'] == char), None)
    if authentic is None:
        continue
        
    if char in ROTATIONAL_REVERSIBLE_CHARS:
        reversed_sample = rotate_sample_180(authentic, target_label=ROTATIONAL_REVERSIBLE_CHARS[char])
        rev_title = f"Rotational 180 Inversion: '{char}' -> '{reversed_sample['label']}'"
    elif char in HORIZONTAL_REVERSIBLE_CHARS:
        reversed_sample = mirror_sample_horizontal(authentic, target_label=HORIZONTAL_REVERSIBLE_CHARS[char])
        rev_title = f"Horizontal Reflection: '{char}' -> '{reversed_sample['label']}'"
    else:
        reversed_sample = mirror_sample_horizontal(authentic)
        rev_title = f"Horizontal Reflection: '{char}' -> '{char}_rev'"
        
    # Column 0: Authentic Sample
    ax_auth = axes[row_idx, 0]
    plot_strokes_with_trajectory(
        ax_auth, 
        authentic['strokes'], 
        title=f"Authentic Standard: '{char}' (ID: {authentic['sample_id']})",
        color_map="Blues"
    )
    if row_idx == 0:
        ax_auth.legend(loc="upper right", fontsize=8)
        
    # Column 1: Reversed Synthetic Sample
    ax_rev = axes[row_idx, 1]
    plot_strokes_with_trajectory(
        ax_rev, 
        reversed_sample['strokes'], 
        title=rev_title,
        color_map="Oranges"
    )

plt.tight_layout()
verification_plot_path = "ujipendatasets/reversal_visual_verification.png"
plt.savefig(verification_plot_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"Visual verification plot saved to: {verification_plot_path}")
"""

def main():
    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)

    # Check if section 11 already exists, remove if so
    clean_cells = []
    in_section_11 = False
    for cell in nb['cells']:
        if cell.get('cell_type') == 'markdown':
            source_text = "".join(cell.get('source', []))
            if "11. In-House Isolated Reversal Classifier" in source_text:
                in_section_11 = True
                continue
            elif in_section_11 and source_text.startswith("## "):
                in_section_11 = False
        if not in_section_11:
            clean_cells.append(cell)

    # New cells
    cell_md = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in section_markdown.splitlines()]
    }
    cell_data = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in section_code_data.splitlines()]
    }
    cell_vis = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in section_code_visualizer.splitlines()]
    }

    clean_cells.extend([cell_md, cell_data, cell_vis])
    nb['cells'] = clean_cells

    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)

    print(f"Successfully updated {NOTEBOOK_PATH} with Section 11 cells. Total cells: {len(nb['cells'])}.")

if __name__ == "__main__":
    main()
