"""
Executes full Dual-Head dataset construction, model compilation, training, and evaluation.
"""
import os, sys, json, base64
os.environ['KERAS_HOME'] = '/tmp/keras'
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
sys.path.insert(0, 'venv/lib/python3.12/site-packages')
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UJIPEN_PATH = "ujipendatasets/ujipenchars2.txt"

VOCABULARY = (
    [chr(i) for i in range(ord('a'), ord('z') + 1)] +
    [chr(i) for i in range(ord('A'), ord('Z') + 1)] +
    [str(d) for d in range(10)]
)
CHAR_TO_IDX = {ch: idx for idx, ch in enumerate(VOCABULARY)}

HORIZONTAL_REVERSIBLE_CHARS = {
    'b': 'd', 'd': 'b',
    'p': 'q', 'q': 'p',
    'B': 'B_rev', 'D': 'D_rev', 'E': 'E_rev', 'F': 'F_rev',
    'J': 'J_rev', 'K': 'K_rev', 'L': 'L_rev', 'N': 'N_rev',
    'P': 'P_rev', 'R': 'R_rev', 'S': 'S_rev', 'Z': 'Z_rev',
    'c': 'c_rev', 'e': 'e_rev', 's': 's_rev', 'z': 'z_rev'
}

ROTATIONAL_REVERSIBLE_CHARS = {
    'm': 'w', 'w': 'm',
    'u': 'n', 'n': 'u',
    'M': 'W', 'W': 'M'
}

def parse_ujipenchars(filepath):
    samples = []
    current_sample = None
    with open(filepath, 'r', encoding='latin1') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            if line.startswith('WORD'):
                parts = line.split()
                label = parts[1]
                sample_id = parts[2] if len(parts) > 2 else ''
                current_sample = {'label': label, 'sample_id': sample_id, 'strokes': []}
                samples.append(current_sample)
            elif line.startswith('POINTS'):
                if current_sample is None: continue
                if '#' in line:
                    pts_str = line.split('#')[1].strip()
                    nums = [float(val) for val in pts_str.split()]
                    pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
                    current_sample['strokes'].append(pts)
    return samples

def resample_and_normalize_sample(sample, target_len=64):
    strokes = sample.get('strokes', [])
    if not strokes or sum(len(s) for s in strokes) == 0:
        return {'x': np.zeros(target_len, dtype=np.float32), 'y': np.zeros(target_len, dtype=np.float32), 'pen_state': np.zeros(target_len, dtype=np.float32)}

    raw_x, raw_y, raw_pen = [], [], []
    for s_idx, stroke in enumerate(strokes):
        if not stroke: continue
        if s_idx > 0 and len(raw_x) > 0:
            raw_x.append(stroke[0][0])
            raw_y.append(stroke[0][1])
            raw_pen.append(0.0)
        for pt in stroke:
            raw_x.append(float(pt[0]))
            raw_y.append(float(pt[1]))
            raw_pen.append(1.0)

    raw_x = np.array(raw_x, dtype=np.float64)
    raw_y = np.array(raw_y, dtype=np.float64)
    raw_pen = np.array(raw_pen, dtype=np.float64)

    min_x, max_x = np.min(raw_x), np.max(raw_x)
    min_y, max_y = np.min(raw_y), np.max(raw_y)
    scale = max(max_x - min_x, max_y - min_y, 1e-6)

    norm_x = (raw_x - min_x) / scale
    norm_y = (raw_y - min_y) / scale

    dx = np.diff(norm_x)
    dy = np.diff(norm_y)
    step_distances = np.sqrt(dx**2 + dy**2)
    cum_dist = np.empty(len(norm_x), dtype=np.float64)
    cum_dist[0] = 0.0
    cum_dist[1:] = np.cumsum(step_distances)
    total_length = cum_dist[-1]

    if total_length < 1e-6:
        return {'x': np.full(target_len, norm_x[0], dtype=np.float32), 'y': np.full(target_len, norm_y[0], dtype=np.float32), 'pen_state': np.ones(target_len, dtype=np.float32)}

    query_dist = np.linspace(0.0, total_length, target_len)
    res_x = np.interp(query_dist, cum_dist, norm_x).astype(np.float32)
    res_y = np.interp(query_dist, cum_dist, norm_y).astype(np.float32)
    interp_pen = np.interp(query_dist, cum_dist, raw_pen)
    res_pen = (interp_pen >= 0.5).astype(np.float32)

    return {'x': res_x, 'y': res_y, 'pen_state': res_pen}

def extract_reversal_kinematic_features(resampled_data, eps=1e-7):
    x = resampled_data['x']
    y = resampled_data['y']
    pen_state = resampled_data['pen_state']
    T = len(x)

    dx = np.empty(T, dtype=np.float32)
    dy = np.empty(T, dtype=np.float32)
    dx[0], dy[0] = 0.0, 0.0
    dx[1:] = np.diff(x)
    dy[1:] = np.diff(y)

    ds = np.sqrt(dx**2 + dy**2) + eps
    cos_theta = dx / ds
    sin_theta = dy / ds

    d_theta = np.zeros(T, dtype=np.float32)
    d_theta[1:] = sin_theta[1:] * cos_theta[:-1] - cos_theta[1:] * sin_theta[:-1]

    d2x = np.zeros(T, dtype=np.float32)
    d2y = np.zeros(T, dtype=np.float32)
    d2x[1:] = np.diff(dx)
    d2y[1:] = np.diff(dy)

    return np.column_stack([dx, dy, cos_theta, sin_theta, d_theta, d2x, d2y, pen_state.astype(np.float32)])

