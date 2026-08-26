import sys
import numpy as np
import tensorflow as tf
from preprocess import analyze_stroke_data

MAX_TIMESTEPS = 500
FEATURES = 3

def predict_sample(csv_filepath):
    # 1. Load the trained brain
    print("Loading AI model...")
    try:
        model = tf.keras.models.load_model("../models/elkinematic.keras")
    except Exception as e:
        print("Error: Could not find model. Did you save it?")
        return
        
    # 2. Load and preprocess the NEW handwriting sample
    print(f"\nAnalyzing handwriting sample: {csv_filepath}")
    df = analyze_stroke_data(csv_filepath)
    stroke_data = df[['velocity', 'pressure', 'touching']].values
    
    # 3. Pad or Truncate (Must match the training shape perfectly!)
    if len(stroke_data) > MAX_TIMESTEPS:
        stroke_data = stroke_data[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), FEATURES))
        stroke_data = np.vstack((stroke_data, padding))
        
    # Neural networks expect a "batch" of files. We only have 1 file, 
    # so we wrap it in an array to change the shape from (500, 3) to (1, 500, 3)
    input_data = np.array([stroke_data])
    
    # 4. Make the Prediction!
    prediction = model.predict(input_data)[0][0]
    
    # 5. Interpret the Results
    confidence = prediction * 100
    print("\n" + "="*45)
    print(" 🔍 AI SCREENING RESULT")
    print("="*45)
    if prediction > 0.5:
        print(f" ⚠️ A typical/Dyslexic Pattern Detected")
        print(f"    Probability: {confidence:.1f}%")
        print("    Indicators: High in-air pausing, irregular velocity.")
    else:
        print(f" Normal Handwriting Pattern")
        print(f"    Probability: {100 - confidence:.1f}%")
        print("    Indicators: Fluid motion, standard writing duration.")
    print("="*45 + "\n")

if __name__ == "__main__":
    # This lets you pass the file path directly in the terminal
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_csv>")
    else:
        predict_sample(sys.argv[1])