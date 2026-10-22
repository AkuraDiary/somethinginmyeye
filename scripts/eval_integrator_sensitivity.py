"""
Systematic Parameter Sensitivity Analysis for SLD Multi-Attribute Integrator.
Follows the experimental protocol of Kunhoth et al. (2024, Table 4) to verify
that classification concordance and screening categories are stable across
heuristic weight variations (w +/- 0.10) and decision thresholds (theta in [0.40, 0.60]).
"""

import sys
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CLASSIFICATION_THRESHOLD, COGNITIVE_LATENCY_THRESHOLD_MS

def compute_risk(ortho_err: float, rev_flag: float, lat_penalty: float, 
                 w_spell: float, w_rev: float, w_lat: float) -> float:
    raw = ortho_err * w_spell + rev_flag * w_rev + lat_penalty * w_lat
    return min(max(raw * 100.0, 0.0), 100.0)

def classify_profile(k_dysgraphia: float, r_dyslexia: float, threshold: float) -> str:
    is_dg = k_dysgraphia >= threshold
    is_dx = r_dyslexia >= threshold
    if is_dg and is_dx:
        return "Comorbid"
    elif is_dg:
        return "Motor Dysgraphia"
    elif is_dx:
        return "Dyslexia"
    else:
        return "Typical"

def run_sensitivity_sweep() -> Tuple[pd.DataFrame, pd.DataFrame]:
    # 1. Synthesize representative cohort covering normal, isolated motor, isolated dyslexic, and comorbid cases
    np.random.seed(42)
    n_samples = 400
    
    # 4 distinct clinical profiles (100 per cohort)
    # Group A: Typical
    gA_k = np.random.uniform(10.0, 42.0, 100)
    gA_err = np.random.uniform(0.0, 0.25, 100)
    gA_rev = np.zeros(100)
    gA_lat = np.random.uniform(0.0, 0.25, 100)
    
    # Group B: Motor Dysgraphia (high K, low ortho)
    gB_k = np.random.uniform(58.0, 95.0, 100)
    gB_err = np.random.uniform(0.0, 0.30, 100)
    gB_rev = np.zeros(100)
    gB_lat = np.random.uniform(0.0, 0.30, 100)
    
    # Group C: Dyslexia (low K, high reversals/ortho/latency)
    gC_k = np.random.uniform(15.0, 44.0, 100)
    gC_err = np.random.uniform(0.40, 0.90, 100)
    gC_rev = np.random.choice([0.0, 1.0], size=100, p=[0.2, 0.8])
    gC_lat = np.random.uniform(0.35, 1.0, 100)
    
    # Group D: Comorbid (high K, high ortho/reversals)
    gD_k = np.random.uniform(55.0, 95.0, 100)
    gD_err = np.random.uniform(0.40, 0.90, 100)
    gD_rev = np.random.choice([0.0, 1.0], size=100, p=[0.2, 0.8])
    gD_lat = np.random.uniform(0.35, 1.0, 100)
    
    k_scores = np.concatenate([gA_k, gB_k, gC_k, gD_k])
    ortho_errors = np.concatenate([gA_err, gB_err, gC_err, gD_err])
    rev_flags = np.concatenate([gA_rev, gB_rev, gC_rev, gD_rev])
    lat_penalties = np.concatenate([gA_lat, gB_lat, gC_lat, gD_lat])
    
    # Baseline configuration
    w_spell_base, w_rev_base, w_lat_base = 0.40, 0.40, 0.20
    theta_base = 50.0
    
    base_risks = [compute_risk(oe, rf, lp, w_spell_base, w_rev_base, w_lat_base) 
                  for oe, rf, lp in zip(ortho_errors, rev_flags, lat_penalties)]
    base_classes = [classify_profile(k, r, theta_base) for k, r in zip(k_scores, base_risks)]
    
    # Sweep 1: Decision Threshold Theta in [40, 45, 50, 55, 60]%
    theta_results = []
    for theta in [40.0, 45.0, 50.0, 55.0, 60.0]:
        cur_classes = [classify_profile(k, r, theta) for k, r in zip(k_scores, base_risks)]
        concordance = np.mean([1 if c1 == c2 else 0 for c1, c2 in zip(base_classes, cur_classes)]) * 100.0
        theta_results.append({
            "Threshold (Theta)": f"{theta:.1f}%",
            "Concordance with Baseline": f"{concordance:.2f}%",
            "Status": "Stable" if concordance >= 90.0 else "Sensitive"
        })
    df_theta = pd.DataFrame(theta_results)
    
    # Sweep 2: Weight Perturbations (w +/- 0.10)
    weight_configs = [
        ("Baseline (0.40 / 0.40 / 0.20)", 0.40, 0.40, 0.20),
        ("Orthographic Emphasis (0.50 / 0.35 / 0.15)", 0.50, 0.35, 0.15),
        ("Reversal Emphasis (0.35 / 0.50 / 0.15)", 0.35, 0.50, 0.15),
        ("Latency Balanced (0.35 / 0.35 / 0.30)", 0.35, 0.35, 0.30),
        ("Equal Linguistic (0.45 / 0.45 / 0.10)", 0.45, 0.45, 0.10),
    ]
    
    weight_results = []
    for label, ws, wr, wl in weight_configs:
        cur_risks = [compute_risk(oe, rf, lp, ws, wr, wl) for oe, rf, lp in zip(ortho_errors, rev_flags, lat_penalties)]
        cur_classes = [classify_profile(k, r, theta_base) for k, r in zip(k_scores, cur_risks)]
        concordance = np.mean([1 if c1 == c2 else 0 for c1, c2 in zip(base_classes, cur_classes)]) * 100.0
        weight_results.append({
            "Configuration": label,
            "Weights (w_spell / w_rev / w_lat)": f"{ws:.2f} / {wr:.2f} / {wl:.2f}",
            "Concordance with Baseline": f"{concordance:.2f}%",
            "Status": "Robust" if concordance >= 92.0 else "Moderate"
        })
    df_weights = pd.DataFrame(weight_results)
    
    return df_theta, df_weights

if __name__ == "__main__":
    df_theta, df_weights = run_sensitivity_sweep()
    print("\n=== SWEEP 1: DECISION THRESHOLD STABILITY (Kunhoth et al. Protocol) ===")
    print(df_theta.to_string(index=False))
    print("\n=== SWEEP 2: HEURISTIC WEIGHT PERTURBATION STABILITY ===")
    print(df_weights.to_string(index=False))
