# config.py
# Centralized configuration for the ML Pipeline

MAX_TIMESTEPS = 500
FEATURES = 8

DATASET_DIR = "../datasets/"
MODEL_DIR = "../models/"

MODEL_PATHS = {
    "v0": f"{MODEL_DIR}elkinematic.keras",
    "v1": f"{MODEL_DIR}elkinematicV2.keras",
    "v2": f"{MODEL_DIR}elkinematicV3.keras"
}

FORCE_RETRAIN = False  # Ubah ke True untuk memaksa training ulang secara adil (Apples-to-Apples)