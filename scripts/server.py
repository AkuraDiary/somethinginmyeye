"""
Lightweight Flask Server for Elkinematics Data Collection & Live Screening.
"""

from __future__ import annotations

import base64
import csv
import gc
import os
import sys
import time
from pathlib import Path

# Ensure script directory and project root are on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Lightweight Environment Configuration
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from flask import Flask, jsonify, request
import pandas as pd
import tensorflow as tf

from config import DATASET_DIR, MODEL_PATHS, PROJECT_ROOT, SCALER_PATH
from universal_pipeline import unified_predict

# Configure TensorFlow threading for low memory consumption
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.get_logger().setLevel("ERROR")

STATIC_DIR = os.path.join(PROJECT_ROOT, "data_collector")
app = Flask(__name__, static_folder=STATIC_DIR)

# Initialize Active Production Model (V2 Bi-LSTM)
print("📥 Loading AI Model V2 (Bi-LSTM)...")
try:
    model = tf.keras.models.load_model(MODEL_PATHS["v2"])
    print(f"✅ Loaded Model V2 from {MODEL_PATHS['v2']}")
except Exception as e:
    print(f"⚠️ Warning: Model V2 failed to load from {MODEL_PATHS['v2']}: {e}")
    model = None

os.makedirs(DATASET_DIR, exist_ok=True)


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def serve_html():
    """Serves the data collection interface."""
    return app.send_static_file("index.html")


@app.route("/screen")
def serve_screening():
    """Serves the live explainable screening dashboard."""
    return app.send_static_file("screening.html")


@app.route("/save_data", methods=["POST"])
def save_data():
    """Receives and stores raw stroke CSV data and image from the web canvas."""
    data = request.json or {}
    prefix = data.get("prefix", "sample")
    stroke_data = data.get("strokes", [])
    image_data_url = data.get("image", "")

    timestamp = int(time.time())
    base_filename = f"{prefix}_{timestamp}"

    if stroke_data:
        csv_path = os.path.join(DATASET_DIR, f"{base_filename}.csv")
        keys = stroke_data[0].keys()
        with open(csv_path, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(stroke_data)

    if image_data_url:
        _, encoded = image_data_url.split(",", 1)
        img_data = base64.b64decode(encoded)
        png_path = os.path.join(DATASET_DIR, f"{base_filename}.png")
        with open(png_path, "wb") as f:
            f.write(img_data)

    print(f"💾 Saved sample '{base_filename}' to datasets.")
    return jsonify({"message": "Successfully saved sample! Thank you for your contribution."})


@app.route("/analyze", methods=["POST"])
def analyze_live():
    """Performs real-time explainable kinematic inference."""
    if model is None:
        return jsonify({"error": "Model not loaded on server."}), 500

    stroke_data = request.json or []
    if not stroke_data:
        return jsonify({"error": "Empty stroke data provided."}), 400

    df = pd.DataFrame(stroke_data)

    try:
        global_score, heatmap_array = unified_predict(
            df=df,
            model=model,
            version="v2",
            scaler_path=SCALER_PATH,
        )
    except Exception as e:
        print(f"❌ Inference error: {e}")
        return jsonify({"error": f"Failed to run inference: {str(e)}"}), 500

    # Purge memory after inference to maintain low resource profile
    gc.collect()

    return jsonify({
        "probability": float(global_score),
        "is_dyslexic": bool(global_score > 0.5),
        "heatmap": heatmap_array,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