def mirror_sample_horizontal(sample):
    strokes = sample['strokes']
    all_x = [pt[0] for s in strokes for pt in s]
    min_x, max_x = min(all_x), max(all_x)
    return {'strokes': [[(min_x + max_x - pt[0], pt[1]) for pt in s] for s in strokes]}

def rotate_sample_180(sample):
    strokes = sample['strokes']
    all_x = [pt[0] for s in strokes for pt in s]
    all_y = [pt[1] for s in strokes for pt in s]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    return {'strokes': [[(min_x + max_x - pt[0], min_y + max_y - pt[1]) for pt in s] for s in strokes]}

def build_dual_head_model(seq_len=64, num_features=8, num_classes=62):
    inputs = layers.Input(shape=(seq_len, num_features), name='trajectory_input')
    x = layers.Conv1D(32, kernel_size=5, padding='same', activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(2)(x)

    x = layers.Conv1D(64, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling1D(2)(x)

    x = layers.Bidirectional(layers.GRU(32, return_sequences=True))(x)
    shared = layers.GlobalAveragePooling1D()(x)
    shared = layers.Dense(64, activation='relu')(shared)
    shared = layers.Dropout(0.3)(shared)

    char_out = layers.Dense(num_classes, activation='softmax', name='char_output')(shared)
    rev_out = layers.Dense(1, activation='sigmoid', name='reversal_output')(shared)

    return Model(inputs=inputs, outputs=[char_out, rev_out], name='dual_head_reversal_model')

def main():
    print("Ingesting UJIpenchars2 samples...")
    raw_samples = parse_ujipenchars(UJIPEN_PATH)
    valid_samples = [s for s in raw_samples if s['label'] in CHAR_TO_IDX]
    print(f"Total valid samples: {len(valid_samples)}")

    X_all, y_char_all, y_rev_all = [], [], []
    for s in valid_samples:
        lbl = s['label']
        c_idx = CHAR_TO_IDX[lbl]
        
        # Authentic
        res_auth = resample_and_normalize_sample(s)
        X_all.append(extract_reversal_kinematic_features(res_auth))
        y_char_all.append(c_idx)
        y_rev_all.append(0.0)

        # Mirrored
        if lbl in HORIZONTAL_REVERSIBLE_CHARS:
            mir = mirror_sample_horizontal(s)
            res_mir = resample_and_normalize_sample(mir)
            X_all.append(extract_reversal_kinematic_features(res_mir))
            y_char_all.append(c_idx)
            y_rev_all.append(1.0)

        # Rotated
        if lbl in ROTATIONAL_REVERSIBLE_CHARS or lbl in {'6', '9'}:
            rot = rotate_sample_180(s)
            res_rot = resample_and_normalize_sample(rot)
            X_all.append(extract_reversal_kinematic_features(res_rot))
            y_char_all.append(c_idx)
            y_rev_all.append(1.0)

    X_all = np.array(X_all, dtype=np.float32)
    y_char_all = np.array(y_char_all, dtype=np.int32)
    y_rev_all = np.array(y_rev_all, dtype=np.float32).reshape(-1, 1)

    train_idx, val_idx = train_test_split(np.arange(len(X_all)), test_size=0.20, random_state=42, stratify=y_rev_all)
    X_train, X_val = X_all[train_idx], X_all[val_idx]
    y_char_train, y_char_val = y_char_all[train_idx], y_char_all[val_idx]
    y_rev_train, y_rev_val = y_rev_all[train_idx], y_rev_all[val_idx]

    print(f"Train set: {X_train.shape}, Val set: {X_val.shape}")

    model = build_dual_head_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss={'char_output': 'sparse_categorical_crossentropy', 'reversal_output': 'binary_crossentropy'},
        loss_weights={'char_output': 1.0, 'reversal_output': 1.5},
        metrics={'char_output': ['accuracy'], 'reversal_output': ['accuracy', tf.keras.metrics.AUC(name='auc')]}
    )

    callbacks = [
        EarlyStopping(monitor='val_reversal_output_auc', mode='max', patience=5, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-5, verbose=1)
    ]

    print("Training model across 15 epochs...")
    history = model.fit(
        X_train,
        {'char_output': y_char_train, 'reversal_output': y_rev_train},
        validation_data=(X_val, {'char_output': y_char_val, 'reversal_output': y_rev_val}),
        epochs=15,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )

    # Evaluation
    print("\nEvaluating on validation set...")
    val_preds = model.predict(X_val, verbose=0)
    char_preds = np.argmax(val_preds[0], axis=1)
    rev_probs = val_preds[1].ravel()
    rev_preds = (rev_probs >= 0.5).astype(int)

    char_acc = np.mean(char_preds == y_char_val) * 100.0
    rev_auc = roc_auc_score(y_rev_val, rev_probs)
    cm = confusion_matrix(y_rev_val, rev_preds)

    print("\n--- FINAL EVALUATION SUMMARY ---")
    print(f"Character Identification Accuracy: {char_acc:.2f}% (62 classes)")
    print(f"Clinical Reversal Detection ROC-AUC: {rev_auc:.4f}")
    print(f"Confusion Matrix:\n{cm}")
    print("\nClassification Report:")
    print(classification_report(y_rev_val, rev_preds, target_names=['Authentic', 'Reversed']))

    # Save trained reversal weights into scratch directory (protecting models/)
    os.makedirs('scratch', exist_ok=True)
    model.save('scratch/dual_head_reversal_model.keras')
    print("Dual-head model weights saved to scratch/dual_head_reversal_model.keras.")

if __name__ == '__main__':
    main()
