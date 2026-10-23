"""
Lightweight Flask Server for Elkinematics Data Collection & Live Screening.
"""

from __future__ import annotations

import base64
import csv
import gc
import json
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

from config import (
    DATASET_DIR,
    DEFAULT_INFERENCE_BACKEND,
    ELKINEMATIC_ONNX_PATH,
    MODEL_PATHS,
    PROJECT_ROOT,
    SCALER_PATH,
)
from sld_integrator import evaluate_sld_differential
from universal_pipeline import unified_predict


# Configure TensorFlow threading for low memory consumption
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.get_logger().setLevel("ERROR")

STATIC_DIR = os.path.join(PROJECT_ROOT, "data_collector")
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

# Initialize Keras Model (V2 Bi-LSTM)
print("Loading Keras AI Model V2 (Bi-LSTM)...")
try:
    model = tf.keras.models.load_model(MODEL_PATHS["v2"])
    print(f"Loaded Keras Model V2 from {MODEL_PATHS['v2']}")
except Exception as e:
    print(f"Warning: Keras Model V2 failed to load from {MODEL_PATHS['v2']}: {e}")
    model = None

# Initialize ONNX Runtime Session (V2 Bi-LSTM)
print("Loading ONNX Model V2 (Bi-LSTM)...")
try:
    import onnxruntime as ort
    if os.path.exists(ELKINEMATIC_ONNX_PATH):
        onnx_session = ort.InferenceSession(ELKINEMATIC_ONNX_PATH)
        print(f"Loaded ONNX Model V2 from {ELKINEMATIC_ONNX_PATH}")
    else:
        print(f"Warning: ONNX model file not found at {ELKINEMATIC_ONNX_PATH}")
        onnx_session = None
except Exception as e:
    print(f"Warning: ONNX Model V2 failed to load: {e}")
    onnx_session = None

CURRENT_BACKEND = DEFAULT_INFERENCE_BACKEND
print(f"Default Active Inference Backend: {CURRENT_BACKEND}")

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

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        metadata = dict(metadata)
        metadata["server_timestamp"] = timestamp
        metadata["base_filename"] = base_filename
        meta_path = os.path.join(DATASET_DIR, f"{base_filename}.meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Saved sample '{base_filename}' to datasets.")
    return jsonify({"message": "Successfully saved sample! Thank you for your contribution."})


@app.route("/backend", methods=["GET", "POST"])
def manage_backend():
    """Toggles or queries active inference backend ('keras' or 'onnx')."""
    global CURRENT_BACKEND
    if request.method == "POST":
        data = request.json or {}
        new_backend = str(data.get("backend", "")).lower().strip()
        if new_backend in ("keras", "onnx"):
            if new_backend == "keras" and model is None:
                return jsonify({"error": "Keras model not loaded on server."}), 400
            if new_backend == "onnx" and onnx_session is None:
                return jsonify({"error": "ONNX model not loaded on server."}), 400
            CURRENT_BACKEND = new_backend
            print(f"Active inference backend toggled to: {CURRENT_BACKEND}")
            return jsonify({
                "message": f"Successfully switched backend to {CURRENT_BACKEND}",
                "backend": CURRENT_BACKEND,
                "keras_loaded": model is not None,
                "onnx_loaded": onnx_session is not None,
            })
        return jsonify({"error": f"Invalid backend: '{new_backend}'. Choose 'keras' or 'onnx'."}), 400

    return jsonify({
        "backend": CURRENT_BACKEND,
        "keras_loaded": model is not None,
        "onnx_loaded": onnx_session is not None,
        "available_backends": ["keras", "onnx"],
    })


@app.route("/analyze", methods=["POST"])
def analyze_live():
    """Performs real-time explainable dual-stream SLD differential inference."""
    if model is None and onnx_session is None:
        return jsonify({"error": "No inference model loaded on server."}), 500

    payload = request.json or {}
    if isinstance(payload, list):
        stroke_data = payload
        expected_prompt = "bebek"
        decoded_text = None
        enable_grammar = False
        requested_backend = CURRENT_BACKEND
    elif isinstance(payload, dict):
        stroke_data = payload.get("strokes", [])
        expected_prompt = payload.get("prompt", "bebek")
        decoded_text = payload.get("decoded_text", None)
        enable_grammar = payload.get("enable_grammar", False)
        requested_backend = str(payload.get("backend", CURRENT_BACKEND)).lower().strip()
    else:
        return jsonify({"error": "Invalid request payload format."}), 400

    if not stroke_data:
        return jsonify({"error": "Empty stroke data provided."}), 400

    if requested_backend not in ("keras", "onnx"):
        requested_backend = CURRENT_BACKEND

    active_model = onnx_session if requested_backend == "onnx" else model
    active_backend = requested_backend
    if active_model is None:
        # Graceful fallback to whichever engine is loaded
        if requested_backend == "onnx" and model is not None:
            active_model = model
            active_backend = "keras"
        elif requested_backend == "keras" and onnx_session is not None:
            active_model = onnx_session
            active_backend = "onnx"
        else:
            return jsonify({"error": f"Model for backend '{requested_backend}' is unavailable."}), 500

    df = pd.DataFrame(stroke_data)

    # Populate top-level latency fallback if missing in individual stroke points
    if isinstance(payload, dict) and "latency" in payload:
        if "latency" not in df.columns or (len(df) > 0 and float(df["latency"].iloc[0]) == 0.0):
            df["latency"] = float(payload.get("latency", 0.0))

    try:
        sld_results = evaluate_sld_differential(
            df=df,
            model=active_model,
            expected_prompt=expected_prompt,
            decoded_text=decoded_text,
            enable_grammar=enable_grammar,
            scaler_path=SCALER_PATH,
            backend=active_backend,
        )
    except Exception as e:
        print(f"Inference error: {e}")
        return jsonify({"error": f"Failed to run inference: {str(e)}"}), 500

    # Maintain backward compatibility fields for legacy clients
    sld_results["probability"] = float(sld_results["dysgraphia_risk_percentage"]) / 100.0
    sld_results["backend_used"] = active_backend
    sld_results["engine_type"] = "ONNX Runtime" if active_backend == "onnx" else "Keras 3 (TensorFlow)"

    # Purge memory after inference to maintain low resource profile
    gc.collect()

    return jsonify(sld_results)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
