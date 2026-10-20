"""
Centralized Model Builder for Elkinematics.
Single source of truth for all neural network architectures (V0 Baseline CNN, V1 CNN+XAI, V2 Bi-LSTM).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

# Ensure scripts dir on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tensorflow as tf
from tensorflow.keras.layers import (
    BatchNormalization,
    Bidirectional,
    Concatenate,
    Conv1D,
    Dense,
    Dropout,
    GlobalAveragePooling1D,
    GRU,
    Input,
    LSTM,
    Masking,
    MaxPooling1D,
    RepeatVector,
    TimeDistributed,
)
from tensorflow.keras.models import Model, Sequential, load_model

from config import (
    DHRC_BATCH_SIZE,
    DHRC_CONV1_FILTERS,
    DHRC_CONV2_FILTERS,
    DHRC_DENSE_UNITS,
    DHRC_DROPOUT,
    DHRC_EPOCHS,
    DHRC_FEATURES,
    DHRC_GRU_UNITS,
    DHRC_LEARNING_RATE,
    DHRC_LOSS_WEIGHT_CHAR,
    DHRC_LOSS_WEIGHT_REV,
    DHRC_MODEL_PATH,
    DHRC_NUM_CLASSES,
    DHRC_ONNX_PATH,
    DHRC_PATIENCE,
    DHRC_REDUCE_LR_PATIENCE,
    DHRC_SEQ_LEN,
    FEATURES,
    LATENCY_DIM,
    LEARNING_RATE,
    MAX_TIMESTEPS,
    MODEL_PATHS,
    V0_CONV1_FILTERS,
    V0_CONV2_FILTERS,
    V0_DENSE_UNITS,
    V0_DROPOUT,
    V0_FEATURES,
    V0_L2_REG,
    V0_LEARNING_RATE,
    V1_CONV1_FILTERS,
    V1_CONV2_FILTERS,
    V1_DENSE_UNITS,
    V1_DROPOUT,
    V1_LEARNING_RATE,
    V2_CLIPNORM,
    V2_DROPOUT,
    V2_LEARNING_RATE,
    V2_LSTM1_UNITS,
    V2_LSTM2_UNITS,
)


def build_v0_baseline(learning_rate: float = V0_LEARNING_RATE) -> Sequential:
    """
    V0: Standard spatial 1D-CNN with Global Average Pooling.
    Input: (MAX_TIMESTEPS, 3) kinematics [velocity, dt, pressure].
    Output: Binary classification scalar.
    """
    l2_reg = tf.keras.regularizers.l2(V0_L2_REG)
    model = Sequential([
        Input(shape=(MAX_TIMESTEPS, V0_FEATURES), name="kinematics_input"),
        Conv1D(filters=V0_CONV1_FILTERS, kernel_size=3, activation="relu", kernel_regularizer=l2_reg, name="conv1"),
        MaxPooling1D(pool_size=2, name="maxpool1"),
        Conv1D(filters=V0_CONV2_FILTERS, kernel_size=3, activation="relu", kernel_regularizer=l2_reg, name="conv2"),
        GlobalAveragePooling1D(name="gap"),
        Dense(V0_DENSE_UNITS, activation="relu", kernel_regularizer=l2_reg, name="dense1"),
        Dropout(V0_DROPOUT, name="dropout"),
        Dense(1, activation="sigmoid", name="classification_output"),
    ], name="elkinematics_v0_baseline")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )
    return model


def build_v1_xai(learning_rate: float = V1_LEARNING_RATE) -> Model:
    """
    V1: Dual-input TimeDistributed CNN with Latency explicitly for Explainable AI (XAI).
    Inputs:
      - Kinematics sequence: (MAX_TIMESTEPS, 3)
      - Latency scalar: (1,)
    Output: TimeDistributed error probability heatmap (MAX_TIMESTEPS, 1).
    """
    seq_in = Input(shape=(MAX_TIMESTEPS, V0_FEATURES), name="kinematics_input")
    x = Conv1D(filters=V1_CONV1_FILTERS, kernel_size=5, activation="relu", padding="same", name="conv1")(seq_in)
    x = BatchNormalization(name="bn_conv1")(x)
    x = Conv1D(filters=V1_CONV2_FILTERS, kernel_size=5, activation="relu", padding="same", name="conv2")(x)
    x = BatchNormalization(name="bn_conv2")(x)

    lat_in = Input(shape=(LATENCY_DIM,), name="latency_input")
    lat_repeated = RepeatVector(MAX_TIMESTEPS, name="repeat_latency")(lat_in)

    merged = Concatenate(name="concat_modalities")([x, lat_repeated])
    y = TimeDistributed(Dense(V1_DENSE_UNITS, activation="relu"), name="td_dense")(merged)
    y = Dropout(V1_DROPOUT, name="dropout")(y)
    out = TimeDistributed(Dense(1, activation="sigmoid"), name="heatmap_output")(y)

    model = Model(inputs=[seq_in, lat_in], outputs=out, name="elkinematics_v1_xai")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )
    return model


def build_v2_bilstm(learning_rate: float = V2_LEARNING_RATE) -> Model:
    """
    V2: Dual-input Bidirectional LSTM on 8 standard kinematic sequence + Latency.
    Inputs:
      - Kinematics sequence: (MAX_TIMESTEPS, 8)
      - Latency scalar: (1,)
    Output: TimeDistributed error probability heatmap per millisecond timestep (MAX_TIMESTEPS, 1).
    """
    seq_in = Input(shape=(MAX_TIMESTEPS, FEATURES), name="kinematics_input")
    masked_seq = Masking(mask_value=0.0, name="mask_padding")(seq_in)

    x = Bidirectional(LSTM(V2_LSTM1_UNITS, return_sequences=True), name="bilstm_1")(masked_seq)
    x = Dropout(V2_DROPOUT, name="dropout_1")(x)
    x = Bidirectional(LSTM(V2_LSTM2_UNITS, return_sequences=True), name="bilstm_2")(x)
    x = Dropout(V2_DROPOUT, name="dropout_2")(x)

    lat_in = Input(shape=(LATENCY_DIM,), name="latency_input")
    lat_repeated = RepeatVector(MAX_TIMESTEPS, name="repeat_latency")(lat_in)

    merged = Concatenate(name="concat_modalities")([x, lat_repeated])
    out = TimeDistributed(Dense(1, activation="sigmoid"), name="heatmap_output")(merged)

    model = Model(inputs=[seq_in, lat_in], outputs=out, name="elkinematics_v2_bilstm")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate, clipnorm=V2_CLIPNORM),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )
    return model


def build_dhrc_model(
    seq_len: int = DHRC_SEQ_LEN,
    num_features: int = DHRC_FEATURES,
    num_classes: int = DHRC_NUM_CLASSES,
    learning_rate: float = DHRC_LEARNING_RATE,
) -> Model:
    """
    Centralized Dual-Head Reversal Classifier (DHRC).
    Input: (seq_len=64, num_features=8)
    Head 1 (char_output): Softmax across num_classes (52 Latin characters)
    Head 2 (reversal_output): Sigmoid probability of clinical reversal
    """
    inputs = Input(shape=(seq_len, num_features), name="trajectory_input")
    x = Conv1D(DHRC_CONV1_FILTERS, kernel_size=5, padding="same", activation="relu")(inputs)
    x = BatchNormalization()(x)
    x = MaxPooling1D(2)(x)

    x = Conv1D(DHRC_CONV2_FILTERS, kernel_size=3, padding="same", activation="relu")(x)
    x = BatchNormalization()(x)
    x = MaxPooling1D(2)(x)

    x = Bidirectional(GRU(DHRC_GRU_UNITS, return_sequences=True))(x)
    shared = GlobalAveragePooling1D()(x)
    shared = Dense(DHRC_DENSE_UNITS, activation="relu")(shared)
    shared = Dropout(DHRC_DROPOUT)(shared)

    char_out = Dense(num_classes, activation="softmax", name="char_output")(shared)
    rev_out = Dense(1, activation="sigmoid", name="reversal_output")(shared)

    model = Model(inputs=inputs, outputs=[char_out, rev_out], name="dual_head_reversal_model")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss={
            "char_output": "sparse_categorical_crossentropy",
            "reversal_output": "binary_crossentropy",
        },
        loss_weights={
            "char_output": DHRC_LOSS_WEIGHT_CHAR,
            "reversal_output": DHRC_LOSS_WEIGHT_REV,
        },
        metrics={
            "char_output": ["accuracy"],
            "reversal_output": ["accuracy", tf.keras.metrics.AUC(name="auc")],
        },
    )
    return model


def build_model(version: str = "v2", learning_rate: Optional[float] = None) -> Model:
    """Factory function returning the compiled model for the specified version."""
    v = version.lower().strip()
    if v == "v0":
        lr = learning_rate if learning_rate is not None else V0_LEARNING_RATE
        return build_v0_baseline(learning_rate=lr)
    elif v == "v1":
        lr = learning_rate if learning_rate is not None else V1_LEARNING_RATE
        return build_v1_xai(learning_rate=lr)
    elif v == "v2":
        lr = learning_rate if learning_rate is not None else V2_LEARNING_RATE
        return build_v2_bilstm(learning_rate=lr)
    elif v == "dhrc":
        lr = learning_rate if learning_rate is not None else DHRC_LEARNING_RATE
        return build_dhrc_model(learning_rate=lr)
    else:
        raise ValueError(f"Unknown model version: '{version}'. Must be 'v0', 'v1', 'v2', or 'dhrc'.")


def load_or_build_model(version: str = "v2", filepath: Optional[str] = None) -> Model:
    """Load existing trained model from disk if available, otherwise build a fresh compiled instance."""
    v = version.lower().strip()
    target_path = filepath or MODEL_PATHS.get(v)

    if target_path and os.path.exists(target_path):
        try:
            print(f"Loading existing {v.upper()} model weights from {target_path}...")
            return load_model(target_path)
        except Exception as e:
            print(f"Warning: Could not load {target_path} ({e}). Building fresh instance.")

    print(f"Building fresh compiled architecture for {v.upper()}...")
    return build_model(version=v)
