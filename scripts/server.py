
# ENVIRONMENT LIGHTWEIGHT CONFIGURATION 

import os
import sys

# 1. Strip out heavy GPU scanning & CUDA graph tracking
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 

# 2. Disable internal oneDNN cache optimizations that spin up multiple threads
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# 3. Prevent TensorFlow from pre-allocating large memory structures
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# 4. Limit CPU threading overhead (vital for low-resource Celeron chips)
os.environ['TF_NUM_INTEROP_THREADS'] = '1'
os.environ['TF_NUM_INTRAOP_THREADS'] = '1'

# 5. Tell TF not to load heavy internal debugging log structures into RAM
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import base64
from config import MAX_TIMESTEPS, MODEL_PATHS
import gc  # Garbage collector interface to force purge RAM

# Force TensorFlow threading limit programmatically
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.get_logger().setLevel('ERROR')

app = Flask(__name__, static_folder='../data_collector')

# --- INITIALIZE MODEL ---
print("Loading AI Model V2 (LSTM)...")
try:
    # Use V2 (elkinematicV3.keras)
    model = tf.keras.models.load_model(MODEL_PATHS['v2'])
except Exception as e:
    print(f"Model V2 failed to load from {MODEL_PATHS['v2']}. Make sure it exists!")
    model = None

# Automatically create a dataset folder if it doesn't exist
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(SCRIPT_DIR, '..', 'datasets')
os.makedirs(DATASETS_DIR, exist_ok=True)

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def serve_html():
    # Keep the original data collector alive at the root
    return app.send_static_file('index.html')

@app.route('/screen')
def serve_screening():
    # The new Screening Dashboard UI
    return app.send_static_file('screening.html')

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    mode = data.get('mode', 'normal')
    prefix = data.get('prefix', 'sample')
    stroke_data = data.get('strokes', [])
    image_dataURL = data.get('image', '')
    
    timestamp = int(time.time())
    base_filename = f"{prefix}_{timestamp}"
    
    if stroke_data:
        import csv
        csv_path = os.path.join(DATASETS_DIR, f"{base_filename}.csv")
        if len(stroke_data) > 0:
            keys = stroke_data[0].keys()
            with open(csv_path, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(stroke_data)
                
    if image_dataURL:
        header, encoded = image_dataURL.split(",", 1)
        img_data = base64.b64decode(encoded)
        png_path = os.path.join(DATASETS_DIR, f"{base_filename}.png")
        with open(png_path, "wb") as f:
            f.write(img_data)
            
    print(f"💾 Saved {base_filename} to server!")
    return jsonify({"message": f"Successfully saved sample! Thank You For Your Contribution ❤️ !!!"})


@app.route('/analyze', methods=['POST'])
def analyze_live():
    if model is None:
        return jsonify({"error": "Model not loaded on server."}), 500
        
    # 1. Receive the stroke data
    stroke_data = request.json
    df = pd.DataFrame(stroke_data)
    
    # 2. Extract Features, Scale Globally, and Predict using Unified Pipeline
    from universal_pipeline import unified_predict
    try:
        global_score, heatmap_array = unified_predict(df, model, "v2", scaler_path="../models/feature_scalers.npz")
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to run unified prediction. Ensure models/feature_scalers.npz exists."}), 500
    
    # 7. RECLAIM MEMORY IMMEDIATELY AFTER AN ANALYSIS RUN
    # This prevents RAM stacking if multiple users call the route back-to-back.
    gc.collect()
    
    return jsonify({
        "probability": float(global_score),
        "is_dyslexic": bool(global_score > 0.5),
        "heatmap": heatmap_array
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
