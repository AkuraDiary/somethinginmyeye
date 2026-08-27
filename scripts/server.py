from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import os
import base64

# Import your existing preprocessing engine!
from preprocess import analyze_stroke_data

# Point Flask to your data_collector folder to serve the HTML
app = Flask(__name__, static_folder='../data_collector')

print("🧠 Loading AI model...")
model = tf.keras.models.load_model("../models/elkinematic.keras")
MAX_TIMESTEPS = 500
FEATURES = 3

# Automatically create a dataset folder if it doesn't exist
os.makedirs("../datasets", exist_ok=True)

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    mode = data.get('mode', 'normal')
    prefix = data.get('prefix', 'sample')
    stroke_data = data.get('strokes', [])
    image_dataURL = data.get('image', '')
    
    # Generate ONE universal timestamp for both files
    timestamp = int(time.time())
    base_filename = f"{mode}_{prefix}_{timestamp}"
    
    # 1. Save the CSV
    if stroke_data:
        df = pd.DataFrame(stroke_data)
        csv_path = os.path.join("../datasets", f"{base_filename}.csv")
        df.to_csv(csv_path, index=False)
    
    # 2. Save the PNG
    if image_dataURL:
        # Strip off the "data:image/png;base64," header
        header, encoded = image_dataURL.split(",", 1)
        img_data = base64.b64decode(encoded)
        png_path = os.path.join("../datasets", f"{base_filename}.png")
        
        with open(png_path, "wb") as f:
            f.write(img_data)
            
    print(f"💾 Saved {base_filename} to server!")
    return jsonify({"message": f"Successfully saved sample! Thank You For Your Contribution ❤️ !!!"})

@app.route('/')
def serve_html():
    return app.send_static_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_live():
    # 1. Receive the stroke data directly from the browser
    stroke_data = request.json
    
    print(f"⏱️ New drawing received! Cognitive Latency: {latency} ms")
    df = pd.DataFrame(stroke_data)
    
    # 2. Save it to a temporary file so we can reuse your exact preprocess logic
    temp_file = "temp_live_sample.csv"
    df.to_csv(temp_file, index=False)
    
    # 3. Extract the biomarkers (Preprocess)
    processed_df = analyze_stroke_data(temp_file)
    latency_val = processed_df['latency'].iloc[0] # latency feature
    model_input = processed_df[['velocity', 'pressure', 'touching']].values # sequence features
    
    # 4. Pad/Truncate
    if len(model_input) > MAX_TIMESTEPS:
        model_input = model_input[:MAX_TIMESTEPS]
    else:
        padding = np.zeros((MAX_TIMESTEPS - len(model_input), FEATURES))
        model_input = np.vstack((model_input, padding))
        
    # 5. Predict!
    # prediction = model.predict(np.array([model_input]))[0][0]
    prediction = model.predict([np.array([model_input]), np.array([latency_val])])[0][0]
            
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