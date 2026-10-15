"""
Centralized Configuration for Elkinematics ML & Screening Pipeline.
Contains all dataset paths, model paths, dimensions, and training/architecture hyperparameters.
"""

from __future__ import annotations

import os

# Base Directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets")
VAL_DATASET_DIR = os.path.join(PROJECT_ROOT, "val_datasets")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
SAMPLE_DIR = os.path.join(PROJECT_ROOT, "sample")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "archive")

# Model Filepaths
MODEL_PATHS = {
    "v0": os.path.join(MODEL_DIR, "elkinematic.keras"),
    "v1": os.path.join(MODEL_DIR, "elkinematicV1.keras"),
    "v2": os.path.join(MODEL_DIR, "elkinematicV2.keras"),
}

SCALER_PATH = os.path.join(MODEL_DIR, "feature_scalers.npz")
TFLITE_PATH = os.path.join(MODEL_DIR, "elkinematicliteV2.tflite")

# Feature Dimensions & Sequences
MAX_TIMESTEPS = 500
FEATURES = 8             # 8 Features : delta_x, delta_y, pressure, tiltX, tiltY, velocity, acceleration, jerk
V0_FEATURES = 3          # Baseline: velocity, dt, pressure
LATENCY_DIM = 1          # Milliseconds latency between prompt and first pen stroke

FEATURE_NAMES = [
    "delta_x", "delta_y", "pressure", "tiltX", "tiltY",
    "velocity", "acceleration", "jerk"
]

# Training & Optimization Hyperparameters
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 1e-3
EARLY_STOPPING_PATIENCE = 15
REDUCE_LR_PATIENCE = 5
MIN_LR = 1e-6
FORCE_RETRAIN = False

# Model Architecture Parameters
# V0 (Baseline CNN)
V0_CONV1_FILTERS = 32
V0_CONV2_FILTERS = 64
V0_DENSE_UNITS = 64
V0_DROPOUT = 0.5

# V1 (CNN + XAI TimeDistributed)
V1_CONV1_FILTERS = 32
V1_CONV2_FILTERS = 64
V1_DENSE_UNITS = 64
V1_DROPOUT = 0.5

# V2 (Bi-LSTM Flagship)
V2_LSTM1_UNITS = 64
V2_LSTM2_UNITS = 32
V2_DROPOUT = 0.3

# Clinical Screening & Inference
CLASSIFICATION_THRESHOLD = 0.5