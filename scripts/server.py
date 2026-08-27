from flask import Flask, request, jsonify
# import pandas as pd
# import numpy as np
# import tensorflow as tf
import time
import os
import base64

# Import your existing preprocessing engine!
# from preprocess import analyze_stroke_data

# # Point Flask to your data_collector folder to serve the HTML
app = Flask(__name__, static_folder='../data_collector')

# print("🧠 Loading AI model...")
# model = tf.keras.models.load_model("../models/elkinematicV2.keras")
# MAX_TIMESTEPS = 500
# FEATURES = 3

# Automatically create a dataset folder if it doesn't exist
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#Go up one folder (to somethinginmyeye) and create 'datasets'
DATASETS_DIR = os.path.join(SCRIPT_DIR, '..', 'datasets')
os.makedirs(DATASETS_DIR, exist_ok=True)

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    mode = data.get('mode', 'normal')
    prefix = data.get('prefix', 'sample')
    stroke_data = data.get('strokes', [])
    image_dataURL = data.get('image', '')
    
    # Generate ONE universal timestamp for both files
    timestamp = int(time.time())
    base_filename = f"{prefix}_{timestamp}"
    
    # 1. Save the CSV
    if stroke_data:
        import csv
        csv_path = os.path.join(DATASETS_DIR, f"{base_filename}.csv")
        
        # Get headers from the first stroke point
        if len(stroke_data) > 0:
            keys = stroke_data[0].keys()
            with open(csv_path, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(stroke_data)
    
    # 2. Save the PNG
    if image_dataURL:
        # Strip off the "data:image/png;base64," header
        header, encoded = image_dataURL.split(",", 1)
        img_data = base64.b64decode(encoded)
        png_path = os.path.join(DATASETS_DIR, f"{base_filename}.png")
        
        with open(png_path, "wb") as f:
            f.write(img_data)
            
    print(f"💾 Saved {base_filename} to server!")
    return jsonify({"message": f"Successfully saved sample! Thank You For Your Contribution ❤️ !!!"})

@app.route('/')
def serve_html():
    return app.send_static_file('index.html')

# @app.route('/analyze', methods=['POST'])
# def analyze_live():
#     # 1. Receive the stroke data directly from the browser
#     stroke_data = request.json
    
#     df = pd.DataFrame(stroke_data)
    
#     # 2. Save it to a temporary file so we can reuse your exact preprocess logic
#     temp_file = "temp_live_sample.csv"
#     df.to_csv(temp_file, index=False)
    
#     # 3. Extract the biomarkers (Preprocess)
#     processed_df = analyze_stroke_data(temp_file)
#     latency_val = processed_df['latency'].iloc[0] # latency feature
#     model_input = processed_df[['velocity', 'pressure', 'touching']].values # sequence features
#     print(f"⏱️ New drawing received! Cognitive Latency: {latency_val} ms")
#     # 4. Pad/Truncate
#     if len(model_input) > MAX_TIMESTEPS:
#         model_input = model_input[:MAX_TIMESTEPS]
#     else:
#         padding = np.zeros((MAX_TIMESTEPS - len(model_input), FEATURES))
#         model_input = np.vstack((model_input, padding))
        
#      # 1. Make the prediction
#     prediction = model.predict([np.array([model_input]), np.array([latency_val])])
    
#     # 2. prediction is shape (1, 500, 1). Flatten it to a list of 500 floats!
#     heatmap_array = prediction[0].flatten().tolist()
    
#     # 3. Calculate an overall "Global Score" for the text readout (e.g., the average anomaly score)
#     global_score = sum(heatmap_array) / len(heatmap_array)
    
#     os.remove(temp_file)
    
#     return jsonify({
#         "probability": float(global_score),
#         "is_dyslexic": bool(global_score > 0.5),
#         "heatmap": heatmap_array  # <--- Send the 500 scores to the UI!
#     })

if __name__ == '__main__':
    # host='0.0.0.0' allows your tablet to connect over Wi-Fi
    app.run(host='0.0.0.0', port=8000)