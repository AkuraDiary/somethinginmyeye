import sys
import argparse
import numpy as np
import tensorflow as tf
from preprocess import analyze_stroke_data
from config import MAX_TIMESTEPS, MODEL_PATHS 

def predict_sample(model_version, csv_filepath):
    # 1. Peta Model otomatis ditarik dari config.py
    filepath = MODEL_PATHS.get(model_version.lower())
    if not filepath:
        print(f"Error: Model versi '{model_version}' tidak terdaftar di config.py!")
        return
        
    print(f"Memuat otak AI (Model {model_version.upper()}) dari: {filepath}")
    
    try:
        model = tf.keras.models.load_model(filepath)
    except Exception as e:
        print(f"Error: Model tidak ditemukan di {filepath}. Pastikan Anda sudah melatihnya!")
        return
        
    print(f"\nMenganalisis sampel: {csv_filepath}")
    processed_df = analyze_stroke_data(csv_filepath)
    
    # 2. Ekstraksi Universal (Membuat 9 Parameter Utama)
    if "touching" not in processed_df.columns: processed_df["touching"] = True
    for col in ["tiltX", "tiltY", "latency"]:
        if col not in processed_df.columns: processed_df[col] = 0
        
    processed_df["dt"] = processed_df["time"].diff().fillna(1)
    processed_df.loc[processed_df["dt"] == 0, "dt"] = 1
    processed_df["delta_x"] = processed_df["x"].diff().fillna(0)
    processed_df["delta_y"] = processed_df["y"].diff().fillna(0)
    processed_df["distance"] = np.sqrt(processed_df["delta_x"]**2 + processed_df["delta_y"]**2)
    processed_df["velocity"] = processed_df["distance"] / processed_df["dt"]
    processed_df["acceleration"] = processed_df["velocity"].diff().fillna(0) / processed_df["dt"]
    processed_df["jerk"] = processed_df["acceleration"].diff().fillna(0) / processed_df["dt"]
    
    universal_features = processed_df[[
        "dt", "pressure", "velocity", 
        "delta_x", "delta_y", "tiltX", 
        "tiltY", "acceleration", "jerk"
    ]].values
    
    latency_val = processed_df['latency'].iloc[0] / 1000.0 
    
    # 3. Clean & Pad (500 Timesteps)
    universal_features = np.nan_to_num(universal_features, nan=0.0, posinf=0.0, neginf=0.0)
    
    if len(universal_features) > MAX_TIMESTEPS:
        universal_features = universal_features[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(universal_features), 9))
        universal_features = np.vstack((universal_features, padding))
        
    # 4. Z-Score Scaling
    feature_means = np.mean(universal_features, axis=0)
    feature_stds = np.std(universal_features, axis=0)
    feature_stds[feature_stds == 0] = 1 
    universal_scaled = (universal_features - feature_means) / feature_stds
    
    # 5. Routing Input berdasarkan Versi Model
    if model_version == "v0":
        model_input = universal_scaled[:, :3]
        prediction = model.predict(np.array([model_input]))
        global_score = float(prediction[0][0])
        
    elif model_version == "v1":
        model_input = universal_scaled[:, :3]
        prediction = model.predict([np.array([model_input]), np.array([latency_val])])
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
        
    elif model_version == "v2":
        model_input = universal_scaled[:, 1:9]
        prediction = model.predict([np.array([model_input]), np.array([latency_val])])
        heatmap_array = prediction[0].flatten().tolist()
        global_score = sum(heatmap_array) / len(heatmap_array)
        
    confidence = global_score * 100
    
    # 6. Tampilkan Hasil UI
    print("\n" + "="*45)
    print(f" 🔍 AI SCREENING RESULT (MODEL {model_version.upper()})")
    print("="*45)
    print(f"Global Score : {global_score:.4f}")
    
    if global_score > 0.5:
        print(f"Atypical/Dyslexic Pattern Detected")
        print(f"Probability: {confidence:.1f}%")
    else:
        print(f"Normal Handwriting Pattern")
        print(f"Probability: {100 - confidence:.1f}%")
    print("="*45 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dyslexia Predictor Universal Runner")
    parser.add_argument("-model", type=str, choices=["v0", "v1", "v2"], required=True, 
                        help="Pilih versi model: v0, v1, atau v2")
    parser.add_argument("-file", type=str, required=True, 
                        help="Path absolut atau relatif ke file CSV")
    
    args = parser.parse_args()
    predict_sample(args.model, args.file)