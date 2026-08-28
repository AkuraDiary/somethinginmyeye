import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, Flatten, Dense, TimeDistributed, Bidirectional, LSTM, RepeatVector, Concatenate
from universal_pipeline import load_and_scale_universal, get_v0_data, get_v1_data, get_v2_data, MAX_TIMESTEPS

from config import *

def build_v0_baseline():
    inp = Input(shape=(MAX_TIMESTEPS, 3))
    x = Conv1D(32, kernel_size=3, activation='relu')(inp)
    x = MaxPooling1D(2)(x)
    x = Flatten()(x)
    x = Dense(16, activation='relu')(x)
    out = Dense(1, activation='sigmoid')(x)
    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Recall(name='recall')])
    return model

def build_v1_xai():
    seq_in = Input(shape=(MAX_TIMESTEPS, 3))
    lat_in = Input(shape=(1,))
    lat_repeated = RepeatVector(MAX_TIMESTEPS)(lat_in)
    concat = Concatenate()([seq_in, lat_repeated])
    
    x = Conv1D(32, kernel_size=3, activation='relu', padding='same')(concat)
    x = Conv1D(64, kernel_size=3, activation='relu', padding='same')(x)
    out = TimeDistributed(Dense(1, activation='sigmoid'))(x)
    model = Model(inputs=[seq_in, lat_in], outputs=out)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Recall(name='recall')])
    return model

def build_v2_lstm():
    seq_in = Input(shape=(MAX_TIMESTEPS, 8))
    lat_in = Input(shape=(1,))
    lat_repeated = RepeatVector(MAX_TIMESTEPS)(lat_in)
    concat = Concatenate()([seq_in, lat_repeated])
    
    x = Bidirectional(LSTM(32, return_sequences=True))(concat)
    out = TimeDistributed(Dense(1, activation='sigmoid'))(x)
    model = Model(inputs=[seq_in, lat_in], outputs=out)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Recall(name='recall')])
    return model

# ====================================================
# 2. RUNNER (LOAD OR RETRAIN LOGIC)
# ====================================================
def get_or_train_model(model_name, filepath, build_fn, X_train, y_train):
    if not FORCE_RETRAIN and os.path.exists(filepath):
        print(f"📦 Me-load {model_name} dari {filepath}...")
        try:
            model = load_model(filepath)
            return model
        except Exception as e:
            print(f"⚠️ Gagal me-load {filepath} (mungkin beda versi arsitektur). Fallback ke training ulang!")
    
    print(f"🚀 Membangun dan men-training ulang {model_name} dari awal...")
    model = build_fn()
    # Training cepat (20 epochs)
    model.fit(X_train, y_train, epochs=20, validation_split=0.2, verbose=1)
    return model

if __name__ == "__main__":
    print("Memproses Data Universal...")
    X_seq_scaled, X_lat_scaled, y = load_and_scale_universal(DATASET_DIR)
    
    # Menyiapkan adapter data
    X_v0, y_v0 = get_v0_data(X_seq_scaled, y)
    X_v1, y_v1 = get_v1_data(X_seq_scaled, X_lat_scaled, y)
    X_v2, y_v2 = get_v2_data(X_seq_scaled, X_lat_scaled, y)
    
    # 1. Dapatkan V0
    model_v0 = get_or_train_model("V0 (Baseline)", MODEL_PATHS['v0'], build_v0_baseline, X_v0, y_v0)
    
    # 2. Dapatkan V1
    model_v1 = get_or_train_model("V1 (XAI CNN)", MODEL_PATHS['v1'], build_v1_xai, X_v1, y_v1)
    
    # 3. Dapatkan V2
    model_v2 = get_or_train_model("V2 (LSTM) [Current]", MODEL_PATHS['v2'], build_v2_lstm, X_v2, y_v2)
    
    # ====================================================
    # 3. LEADERBOARD (EVALUASI MENGGUNAKAN DATA NORMALISASI)
    # ====================================================
    print("\n\n🏆 FINAL LEADERBOARD (EVALUATION SCORES) 🏆")
    print("-" * 65)
    print(f"{'Model':<15} | {'Accuracy':<15} | {'Recall':<15} | {'Loss':<10}")
    print("-" * 65)
    
    models_to_test = [
        ("V0", model_v0, X_v0, y_v0),
        ("V1", model_v1, X_v1, y_v1),
        ("V2", model_v2, X_v2, y_v2)
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