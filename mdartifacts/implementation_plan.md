# Dyslexia Handwriting Kinematics Evaluator (V1 MVP Completed)

Building an intelligent, lightweight system to evaluate writing processes for dyslexic patterns using spatiotemporal handwriting data (kinematics).

## Academic Foundations
1. **Online vs. Offline Data:** Extracting temporal and kinematic features is significantly more effective at capturing cognitive and motor deficits than analyzing static images.
2. **Key Biomarkers:** Dyslexic and dysgraphic patterns manifest strongly in the *pauses* and *fluency* of writing. Critical features: In-air pen duration, Writing duration, Peaks of speed.
3. **Prompt Complexity:** Narrative/expository prompts (generating ideas) trigger the cognitive load necessary to reveal dyslexia, unlike simple copying tasks.

## MVP Implementation Status: [COMPLETED]

### Phase 1: Data Collection Engine ✅
- **Web-based Data Collector:** Built an HTML5 Canvas application capturing pointer events.
- **Features Extracted:** `[Timestamp, X, Y, Stylus Pressure, Pen-down State]`.
- **UI Upgrades:** Added image (PNG) export and Data Labeling toggles.

### Phase 2: Data Preprocessing ✅
- **Kinematic Feature Engineering:** Extracted Velocity (Δdistance/Δtime) and calculated In-Air Pauses vs Writing Duration.
- **Sequence Padding:** Standardized time-series arrays to `MAX_TIMESTEPS = 500`.

### Phase 3: Model Architecture & Deployment ✅
- **Core Model:** Built a highly lightweight 1D-CNN (~10,000 parameters) in Keras/TensorFlow.
- **Live Inference:** Deployed a Flask API to receive live canvas data and return instantaneous predictions.

---

## Future Improvement Plan (V2 Architecture)

As we look to scale this prototype into a production-grade diagnostic tool, the following advanced architectural upgrades have been identified:

### 1. Explainable AI: Letter-Level Anomaly Highlighting (The "Heatmap")
- **Concept:** Sentences are practically infinite, so the AI will not classify the words; it will evaluate the *physics* over time to pinpoint the exact location of cognitive hesitation.
- **Execution Option A (Time-Distributed):** Remove the `GlobalAveragePooling1D` (Time-Squasher) layer. Wrap the final output in a `TimeDistributed(Dense(1))` layer so the model outputs a probability for *every single millisecond*.
- **Execution Option B (Autoencoder):** Train an RNN Autoencoder purely on neurotypical data. Measure the "Reconstruction Error" on new samples to find the exact millisecond the rhythm broke.
- **UI Integration:** Map the specific milliseconds with high probabilities (or high errors) back to their X,Y coordinates to draw a glowing red heatmap around the exact letter/stroke where the user struggled.

### 2. Multi-Modal "Two-Headed" Network
- **Concept:** Combine Kinematic (Temporal) and Visual (Spatial) AI into one model.
- **Execution:** 
  - *Branch A:* 1D-CNN processes the CSV sequence for hesitations/speed.
  - *Branch B:* Lightweight 2D-CNN processes the saved Canvas PNG for letter reversals (e.g., 'b' vs 'd') and spatial layout.
  - *Merge:* Concatenate both branches in Keras to make a final holistic prediction.

### 3. Noise Filtering & OOD Detection (The "Bouncer")
- **Concept:** Children are unpredictable and may draw scribbles, incomplete letters, or pictures on the canvas. A binary classifier will incorrectly attempt to diagnose these doodles as dyslexia.
- **Execution:** Implement an Out-of-Distribution (OOD) rejection step before the final diagnosis. 
  - *Option A (The Garbage Class):* Upgrade the current CNN to a 3-class system (`Normal`, `Dyslexia`, `Scribble/Noise`) and train it on mock doodles.
  - *Option B (The Bouncer):* Use the Autoencoder's Reconstruction Error to immediately reject non-handwriting inputs.

## Immediate Action Items ("Closest Things We Can Go")

If you want to start building toward V2 immediately, these are the two closest, most accessible steps:

**1. Latency Metric Integration (UI Upgrade)**
Research shows the delay *before* starting to write is a massive cognitive indicator.
- *Action:* Add a "Start" button to the UI. Calculate the delta between the "Start" click and the very first `pointerdown` event. Pass this "Latency" number to the Flask API to include in the ML evaluation.

**2. Real-World Data Gathering (Data Science)**
Transition from mock training data to a real dataset.
- *Action:* Use the deployed Web App to collect 50+ samples from neurotypical individuals and individuals with dyslexia. Crucially, ask them an expository question (e.g., *"Write about your ideal trip"*) to force cognitive load, rather than just having them copy a word.
