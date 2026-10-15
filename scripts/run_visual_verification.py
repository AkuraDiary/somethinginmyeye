"""
Executes the visualization code for Section 11 and generates the comparison plot.
"""
import sys, os
sys.path.insert(0, 'venv/lib/python3.12/site-packages')
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional

UJIPEN_PATH = "ujipendatasets/ujipenchars2.txt"
LOCAL_DATASETS_DIR = "datasets"
BLEND_LOCAL_SAMPLES = False

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

def parse_ujipenchars(filepath: str) -> List[Dict[str, Any]]:
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

def get_sample_bounding_box(strokes: List[List[Tuple[float, float]]]) -> Tuple[float, float, float, float]:
    all_x = [pt[0] for stroke in strokes for pt in stroke]
    all_y = [pt[1] for stroke in strokes for pt in stroke]
    if not all_x or not all_y:
        return 0.0, 1.0, 0.0, 1.0
    return min(all_x), max(all_x), min(all_y), max(all_y)

def mirror_sample_horizontal(sample: Dict[str, Any], target_label: Optional[str] = None) -> Dict[str, Any]:
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

def plot_strokes_with_trajectory(ax, strokes, title, color_map="Blues"):
    cmap = plt.get_cmap(color_map)
    total_pts = sum(len(s) for s in strokes)
    pt_counter = 0
    for s_idx, stroke in enumerate(strokes):
        if not stroke:
            continue
        xs = [pt[0] for pt in stroke]
        ys = [pt[1] for pt in stroke]
        for i in range(len(stroke) - 1):
            t = (pt_counter + i) / max(total_pts - 1, 1)
            ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]], color=cmap(0.35 + 0.65 * t), linewidth=2.8, solid_capstyle='round')
            if len(stroke) >= 4 and i == len(stroke) // 2:
                dx = xs[i+1] - xs[i]
                dy = ys[i+1] - ys[i]
                if abs(dx) > 1e-4 or abs(dy) > 1e-4:
                    ax.annotate('', xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                                arrowprops=dict(arrowstyle="->,head_length=0.4,head_width=0.3", color='red', lw=1.5))
        ax.scatter(xs[0], ys[0], color='green', s=35, zorder=5, label='Start' if s_idx == 0 else "")
        ax.scatter(xs[-1], ys[-1], color='crimson', s=35, marker='s', zorder=5, label='End' if s_idx == 0 else "")
        pt_counter += len(stroke)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=8)
    ax.set_aspect('equal', adjustable='datalim')
    ax.invert_yaxis()
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xticks([])
    ax.set_yticks([])

def main():
    print("Ingesting UJIpenchars2 dataset...")
    samples = parse_ujipenchars(UJIPEN_PATH)
    print(f"Total samples: {len(samples)}")
    
    target_characters = ['B', 'b', 'd', 'E', 'N', 'S', 'm', 'w']
    fig, axes = plt.subplots(len(target_characters), 2, figsize=(8.5, 3.2 * len(target_characters)))
    
    for row_idx, char in enumerate(target_characters):
        authentic = next((s for s in samples if s['label'] == char), None)
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
            
        ax_auth = axes[row_idx, 0]
        plot_strokes_with_trajectory(ax_auth, authentic['strokes'], title=f"Authentic Standard: '{char}' (ID: {authentic['sample_id']})", color_map="Blues")
        if row_idx == 0:
            ax_auth.legend(loc="upper right", fontsize=8)
            
        ax_rev = axes[row_idx, 1]
        plot_strokes_with_trajectory(ax_rev, reversed_sample['strokes'], title=rev_title, color_map="Oranges")
        
    plt.tight_layout()
    out_path = "ujipendatasets/reversal_visual_verification.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved successfully to: {out_path}")

if __name__ == "__main__":
    main()
