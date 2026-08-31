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
        # Index 0 s/d 7 (Golden 8 in model V2/V3) 
        "delta_x", "delta_y", "pressure", "tiltX", "tiltY", "velocity", "acceleration", "jerk",
        # Index 8 (Durasi/dt khusus untuk V0 dan V1) 
        "dt"
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
        elif "dysgraphia" in filename: label = 1
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
    
    # Save the global scalers for the live web server!
    os.makedirs("../models", exist_ok=True)
    np.savez("../models/feature_scalers.npz", means=feature_means, stds=feature_stds)
    print(f"✅ Saved Global Feature Scalers to ../models/feature_scalers.npz")
    
    return X_seq_scaled, X_lat_scaled, y

# ====================================================
# THE ADAPTERS (Memotong data sesuai Model)
# ====================================================

def get_v0_data(X_seq_scaled, y):
    """ V0: [velocity, duration, pressure] -> Index 5, 8, 2 """
    X_v0 = X_seq_scaled[:, :, [5, 8, 2]] 
    y_v0 = y 
    return X_v0, y_v0
def get_v1_data(X_seq_scaled, X_lat_scaled, y):
    """ V1: [velocity, duration, pressure] -> Index 5, 8, 2 + Latency """
    X_v1_seq = X_seq_scaled[:, :, [5, 8, 2]]
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v1_seq, X_lat_scaled], y_time_distributed
def get_v2_data(X_seq_scaled, X_lat_scaled, y):
    """ V2: Ambil 8 fitur pertama persis seperti saat ditraining! """
    X_v2_seq = X_seq_scaled[:, :, :8] 
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v2_seq, X_lat_scaled], y_time_distributed
def get_or_create_scalers(data_dir="../datasets/", scaler_path="../models/feature_scalers.npz"):
    """
    Computes or loads the global feature scalers for live inference.
    """
    if os.path.exists(scaler_path):
        data = np.load(scaler_path)
        return data['means'], data['stds']
        
    print("⚠️ Scalers not found! Computing global scale from dataset...")
    # Compute them by loading the dataset
    X_seq_scaled, X_lat_scaled, y = load_and_scale_universal(data_dir)
    # The load_and_scale_universal function needs to save them! We'll override it below.
    return None, None

def unified_predict(df, model, version, scaler_path="../models/feature_scalers.npz"):
    """
    Universal prediction function for ANY version of the model.
    Loads the true global scalers so the math exactly matches the training phase.
    """
    # 1. Extract Raw Features
    stroke_data = extract_universal_features(df)
    
    # 2. Extract Latency
    latency_val = df["latency"].iloc[0] / 1000.0 if "latency" in df.columns and len(df) > 0 else 0.0
    
    # 3. Clean and Pad Sequence
    stroke_data = np.nan_to_num(stroke_data, nan=0.0, posinf=0.0, neginf=0.0)
    if len(stroke_data) > MAX_TIMESTEPS:
        stroke_data = stroke_data[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9))
        stroke_data = np.vstack((stroke_data, padding))
        
    # 4. Load Global Scalers (CRITICAL BUG FIX)
    try:
        scaler_data = np.load(scaler_path)
        feature_means = scaler_data['means']
        feature_stds = scaler_data['stds']
    except Exception as e:
        print(f"Error loading {scaler_path}. Did you run training/metrics to generate it?")
        raise e
        
    # 5. Apply Global Z-Score Scaling
    stroke_scaled = (stroke_data - feature_means) / feature_stds
    
    # We must add the batch dimension (1, 500, 9)
    stroke_scaled = np.expand_dims(stroke_scaled, axis=0)
    latency_val = np.expand_dims(np.array([latency_val]), axis=0)
    
    # 6. Route to the correct Model Input Shape
    if version == "v0":
        # V0: [velocity, duration, pressure] -> Index 5, 8, 2
        model_input = stroke_scaled[:, :, [5, 8, 2]]
        prediction = model.predict(model_input, verbose=0)
        global_score = float(prediction[0][0])
        heatmap_array = [] # V0 has no heatmap
        
    elif version == "v1":
        # V1: Index 5, 8, 2 + Latency
        model_input = stroke_scaled[:, :, [5, 8, 2]]
        prediction = model.predict([model_input, latency_val], verbose=0)
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
        
    elif version == "v2":
        # V2: First 8 features + Latency
        model_input = stroke_scaled[:, :, :8]
        prediction = model.predict([model_input, latency_val], verbose=0)
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
        
    return global_score, heatmap_array

