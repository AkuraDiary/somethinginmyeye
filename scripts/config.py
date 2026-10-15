"""Centralized configuration for the Elkinematics ML & Screening Pipeline."""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

MAX_TIMESTEPS = 500
FEATURES = 8

DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets")
VAL_DATASET_DIR = os.path.join(PROJECT_ROOT, "val_datasets")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

MODEL_PATHS = {
    "v0": os.path.join(MODEL_DIR, "elkinematic.keras"),
    "v1": os.path.join(MODEL_DIR, "elkinematicV1.keras"),
    "v2": os.path.join(MODEL_DIR, "elkinematicV2.keras"),
}

SCALER_PATH = os.path.join(MODEL_DIR, "feature_scalers.npz")
FORCE_RETRAIN = False