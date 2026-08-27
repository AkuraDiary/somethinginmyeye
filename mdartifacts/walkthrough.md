# Project Walkthrough: Dyslexia Kinematics Evaluator

## Overview
We successfully built an end-to-end, lightweight intelligent system designed to evaluate dyslexic and dysgraphic writing patterns based on the kinematics of handwriting (X, Y, Time, Pressure). We have progressed from a V1 "Black Box" Binary Classifier to a V2 **Explainable AI** anomaly detector.

## Architecture Built

### 1. Data Collection & Telemetry (Frontend)
- **Tech Stack:** HTML5 Canvas, JavaScript.
- **Functionality:** Captures high-resolution `PointerEvent` data in real-time. Features a UI for custom data labeling.
- **Automated Telemetry:** We abandoned manual downloads. A "Save to Server" button bundles the base64 PNG image and the Kinematic CSV array (injected with Cognitive Latency timing) into a single JSON payload and beams it to a Flask endpoint, saving perfectly linked, timestamped files.

### 2. Preprocessing & Data Science Pipeline
- **Tech Stack:** Python, Pandas, NumPy, Jupyter Notebook (`.ipynb`).
- **Functionality:** Migrated the data loading and training logic to a Jupyter Notebook for professional, reproducible Data Science exploration.
- **Smart Labeling:** Instead of weakly labeling entire files as Dyslexic, we built an algorithmic labeler that assigns `1` (Anomaly) *only* to the specific milliseconds where the pen velocity drops (stutters) or the pen lifts (in-air pauses).

### 3. Explainable AI Model (The Brain)
- **Tech Stack:** TensorFlow / Keras (Functional API).
- **Architecture (Multi-Input Sequence-to-Sequence):**
  - **Branch A (Kinematics):** Processes `(500, 3)` sequence via Conv1D layers.
  - **Branch B (Latency):** Processes a single static number `(1,)`, stretched via `RepeatVector(500)` to match Branch A.
  - **Merge & Output:** Branches concatenate and feed into `TimeDistributed` Dense layers.
- **Performance Tuning:** We expanded the Receptive Field (`kernel_size=15`) and added `dilation_rate=2` to give the AI wider contextual vision. We also applied mathematically derived `class_weight`s to force the model to hunt for rare anomalies, dodging the "Class Imbalance Trap".

### 4. Live Inference API & Heatmap (Deployment)
- **Tech Stack:** Python, Flask, JavaScript.
- **Functionality:** The `/analyze` endpoint feeds live drawing data into the `.keras` model. Instead of returning one score, it returns **500 probabilities**.
- **The Heatmap UI:** The frontend JavaScript loops through the 500 predictions and physically paints glowing red circles over the exact X/Y coordinates where the AI detected a cognitive stutter, transforming the AI from a Black Box into a transparent diagnostic tool.

## Next Steps for Production
1. **Mass Data Collection:** Gather 200 high-quality samples (100 Normal, 100 Dyslexic) using strict acting rules to train the Heatmap.
2. **The "Sliding Window" Upgrade (V3):** Replace the padding/truncating logic (`MAX_TIMESTEPS = 500`) with a Sliding Window architecture, allowing for infinite, real-time inference while the child is drawing.
3. **Multimodal Expansion (Two-Headed Network):** Integrate a Vision Branch (e.g., SWIN Transformer or 2D-CNN) to evaluate the PNG image for spatial/structural errors (like reversed letters) alongside the kinematic data.
