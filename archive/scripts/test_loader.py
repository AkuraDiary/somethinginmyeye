import os, glob, numpy as np, pandas as pd
from scripts.universal_pipeline import extract_universal_features, MAX_TIMESTEPS

csv_files = glob.glob(os.path.join("../datasets", "*.csv"))
print(f"Total CSVs found: {len(csv_files)}")
sequences = []
for file in csv_files:
    df = pd.read_csv(file)
    if len(df) == 0: continue
    filename = os.path.basename(file).lower()
    if "normal" in filename: label = 0
    elif "dyslexia" in filename or "dysgraphia" in filename: label = 1
    else: continue
    
    stroke_data = extract_universal_features(df)
    if len(stroke_data) > MAX_TIMESTEPS:
        stroke_data = stroke_data[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), 9))
        stroke_data = np.vstack((stroke_data, padding))
    sequences.append(stroke_data)

print(f"Total valid sequences loaded: {len(sequences)}")
if len(sequences) > 0:
    X_seq = np.array(sequences)
    print(f"X_seq shape: {X_seq.shape}")
