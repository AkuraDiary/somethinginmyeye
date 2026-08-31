import sys
import argparse
import numpy as np
import tensorflow as tf
from config import MAX_TIMESTEPS, MODEL_PATHS 
import pandas as pd

def predict_sample(model_version, csv_filepath):
    # 1. Peta Model otomatis ditarik dari config.py
    filepath = MODEL_PATHS.get(model_version.lower())
    if not filepath:
        print(f"Error: Model versi '{model_version}' tidak terdaftar di config.py!")
        return
        
    print(f"Memuat Model {model_version.upper()}) dari: {filepath}")
    
    try:
        model = tf.keras.models.load_model(filepath)
    except Exception as e:
        print(f"Error: Model tidak ditemukan di {filepath}. Pastikan Anda sudah melatihnya!")
        return
        
    print(f"\nMenganalisis sampel: {csv_filepath}")
    df =  pd.read_csv(csv_filepath) 
    from universal_pipeline import unified_predict
    try:
        global_score, heatmap_array = unified_predict(df, model, model_version.lower(), scaler_path="../models/feature_scalers.npz")
    except Exception as e:
        print(f"Error during prediction: {e}")
        return
        
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