import os
import glob
import numpy as np
import pandas as pd
from config import MAX_TIMESTEPS

def extract_universal_features(df):
    """
    Mengekstrak SEMUA fitur (baik untuk V0, V1, maupun V2).
    Kita akan mengambil 9 parameter agar kompatibel dengan sejarah RAD Anda.
    """
    if "touching" not in df.columns: df["touching"] = True
    for col in ["tiltX", "tiltY", "latency"]:
        if col not in df.columns: df[col] = 0
        
    df["dt"] = df["time"].diff().fillna(1)
    df.loc[df["dt"] == 0, "dt"] = 1
    
    df["delta_x"] = df["x"].diff().fillna(0)
    df["delta_y"] = df["y"].diff().fillna(0)
    df["distance"] = np.sqrt(df["delta_x"]**2 + df["delta_y"]**2)
    df["velocity"] = df["distance"] / df["dt"]
    df["acceleration"] = df["velocity"].diff().fillna(0) / df["dt"]
    df["jerk"] = df["acceleration"].diff().fillna(0) / df["dt"]
    
    # KITA EKSTRAK 9 FITUR SEKALIGUS!
    # Indeks 0, 1, 2 adalah fitur klasik V0/V1 (Duration/dt, Pressure, Velocity)
    # Indeks 3 sampai 8 adalah tambahan fitur Golden untuk V2
    universal_df = df[[
        "dt", "pressure", "velocity",           # Index 0, 1, 2 (Untuk V0 & V1)
        "delta_x", "delta_y", "tiltX",          # Index 3, 4, 5
        "tiltY", "acceleration", "jerk"         # Index 6, 7, 8
    ]]
    
    universal_df = universal_df.fillna(0)
    return universal_df.values

def load_and_scale_universal(data_dir="datasets/"):
    """
    Me-load semua data, memotong (padding), dan MENGAPLIKASIKAN Z-SCORE NORMALIZATION
    secara universal sebelum masuk ke wrapper model.
    """
    sequences = []
    latencies = []
    labels = []
    
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    for file in csv_files:
        df = pd.read_csv(file)
        if len(df) == 0: continue
            
        latency_val = df["latency"].iloc[0] if "latency" in df.columns else 0
        
        filename = os.path.basename(file).lower()
        if "normal" in filename: label = 0
        elif "dyslexia" in filename: label = 1
        else: continue
            
        stroke_data = extract_universal_features(df)
        
        # Padding
        if len(stroke_data) > MAX_TIMESTEPS:
            stroke_data = stroke_data[:MAX_TIMESTEPS]
        else:
            padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9)) # 9 Fitur total
            stroke_data = np.vstack((stroke_data, padding))
            
        sequences.append(stroke_data)
        latencies.append(latency_val)
        labels.append(label)

    # Convert to Numpy
    X_seq = np.array(sequences)
    X_lat = np.array(latencies)
    y = np.array(labels)
    
    # ----------------------------------------------------
    # UNIVERSAL SCALING PIPELINE
    # ----------------------------------------------------
    X_seq_clean = np.nan_to_num(X_seq, nan=0.0, posinf=0.0, neginf=0.0)
    feature_means = np.mean(X_seq_clean, axis=(0, 1))
    feature_stds = np.std(X_seq_clean, axis=(0, 1))
    feature_stds[feature_stds == 0] = 1 # Hindari divide-by-zero
    
    X_seq_scaled = (X_seq_clean - feature_means) / feature_stds
    X_lat_scaled = X_lat / 1000.0
    
    return X_seq_scaled, X_lat_scaled, y

# ====================================================
# THE ADAPTERS (Memotong data sesuai Model)
# ====================================================

def get_v0_data(X_seq_scaled, y):
    """ V0: Input 3 fitur klasik, Output skor tunggal. """
    X_v0 = X_seq_scaled[:, :, :3] # Hanya ambil Index 0, 1, 2 (dt, pressure, velocity)
    y_v0 = y # Skor biner tunggal (Samples, 1)
    return X_v0, y_v0

def get_v1_data(X_seq_scaled, X_lat_scaled, y):
    """ V1: Input 3 fitur + Latency, Output TimeDistributed """
    X_v1_seq = X_seq_scaled[:, :, :3] # Hanya ambil Index 0, 1, 2
    # Expand y jadi (Samples, 500, 1) untuk TimeDistributed
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v1_seq, X_lat_scaled], y_time_distributed

def get_v2_data(X_seq_scaled, X_lat_scaled, y):
    """ V2: Input Golden 8 (Hilangkan dt, pakai 8 parameter lainnya) + Latency, Output TimeDistributed """
    # Ambil index 1 sampai 8 (buang index 0 'dt' karena model V3 Anda hanya pakai 8 fitur kinematik murni)
    X_v2_seq = X_seq_scaled[:, :, 1:9] 
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v2_seq, X_lat_scaled], y_time_distributed