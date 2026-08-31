import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model, Sequential
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, Flatten, Dense, TimeDistributed, Concatenate, RepeatVector, Bidirectional, LSTM, GlobalAveragePooling1D, Dropout
from universal_pipeline import load_and_scale_universal, get_v0_data, get_v1_data, get_v2_data, MAX_TIMESTEPS

from config import *

# ====================================================
# 1. MODEL ARCHITECTURES (TRUE SAVED VERSIONS)
# ====================================================

def build_v0_baseline():
    """V0: Standard spatial CNN with GlobalAveragePooling"""
    model = Sequential([
        Input(shape=(MAX_TIMESTEPS, 3), name="kinematics_input"),
        Conv1D(filters=32, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=64, kernel_size=3, activation='relu'),
        GlobalAveragePooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ], name="elkinematicsv0")
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Recall(name='recall')])
    return model

def build_v1_xai():
    """V1: TimeDistributed CNN with Latency explicitly for XAI"""
    seq_in = Input(shape=(MAX_TIMESTEPS, 3), name="kinematics_input")
    x = Conv1D(32, 3, activation='relu', padding='same')(seq_in)
    x = Conv1D(64, 3, activation='relu', padding='same')(x)
    
    lat_in = Input(shape=(1,), name="latency_input")
    lat_repeated = RepeatVector(MAX_TIMESTEPS)(lat_in)
    
    merged = Concatenate()([x, lat_repeated])
    
    y = TimeDistributed(Dense(64, activation='relu'))(merged)
    y = Dropout(0.5)(y)
    out = TimeDistributed(Dense(1, activation='sigmoid'))(y)
    
    model = Model(inputs=[seq_in, lat_in], outputs=out, name="elkinematicsv1")
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Recall(name='recall')])
    return model

def build_v2_lstm():
    """V2: TimeDistributed Bi-LSTM from Jupyter Notebook"""
    seq_in = Input(shape=(MAX_TIMESTEPS, 8), name="kinematics_input")
    x = Bidirectional(LSTM(64, return_sequences=True))(seq_in)
    x = Dropout(0.3)(x)
    x = Bidirectional(LSTM(32, return_sequences=True))(x)
    x = Dropout(0.3)(x)
    
    lat_in = Input(shape=(1,), name="latency_input")
    lat_repeated = RepeatVector(MAX_TIMESTEPS)(lat_in)
    
    merged = Concatenate()([x, lat_repeated])
    out = TimeDistributed(Dense(1, activation='sigmoid'), name="heatmap_output")(merged)
    
    model = Model(inputs=[seq_in, lat_in], outputs=out, name='elkinematicsv2')
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Recall(name='recall')])
    return model

# ====================================================
# 2. RUNNER (LOAD OR RETRAIN LOGIC)
# ====================================================
def get_or_train_model_with_tuning(model_name, filepath, build_fn, X_train, y_train, X_val, y_val):
    if not FORCE_RETRAIN and os.path.exists(filepath):
        print(f"Me-load {model_name} dari {filepath}...")
        try:
            model = load_model(filepath)
            return model
        except Exception as e:
            print(f"⚠️ Gagal me-load {filepath}. Fallback ke training ulang!")
    
    print(f"Men-training ulang {model_name} dari awal dengan Tuning...")
    from universal_pipeline import train_with_tuning
    model = build_fn()
    model, _ = train_with_tuning(model, X_train, y_train, X_val, y_val)
    return model

if __name__ == "__main__":
    from universal_pipeline import load_validation_with_train_scalers
    
    print("Memproses TRAINING Data (datasets/)...")
    X_train_seq_scaled, X_train_lat_scaled, y_train = load_and_scale_universal("../datasets")
    
    print("Memproses VALIDATION Data (val_datasets/)...")
    X_val_seq_scaled, X_val_lat_scaled, y_val = load_validation_with_train_scalers("../val_datasets")
    
    # Menyiapkan adapter data TRAIN
    X_train_v0, y_train_v0 = get_v0_data(X_train_seq_scaled, y_train)
    X_train_v1, y_train_v1 = get_v1_data(X_train_seq_scaled, X_train_lat_scaled, y_train)
    X_train_v2, y_train_v2 = get_v2_data(X_train_seq_scaled, X_train_lat_scaled, y_train)
    
    # Menyiapkan adapter data VAL
    X_val_v0, y_val_v0 = get_v0_data(X_val_seq_scaled, y_val)
    X_val_v1, y_val_v1 = get_v1_data(X_val_seq_scaled, X_val_lat_scaled, y_val)
    X_val_v2, y_val_v2 = get_v2_data(X_val_seq_scaled, X_val_lat_scaled, y_val)
    
    # 1. Dapatkan V0
    model_v0 = get_or_train_model_with_tuning("V0 (Baseline)", MODEL_PATHS['v0'], build_v0_baseline, X_train_v0, y_train_v0, X_val_v0, y_val_v0)
    
    # 2. Dapatkan V1
    model_v1 = get_or_train_model_with_tuning("V1 (XAI CNN)", MODEL_PATHS['v1'], build_v1_xai, X_train_v1, y_train_v1, X_val_v1, y_val_v1)
    
    # 3. Dapatkan V2
    model_v2 = get_or_train_model_with_tuning("V2 (LSTM) [Current]", MODEL_PATHS['v2'], build_v2_lstm, X_train_v2, y_train_v2, X_val_v2, y_val_v2)
    
    # ====================================================
    # 3. LEADERBOARD (EVALUASI MENGGUNAKAN DATA NORMALISASI)
    # ====================================================
    print("\n\n🏆 FINAL LEADERBOARD (EVALUATION SCORES) 🏆")
    print("-" * 65)
    print(f"{'Model':<15} | {'Accuracy':<15} | {'Recall':<15} | {'Loss':<10}")
    print("-" * 65)
    
    models_to_test = [
        ("V0", model_v0, X_val_v0, y_val_v0),
        ("V1", model_v1, X_val_v1, y_val_v1),
        ("V2", model_v2, X_val_v2, y_val_v2)
    ]
    
    for name, model, X, y_true in models_to_test:
        print(f"Mengevaluasi {name}.|")
        # Evaluate mengembalikan [loss, accuracy, recall]
        scores = model.evaluate(X, y_true, verbose=0)
        loss, acc = scores[0], scores[1]
        recall = scores[2] if len(scores) > 2 else 0.0 
        print(f"{name:<15} | {acc*100:>13.2f}% | {recall*100:>13.2f}% | {loss:>10.4f}")
    
    print("-" * 65)
    print("Catatan: Jika skor V0/V1 sangat buruk saat di-load dari disk, itu adalah bukti")
    print("bahwa model lama tidak bisa memproses data yang dinormalisasi (Scaling).")
    print("Ubah FORCE_RETRAIN = True untuk membuktikan perbandingan yang 100% adil!")