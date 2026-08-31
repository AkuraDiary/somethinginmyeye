import os
import glob
import numpy as np
import pandas as pd
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from config import MAX_TIMESTEPS

def extract_universal_features(df):
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
    
    universal_df = df[[
        "delta_x", "delta_y", "pressure", "tiltX", "tiltY", "velocity", "acceleration", "jerk",
        "dt"
    ]]
    
    universal_df = universal_df.fillna(0)
    return universal_df.values

def load_and_scale_universal(data_dir="../datasets/"):
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
        elif "dyslexia" in filename or "dysgraphia" in filename: label = 1
        else: continue
            
        stroke_data = extract_universal_features(df)
        
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
    feature_stds[feature_stds == 0] = 1 
    
    X_seq_scaled = (X_seq_clean - feature_means) / feature_stds
    X_lat_scaled = X_lat / 1000.0
    
    os.makedirs("../models", exist_ok=True)
    scaler_path = "../models/feature_scalers.npz"
    if not os.path.exists("../models"):
        os.makedirs("models", exist_ok=True)
        scaler_path = "../models/feature_scalers.npz"
        
    np.savez(scaler_path, means=feature_means, stds=feature_stds)
    print(f"✅ Saved Global Feature Scalers to {scaler_path}")
    
    return X_seq_scaled, X_lat_scaled, y

def load_validation_with_train_scalers(data_dir="../val_datasets/", scaler_path="../models/feature_scalers.npz"):
    if not os.path.exists(scaler_path):
        scaler_path = "../models/feature_scalers.npz"
        
    scaler_data = np.load(scaler_path)
    feature_means = scaler_data['means']
    feature_stds = scaler_data['stds']
        
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
        elif "dyslexia" in filename or "dysgraphia" in filename: label = 1
        else: continue
            
        stroke_data = extract_universal_features(df)
        
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

def train_with_tuning(model, X_train, y_train, X_val, y_val):
    early_stop = EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True, verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6, verbose=1)
    
    history = model.fit(
        X_train, y_train, 
        epochs=50, 
        batch_size=32, 
        validation_data=(X_val, y_val),
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )
    return model, history

def get_v0_data(X_seq_scaled, y):
    X_v0 = X_seq_scaled[:, :, [5, 8, 2]] 
    y_v0 = y 
    return X_v0, y_v0

def get_v1_data(X_seq_scaled, X_lat_scaled, y):
    X_v1_seq = X_seq_scaled[:, :, [5, 8, 2]]
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v1_seq, X_lat_scaled], y_time_distributed

def get_v2_data(X_seq_scaled, X_lat_scaled, y):
    X_v2_seq = X_seq_scaled[:, :, :8] 
    y_time_distributed = np.repeat(np.expand_dims(y, axis=(1, 2)), MAX_TIMESTEPS, axis=1)
    return [X_v2_seq, X_lat_scaled], y_time_distributed

def get_or_create_scalers(data_dir="../datasets/", scaler_path="../models/feature_scalers.npz"):
    if os.path.exists(scaler_path):
        data = np.load(scaler_path)
        return data['means'], data['stds']
    X_seq_scaled, X_lat_scaled, y = load_and_scale_universal(data_dir)
    return None, None

def unified_predict(df, model, version, scaler_path="../models/feature_scalers.npz"):
    stroke_data = extract_universal_features(df)
    latency_val = df["latency"].iloc[0] / 1000.0 if "latency" in df.columns and len(df) > 0 else 0.0
    stroke_data = np.nan_to_num(stroke_data, nan=0.0, posinf=0.0, neginf=0.0)
    if len(stroke_data) > MAX_TIMESTEPS:
        stroke_data = stroke_data[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9))
        stroke_data = np.vstack((stroke_data, padding))
    try:
        scaler_data = np.load(scaler_path)
        feature_means = scaler_data['means']
        feature_stds = scaler_data['stds']
    except Exception as e:
        print(f"Error loading {scaler_path}. Did you run training/metrics to generate it?")
        raise e
    stroke_scaled = (stroke_data - feature_means) / feature_stds
    stroke_scaled = np.expand_dims(stroke_scaled, axis=0)
    latency_val = np.expand_dims(np.array([latency_val]), axis=0)
    if version == "v0":
        model_input = stroke_scaled[:, :, [5, 8, 2]]
        prediction = model.predict(model_input, verbose=0)
        global_score = float(prediction[0][0])
        heatmap_array = []
    elif version == "v1":
        model_input = stroke_scaled[:, :, [5, 8, 2]]
        prediction = model.predict([model_input, latency_val], verbose=0)
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
    elif version == "v2":
        model_input = stroke_scaled[:, :, :8]
        prediction = model.predict([model_input, latency_val], verbose=0)
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
    return global_score, heatmap_array
