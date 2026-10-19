"""
Universal Kinematic Feature Extraction, Scaling, and Prediction Pipeline.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from config import DATASET_DIR, MAX_TIMESTEPS, SAMPLING_RATE_HZ, SCALER_PATH, VAL_DATASET_DIR


def resample_stroke_trajectory(df: pd.DataFrame, target_hz: float = SAMPLING_RATE_HZ) -> pd.DataFrame:
    """Harmonize multi-hardware stroke trajectories by temporally resampling on-surface
    strokes onto a uniform time grid (default 60 Hz = 16.67 ms).
    Decouples sequence length and derivative calculations from hardware polling fluctuations.
    """
    if len(df) < 2 or "time" not in df.columns or "x" not in df.columns or "y" not in df.columns:
        return df.copy()

    df_clean = df.copy()

    # Clamp and normalize pressure to [0.0, 1.0]
    if "pressure" in df_clean.columns:
        p_raw = df_clean["pressure"].values.astype(float)
        p_raw = np.where(p_raw > 1.0, np.minimum(1.0, p_raw / 2.5), p_raw)
        df_clean["pressure"] = np.clip(p_raw, 0.0, 1.0)
    else:
        df_clean["pressure"] = 0.5

    for col in ["tiltX", "tiltY", "touching"]:
        if col not in df_clean.columns:
            df_clean[col] = 0.0 if "tilt" in col else True

    time_ms = df_clean["time"].values.astype(float)
    touching = df_clean["touching"].values.astype(bool)

    dt_raw = np.diff(time_ms, prepend=time_ms[0])
    stroke_breaks = (~touching) | (dt_raw > 200.0)
    stroke_ids = np.cumsum(stroke_breaks)

    target_dt_ms = 1000.0 / target_hz
    resampled_rows = []

    for _, group in df_clean.groupby(stroke_ids):
        g_len = len(group)
        if g_len == 0:
            continue

        g_time = group["time"].values.astype(float)
        g_x = group["x"].values.astype(float)
        g_y = group["y"].values.astype(float)
        g_p = group["pressure"].values.astype(float)
        g_tx = group["tiltX"].values.astype(float)
        g_ty = group["tiltY"].values.astype(float)

        duration = g_time[-1] - g_time[0]
        if duration < target_dt_ms or g_len < 2:
            for _, r in group.iterrows():
                resampled_rows.append(r.to_dict())
            continue

        new_time = np.arange(g_time[0], g_time[-1], target_dt_ms)
        if len(new_time) < 1:
            new_time = np.array([g_time[0]])

        new_x = np.interp(new_time, g_time, g_x)
        new_y = np.interp(new_time, g_time, g_y)
        new_p = np.interp(new_time, g_time, g_p)
        new_tx = np.interp(new_time, g_time, g_tx)
        new_ty = np.interp(new_time, g_time, g_ty)

        lat_val = group["latency"].iloc[0] if "latency" in group.columns else 0.0
        for i in range(len(new_time)):
            resampled_rows.append({
                "time": new_time[i],
                "x": new_x[i],
                "y": new_y[i],
                "pressure": new_p[i],
                "tiltX": new_tx[i],
                "tiltY": new_ty[i],
                "touching": True,
                "latency": lat_val
            })

    if not resampled_rows:
        return df_clean

    return pd.DataFrame(resampled_rows)


def extract_universal_features(df: pd.DataFrame, resample: bool = True) -> np.ndarray:
    """Extract physical and kinematic properties from raw stroke events."""
    if resample and len(df) >= 2:
        df = resample_stroke_trajectory(df)

    if "touching" not in df.columns:
        df["touching"] = True
    for col in ["tiltX", "tiltY", "latency"]:
        if col not in df.columns:
            df[col] = 0.0

    df["dt"] = df["time"].diff().fillna(1.0)
    df.loc[df["dt"] == 0, "dt"] = 1.0

    df["delta_x"] = df["x"].diff().fillna(0.0)
    df["delta_y"] = df["y"].diff().fillna(0.0)
    df["distance"] = np.sqrt(df["delta_x"] ** 2 + df["delta_y"] ** 2)
    df["velocity"] = df["distance"] / df["dt"]
    df["acceleration"] = df["velocity"].diff().fillna(0.0) / df["dt"]
    df["jerk"] = df["acceleration"].diff().fillna(0.0) / df["dt"]

    features_df = df[[
        "delta_x", "delta_y", "pressure", "tiltX", "tiltY",
        "velocity", "acceleration", "jerk", "dt"
    ]].fillna(0.0)

    return features_df.values


def load_and_scale_universal(
    data_dir: str = DATASET_DIR,
    scaler_save_path: str = SCALER_PATH,
    resample: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load training CSV sequences, calculate global z-score parameters, and scale data."""
    sequences: List[np.ndarray] = []
    latencies: List[float] = []
    labels: List[int] = []

    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)
        if len(df) == 0:
            continue

        latency_val = float(df["latency"].iloc[0]) if "latency" in df.columns else 0.0
        filename = os.path.basename(file).lower()
        if "normal" in filename:
            label = 0
        elif "dyslexia" in filename or "dysgraphia" in filename:
            label = 1
        else:
            continue

        stroke_data = extract_universal_features(df, resample=resample)
        if len(stroke_data) > MAX_TIMESTEPS:
            stroke_data = stroke_data[:MAX_TIMESTEPS]
        else:
            padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9))
            stroke_data = np.vstack((stroke_data, padding))

        sequences.append(stroke_data)
        latencies.append(latency_val)
        labels.append(label)

    X_seq = np.array(sequences)
    X_lat = np.array(latencies)
    y = np.array(labels)

    X_seq_clean = np.nan_to_num(X_seq, nan=0.0, posinf=0.0, neginf=0.0)
    feature_means = np.mean(X_seq_clean, axis=(0, 1))
    feature_stds = np.std(X_seq_clean, axis=(0, 1))
    feature_stds[feature_stds == 0] = 1.0

    X_seq_scaled = (X_seq_clean - feature_means) / feature_stds
    X_lat_scaled = X_lat / 1000.0

    os.makedirs(os.path.dirname(scaler_save_path), exist_ok=True)
    np.savez(scaler_save_path, means=feature_means, stds=feature_stds)
    print(f"Saved global feature scalers to: {scaler_save_path}")

    return X_seq_scaled, X_lat_scaled, y


