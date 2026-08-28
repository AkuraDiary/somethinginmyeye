import sys
import numpy as np
import tensorflow as tf
from preprocess import analyze_stroke_data
from config import MAX_TIMESTEPS, FEATURES

def predict_sample(csv_filepath):
    # 1. Load the trained brain
    print("Loading AI model...")
    try:
        # NOTE: Double check this name matches your notebook!
        model = tf.keras.models.load_model("../models/elkinematicV3.keras") 
    except Exception as e:
        print("Error: Could not find model. Did you save it?")
        return
        
    # 2. Load and preprocess the NEW handwriting sample
    print(f"\nAnalyzing handwriting sample: {csv_filepath}")
    processed_df = analyze_stroke_data(csv_filepath)
    
    # --- FIX 1: Scale Latency exactly like training ---
    latency_val = processed_df['latency'].iloc[0] / 1000.0 
    
    model_input = processed_df[["delta_x", "delta_y", "pressure", "tiltX", "tiltY", "velocity", "acceleration", "jerk"]].values
    
    # --- FIX 2: Clean Infinity/NaN values ---
    model_input = np.nan_to_num(model_input, nan=0.0, posinf=0.0, neginf=0.0)
    
    # 3. Pad or Truncate (Must match the training shape perfectly!)
    if len(model_input) > MAX_TIMESTEPS:
        model_input = model_input[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(model_input), FEATURES))
        model_input = np.vstack((model_input, padding))
        
    # --- FIX 3: Apply Z-Score Normalization (Scaling) ---
    # (Note: For a quick hot test, scaling the single sample by its own mean/std works fine)
    feature_means = np.mean(model_input, axis=0)
    feature_stds = np.std(model_input, axis=0)
    feature_stds[feature_stds == 0] = 1 # Prevent division by zero
    
    model_input_scaled = (model_input - feature_means) / feature_stds
        
    # 4. Make the prediction (using the SCALED data)
    prediction = model.predict([np.array([model_input_scaled]), np.array([latency_val])])
    
    # 5. prediction is shape (1, 500, 1). Flatten it to a list of 500 floats!
    heatmap_array = prediction[0].flatten().tolist()
    
    # 6. Interpret the Results
    global_score = sum(heatmap_array) / len(heatmap_array)
    confidence = global_score * 100
    
    print("\n" + "="*45)
    print(" 🔍 AI SCREENING RESULT")
    print("="*45)
    print(f"Global Score : {global_score:.4f}")
    
    if global_score > 0.5:
        print(f"Atypical/Dyslexic Pattern Detected")
        print(f"Probability: {confidence:.1f}%")
    else:
        print(f"Normal Handwriting Pattern")
        print(f"Probability: {100 - confidence:.1f}%")
    print("="*45 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_csv>")
    else:
        predict_sample(sys.argv[1])