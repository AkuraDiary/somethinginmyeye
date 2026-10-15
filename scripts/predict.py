"""
CLI Inference Script for Elkinematics Dysgraphia Screening.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure script directory and project root are on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import tensorflow as tf

from config import MAX_TIMESTEPS, MODEL_PATHS, SCALER_PATH
from universal_pipeline import unified_predict


def predict_sample(model_version: str, csv_filepath: str) -> None:
    version_key = model_version.lower()
    filepath = MODEL_PATHS.get(version_key)
    if not filepath or not os.path.exists(filepath):
        print(f"❌ Error: Model '{model_version}' not found at: {filepath}")
        return

    print(f"📥 Loading Model ({model_version.upper()}) from: {filepath}")
    try:
        model = tf.keras.models.load_model(filepath)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    print(f"📄 Analyzing handwriting stroke sample: {csv_filepath}")
    try:
        df = pd.read_csv(csv_filepath)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return

    try:
        global_score, heatmap_array = unified_predict(
            df=df,
            model=model,
            version=version_key,
            scaler_path=SCALER_PATH,
        )
    except Exception as e:
        print(f"❌ Error during prediction inference: {e}")
        return

    confidence = global_score * 100.0

    print("\n" + "=" * 48)
    print(f" 🔍 ELKINEMATICS AI SCREENING ({model_version.upper()})")
    print("=" * 48)
    print(f"Risk Score : {global_score:.4f}")
    if global_score > 0.5:
        print(f"Status     : Atypical / Dysgraphic Pattern Detected")
        print(f"Confidence : {confidence:.1f}%")
    else:
        print(f"Status     : Typical / Normal Handwriting Pattern")
        print(f"Confidence : {100.0 - confidence:.1f}%")
    print("=" * 48 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Elkinematics Kinematic Inference CLI")
    parser.add_argument(
        "-model",
        type=str,
        choices=["v0", "v1", "v2"],
        default="v2",
        help="Model version to use for inference: v0 (Baseline), v1 (CNN+XAI), or v2 (BiLSTM)",
    )
    parser.add_argument(
        "-file",
        type=str,
        required=True,
        help="Path to handwriting stroke CSV data file",
    )
    args = parser.parse_args()
    predict_sample(args.model, args.file)