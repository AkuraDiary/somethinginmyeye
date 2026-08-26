from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import tensorflow as tf
import os

# Import your existing preprocessing engine!
from preprocess import analyze_stroke_data

# Point Flask to your data_collector folder to serve the HTML
app = Flask(__name__, static_folder='../data_collector')

print("🧠 Loading AI model...")
model = tf.keras.models.load_model("../models/selkinematic.keras")
MAX_TIMESTEPS = 500
FEATURES = 3

@app.route('/')
def serve_html():
    return app.send_static_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_live():
    # 1. Receive the stroke data directly from the browser
    stroke_data = request.json
    df = pd.DataFrame(stroke_data)
    
    # 2. Save it to a temporary file so we can reuse your exact preprocess logic
    temp_file = "temp_live_sample.csv"
    df.to_csv(temp_file, index=False)
    
    # 3. Extract the biomarkers
    processed_df = analyze_stroke_data(temp_file)
    model_input = processed_df[['velocity', 'pressure', 'touching']].values
    
    # 4. Pad/Truncate
    if len(model_input) > MAX_TIMESTEPS:
        model_input = model_input[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(model_input), FEATURES))
        model_input = np.vstack((model_input, padding))
        
    # 5. Predict!
    prediction = model.predict(np.array([model_input]))[0][0]
    
    # Clean up the temp file
    os.remove(temp_file)
    
    # 6. Send the result back to the browser
    return jsonify({
        "probability": float(prediction),
        "is_dyslexic": bool(prediction > 0.5)
    })

if __name__ == '__main__':
    # host='0.0.0.0' allows your tablet to connect over Wi-Fi
    app.run(host='0.0.0.0', port=8000)