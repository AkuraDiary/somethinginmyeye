"""
Exports the Elkinematics V2 Bi-LSTM model to ONNX format and verifies numerical parity
with ONNX Runtime.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

# Add venv site-packages if running with system python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "venv" / "lib" / "python3.12" / "site-packages"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

os.environ["KERAS_HOME"] = "/tmp/keras"
os.environ["MPLCONFIGDIR"] = "/tmp/mplconfig"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np
import onnx
import onnxruntime as ort
import tensorflow as tf
import tf2onnx

from config import (
    FEATURES,
    FEATURE_NAMES,
    LATENCY_DIM,
    MAX_TIMESTEPS,
    MODEL_DIR,
    MODEL_PATHS,
    PROJECT_ROOT,
    SCALER_JSON_PATH,
    SCALER_PATH,
    WEB_SCALER_JSON_PATH,
)

MODEL_KERAS_PATH = MODEL_PATHS["v2"]
MODEL_ONNX_PATH = os.path.join(MODEL_DIR, "elkinematicV2.onnx")
WEB_MODEL_ONNX_PATH = os.path.join(PROJECT_ROOT, "data_collector", "models", "elkinematicV2.onnx")


def export_elkinematic_v2_to_onnx() -> str:
    """Exports elkinematicV2.keras to ONNX and synchronizes to web models directory."""
    print(f"Loading Keras model from: {MODEL_KERAS_PATH}")
    if not os.path.exists(MODEL_KERAS_PATH):
        raise FileNotFoundError(f"Model file not found at: {MODEL_KERAS_PATH}")

    model = tf.keras.models.load_model(MODEL_KERAS_PATH)
    print("Keras model loaded successfully.")

    input_signature = [
        tf.TensorSpec(shape=(None, MAX_TIMESTEPS, FEATURES), dtype=tf.float32, name="kinematics_input"),
        tf.TensorSpec(shape=(None, LATENCY_DIM), dtype=tf.float32, name="latency_input"),
    ]

    print("Converting model to ONNX format (opset 15)...")
    os.makedirs(os.path.dirname(MODEL_ONNX_PATH), exist_ok=True)
    onnx_model, _ = tf2onnx.convert.from_keras(
        model,
        input_signature=input_signature,
        opset=15,
        output_path=MODEL_ONNX_PATH,
    )

    onnx_size_kb = os.path.getsize(MODEL_ONNX_PATH) / 1024.0
    print(f"ONNX model saved to: {MODEL_ONNX_PATH}")
    print(f"Model file size: {onnx_size_kb:.2f} KB")

    # Mirror copy to web models directory for browser inference
    os.makedirs(os.path.dirname(WEB_MODEL_ONNX_PATH), exist_ok=True)
    shutil.copy2(MODEL_ONNX_PATH, WEB_MODEL_ONNX_PATH)
    print(f"Mirrored ONNX model to web directory: {WEB_MODEL_ONNX_PATH}")

    # Export scaler configuration to JSON for browser-native client-side normalization
    if os.path.exists(SCALER_PATH):
        scaler_data = np.load(SCALER_PATH)
        scaler_dict = {
            "feature_names": FEATURE_NAMES,
            "means": [float(m) for m in scaler_data["means"][:FEATURES]],
            "stds": [float(s) for s in scaler_data["stds"][:FEATURES]],
            "all_means": [float(m) for m in scaler_data["means"]],
            "all_stds": [float(s) for s in scaler_data["stds"]],
            "max_timesteps": MAX_TIMESTEPS,
            "features_dim": FEATURES,
        }
        with open(SCALER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(scaler_dict, f, indent=2)
        print(f"Exported scaler parameters to: {SCALER_JSON_PATH}")
        with open(WEB_SCALER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(scaler_dict, f, indent=2)
        print(f"Mirrored scaler parameters to: {WEB_SCALER_JSON_PATH}")

    # Numerical Parity Verification with ONNX Runtime
    print("\nVerifying numerical parity with ONNX Runtime...")
    ort_session = ort.InferenceSession(MODEL_ONNX_PATH)

    np.random.seed(42)
    test_kinematics = np.random.randn(4, MAX_TIMESTEPS, FEATURES).astype(np.float32)
    test_latency = np.array([[0.5], [1.2], [2.0], [0.1]], dtype=np.float32)

    # 1. Keras inference
    keras_pred = model.predict([test_kinematics, test_latency], verbose=0)

    # 2. ONNX Runtime inference
    ort_inputs = {
        "kinematics_input": test_kinematics,
        "latency_input": test_latency,
    }
    ort_outputs = ort_session.run(None, ort_inputs)
    ort_pred = ort_outputs[0]

    max_diff = float(np.max(np.abs(keras_pred - ort_pred)))
    mean_diff = float(np.mean(np.abs(keras_pred - ort_pred)))

    print(f"Max absolute discrepancy:  {max_diff:.2e}")
    print(f"Mean absolute discrepancy: {mean_diff:.2e}")

    if max_diff < 1e-4:
        print("Verification SUCCESS: Perfect numerical parity between Keras and ONNX Runtime!")
    else:
        print("Warning: Discrepancy exceeds standard tolerance (1e-4).")

    return MODEL_ONNX_PATH


if __name__ == "__main__":
    export_elkinematic_v2_to_onnx()
