# 🌮 Something In My Eye

A machine learning project designed to detect handwriting patterns related to dyslexia using kinematic analysis. It collects handwriting data via a tablet interface, extracts features (velocity, pressure, touching, latency), and runs a dual-input Convolutional Neural Network (Conv1D) to output predictions and generate a heatmap of anomalous strokes.

## 🍱 Project Structure

- **`data_collector/`** 🍩
  Contains the front-end user interface (`index.html`). It provides an interactive canvas to capture handwriting strokes, pressure, and cognitive latency, communicating with the backend.

- **`scripts/`** 🍜
  The core Python backend and AI logic.
  - `server.py`: Flask application that serves the frontend, receives data, and handles real-time model inference.
  - `train_model.py`: TensorFlow/Keras script for building and training the dual-input `Conv1D` and TimeDistributed heatmap model.
  - `predict.py`: CLI script to run inference and calculate global scores on new CSV samples.
  - `preprocess.py`: Extracts kinematic biomarkers (like velocity) from raw coordinate and timestamp data.
  - `visualize.py` & `config.py`: Utilities for plotting data and configuring parameters.

- **`datasets/`** 🍓
  Directory for storing collected CSV datasets and their corresponding PNG image captures.

- **`models/`** 🥟
  Saved trained models (e.g., `.keras` files) used by the inference server.

- **`somethinginmyeye.ipynb`** 🥗
  Jupyter Notebook for exploratory data analysis, prototyping, and model testing.

- **`requirements.txt`** 🍟
  Python dependencies needed to run the project.

## 🥘 How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the collector:**
   ```bash
   cd scripts && python server.py
   ```
3. **Open the UI:**
   Navigate to `http://localhost:8000` on your machine, or the provided local IP on your tablet.

## 🍳 Features

- Real-time stroke capturing (X/Y, pressure, timestamp).
- Cognitive latency measurement.
- Live inference with a visual heatmap overlay highlighting unusual kinematic patterns.
