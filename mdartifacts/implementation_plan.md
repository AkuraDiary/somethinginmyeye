# Dyslexia Handwriting Kinematics Evaluator

Building an intelligent, lightweight system to evaluate writing processes for dyslexic patterns using spatiotemporal handwriting data (kinematics).

## Academic Foundations
1. **Online vs. Offline Data:** Extracting temporal and kinematic features is significantly more effective at capturing cognitive and motor deficits than analyzing static images alone.
2. **Key Biomarkers:** Dyslexic and dysgraphic patterns manifest strongly in the *pauses* and *fluency* of writing. Critical features: In-air pen duration, Writing duration, Peaks of speed.
3. **Prompt Complexity:** Narrative/expository prompts (generating ideas) trigger the cognitive load necessary to reveal dyslexia, unlike simple copying tasks.
4. **Spatial & Temporal Dominance:** Modern research proves pure kinematics (speed/acceleration) are weak indicators. Spatial (stroke lengths) and Temporal (pauses) are the most dominant.
5. **Multimodal Early Fusion:** Combining Kinematic data (Rhythm) and Visual data (Messiness) drastically improves grading over single modalities.

---

## Roadmap & Implementation Plan (Ascending Order)
*Ordered from immediate/actionable to distant/complex.*

### Phase 1: Data Collection & Deployment [✅ COMPLETED]
- Built HTML5 Canvas application capturing pointer events.
- Extracted Kinematic Features (Velocity, Pauses).
- Sequence Padding to `MAX_TIMESTEPS = 500`.
- Deployed a Flask API data collector to shared hosting.

### Phase 2: Live Data Acquisition [🟢 IN PROGRESS]
- **Real-World Gathering:** Use the deployed Web App to collect 200 samples (100 Normal, 100 Dyslexic-Acted).
- **Latency Metric:** Calculate the delta between the "Start" prompt and the very first `pointerdown` event to measure cognitive spelling load.

### Phase 3: The LSTM Sequence Upgrade [🔜 NEXT UP]
- **Concept:** The current 1D-CNN has "amnesia" and only looks at 1-2 seconds of data at a time. It forgets the baseline writing speed of the user.
- **Execution:** Swap the `Conv1D` layers for `Bidirectional(LSTM)` layers. 
- **Why:** LSTMs are the industry standard for time-series data. A Bidirectional LSTM reads the handwriting forwards and backwards, allowing the AI to understand long-term context and detect if a child's rhythm degrades over time.

### Phase 4: Explainable AI & Heatmaps [🟢 IN PROGRESS]
- **Concept:** Pinpoint the exact physical location of cognitive hesitation instead of a generic "Yes/No" diagnosis.
- **Execution (Done):** You already implemented the `TimeDistributed(Dense(1))` layer in your Jupyter Notebook so the model outputs a probability for *every single millisecond*.
- **UI Integration (Pending):** Map the high-probability milliseconds back to their X,Y coordinates to draw a glowing heatmap around the specific letter/stroke where the user hesitated.

### Phase 5: The Dual-Stream Vision Upgrade [🚀 FUTURE]
- **Concept:** Build a "Two-Headed Network" (Multimodal Early Fusion) to evaluate both Rhythm (Temporal) and Messiness (Spatial).
- **Execution:** 
  - *Stream 1 (Temporal):* The Bidirectional LSTM processes the 500-timestep CSV.
  - *Stream 2 (Spatial):* A lightweight 2D-CNN (like MobileNet) processes the saved Canvas PNG for letter reversals (e.g., 'b' vs 'd') and spatial layout.
  - *Merge:* Concatenate both streams in Keras before the final Dense layer.

### Phase 6: Semantic Analysis & Autoencoders [🌌 MISC / DISTANT]
- **OOD Detection (The Bouncer):** Use an Autoencoder to reject random scribbles/noise before running the main AI.
- **Semantic OCR:** Eventually extract the text to grade vocabulary. *Warning:* Must avoid off-the-shelf Transformers (like TrOCR) because they silently "auto-correct" spelling mistakes, which destroys dyslexic diagnostic data.
