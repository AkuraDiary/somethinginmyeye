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
HUAWEI_DATASET_DIR = os.path.join(PROJECT_ROOT, "huawei_datasets")

# Partitioned Target Dataset Directories
DHRC_TRAIN_DIR = os.path.join(PROJECT_ROOT, "dhrc_train_datasets")
DHRC_VAL_DIR = os.path.join(PROJECT_ROOT, "dhrc_val_datasets")
ELKINEMATICS_TRAIN_DIR = os.path.join(PROJECT_ROOT, "elkinematics_train_datasets")
ELKINEMATICS_VAL_DIR = os.path.join(PROJECT_ROOT, "elkinematics_val_datasets")

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
SAMPLING_RATE_HZ = 60.0  # Standardized temporal polling rate for hardware-agnostic resampling
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

# DHRC (Dual-Head Reversal Classifier) Architecture & Training
DHRC_SEQ_LEN = 64
DHRC_FEATURES = 8
DHRC_NUM_CLASSES = 52
DHRC_CONV1_FILTERS = 32
DHRC_CONV2_FILTERS = 64
DHRC_GRU_UNITS = 32
DHRC_DENSE_UNITS = 64
DHRC_DROPOUT = 0.35
DHRC_EPOCHS = 50
DHRC_BATCH_SIZE = 32
DHRC_PATIENCE = 10
DHRC_REDUCE_LR_PATIENCE = 4
DHRC_LEARNING_RATE = 1e-3
DHRC_LOSS_WEIGHT_CHAR = 1.0
DHRC_LOSS_WEIGHT_REV = 1.0
DHRC_MODEL_PATH = os.path.join(MODEL_DIR, "dual_head_reversal_model.keras")
DHRC_ONNX_PATH = os.path.join(PROJECT_ROOT, "data_collector", "models", "dual_head_reversal.onnx")

DHRC_VOCABULARY = (
    [chr(i) for i in range(ord('a'), ord('z') + 1)] +
    [chr(i) for i in range(ord('A'), ord('Z') + 1)]
)
DHRC_CHAR_TO_IDX = {ch: idx for idx, ch in enumerate(DHRC_VOCABULARY)}

# Clinical Screening & Inference
CLASSIFICATION_THRESHOLD = 0.5
COGNITIVE_LATENCY_THRESHOLD_MS = 1500.0  # Threshold for working memory delay in ms
REVERSAL_PENALTY_WEIGHT = 0.40
SPELLING_ERROR_WEIGHT = 0.40
LATENCY_RISK_WEIGHT = 0.20
KINEMATIC_DYSGRAPHIA_WEIGHT = 0.85
FINE_MOTOR_VARIANCE_WEIGHT = 0.15
ENABLE_GRAMMAR_ANALYSIS = False