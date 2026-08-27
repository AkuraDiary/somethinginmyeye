import sys
import numpy as np
import tensorflow as tf
from preprocess import analyze_stroke_data
from config import MAX_TIMESTEPS, FEATURES

def predict_sample(csv_filepath):
    # 1. Load the trained brain
    print("Loading AI model...")
    try:
        model = tf.keras.models.load_model("../models/elkinematicV3.keras")
    except Exception as e:
        print("Error: Could not find model. Did you save it?")
        return
        
    # 2. Load and preprocess the NEW handwriting sample
    print(f"\nAnalyzing handwriting sample: {csv_filepath}")

    processed_df = analyze_stroke_data(csv_filepath)
    latency_val = processed_df['latency'].iloc[0] # latency feature
    model_input = processed_df[["delta_x", "delta_y", "pressure", "tiltX", "tiltY", "velocity", "acceleration", "jerk"]].values # sequence features
    
    # 3. Pad or Truncate (Must match the training shape perfectly!)
    if len(model_input) > MAX_TIMESTEPS:
        model_input = model_input[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(model_input), FEATURES))
        model_input = np.vstack((model_input, padding))
        
    # 4. Pad/Truncate
    if len(model_input) > MAX_TIMESTEPS:
        model_input = model_input[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(model_input), FEATURES))
        model_input = np.vstack((model_input, padding))
        
     # 1. Make the prediction
    prediction = model.predict([np.array([model_input]), np.array([latency_val])])
    
    # 2. prediction is shape (1, 500, 1). Flatten it to a list of 500 floats!
    heatmap_array = prediction[0].flatten().tolist()
    
    # 5. Interpret the Results
    global_score = sum(heatmap_array) / len(heatmap_array)
    
    confidence = global_score * 100
    print("\n" + "="*45)
    print(" 🔍 AI SCREENING RESULT")
    print("="*45)
    print("Global Score : ", global_score)
    # print("Confidence : ", confidence)
    if global_score > 0.5:
        print(f"A typical/Dyslexic Pattern Detected")
        print(f"Probability: {confidence:.1f}%")
    else:
        print(f"Normal Handwriting Pattern")
        print(f"Probability: {100 - confidence:.1f}%")
    print("="*45 + "\n")

if __name__ == "__main__":
    # This lets you pass the file path directly in the terminal
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_csv>")
    else:
        predict_sample(sys.argv[1])