def load_validation_with_train_scalers(
    data_dir: str = VAL_DATASET_DIR,
    scaler_path: str = SCALER_PATH,
    resample: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load validation cohort using strictly precomputed training scalers to prevent leakage."""
    scaler_data = np.load(scaler_path)
    feature_means = scaler_data["means"]
    feature_stds = scaler_data["stds"]

    sequences: List[np.ndarray] = []
    latencies: List[float] = []
    labels: List[int] = []

    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)
        if len(df) == 0:
            continue

        latency_val = float(df["latency"].iloc[0]) if "latency" in df.columns else 0.0
        filename = os.path.basename(file).lower()
        if "normal" in filename:
            label = 0
        elif "dyslexia" in filename or "dysgraphia" in filename:
            label = 1
        else:
            continue

        stroke_data = extract_universal_features(df, resample=resample)
        if len(stroke_data) > MAX_TIMESTEPS:
            stroke_data = stroke_data[:MAX_TIMESTEPS]
        else:
            padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9))
            stroke_data = np.vstack((stroke_data, padding))

        sequences.append(stroke_data)
        latencies.append(latency_val)
        labels.append(label)

    X_seq = np.array(sequences)
    X_lat = np.array(latencies)
    y = np.array(labels)

    X_seq_clean = np.nan_to_num(X_seq, nan=0.0, posinf=0.0, neginf=0.0)
    X_seq_scaled = (X_seq_clean - feature_means) / feature_stds
    X_lat_scaled = X_lat / 1000.0

    return X_seq_scaled, X_lat_scaled, y


def get_v0_data(X_seq_scaled: np.ndarray, y: np.ndarray):
    """V0: Baseline single-sequence 3 features (velocity, dt, pressure)."""
    X_v0 = X_seq_scaled[:, :, [5, 8, 2]]
    return X_v0, y


def get_v1_data(X_seq_scaled: np.ndarray, X_lat_scaled: np.ndarray, y: np.ndarray):
    """V1: Multi-input (velocity, dt, pressure) + latency."""
    X_v1_seq = X_seq_scaled[:, :, [5, 8, 2]]
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v1_seq, X_lat_scaled], y_time_distributed


def get_v2_data(X_seq_scaled: np.ndarray, X_lat_scaled: np.ndarray, y: np.ndarray):
    """V2: Multi-input 8 standard kinematic sequence + latency."""
    X_v2_seq = X_seq_scaled[:, :, :8]
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v2_seq, X_lat_scaled], y_time_distributed


def unified_predict(
    df: pd.DataFrame,
    model,
    version: str,
    scaler_path: str = SCALER_PATH,
    resample: bool = True,
) -> Tuple[float, List[float]]:
    """Universal inference predicting dysgraphia probability and generating XAI heatmaps."""
    stroke_data = extract_universal_features(df, resample=resample)
    latency_val = float(df["latency"].iloc[0]) / 1000.0 if "latency" in df.columns and len(df) > 0 else 0.0
    stroke_data = np.nan_to_num(stroke_data, nan=0.0, posinf=0.0, neginf=0.0)

    if len(stroke_data) > MAX_TIMESTEPS:
        stroke_data = stroke_data[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9))
        stroke_data = np.vstack((stroke_data, padding))

    scaler_data = np.load(scaler_path)
    feature_means = scaler_data["means"]
    feature_stds = scaler_data["stds"]

    stroke_scaled = (stroke_data - feature_means) / feature_stds
    stroke_scaled = np.expand_dims(stroke_scaled, axis=0)
    latency_tensor = np.expand_dims(np.array([latency_val]), axis=0)

    if version == "v0":
        model_input = stroke_scaled[:, :, [5, 8, 2]]
        prediction = model.predict(model_input, verbose=0)
        global_score = float(prediction[0][0])
        heatmap_array: List[float] = []
    elif version == "v1":
        model_input = stroke_scaled[:, :, [5, 8, 2]]
        prediction = model.predict([model_input, latency_tensor], verbose=0)
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
    elif version == "v2":
        model_input = stroke_scaled[:, :, :8]
        prediction = model.predict([model_input, latency_tensor], verbose=0)
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
    else:
        raise ValueError(f"Unsupported model version: {version}")

    return global_score, heatmap_array
