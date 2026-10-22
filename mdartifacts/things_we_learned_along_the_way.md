# Things We Learned Along the Way

This document serves as a "Cheat Sheet" for the core Machine Learning concepts, physics, and architectural theories we explored while building the Dyslexia Kinematics Evaluator.

---

## 1. The Physics of the Data
When we process the raw coordinate data, we are applying discrete calculus:
* **Distance:** We use the Pythagorean theorem (`np.sqrt(dx**2 + dy**2)`) to find the exact pixel distance the pen traveled between two points.
* **Velocity:** Velocity is the derivative of position with respect to time ($v = dp/dt$). We approximate this by dividing the pixel distance by the delta-time (`dt`).

## 2. The Tensor (Matrix Shapes)
When the data enters the Neural Network, it takes the shape `(Batch_Size, Timesteps, Features)`. For example, `(8, 500, 3)` means:
* **8:** We passed in 8 files.
* **500:** Every file was standardized (padded or truncated) to exactly 500 milliseconds of time.
* **3:** At every millisecond, we look at 3 variables (`Velocity`, `Pressure`, `Touching`).

---

## 3. The 1D-CNN (Layer by Layer)

### `Conv1D` and the "Kernel Size"
A Convolutional layer acts as a feature detector using a sliding window. 
* **The "Time" Window:** `kernel_size=3` does **not** correspond to our 3 features. It corresponds to **Time**. It looks at the *Past (t-1)*, *Present (t)*, and *Future (t+1)* simultaneously to understand the trajectory of the pen.
* It slides this window down the 500 rows, multiplying the data by learned "filters" to find patterns (like a "sudden stop" or "pressure spike").

### The Pooling Layers
* **`MaxPooling1D` (The Summarizer):** Keeps only the highest value in a small window. It shrinks the timeline (e.g., from 500 to 250 steps) because we don't care *exactly* when a stutter happened, just that it happened in that general area.
* **`GlobalAveragePooling1D` (The Time-Squasher):** Destroys the concept of "time" entirely. It squashes the 2D matrix into a flat 1D array, summarizing the entire 3-second writing session into holistic scores.

---

## 4. Hyperparameters & Tuning

### The Tale of Two Accuracies
Tuning a model means watching two metrics: `accuracy` (the training data) and `val_accuracy` (the hidden "Pop Quiz" data).
* **The Memorizer (Overfitting):** `accuracy` is 99%, `val_accuracy` is 50%. The model is too big. It memorized the specific training files but fails in the real world. *Fix: Tune down the Dense layer or increase Dropout.*
* **The Slacker (Underfitting):** `accuracy` is 55%, `val_accuracy` is 55%. The model is too small and lacks the synapses to understand the complexity. *Fix: Tune up the Dense layer or add another Convolutional layer.*
* **The Goldilocks:** Both accuracies are high and closely matched.

### Width vs. Depth
* **Width (`Dense(64)` to `Dense(128)`):** Allows the network to look at more features and thoughts simultaneously. We usually stick to powers of 2 (32, 64, 128) because CPUs/GPUs process base-2 math faster.
* **Depth (Adding a second `Dense` layer):** Allows the network to form **Abstractions**. It combines simple thoughts from Layer 1 ("velocity dropped") into complex thoughts in Layer 2 ("velocity dropped while pressure spiked at the end of a word").
* **The Danger of Depth:** Adding too many layers to a simple problem causes massive Overfitting and the "Vanishing Gradient" problem (where the error-correction signal gets lost traveling backward through too many layers). A "funnel" architecture (e.g., `64` -> `32` -> `1`) is a safe best practice.

---

## 5. Normalization (Leveling the Playing Field)
Neural networks are mathematical formulas, meaning they are easily overwhelmed by massive numbers. If one feature is measured in the millions (like a timestamp) and another in decimals (like velocity), the network will incorrectly assume the massive number is more important.
* **Feature Normalization (Min-Max Scaling):** Squashing all data to a scale between `0.0` and `1.0` (often by dividing a column by its maximum value). This forces the AI to look at *patterns* rather than raw size.
* **Spatial Normalization:** In coordinate tracking, shifting all drawings to start at `(0,0)` by subtracting the initial `X` and `Y` from all points. This ensures the AI judges the *shape* of the line, regardless of where on the screen it was drawn.

---

## 6. How the AI Learns Concepts (Supervised Learning & Labels)
If we want the AI to recognize specific letters (A, B, C), we can't just give it the number 1, 2, or 3, because the AI's math will assume "C" is three times greater than "A".
* **One-Hot Encoding:** We translate categories into math using arrays of switches. "A" becomes `[1, 0, 0]`, "B" becomes `[0, 1, 0]`, etc.
* **Softmax Activation:** To predict multiple classes, we change our final layer to `Dense(26, activation='softmax')`. Softmax forces all output neurons to output probabilities that collectively add up to exactly 100%.

## 7. Reading Physics, Not Words (Handling Infinite Sentences)
Because phrases and sentences are infinite, we cannot label every possible sentence. Instead of teaching the AI to read English, we teach it to read *physics*. We don't care *what* word they wrote, we only care *when* the physical rhythm breaks.
* **The "Heatmap" Approach (Time-Distributed Layers):** Instead of using a `GlobalAveragePooling1D` layer (the "Time-Squasher") to get 1 overall score for the sentence, we remove it and use `TimeDistributed(Dense(1))`. This outputs a Dyslexia probability for *every single millisecond*. We can map the high-probability milliseconds back to the X/Y coordinates to draw a red box around the exact stutter!
* **Autoencoders (Reconstruction Error):** We train a model to perfectly recreate *only* normal handwriting. When fed an atypical sample, it fails to recreate the stuttering parts. We measure the "Reconstruction Error" for every millisecond; where the error is highest is where the anomaly occurred.

---

## 8. Activation Functions (The Gatekeepers)
Without activation functions, a Neural Network is just a giant linear math formula ($y = wx+b$) and could only ever draw a straight line. Activation functions introduce non-linearity, allowing the network to learn complex curves and patterns.
* **ReLU (Rectified Linear Unit):** The workhorse of the hidden layers. Rule: *If negative, output 0. If positive, pass it through unchanged.* It is computationally lightning-fast and prevents the network from stalling out.
* **Sigmoid:** The percentage squeezer. Rule: *Take any raw number from $-\infty$ to $\infty$ and squash it into an S-curve between `0.0` and `1.0`.* Used exclusively on the final output neuron for binary (Yes/No) classification to give us a clean probability.

## 9. Optimizers (The Navigators)
During training, the network makes a guess, checks the error (Loss), and adjusts its synapses to be better next time. The Optimizer is the algorithm that decides *how* to make those adjustments.
* **Adam (Adaptive Moment Estimation):** Imagine walking blindfolded down a mountain trying to find the lowest valley (Zero Error). Adam is a smart navigator that tracks your "momentum" (so you don't get stuck in small ditches) and dynamically adapts your step size (taking massive leaps on steep slopes, and tiny baby steps when you are near the bottom).

---

## 10. The Out-of-Distribution (OOD) Problem (Dealing with Chaos)
A basic binary classifier *must* pick one of its trained options. If you feed a Dyslexia vs. Normal AI a drawing of Batman, it will confidently diagnose Batman as Dyslexic. It lacks the ability to say, "This isn't handwriting."
To handle unpredictable real-world users (like children scribbling), we implement noise filters:
* **The Garbage Class (Multi-Class):** Adding a 3rd output neuron (`2 = Noise/Scribble`) and explicitly training the AI on intentionally bad drawings so it knows what garbage looks like.
* **The Bouncer (Autoencoders):** Because an autoencoder is trained to mathematically reconstruct *only* English text, a doodle will cause an astronomically high "Reconstruction Error." We can use this math error to "bounce" the drawing out of the app before it is diagnosed.
* **The Jury (GAN Discriminator):** Using a separate, adversarial network whose entire job is to act as a detective and ask, "Is this real text, or is this fake/noise?" 

**Best Practice (Do we use all of them?):** No. Using them all together is redundant and wastes computer memory. You pick **one**. For lightweight systems, the *Garbage Class* is the fastest to run, but the *Bouncer (Autoencoder)* is the most mathematically elegant since it doesn't require you to manually draw thousands of scribbles to train it.

---

## 11. V2 Explainable AI: The Anomaly Detector
* **Document Classification (V1) vs. Anomaly Detection (V2):** V1 acts like a teacher grading an entire essay with one letter grade. V2 acts like a spell-checker, putting a microscope on every single millisecond independently.
* **The Labeling Crisis (Weak vs. Strong Labels):** If we take a Dyslexic sample and label the entire 500-step array as `1`, the AI gets horribly confused because 90% of a dyslexic child's strokes are actually smooth and normal! To fine-tune V2 effectively, we must use "Smart Labels" (algorithmic labeling) that only assign `1` to the specific milliseconds where a stutter or pause physically occurs.

## 12. CNN Tuning (Receptive Fields & Dilation)
When we remove Pooling layers (so our output stays exactly 500 steps long to perfectly map to the UI canvas), the CNN loses its ability to "zoom out." 
* **Receptive Field (Kernel Size):** A `kernel_size=3` at 25Hz means the AI only sees 0.1 seconds of context at a time. It is impossible to detect a pause if you can only see 0.1 seconds of history. We must increase the kernel size (e.g., 10 or 15) so the AI can see a wider context.
* **Dilation Rate:** By adding `dilation_rate=2`, the CNN skips every other frame, artificially widening its "Receptive Field" (how much of the word it can see at once) without actually increasing the computational weight.

## 13. The Variable Length Problem (The Sliding Window)
Standard neural networks demand fixed-size inputs (e.g., `MAX_TIMESTEPS = 500`). However, standardizing human behavior to a fixed length introduces fatal edge cases:
* **The Guillotine (Truncating):** If a child takes a long time to write a word, enforcing a maximum length literally deletes the end of their data.
* **The Zero-Padding Trap:** If a child writes very quickly, the remaining empty space is padded with zeros. If we label the whole array as "Dyslexic", we accidentally teach the AI that "blank paper" equals dyslexia.

**The Production Solution: The Sliding Window**
Instead of forcing the entire writing session into one massive AI evaluation, we shrink the AI's "Receptive Field" to a small chunk (e.g., a 100-frame / 2-second window).
1. We place this window over the beginning of the writing data and evaluate it.
2. We "slide" the window forward by a few frames and evaluate again.
3. We repeat this infinitely until the writing stops.

**Why this is the ultimate V3 architecture:**
* It handles infinite writing lengths with zero truncation.
* It completely eliminates the need for zero-padding.
* It allows for **Real-Time Inference**. Because the window is only 2 seconds long, the AI can evaluate the kinematics *while* the child is drawing, creating a heatmap that updates live on the canvas.

---

## 14. The Class Imbalance Trap (Accuracy vs. Recall)
When training an Anomaly Detector (like a Dyslexia stutter detector), the anomalies (`1`) might only make up 2% of the total dataset, while smooth writing and empty space (`0`) make up 98%.
* **The Illusion of 98% Accuracy:** A lazy AI will quickly realize that if it just blindly guesses `0` for every single millisecond, it will score a 98% on the test. The `Accuracy` metric is useless here because it hides the fact that the AI caught 0% of the actual anomalies.
* **The `Recall` Metric:** To reveal the truth, we use the `Recall` metric. It answers: *"Out of all the actual stutters (1s) in the dataset, what percentage did you successfully catch?"*
* **The Fix (`class_weight`):** To force the AI to stop being lazy, we rig the mathematical grading rubric using `class_weight`. By setting `{0: 1.0, 1: 50.0}`, we tell the AI that missing a `1` is 50 times more painful than missing a `0`. The AI panics, stops guessing zeroes blindly, and actively starts hunting for anomalies.

## 15. The "Garbage In, Garbage Out" Rule (Dataset Generation)
The golden rule of Machine Learning is that the AI will only ever be as good as the data it learns from. 
Because our V2 model reads the physics of the pen (not the spelling of the word), we do not need 1,000 samples of every letter in the alphabet. We just need enough examples of *stuttering* vs *smooth* physics.
* **Target Size for MVP:** ~100 Normal samples, ~100 Dyslexic samples.
* **Acting like the Patient:** When faking dyslexic data, you must be a robotic actor. The anomalies must be consistent.
    1. **High Latency:** Wait 2 full seconds before touching the screen.
    2. **Micro-Stutter:** Drag the pen incredibly slowly around curves.
    3. **In-Air Pause:** Completely lift the pen in the middle of a word for 1 second.

---

## 16. Dataset Validation & Best Practices

### User-Independent Evaluation (The Train/Test Split)
When building the first version of the dataset, it is absolutely critical to split the dataset by **Annotators (People)**, not just randomly shuffling the files.
* **The Trap:** If Seta's writing is in the `train` folder, and Seta's writing is also in the `test` folder, the AI will cheat. It won't learn the pattern of "Dyslexia," it will just memorize Seta's personal handwriting style.
* **The Solution:** The `test` folder must contain data from people the AI has **never seen before**. If Seta and Stevan are the `train` subjects, the `test` subjects must be completely different people. This proves the AI generalizes to the real world.

### Why Not Cohen's Kappa?
In machine learning, **Cohen's Kappa** is used to measure *Inter-Rater Reliability*. This is used when humans have to subjectively guess the label (e.g., three doctors looking at the same X-Ray and trying to agree if it's cancer). 
In our case, the label is objective ground truth (the child either has a clinical diagnosis of Dyslexia or they don't). The annotators aren't guessing the label, they are just producing the physical data. Therefore, Cohen's Kappa is not applicable. 
* To validate a dataset like this, we rely on rigid data collection protocols (everyone writes A-Z for 5 rounds) and statistical tests like the **T-Test** or **Mann-Whitney U Test** to prove there is a mathematically significant difference in the physics (latency, speed) between the two groups.

### Classification vs. Regression
* **Classification (Our Case):** We are separating the data into discrete, distinct "buckets" or labels (`Normal` vs `Dyslexia`). Even though the AI outputs a probability (e.g., "85% Dyslexic"), it uses that math purely to drop the sample into the correct bucket. We evaluate this using metrics like *Accuracy*, *Precision*, and *Recall*.
* **Regression:** We would only use Regression if we wanted the AI to predict a highly specific, continuous clinical score (e.g., predicting that a child will score exactly "73.5 points" on a standard reading severity index).

## 6. The Architecture Dilemma: CNN vs. LSTM vs. Transformers
As we scale the AI, choosing the right architecture is critical. Here is what we learned from 2026 research:
* **1D-CNN (Our Baseline):** Great for "local" reflexes. It catches sudden micro-stutters perfectly and is incredibly fast. However, it suffers from a limited "Receptive Field" (amnesia) and cannot remember the user's baseline speed from the beginning of the sentence.
* **Bidirectional LSTM (The Immediate Upgrade):** LSTMs are the industry standard for time-series data because they have a "memory cell". A Bidirectional LSTM reads the 500-timestep sequence forwards and backwards. This allows the AI to calculate long-term context (e.g., "The user is writing 50% slower now than they were 5 seconds ago").
* **Transformers (The Danger Zone):** While Transformers (Self-Attention) dominate modern AI, they are fundamentally incompatible with our current phase for two reasons:
  1. *Resource Hungry:* They require massive compute (our server only has 1GB RAM) and massive datasets (10,000+ samples). Feeding a Transformer our 200 samples would result in catastrophic overfitting.
  2. *The Auto-Correct Flaw:* Transformer-based Vision/OCR models (like TrOCR) are so heavily optimized for reading comprehension that they silently auto-correct spelling mistakes. If a dyslexic child writes "wen", the Transformer outputs "when". This literally erases the diagnostic data we need.

## 7. The Spatial vs. Temporal Dominance
We learned that pure kinematics (raw speed and raw acceleration) are actually very weak indicators of dysgraphia. The AI cares overwhelmingly about:
* **Spatial Data:** The physical length/width of the strokes, erratic baseline drifting, and letter crowding.
* **Temporal Data:** How long the pen hovers in the air (pauses).
This destroys the old-school teacher mentality of "You are writing too slow." A child can scribble very fast (normal speed metrics), but the spatial dimensions of their letters will be completely chaotic. This validates our plan to eventually build a **Dual-Stream Network** that looks at both the CSV (Time) and the PNG (Space).

## 8. Demystifying Data Science Jargon
As we reviewed more advanced 2026 literature, we encountered several heavy data science terms. Here is how they translate to our project:
* **Feature Extraction vs. Feature Selection:** 
  * *Extraction* (Established): Using physics math to create new meaning out of raw data (e.g., turning raw X, Y coordinates into "Velocity" and "Acceleration").
  * *Selection* (Established): Throwing 150 features at an AI causes it to panic and "overfit". Selection is the mathematical process of deleting the useless features and keeping only the "Golden" indicators (like stroke length and pause duration).
* **Dual-Stream Network / Multimodal Fusion:** (Established). Imagine interrogating two witnesses. One is blind with great hearing (1D-CNN reading the CSV rhythm). One is deaf with great eyesight (2D-CNN reading the PNG image). If you ask them separately, they might be wrong. A Dual-Stream network asks them simultaneously and "fuses" their answers to solve the crime.
* **Hill Climbing & Local Optima:** (Established). An old AI search algorithm. Imagine trying to find the tallest mountain peak in pitch-black fog. You just keep stepping "up". The flaw is getting trapped on a tiny hill next to Mount Everest because every step from the tiny hill goes "down" (*Local Optima*). 
* **Fisher-Based Supervised Hill Climbing:** (Novel/Made Up). The authors of Paper #13 invented this specific software loop. They used the old Hill Climbing algorithm, but added an SVM (Support Vector Machine) as a "supervisor" to pull the AI off the tiny hills and force it to keep searching for the true peak.
* **Reading Research Equations:** When reading papers, equations for Velocity/Jerk are established Isaac Newton physics. Equations for REINFORCE or SVMs are established 1990s math. But equations describing thresholds and loops (like $S_{best}$) are the authors mathematically defining the novel software loop they just coded.

## 9. The "Golden 8" Features (Optimized Feature Selection)
Based on the finding in Paper #13 that extracting too many features causes overfitting (and purely kinematic features like raw speed are insufficient), we have defined a highly optimized, 8-feature array for our V2/V3 ML Architecture. This array perfectly balances Spatial, Temporal, and Kinematic data without overloading the `Bidirectional(LSTM)`:

1. **`Delta_X` (Spatial - Stroke Width):** The pixel distance the pen traveled horizontally in one millisecond. Prevents the AI from getting confused by *where* on the screen the child drew, focusing instead on the physical size of the letter.
2. **`Delta_Y` (Spatial - Stroke Height):** The pixel distance traveled vertically. Captures inconsistent letter sizing (a core dysgraphia biomarker).
3. **`Pressure` (Dynamic - Stress/Force):** Raw stylus pressure. If mapped to line-width in the HTML Canvas, the 2D-CNN Vision model will seamlessly learn this as well. Indicates stress or hesitation.
4. **`Tilt_X` (Dynamic - Pen Grip):** The altitude/azimuth angle of the stylus. Dysgraphic children physically grip the pen at rigid, awkward angles to compensate for poor motor control.
5. **`Tilt_Y` (Dynamic - Pen Grip):** The secondary angle of the stylus.
6. **`Velocity` (Kinematic - Speed):** The baseline speed ($\Delta Distance / \Delta Time$).
7. **`Acceleration` (Kinematic - Momentum):** The rate of change in speed.
8. **`Jerk` (Kinematic - Smoothness):** The rate of change in acceleration. This is the ultimate mathematical measurement for "smoothness". High Jerk perfectly captures the jagged micro-stutters of a dysgraphic hand fighting to draw a curve.

## 10. The Three Subtypes of Dysgraphia
We learned from Sindhu & Kavitha (2026) that Dysgraphia is not a blanket diagnosis. It actually breaks down into three distinct clinical subtypes. Our "Golden 8" features are perfectly positioned to classify exactly which subtype a child has:
1. **Motor Dysgraphia:** The child has poor fine-motor control. They try to compensate by pressing down extremely hard. *Signature:* High `Pressure`, Low `Velocity`, High `Jerk`.
2. **Spatial Dysgraphia:** The child has no problem moving the pen, but they lack spatial awareness (letters overlap, sizing is chaotic). *Signature:* Normal `Velocity` & `Pressure`, but chaotic `Delta_X` and `Delta_Y` variances.
3. **Dyslexic Dysgraphia:** The child's motor and spatial skills are completely normal. The delay happens in the brain trying to spell the word. *Signature:* Normal features everywhere, except massive spikes in `Latency` (hesitation before writing) and pauses in the middle of words.

## 11. The "Ablation" Warning: Why Kinematics Needs Space
A major 2026 study (Pamungkas et al.) attempted to build a Trajectory-Transformer that only looked at Time, Speed, and Pressure. In their "ablation study" (where they test the AI by turning off certain features), the Trajectory model failed catastrophically when it couldn't see the spatial image. 
* **The Insight:** Raw speed and pressure mean nothing without spatial context. Moving the pen fast to draw a huge straight line is normal; moving the pen fast to draw a tiny, tight circle is highly erratic. 
* **Our Solution:** This perfectly validates our decision to inject `Delta_X` and `Delta_Y` (stroke distances) into our LSTM array. By giving the LSTM the spatial stroke sizes alongside the velocity, we prevent the catastrophic failure seen in the Pamungkas study, even before we build our final V4 Dual-Stream Vision Model!

## 12. Project Positioning vs. 2026 State-of-the-Art
By comparing our architecture to the latest 2026 literature, we have validated that our project sits in a highly competitive and unique position in the academic landscape:
* **The "Goldilocks" Feature Count:** We successfully avoided the "Curse of Dimensionality". Papers that extracted 1,000+ features for small datasets (~100 samples) severely overfit and failed in generalization. By aggressively isolating our dataset to just the "Golden 8" features for 200 samples, our LSTM remains mathematically stable and immune to the overfitting trap.
* **The Accessibility Edge (Web vs. Clinical Hardware):** Most state-of-the-art studies rely on expensive, clinical-grade WACOM Intuos tablets in laboratory settings. By engineering a cloud-hosted HTML5 Canvas data collector, our research proves that highly accurate, multi-dimensional dysgraphia screening can be deployed directly to standard consumer tablets (like iPads) in public schools.
* **Solving the "Black Box" Problem (Explainable AI):** Standard AI models simply output a blind diagnosis (e.g., "Dysgraphia: 95%"). By utilizing a `TimeDistributed(Dense(1))` final layer, our model acts as Explainable AI (XAI). It doesn't just give a diagnosis; it generates a spatial heatmap pinpointing the exact millisecond and physical X/Y coordinate where the cognitive hesitation occurred, making the AI's reasoning fully transparent to teachers and doctors.

## 13. Dyslexia vs. Dysgraphia: The Parameter Distinction (Lecturer Clarification)
A critical distinction must be made between **Dyslexia** (a cognitive/phonological disorder) and **Dysgraphia** (a motor/spatial execution disorder). While they are often studied together, their data signatures in handwriting are completely different:

* **Pure Dysgraphia (Motor/Spatial):** The brain knows exactly how to spell the word, but the physical hand or spatial awareness fails. The biomarkers are purely physical: **High Jerk** (stuttering muscles), **High Pressure** (compensatory grip tension), or **Chaotic Delta_X/Delta_Y** (poor spatial scaling).
* **Pure Dyslexia (Cognitive/Spelling):** The physical hand muscles work perfectly, and spatial scaling is normal. The bottleneck is the brain trying to remember how to spell the word. The biomarkers are purely cognitive hesitations: **Massive Initial Latency** (staring at the screen before drawing the first letter) and **In-Air Pauses** (lifting the pen in the middle of a word to think about the next letter).

**Why our app works for Dyslexia:**
If our app only recorded X and Y, we would be building a Dysgraphia app. Because our app explicitly tracks **Latency** and separates **Touching vs In-Air Time**, we are actively measuring the *cognitive hesitation* happening in the air. This perfectly aligns with our goal of screening for Dyslexia, rather than just physical motor impairment.

## 14. The Danger of Unscaled Data (The "Dead Neuron" Problem)
During the first training run of our LSTM on the 302-sample dataset, the model completely froze on Epoch 1 (Accuracy locked, Recall stuck at 1.0000). We learned that this is a classic mathematical failure caused by feeding **unscaled physics data** into a neural network.

* **The Problem (Apples vs. Watermelons):** Our Golden 8 features have vastly different numerical scales. `Pressure` ranges from 0 to 1, while `Jerk` can spike to ±500, and `Latency` can exceed 2500 ms. If fed raw data, the neural network mistakenly assumes the larger numbers are inherently more "important." Worse, multiplying these massive numbers by the network's weights causes the activation functions to instantly max out at 100%. The math hits a brick wall, gradients drop to zero, and the LSTM neurons essentially "die."
* **The Solution (Z-Score Normalization):** To prevent this mathematical overload, we must normalize the data before training using the formula: `(Value - Mean) / Standard Deviation`.
* **The Result:** This math strips away the raw units (pixels, grams, milliseconds) and converts every feature into a standardized score. A value of `0.0` now represents "exactly average," while `+1.0` represents "above average." By forcing `Pressure`, `Velocity`, and `Jerk` to all hover safely between `-2.0` and `+2.0`, we put all features on a perfectly level playing field. This allows the LSTM to actually perceive the *patterns* in the writing rather than being blinded by massive integers.

## 15. Reading the AI Report Card (Diagnosing Model Health)
When training the LSTM, the terminal outputs a stream of metrics. Understanding these numbers is crucial for diagnosing the health of the AI's "brain" and knowing when to tune the model.

### Core Definitions
* **Epoch:** One complete pass through your entire dataset.
* **Step (Batch):** A smaller chunk of data (e.g., 32 samples). The AI reviews one step, updates its mathematical weights, and then moves to the next step to save RAM.
* **Training Metrics (`loss`, `accuracy`, `recall`):** The AI's performance on the data it is actively studying (the "textbook").
* **Validation Metrics (`val_loss`, `val_accuracy`, `val_recall`):** The AI's performance on the 20% of data hidden from it during training (the "final exam").
* **Loss:** The mathematical penalty score for making mistakes. A high loss means the AI is arrogant and wrong. The goal is to drive this as close to `0.0` as possible.
* **Accuracy:** The total percentage of correct diagnoses (e.g., `0.85` = 85%).
* **Recall:** The Sensitivity. Out of all the truly Dyslexic children, what percentage did the AI successfully catch?

### Diagnosing Training States
**1. The "Lazy Doctor" Syndrome (Dead Model):**
* *Symptom:* `recall: 1.0000` but `accuracy: 0.5000`. 
* *Diagnosis:* The AI suffered mathematical overload (usually due to unscaled data) and gave up. It decided to simply diagnose *every single patient* with Dyslexia. By doing so, it successfully catches 100% of the Dyslexic cases (Recall = 1.0), but falsely diagnoses all the healthy children (Accuracy drops to the 50% baseline).

**2. Underfitting (The AI is confused):**
* *Symptom:* `accuracy: 0.55` / `val_accuracy: 0.54` / `loss: 2.5`
* *Diagnosis:* The AI is too simple, or the data is too messy, for it to learn anything. Both training and validation scores are terrible and refuse to improve over multiple epochs.

**3. Overfitting (The AI memorized the textbook):**
* *Symptom:* `accuracy: 0.99` / `val_accuracy: 0.55` / `val_loss` starts increasing.
* *Diagnosis:* A massive gap opens between the two accuracies. The AI trained for too long. It stopped learning the general physical rules of Dyslexia and started strictly memorizing the specific handwriting quirks of the exact kids in the training set. When tested on unseen real-world kids (validation), it fails miserably.

**4. The Sweet Spot (Optimal Learning):**
* *Symptom:* `accuracy: 0.88` / `val_accuracy: 0.86` / `loss: 0.25` / `val_loss: 0.28`.
* *Diagnosis:* The training and validation metrics improve together, side-by-side. The AI is learning universal clinical rules that apply perfectly to both the training data and real-world, unseen data.

## 16. Beyond Kinematics: The Tri-Stream Architecture & The OCR Paradox
While our current Bidirectional LSTM effectively captures the motor struggles of Dysgraphia and the cognitive hesitations (latency) of Dyslexia, a complete clinical system requires analyzing *what* the child is writing, not just *how* they write it. We conceptualized a theoretical **Tri-Stream Architecture**:

1. **Kinematic Stream (LSTM):** Analyzes Speed/Jerk/Latency (Detects Motor Dysgraphia & Cognitive Hesitation).
2. **Visuospatial Stream (CNN):** Analyzes the final canvas image (Detects Spatial Dysgraphia like drifting lines and overlapping letters).
3. **Semantic Stream (NLP):** Analyzes the transcribed text for spelling errors, transpositions, omissions, and low lexical diversity (Directly detects Dyslexia).

### The Prompting Requirement
For the Semantic Stream to work, data collection cannot rely on copying text (e.g., "Copy this sentence"). Copying heavily bypasses the phonological processing center of the brain. Prompts must be expository (e.g., "Write a story about a dog") to force the child to formulate the spelling and grammar from scratch.

### The "Smart OCR" Paradox
To feed handwriting into an NLP model, it must first be transcribed via OCR. However, this creates a massive technical paradox:
* **The Autocorrect Trap:** Modern OCRs (Google Vision, Apple Vision) intelligently auto-correct misspelled words (e.g., reading "whent" and outputting "went"). This completely erases the Dyslexic spelling biomarkers before the NLP stream can even see them.
* **The Visuospatial Trap:** If we train a custom "dumb" OCR that doesn't autocorrect, it will still fail if the child has Spatial Dysgraphia. Severely overlapping, deformed letters will be transcribed as random garbage characters. The NLP will read this garbage and falsely diagnose severe Dyslexia, when the core issue was actually just physical motor control.

### Architectural Solutions to the OCR Paradox
To bypass OCR transcription failures on severely degraded handwriting, we documented three potential solutions:
1. **Trajectory Decoding (Online OCR):** Standard OCR looks at a static image and gets confused by overlapping ink. Because our web app records the exact millisecond timeline (`dt`), an AI can read the *chronological sequence of strokes* over time. Two overlapping letters drawn seconds apart will not confuse a temporal model.
2. **The "Quad-Stream" Model (Multimodal Audio/Speech):** Adding a microphone to record the child telling the story out loud while writing. By running Speech-to-Text, the AI captures the perfect "Intended Text" directly from the child's mind. It then mathematically compares this fluent speech to the failing handwriting to pinpoint the exact brain-to-hand cognitive bottleneck.
3. **Human-in-the-Loop (Teacher Ground Truth):** The most practical clinical solution. The app simply asks the teacher or clinician to type the child's intended sentence after the test is over. The AI uses this clean Ground Truth to perform "Forced Alignment" against the messy strokes, completely removing the need for a flawless AI OCR.

---

## 17. The Transparent Stroke Coder & Sayre's Paradox
When translating online handwriting trajectories (x, y, t) into characters for dyslexia and dysgraphia screening, we encountered the limitations of manual heuristic engineering:

* **Failure of Decision Trees & Prototype Dictionaries:** Hand-crafting 26-letter geometric decision trees (`if has_loop and stem_on_left: 'b'`) or template coordinate dictionaries is fundamentally fragile. Children rotate tablets, write at erratic baseline tilts, skip strokes, or vary handwriting order.
* **The PCA Deskewing Trap:** Applying 2D Principal Component Analysis (PCA) to deskew individual letters fails. For an upright letter like 'A', PCA treats the spread of the legs as a dominant tilt axis, rotating the letter sideways by ~55 degrees.
* **Sayre's Paradox in Cursive Writing:** In connected handwriting (e.g., "bebek" written without pen lifts), letters cannot be segmented without first knowing what was written, and words cannot be recognized without segmenting letters.
* **Online Handwriting Recognition (OHR) via Digital Ink:** Modern on-line decoders (such as Google Digital Ink / CTC temporal decoders) operate directly on temporal coordinate streams. For clinical screening, the language model (autocorrect / spell snapping) must be bypassed so that raw orthographic errors (letter reversals, transpositions, omissions) remain uncorrected and observable.

---

## 18. Quantifying Motor Hesitation & NIV Calibration
* **Number of Inversions of Velocity (NIV):** Measures the count of acceleration zero-crossings (direction changes between acceleration and deceleration). A single fluent ballistic stroke produces a single velocity peak (NIV close to zero). Motor tremor, hesitations, and visual-feedback corrections produce high NIV counts.
* **Clinical Benchmark (Asselborn et al., Nature Scientific Reports 2020 / EPFL CHILI Lab):**
  - Typical school-aged children produce 4 to 7 inversions of velocity per character during fluent feedforward motor execution.
  - Children with motor dysgraphia produce 12 to 15+ inversions per character due to continuous closed-loop corrective micro-movements.
* **Empirical Local Calibration:**
  - In `sample_normal_bebek.csv` (fluent 5-letter word), total NIV across all 5 characters is 37 (~7 per letter).
  - In `sample_dyslexia.csv`, a single hesitant letter 'A' produced 71 inversions.
  - Screening thresholds on our canvas are calibrated as: <= 30 Smooth, 31 to 55 Variable, > 55 Hesitant.

---

## 19. User Interface Decoupling & Anti-Jargon Guardrail
* **Decoupled Workflows:** Stroke-to-text decoding must be independent of neural network inference. Testing stroke decoding should not force a heavy backend inference pass.
* **Clean, Non-Intimidating Terminology:** Clinical screening interfaces used by educators and children must avoid academic buzzwords (e.g., using "Movement Smoothness" instead of "Bi-LSTM Kinematic Instability Metric", and "Direction Changes" instead of "EPFL Asselborn NIV Tremor Index").

---

## 20. The Reciprocal Pair Ambiguity in Free Writing (The b-d Dilemma)
When applying horizontal reflection testing, we uncovered a fundamental mathematical distinction between two classes of letter reversals:

* **Class 1: Non-Character Chiral Reversals ($N \to И, S \to Ƨ, E \to Ǝ, 3 \to Ɛ$):**
  These characters possess an intrinsic asymmetry whose mirror reflection does *not* form another valid character in the standard Latin alphabet. Therefore, if mirroring the stroke produces a high-confidence target (e.g., mirrored stroke cleanly matches 'N' or 'S'), it is unconditionally a mirror reversal, even in unprompted free writing.
* **Class 2: Reciprocal Letter Pairs ($b \leftrightarrow d, p \leftrightarrow q, n \leftrightarrow u$):**
  The horizontal reflection of a valid lowercase 'd' is a valid lowercase 'b'. In free-flow writing without an assigned reference prompt, the algorithm cannot determine whether the writer intended to write a 'd' or a 'b'. 
  - *The Trap:* Naively flagging every 'd' whose mirror is 'b' as a "reversed b" causes 100% false-positive reversal rates on regular, correct writing.
  - *The Solution:* In unprompted free-writing, reciprocal pairs must only be evaluated if a prompt is specified (e.g., user was asked to write 'b' but produced 'd'), or through stroke formation directionality (e.g., whether the circular loop was formed clockwise vs. counter-clockwise relative to the vertical stem).

---

## 21. Deep Candidate Pool Matching & Spatial Disconnect in Pediatric Dysgraphia

### The Top-1 Winner Bias in Online OCR
Standard handwriting decoders optimize for maximum-likelihood character sequences under a standard dictionary prior. When a child draws an orthographic reversal such as a mirrored capital **B** (ᙠ), the decoder's language prior actively suppresses the non-standard glyph in `candidates[0]`, preferring visually similar standard symbols (such as `"8"` or `"3"` or `"E"`). 
* *The Finding:* The correct mirrored character (`"B"`) almost always exists within the top 5 alternative candidates (`candidates[0..4]`) of the horizontally reflected stroke.
* *The Solution:* Deep Candidate Pool Search across the top 5 mirror candidates ensures autonomous recovery of chiral reversals without requiring human chip-selection.

### Capital 'B' vs Lowercase 'b' Asymmetry Invariant
* While lowercase `b` and `d` are reciprocal characters (where mirroring produces another valid Latin letter), **capital `B` and `D` are strictly non-reciprocal**.
* A mirrored capital `B` (ᙠ) is an asymmetric chiral reversal, not a `D`.
* Deterministic geometric spine-direction testing ($x_{\text{spine}} \approx x_{\text{max}}$ with left-bulging loops vs. $x_{\text{spine}} \approx x_{\text{min}}$ with right-bulging loops) provides mathematical ground truth that overrides cloud OCR ambiguity.

### Spatial Segmentation Disconnect (The b/d vs l Deficit)
In children with motor dysgraphia or visuospatial integration deficits, writing characters with ascenders and loops (`b`, `d`, `p`, `q`) often involves a pen lift and a spatial pause between drawing the vertical stem and drawing the circular loop:
* *The OCR Failure:* When a spatial gap separates the stem and loop, online stroke clustering frequently isolates the tall vertical stem, transcribing it as `'l'`, `'1'`, or `'I'`, and dropping or splitting the loop into noise (`'lo'`, `'cl'`).
* *The Autonomous Consolidator:* By evaluating the geometric relationship between a tall vertical stroke ($h/w \ge 1.5, h \ge 0.55 H$) and an adjacent lower lobe ($cy > y_{min} + 0.25 H$), the decoder autonomously binds the components:
  - Loop to the right of stem $\to$ **`b`**
  - Loop to the left of stem $\to$ **`d`**
  This completely eliminates false `'l'` transcriptions caused by pediatric motor segmentation.

---

## 22. Writing Speed Invariance & The Equi-Affine Velocity Dilemma in SLD

### The Problem: Velocity Profile Fluctuation
Pediatric handwriting—especially in Specific Learning Disorders (SLD) like motor dysgraphia and dyslexia—displays high velocity variance. Fast writers produce sparse, elongated stroke samples, while hesitant writers produce dense clusters with tremors and local velocity inversions (NIVs).
* *The Failure Mode:* Naive segmentation that relies on temporal time windows ($dt < 300\text{ms}$) or raw Euclidean point distances ($\Delta x > \text{threshold}$) splits slow, hesitant strokes into fragments or merges fast, continuous phrases into a single bounding box.
* *The Clinical Principle (2/3 Power Law):* Human motor control couples velocity nonlinearly to curvature ($v(t) \propto \kappa(t)^{-1/3}$). Raw velocity fluctuates unpredictably across children.
* *The Solution (Arc-Length Parameterization):*
  1. Spatially resample all strokes to uniform arc-length increments ($ds = 3\text{px}$) before clustering.
  2. Normalize horizontal and vertical gap tolerances strictly relative to character height ($H = y_{\text{max}} - y_{\text{min}}$).
  3. Detect cursive ligature splitting points using curvature extrema ($\kappa_{\text{extrema}}$) at the baseline rather than raw velocity drops.

---

## 23. The Dual-Track Hybrid Resolver Architecture

When decoding handwriting in clinical screening, two distinct requirements conflict:
1. **Lexical Context:** Whole words require dictionary priors to resolve ambiguous cursive ligatures.
2. **Clinical Anomaly Detection:** Orthographic mirror reversals (e.g., $D \to ᗡ$, $B \to ꓭ$) are actively suppressed by standard language models, which misclassify them as valid standard letters (e.g., reading $ᗡ$ as `I` or `|`).

### The Architecture:
* **Track 1 (Lexical Backbone):** Google Digital Ink evaluates global stroke flow to provide word context (`candidates[0]`).
* **Track 2 (Clinical Kinematic Inspector):** The In-House Dual-Head ONNX Classifier independently evaluates each isolated stroke cluster $(1, 64, 8)$ for:
  - Head 1: 62-class alphanumeric identity ($p_{\text{char}}$)
  - Head 2: Binary reversal detection ($p_{\text{rev}} \ge 0.50$)
* **The Resolver:**
  - If Head 2 flags a reversal ($p_{\text{rev}} \ge 0.50$), the resolver overrides the lexical engine at that character index, mapping the recognized canonical letter to its exact mirror glyph (e.g., $D \to ᗡ$, $B \to ꓭ$, $b \to d$, $E \to Ǝ$, $N \to И$).
  - If normal ($p_{\text{rev}} < 0.50$), the resolver retains the lexical engine's output.

---

## 24. Clinical Grounding: How Dyslexia & Dysgraphia Are Actually Tested, Why Writing Matters, and Why Task Design Replaces NLP

Synthesized from 10 peer-reviewed clinical and engineering studies added in October 2026:

### 1. How Dyslexia Is Clinically Tested & The Weight of Written Expression
* **UK Certified Assessors Survey ($N = 274$, Daniel et al., 2025, *Annals of Dyslexia*):**
  Clinical dyslexia assessments take a median of 150–220 minutes across 6–8 batteries. Assessors administer:
  - Reading assessments (word reading 91.5%, reading fluency 87.7%, comprehension 85.9%, pseudoword reading 81.1%): **98%**
  - Working memory: **98%**
  - Phonological processing: **97%**
  - **Writing assessments (punctuation, composition): 93%**
  - **Orthographic processing (spelling tests): 93%**
  - Rapid Automatized Naming (RAN): **91%**
  - Fine motor skills: **38%**
* **Norwegian EPS Survey ($N = 118$, Andresen & Monsrud, 2022) & Global School Screening Review (16 studies, Bakhti et al., 2025, *Frontiers in Public Health*):**
  Standardized batteries (Logos, STAS, DDE-2, and Norway's *Dyslexia Marker Test for Children* with **90.6% sensitivity**) treat **nonword/word decoding** and **dictated spelling accuracy (dysorthographia)** as co-primary behavioral diagnostic criteria.

### 2. Predictive Power of Written Expression Alone in Dyslexia Screening
* **Longitudinal Evidence (Andrade et al., 2015, *Frontiers in Psychology*):**
  - On the core Literacy factor in Principal Component Analysis (PCA), **Writing Dictated Words had the single highest loading (0.818)** and **Writing Dictated Pseudowords loaded at 0.765**—exceeding oral reading accuracy (0.787) and reading fluency (0.752).
  - Second-grade written dictation scores alone accounted for **48.8% of the variance** ($p < 0.001$) in 5th-grade literacy status.
  - Using **only written dictation (30 real words + 10 pseudowords)** predicted future poor literacy/dyslexia with **100% Sensitivity, 84.2% Specificity, and 86.7% Overall Accuracy** (rising to **91.1% accuracy** when paired with phonological matching).
  - *Clinical Mechanism (Snowling & Hulme, 2012):* Reading permits partial visual/contextual guessing, whereas spelling requires complete phoneme-to-grapheme mapping and explicit orthographic retrieval from memory. Consequently, writing and spelling deficits are more severe and persistent than reading deficits in individuals with dyslexia.

### 3. Differential Diagnosis via Task Dissociation (Chung et al., 2020, *Translational Pediatrics*)
Comorbidity between writing disorders and reading dyslexia is **30% to 47%**. The three clinical subtypes are separated by comparing **Visual Copying** against **Auditory Dictation / Spontaneous Writing**:
1. **Motor (Peripheral) Dysgraphia:** Fine motor / cerebellar deficit. **Oral spelling is intact**, but **visual copying, dictated writing, and drawing are all impaired** (captured by the 8 standard kinematic features: velocity, acceleration, jerk, pressure, tilt, NIV).
2. **Spatial Dysgraphia:** Visuospatial deficit. **Oral spelling and finger tapping are intact**, but **visual copying, letter spacing, margins, and baseline alignment are impaired**.
3. **Dyslexic Dysgraphia (Dysorthographia):** Inefficiency of the **graphomotor loop** (phonologic-to-orthographic memory transfer). **Visual copying and finger tapping are preserved**, whereas **dictated/spontaneous spelling (especially on pseudowords requiring sublexical phoneme-grapheme conversion) is impaired**, producing pre-writing latency spikes, intra-word in-air stalls, and orthographic errors.

### 4. Static Letter Reversals vs. Letter Position Migrations (Daniel et al., 2025; Hussein et al., 2024)
* **Static Mirror Reversals (`b/d`, `p/q`, `B/D`):** Characteristic of an early developmental stage of literacy (preschool to Grade 1 readiness, Chung et al., 2020; Kaggle/ADM 138,680-letter dataset in Murnani et al., 2025). In older children, static reversals alone do not differentiate dyslexic from non-dyslexic readers.
* **True Dyslexic Orthographic Markers:**
  1. **Sublexical Pseudoword Breakdown:** Errors and latency stalls when writing dictated nonwords (e.g., *lamoken*).
  2. **Letter Position Dyslexia (LPD) / Migrations:** Transposing internal letters in anagram words (e.g., *smile* $\leftrightarrow$ *slime*, *tried* $\leftrightarrow$ *tired*), alongside vowel/consonant omissions (Neglect/Surface dyslexia).

### 5. Why 2D Task Design Replaces Heavy NLP Models (Murnani et al., 2025; Fallah et al., 2025; Patil et al., 2024; Ramlan et al., 2024)
Across 107 studies in Murnani et al. (2025) and 21 AI studies in Fallah et al. (2025), **zero studies require an LLM or open-ended NLP semantic parser**. Instead, cognitive-linguistic load is controlled via **2D Task Design (Content Complexity $\times$ Execution Mode)**:
* **Level 1 (Isolated Letters & Shapes - Copying/Recall):** Evaluates motor automaticity and early visuospatial chiral reversals (`Dual-Head ONNX` + `Bi-LSTM`) with **zero multi-character segmentation ambiguity**.
* **Level 2 (Real Words, Pseudowords, & Migration Words - Copying vs. Dictation):** Isolates Motor/Spatial Dysgraphia from Dyslexic Dysgraphia using `Bi-LSTM` kinematics + Latency/In-Air pauses + deterministic **Damerau-Levenshtein edit distance** against the known target prompt.
* **Level 3 (Fixed Short Sentences - Copying/Dictation):** Evaluates sustained graphomotor endurance, word spacing, baseline drift, and Word Error Rate (WER).

---

## 25. Mathematical Formulations & Parameter Justifications

### 1. Equidistant Arc-Length Parameterization & Cursive Splitting
* **The Problem:** Raw temporal coordinates ($p_i = (x_i, y_i, t_i)$) cause segmentation to fail when children write at varying speeds. Fast writing yields large Euclidean gaps between consecutive samples ($\Delta s > 15\text{px}$), causing premature stroke cuts. Slow or hesitant writing yields dense point clusters ($\Delta s < 1\text{px}$), causing noise spikes and false cursive splits.
* **Continuous Cumulative Arc-Length:**
  $$S_0 = 0, \quad S_i = S_{i-1} + \sqrt{(x_i - x_{i-1})^2 + (y_i - y_{i-1})^2}$$
* **Resampled Equidistant Trajectory ($\Delta s = 3.5\text{px}$):**
  $$P(s) = P_k + \frac{s - S_k}{S_{k+1} - S_k} (P_{k+1} - P_k), \quad s \in [0, S_{\text{total}}]$$
* **Spatial Moving-Average Smoothing (3-point window):**
  $$\tilde{x}_i = \frac{x_{i-1} + 2x_i + x_{i+1}}{4}, \quad \tilde{y}_i = \frac{y_{i-1} + 2y_i + y_{i+1}}{4}$$
* **Cursive Ligature Valley Splitting Criterion:**
  A cursive stroke connecting two characters is split at index $k$ if and only if:
  $$\tilde{y}_k \ge \tilde{y}_{\text{baseline}} - 0.35 H, \quad \tilde{y}_k > \tilde{y}_{k-1}, \quad \tilde{y}_k > \tilde{y}_{k+1}$$
  $$\text{and } \min(\text{width}(\text{body}_1), \text{width}(\text{body}_2)) \ge 0.30 H$$
  where $H = y_{\text{max}} - y_{\text{min}}$ is the word bounding-box height.
* **Academic Grounding:** Plamondon & Srihari (2000, *IEEE TPAMI*); Fallah et al. (2025, *PLOS One*); Ramlan et al. (2024, *Data in Brief*).

### 2. Damerau-Levenshtein Optimal String Alignment (OSA) for Orthographic Deficit
* **The Problem:** Standard Levenshtein distance only accounts for insertions, deletions, and substitutions. In dyslexic dysgraphia, a pathognomonic marker is **Letter Position Dyslexia (LPD)** or character migration (e.g. *smile* $\leftrightarrow$ *slime*, *tried* $\leftrightarrow$ *tired*, Friedmann & Rahamim, 2014; Daniel et al., 2025). Standard Levenshtein scores a transposition as 2 operations (1 deletion + 1 insertion), misrepresenting cognitive-linguistic distance.
* **Formulation:**
  Given expected prompt string $A$ of length $M$ and recognized string $B$ of length $N$:
  $$D(i, j) = \min \begin{cases}
  D(i-1, j) + 1 & \text{(Deletion)} \\
  D(i, j-1) + 1 & \text{(Insertion)} \\
  D(i-1, j-1) + \mathbb{I}(A_i \ne B_j) & \text{(Substitution)} \\
  D(i-2, j-2) + 1 & \text{if } i,j > 1 \text{ and } A_i = B_{j-1} \text{ and } A_{i-1} = B_j \text{ (Adjacent Transposition)}
  \end{cases}$$
* **Normalized Orthographic Error Score ($E_{\text{ortho}}$):**
  $$E_{\text{ortho}} = \frac{D(M, N)}{\max(M, N)} \in [0.0, 1.0]$$
* **Academic Grounding:** Damerau (1964); Levenshtein (1966); Daniel et al. (2025, *Annals of Dyslexia*); Andrade et al. (2015, *Frontiers in Psychology*).

### 3. Multi-Dimensional Specific Learning Disorder (SLD) Risk Scoring Formulation
* **The Problem:** Motor dysgraphia and dyslexic dysorthographia have distinct pathophysiological roots (cerebellar/visuomotor motor control vs. phonological-orthographic retrieval). A single classification score confounds the two disorders.
* **Motor Dysgraphia Risk ($R_{\text{dysgraphia}}$):**
  Evaluated strictly on the 8 standardized kinematic features via the Bi-LSTM network:
  $$R_{\text{dysgraphia}} = P_{\text{Bi-LSTM}}(\mathbf{X}_{1:T}) \times 100\% \quad (\text{Threshold } \ge 50\%)$$
* **Dyslexic Dysgraphia (Dysorthographia) Risk ($R_{\text{dyslexia}}$):**
  Evaluated from the orthographic error, character reversal incidence, and cognitive latency:
  $$R_{\text{dyslexia}} = \min\Big(100\%, \big(0.40 \cdot E_{\text{ortho}} + 0.40 \cdot F_{\text{rev}} + 0.20 \cdot L_{\text{risk}}\big) \times 100\%\Big)$$
  Where:
  - $E_{\text{ortho}} = \frac{D_{\text{OSA}}(\text{target}, \text{recognized})}{\max(M, N)}$
  - $F_{\text{rev}} = \min\left(1.0, \frac{\text{Count}(\text{reversals})}{N_{\text{reversible\_letters}}}\right)$
  - $L_{\text{risk}} = \text{clip}\left(\frac{\text{Latency}_{\text{ms}} - 1200}{2800}, 0.0, 1.0\right)$ (Latency baseline $1200\text{ms}$, severe delay $\ge 4000\text{ms}$)
* **DSM-5 Subtype Dissociation Matrix:**
  $$\text{Diagnosis} = \begin{cases}
  \text{"Combined Dyslexia \& Dysgraphia"} & \text{if } R_{\text{dysgraphia}} \ge 50\% \text{ and } R_{\text{dyslexia}} \ge 50\% \\
  \text{"Motor Dysgraphia"} & \text{if } R_{\text{dysgraphia}} \ge 50\% \text{ and } R_{\text{dyslexia}} < 50\% \\
  \text{"Dyslexic Dysgraphia (Dysorthographia)"} & \text{if } R_{\text{dysgraphia}} < 50\% \text{ and } R_{\text{dyslexia}} \ge 50\% \\
  \text{"Typical Development"} & \text{otherwise}
  \end{cases}$$
* **Academic Grounding:** DSM-5 Specific Learning Disorder criteria (APA, 2013); Chung et al. (2020); Andrade et al. (2015); Daniel et al. (2025).

### 4. Dual-Track Hybrid Resolver Arbitration Logic
* **Formulation:**
  For character cluster $k \in \{1, \dots, K\}$:
  Let $y_{\text{lexical}}[k]$ be the character predicted by Google Digital Ink.
  Let $(c_1, p_{\text{char}}), p_{\text{rev}}$ be the predictions of the In-House Dual-Head ONNX Classifier.
  $$\text{ResolvedGlyph}[k] = \begin{cases}
  \text{MirrorMap}(c_{\text{expected}}) & \text{if } p_{\text{rev}} \ge 0.50 \text{ and isPrompted} \\
  \text{MirrorMap}(c_1) & \text{if } p_{\text{rev}} \ge 0.50 \text{ and isFreeWriting} \\
  y_{\text{lexical}}[k] & \text{if } p_{\text{rev}} < 0.50 \text{ and } y_{\text{lexical}}[k] \ne \text{empty} \\
  c_1 & \text{otherwise}
  \end{cases}$$
  *Domain Mask Invariant:* Numeral reversals ($6 \leftrightarrow 9$) are suppressed when the expected prompt context is alphabetic ($[a\text{-}zA\text{-}Z]$).
* **Academic Grounding:** Murnani et al. (2025); Hussein et al. (2024); Patil et al. (2024).

---

## 26. Bilingual Localization, Moderated Semi-Gamified Data Intake, and Speech Synthesis Architecture

### 1. Unified Bilingual Localization Architecture
* **The Problem:** Clinical tools operated in Indonesia require native Indonesian instructions and field labels for local annotators and pediatric subjects. However, academic validation, research documentation, and international peer review require rigorous English terminology.
* **Synchronized Client-Side State:**
  - Both `data_collector/index.html` (Data Collector) and `data_collector/screening.html` (Screening Evaluator) store and read the active language code (`id` or `en`) via `localStorage.getItem('elkinematics_lang')`.
  - Changing the language toggle pill (`[ID] | [EN]`) on either interface instantaneously applies translation across all DOM elements via data attributes (`data-i18n`, `data-i18n-ph`) and updates internal telemetry/diagnostic text generators without page reloads.
  - When navigating between interfaces, the selected language preference is automatically preserved.
* **Restoration of Full 6-Point Research Guidelines:**
  - The guided usage instructions were restored to full scientific rigor, explicitly educating annotators on:
    1. Dataset type (`Train` vs `Validation`) and annotator attribution.
    2. Classification label mode (`Normal` vs `Dyslexia` / `Dysgraphia`).
    3. Cognitive latency initiation protocol (measuring pre-writing hesitation).
    4. Hardware-level kinematic dynamics: stroke direction ($\Delta x, \Delta y$), velocity ($v$), pressure ($p$), and inter-stroke in-air hesitation ($t_{\text{air}}$).
    5. Server persistence and companion `.meta.json` logging.
    6. Canvas reset and stimulus transition protocol.

### 2. Task-Type Grounded Semi-Gamified Moderated Intake Protocol
* **Clinical Justification by Task Type (Danna et al., 2023; Daniel et al., 2025):**
  - Following the methodological framework established in Danna et al. (2023, *Children* 10(12):1925), cognitive-motor loads are graded by **Task Type** rather than arbitrary lexical claims:
    - *Task Type 1 (Isolated Letters & Digits):* Evaluates baseline visuospatial orientation and mirror reversals ($b, d, p, q, m, w, 3, 6, 9$).
    - *Task Type 2A (High-Frequency Regular Words):* Assesses lexical graphomotor flow and velocity-invariant arc-length trajectories in typical Indonesian vocabulary (`buku`, `kucing`, `pohon`, `dadu`, `meja`, `sekolah`).
    - *Task Type 2B (Transposition & Migration Anagram Words):* Directly targets Letter Position Dyslexia (LPD) and orthographic transposition errors (`kapal` / `pakal`, `kasur` / `rusak`, `bakar` / `kabar`).
    - *Task Type 3 (Short Continuous Sentences):* Evaluates sustained graphomotor endurance, inter-word spacing, and baseline stability (`budi suka baca buku cerita`, `kucing hitam tidur di kasur`).
* **Semi-Gamification & Throughput Optimization:**
  - To eliminate annotator cognitive fatigue and data entry bottlenecks, a one-time session setup modal configures: Annotator Name, Target Dataset, Classification Mode, Execution Mode (*Visual Copying* vs. *Spoken Dictation*), and Batch Count ($N = 5, 10, 20$).
  - Once started, the engine automatically draws pseudorandom balanced items from the target pools, displays dynamic progress bars (`Item i of N`), automatically clears canvas state upon submission, and presents the next item seamlessly.

### 3. Examiner-Administered Oral Dictation Protocol & Speech Fallback Architecture
* **Clinical Justification over Synthetic TTS (Daniel et al., 2025; Danna et al., 2023; Chung et al., 2020):**
  - In standardized pediatric psycho-educational batteries (e.g. WIST, WIAT-III, BHK), oral spelling and dictation subtests are administered by a human examiner speaking the target word aloud with natural cadence and phonemic clarity (e.g., *"Tulis kata: bebek. Bebek."*).
  - Synthetic TTS models introduce robotic formant flattening and unnatural prosody, which disproportionately confound children with subtle auditory processing or phonological discrimination deficits.
  - Formally establishing the primary protocol as **Examiner-Administered Oral Dictation** elevates the clinical and ecological validity of the dataset.
* **Examiner HUD & Latency Trigger:**
  - In *Examiner Spoken Dictation* mode, the visual target is masked on the child's canvas area to prevent visual copying shortcuts.
  - The target glyph/word is displayed prominently in an Examiner HUD callout (`Instruksi Penguji: Ucapkan kata berikut ke anak: "bebek"`).
  - Once the examiner finishes speaking, they trigger latency timing via an on-screen button (`Mulai Ukur Latency`) or keyboard shortcut (`Spacebar`).
  - If the participant touches the canvas prior to manual trigger, an automatic baseline reaction window ($350\text{ms}$) is applied.
* **Zero-Dependency Audio Fallback:**
  - External network TTS dependencies are disabled to ensure offline reliability in field and school settings.
  - An optional browser speech button (`window.speechSynthesis`) is maintained in the Examiner HUD for solo testing workflows, automatically initiating latency timing once synthetic speech terminates.

### 4. Data Storage & Pipeline Backward Compatibility
* **Filename Continuity:**
  - Downstream training and evaluation scripts in `scripts/universal_pipeline.py` rely on string-based filename tokenization.
  - To prevent pipeline breakage, files continue to be written to disk following the standardized legacy pattern: `${dataset}_${mode}_${prompt}_${annotator}_${timestamp}.csv` and `.png`.
* **Companion Metadata Manifest (`.meta.json`):**
  - All extended clinical fields (session ID, task tier, execution mode, language code, cognitive latency, raw stroke count) are written synchronously as a companion `.meta.json` sidecar alongside the CSV and PNG, enabling rich longitudinal cohort analytics without altering legacy binary parsers.

---

## 27. Hardware-Agnostic Digitizer Normalization & Cross-Device Generalization

### 1. The Multi-Hardware Discrepancy Problem
* **Empirical Observation:** Comparing samples across high-end active digitizers (iPad + Apple Pencil) versus budget capacitive hardware (Huawei tablet + generic stylus) reveals four critical sensor discrepancies:
  1. *Temporal Polling Discrepancy:* iPad records at $\approx 120\text{Hz}$ ($\approx 360$ points per 3-second stroke), while budget hardware records at $\approx 25\text{Hz}$ ($\approx 75$ points per 3-second stroke).
  2. *Sequence Length & Zero-Padding Bias:* Under fixed sequence input (`MAX_TIMESTEPS = 500`), the budget sample contains $425$ padded zeros, whereas the iPad sample contains only $140$ padded zeros. Neural classifiers rapidly learn to discriminate the hardware polling rate rather than neuromuscular pathology.
  3. *Sensor Channel Invariance (Tilt):* Active digitizers report continuous dual-axis tilt (`tiltX`, `tiltY`), while passive capacitive styluses report constant $0.00$.
  4. *Uncalibrated Pressure Ranges:* Certain Android drivers emit uncalibrated raw pressure values exceeding the standard $1.00$ maximum (e.g. up to $2.20$), resulting in extreme z-score outliers ($z > 5.0$) against pre-fitted standard scalers.

### 2. Standardized Temporal Resampling ($\Delta t = 16.67\text{ms}$, $60\text{Hz}$)
* **Mathematical Invariant:**
  To decouple sequence length and derivative calculations from hardware polling fluctuations, stroke trajectories are resampled onto an equidistant temporal grid:
  $$t_{\text{grid}} = [t_0, t_0 + \Delta t, t_0 + 2\Delta t, \dots, t_{\text{end}}], \quad \Delta t = \frac{1000.0}{\text{SAMPLING\_RATE\_HZ}} = 16.67\text{ms}$$
* Continuous spatial coordinates $(x, y)$, pressure ($p$), and tilt channels are interpolated linearly:
  $$x(t) = x_k + \frac{t - t_k}{t_{k+1} - t_k} (x_{k+1} - x_k)$$
* **Outcome:** A 3-second handwriting stroke produces exactly $180$ timesteps regardless of whether recorded on an iPad ($120\text{Hz}$ downsampled) or a budget tablet ($25\text{Hz}$ upsampled), preserving identical kinematic derivative scales and eliminating zero-padding shortcut learning.

### 3. Client-Side Pressure Normalization & Device Auditing
* **Pressure Clamping:**
  Raw pressure readings are guarded on input:
  $$p_{\text{norm}} = \text{clip}\left(\begin{cases} \frac{p_{\text{raw}}}{2.5} & \text{if } p_{\text{raw}} > 1.0 \\ p_{\text{raw}} & \text{otherwise} \end{cases}, 0.0, 1.0\right)$$
* **Automated Device Auditing:** Every collected sample records client hardware parameters (`navigator.userAgent`, screen dimensions, `devicePixelRatio`, `maxTouchPoints`) in the companion `.meta.json` sidecar.

### 4. Cross-Hardware Experimental Strategy for Academic Publishing
* **Preserving Existing Data:** Data collected across different hardware must **not** be discarded. It provides empirical proof of real-world generalization:
  * *Benchmark 1 (Cross-Hardware Zero-Shot Evaluation):* Train on iPad reference data, evaluate generalization performance on budget Android tablets without re-training.
  * *Benchmark 2 (Mixed Cohort Training):* Harmonize iPad and Huawei samples into a unified training distribution, demonstrating robustness across hardware tiers.
  * *Golden Invariant:* Ensure diagnostic labels (`Normal` vs `Dyslexia`/`Dysgraphia`) are never completely segregated by hardware device.

### 5. iPadOS WebKit Stylus Long-Press & Accidental Selection Suppression
* **The Problem:** In iPadOS Safari, holding down an Apple Pencil or capacitive stylus (or pausing briefly before writing) causes WebKit's default gesture engine to trigger text selection handles, magnifying glasses, image drag-and-drop, or the system context menu ("Copy | Look Up | Share"), accidentally selecting the whole canvas or surrounding layout.
* **The Solution:**
  1. *CSS Selection & Callout Suppression:* Apply `-webkit-user-select: none; user-select: none; -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent;` to `body` and `canvas`, while explicitly preserving `-webkit-user-select: text; user-select: text;` on text fields (`input, select, textarea`).
  2. *Drag Suppression:* Apply `-webkit-user-drag: none;` on `canvas` so WebKit never treats canvas strokes as draggable image objects.
  3. *Pointer Capture Locking:* Invoke `canvas.setPointerCapture(e.pointerId)` on `pointerdown` and `canvas.releasePointerCapture(e.pointerId)` on `pointerup` and `pointercancel`, directing all stylus trajectory events strictly to the canvas.
  4. *Synthetic Context Menu Neutralization:* Intercept `contextmenu` and `selectstart` events on `canvas` via `e.preventDefault()`.

---

## 28. Canvas PNG Image Export Calibration & Dual-Track Reversal Arbitration

### 1. Canvas PNG Coloration & Transparency Artifacts
* **The Problem:** In HTML5 Canvas 2D contexts, calling `ctx.clearRect()` resets all pixels to transparent black (`rgba(0,0,0,0)`). When strokes are rendered with dark slate styling (e.g. Tailwind `slate-900` `#0f172a`, RGB `15, 23, 42`) and exported via `canvas.toDataURL('image/png')`, the resulting `.png` file has a transparent background. When opened in photo galleries, dark-mode viewers, or computer vision scripts without alpha compositing, the transparent background causes the strokes to appear visibly blue/navy or get distorted against dark backgrounds.
* **The Invariant:**
  1. Stroke drawing style must use pure solid black `#000000` (RGB `0, 0, 0`).
  2. Image export (`postSample()`) must composite the active canvas over an offscreen buffer filled with solid white `#ffffff` (RGB `255, 255, 255`) prior to serialization, guaranteeing crisp, non-transparent pure black ink on solid white paper for all datasets on disk.
  3. Raw sensor CSV coordinates remain 100% pure hardware events.

### 2. Dual-Track Hybrid Resolver Arbitration & Clinical Reversal Representation
* **The Problem:** When character reversals are detected (e.g. reversed 'B' or 'd'), two conflicts arose in the transcription resolver:
  1. *Case Sensitivity Discrepancy:* In Free Writing mode, 62-class Head 1 classification biased toward lowercase `'b'`, which mapped to `'d'`. To the examiner, drawing an uppercase reversed 'B' displayed as lowercase `'d'`.
  2. *Lexical Overwrite:* The resolver previously tied character replacement to Google Digital Ink's string indices (`rawWinner.split('')`). If Google Ink recognized a reversed 'b' as 'd', substituting `'d'` made it appear that the reversal was ignored. If Google Ink returned a different word length (or dropped spaces), indices were thrown out of alignment.
* **The Invariant:**
  1. *Prompt & Height-Aware Case Disambiguation:* In Prompted Mode, the prompt target casing is preserved. In Free Writing Mode, tall strokes ($\ge 55\text{px}$) or uppercase candidate agreement in Head 1 top-3 are promoted to uppercase.
  2. *Direct Character Representation:* Reversals are never silently replaced with unreversed canonical characters. To keep both the transcript result and the diagnostics clean and unencumbered by artificial formatting, the interface renders the exact detected character glyph directly (e.g. `ꓭ`, `ᗡ`, `d`, `b`, `q`, or `debek`), completely eliminating verbose bracket annotations (`[ normal -> reversed ]` or `[Rev: ...]`).
  3. *Consistent Payload:* Both `displayWinner` and `cleanWinner` carry the exact glyph string, ensuring direct visual-to-phonetic alignment and pure Levenshtein edit distance calculations in `/analyze`.---

## 29. Standardized Indonesian Linguistic Corpus, Zero-Digit Orthographic Invariant, and Anti-Repetition Randomization

### 1. Orthographic Screening Scope & The Zero-Digit Invariant
* **Scope Definition:** The Elkinematics system screens for Specific Learning Disorder (SLD) subtypes: Motor Dysgraphia, Spatial Dysgraphia, and Dyslexic Dysgraphia (Dysorthographia) under DSM-5 criteria. Mathematical calculation (dyscalculia) and numeral handwriting are outside this scope.
* **The Invariant:** Numeric digits (`0–9`, specifically legacy chiral digits `3`, `6`, `9`) are completely eliminated from all stimulus banks, candidate pools, and generation algorithms. Level 1 evaluates strictly the Latin alphabet: all 26 lowercase letters ($a\text{–}z$) and 26 uppercase letters ($A\text{–}Z$), with balanced weighting toward clinically significant chiral letters ($b, d, p, q, B, D, E, S, N, C, J, L, P, R, Z$).

### 2. Standardized Indonesian Linguistic Corpus (`vocabularies/stimuli_id.json`)
* **Decoupled Architecture:** Hardcoded JavaScript arrays are replaced by an extensible, structured JSON repository grounded in early childhood literacy research (EGRA Indonesia, USAID PRIORITAS, Danna et al. 2023):
  * **Level 1 (Alphabet Letters):** 52 lowercase and uppercase letters with 15 chiral priority items.
  * **Level 2A (High-Frequency Regular Words):** 68 two-to-three syllable CVCV/CVCVC words across 5 authentic categories (animals, common objects, family, nature, food).
  * **Level 2B (Letter Migration Anagram & Minimal Pairs):** 22 anagram transposition pairs (e.g. *batu/buta, kasur/rusak, tali/liat, kapal/pakal*) and 16 minimal phonological contrast pairs (e.g. *bata/data, pola/bola, buku/kuku*) designed to expose sublexical position migrations.
  * **Level 2C (Pronounceable Pseudowords):** 33 pronounceable Indonesian nonwords (e.g. *kumo, mado, beka, tuko, dapi, fodi*) conforming to standard Indonesian phonotactics to test sublexical phoneme-grapheme conversion without whole-word visual memory shortcuts.
  * **Level 3 (Standardized Sentences):** 18 standardized short sentences (4–6 words) suitable for early primary school children.
* **Embedded Fail-Safe Fallback:** The client embeds a complete fallback memory bank (`DEFAULT_STIMULUS_BANK`), ensuring 100% offline and standalone functionality if HTTP fetching is blocked.

### 3. Intra-Session Uniqueness & History Anti-Repetition Buffer
* **The Repetition Problem:** Small stimulus arrays and rigid tier-alternating sorting previously caused consecutive sessions to present the exact same sequence of words, reducing participant engagement and biasing data collection.
* **The Solution:**
  1. *Intra-Session Uniqueness:* Candidate pools are sampled without replacement within each session, guaranteeing 0 duplicate items across all session lengths ($5, 10, 15, 20, 26$).
  2. *Cross-Session Memory Buffer:* Recent prompts are cached in `sessionStorage` (`elkinematics_recent_stimuli`, rolling buffer of 80 items). The generator filters out recently presented items, ensuring participants encounter fresh vocabulary across multiple consecutive sessions.
  3. *Adaptive Anti-Clash Shuffling:* Resolves adjacent tier or prompt clashes for multi-tier sessions, while correctly permitting same-tier consecutive prompts in single-tier focused runs.

### 4. Examiner Tier Focus Selector
* **Clinical Purpose:** In research or diagnostic contexts, examiners often need to target specific subtests (e.g. collecting purely chiral letters, or running a focused anagram-migration battery).
* **The Selector:** A dropdown `#modTierFocus` allows selecting:
  * `All Levels (Balanced)`: 25% L1, 25% L2A, 20% L2B, 15% L2C, 15% L3.
  * `Letters Only (Level 1)`: 100% Alphabet letters.
  * `Regular Words Only (Level 2A)`: 100% High-frequency vocabulary.
  * `Anagram Words Only (Level 2B)`: 100% Migration/anagram pairs.
  * `Pseudowords Only (Level 2C)`: 100% Sublexical nonwords.
  * `Sentences Only (Level 3)`: 100% Short standardized sentences.
* **Clinical Traceability:** The selected `tier_focus` is logged in the companion metadata alongside `task_tier` and `execution_mode`, preserved across reloads via `localStorage`.

---

## 30. IEEE Conference Template (A4 Format) Grounding Guidelines and Publication Invariants

### 1. Document Architecture & Length Restrictions
* **Page Limit:** Strictly **4 to 6 pages** in IEEE A4 2-column format (approximately 3,000–5,000 words including figures, tables, equations, and references).
* **Title Invariants:** Strictly zero mathematical notation, special symbols, or footnotes in the paper title. Subtitles are prohibited (not indexed by IEEE Xplore). If the words *"that uses"* can replace *"using"*, capitalize *"Using"*; otherwise, keep *"using"* lower-case.
* **Abstract Invariants:** Must be a self-contained, single-paragraph overview (150–250 words). *CRITICAL:* Do not use symbols, special characters, footnotes, math, or bracketed citations (`[1]`) in the abstract.
* **Index Terms:** Prefixed by `Keywords—` or `Index Terms—` formatted with an em-dash.

### 2. Authors and Affiliations
* Maximum of 6 authors in the default configuration, arranged horizontally from left to right across columns, wrapping to the next line.
* Keep affiliations succinct: do not differentiate departments within the same parent organization or university.

### 3. Equations and Mathematical Typography
* **Equation Numbering:** Consecutively numbered flush right with parentheses: `(1)`, `(2)`. Center-aligned via tab stop.
* **In-Text Citation:** In running text, refer strictly as `(1)`, **never** `Eq. (1)` or `equation (1)`, except at the beginning of a sentence (*"Equation (1) is..."*).
* **Font Standards:** Italicize Roman characters for variables and physical quantities ($x, y, v, a, j, P, T, w$). Keep Greek symbols upright/non-italicized ($\theta, \phi, \mu, \sigma, \tau$).
* **Operators & Punctuation:** Use an en-dash or minus sign ($-$), never a hyphen (`-`), for minus/subtraction. Punctuate equations with commas or periods when they conclude or form clauses in a sentence. Define all symbols before or immediately after the equation.

### 4. Figures and Tables Layout
* **Column Positioning:** Position figures and tables strictly at the **top** or **bottom** of columns. Never position figures or tables in the middle of a column. Large figures/tables may span across both columns.
* **Captions & Headers:** Table heads appear **above** tables (`TABLE I: Title`); Figure captions appear **below** figures (`Fig. 1. Description`).
* **In-Text Reference:** In running text, always use `Fig. 1` (even at the start of a sentence).
* **Axis Labels:** Axis labels must be 8 pt Times New Roman, written as full descriptive words, not bare mathematical letters (e.g., `Velocity (px/s)`, not just `v`). Units enclosed in parentheses, never ratios (`Velocity (px/s)`, not `Velocity/px/s`).

### 5. References & Citation Standards
* **In-Text Citations:** Numbered consecutively in brackets `[1]`, with sentence punctuation placed *after* the closing bracket (`...as shown in [1], [3].`). Refer simply as `[1]`, never `Ref. [1]`, unless starting a sentence.
* **Author List:** List all authors up to 5 authors. Use `et al.` only for **6 or more** authors.
* **Article Title Capitalization:** Sentence case (capitalize only the first word and proper nouns). Journal names and conferences use title case in italics.
* **Status Labels:** Explicitly label unpublished work as `unpublished` and accepted work as `in press`.

### 6. Lexical & Editorial Invariants (IEEE Style Guide)
* **American English:** Use American spelling (`acknowledgment` without middle 'e', `modeling`, `behavior`).
* **Grammatical Plurality:** The word `"data"` is strictly **plural** (*"The data show..."*, not *"The data shows..."*).
* **Leading Zeros:** Always use a leading zero before decimals (`0.25`, not `.25`).
* **Unit Formatting:** Primary units must be SI (MKS). Spell out units in text (*"a few henries"*). Use `cm3`, not `cc`.
* **Prefixes:** The prefix `"non"` is joined directly without hyphens (*nonwords, nonparametric, nonlinear*).
* **Word Choice:** Use `"alternatively"` (not `"alternately"`), `"inset"` for a graph within a graph (not `"insert"`). Avoid `"essentially"` as a vague filler for *"approximately"* or *"effectively"*. Distinguish homophones (*affect* vs *effect*, *discrete* vs *discreet*, *principal* vs *principle*, *imply* vs *infer*).
* **Scientific Constants:** Vacuum permeability constant is $\mu_0$ (subscript zero, not letter 'o').
* **Latin Abbreviations:** `"i.e."` (that is), `"e.g."` (for example), and `"et al."` (no period after `et`).
* **Template Hygiene:** Completely excise all template instructional text, sample text, and placeholder annotations prior to document submission.

---

## 31. Strict Physical Document Grounding Invariant (Zero-Hallucination Citation Policy)

### 1. The Principle
* **Problem:** Large language models frequently hallucinate academic citations, author names, years, or venues when generating scholarly prose, or carry over unverified references from legacy bibliographies. In academic peer review (especially IEEE), a single non-existent reference or misattributed claim severely damages paper credibility.
* **The Invariant:** Every academic citation, author name, publication year, and empirical finding integrated into manuscripts or research artifacts must be grounded strictly and exclusively in physical PDF documents present on disk within `academic_resources/`.
* **Zero-Hallucination Policy:** Agents must never invent references, pull unverified citations from general memory, or import external citations from older rejected manuscripts without verifying that the source PDF file is present in `academic_resources/`.

### 2. Physical Verification Catalog (Mendeley Grounded)
All citations for the current manuscript are cross-referenced with their physical PDF filenames:
* *DSM-5:* `academic_resources/DSM-5.pdf` (American Psychiatric Association, 2013)
* *SLD Neurobiology & Comorbidity:* `academic_resources/Specific_Learning_Disorders_Neurobiological_Founda.pdf` (Flores, 2025); `academic_resources/tp-09-S1-S46.pdf` (Chung et al., 2020)
* *Developmental Dyslexia & Orthography:* `academic_resources/children-12-00572.pdf` (Traficante et al., 2025); `academic_resources/flang-4-1504770.pdf` (Martínez-Tomás et al., 2025); `academic_resources/fpsyg-13-1063021.pdf` (Germano & Capellini, 2023)
* *Handwriting Kinematics & Robotics:* `academic_resources/1-s2.0-S1746809425010717-main.pdf` (Brescia et al., 2026); `academic_resources/journal.pdig.0001503.pdf` (Toffoli et al., 2026); `academic_resources/frai-8-1426455.pdf` (Babushkin et al., 2025); `academic_resources/Multi-Dimensional_Parameters_for_the_Clinical_Diagnosis_of_Dysgraphia_in_School-Aged_Children.pdf` (Sindhu & Kavitha, 2026)
* *Computer Vision & Image Baselines:* `academic_resources/3573128.3609351.pdf` (Gemelli et al., 2023); `academic_resources/jdr20240010.pdf` (Aldehim et al., 2024); `academic_resources/peerj-cs-3296.pdf` (Al Abadleh et al., 2025); `academic_resources/jdr20250612.pdf` (Al Abadleh & Al-Shqeerat, 2025)
* *Machine Learning Software Engineering & Prototyping:* `academic_resources/3461778.3462163.pdf` (Scurto et al., 2021); `academic_resources/1-s2.0-S0164121223003023-main.pdf` (Serban et al., 2024)
* *Digital Screening & Gamified Assessment:* `academic_resources/fpsyg-17-1872307.pdf` (Micalizzi & Zaccaria, 2026); `academic_resources/s42979-025-03927-0.pdf` (Rangasrinivasan et al., 2025)





## 32. Multi-Attribute Risk Integrator: Evidence Status of Weights, Threshold, and Fuzzy Logic Alternative

### Formulas under discussion
```
R_dysgraphia = K_score * 100%
R_dyslexia   = min(1.0, 0.40 * E_ortho + 0.40 * F_rev + 0.20 * L_risk) * 100%
```

### Evidence status
- No paper in `academic_resources/` supports the weights 0.40 / 0.40 / 0.20. They are heuristic design choices.
- No citation exists for the 50% decision threshold or for the piecewise latency function (offsets of 1000 and 500, divisor 2000). These originate from engineering iterations.
- The literature supports the individual inputs, not their aggregation: latency or pauses, reversals, spelling errors, and kinematic instability (Germano & Capellini; Martinez-Tomas et al.; Traficante et al.; Brescia et al.).
- Section II must not describe the weights as "clinically calibrated". Use wording such as "expert-informed heuristic weights, not fitted to clinical outcomes".
- Expected reviewer question: how were the weights chosen, and were they validated.

### Weighted linear sum: suitability
Advantages for a RAD prototype:
- Transparent and consistent with the explainable AI theme.
- Requires no clinical outcome labels, which are not available.
- Trivial CPU cost.
- Per-component contribution can be shown to educators.

Weaknesses:
- Arbitrary weights.
- Assumes independent additive components.
- Arbitrary hard cutoff at 50%.

### Fuzzy logic alternative
For:
- Linguistic rules (IF latency is high AND reversal is present THEN dyslexia risk is high) resemble clinical reasoning.
- Gradual class boundaries instead of a hard cutoff.
- Can model interactions between components.

Against, for the current project:
- Membership functions and rule bases also require expert-set parameters, so the arbitrariness is relocated rather than removed.
- Without clinician input or outcome labels the rules are equally ungrounded and more complex.
- Harder to explain within 4 to 6 pages.
- The rule base grows with each added feature.
- No fuzzy-logic citation may be taken from memory. Only papers physically present in `academic_resources/` may be cited.

### Decisions
1. Keep the weighted sum.
2. Present weights as initial heuristics and the integrator as a transparent rule-based layer, not a validated diagnostic model.
3. Add a weight sensitivity analysis (vary each weight by 0.10 on tablet data, report the number of changed screening flags).
4. List fuzzy inference, logistic regression, and learned fusion layers as future work once clinician-labeled data exists.
5. Present the 50% cutoff as a screening flag, consistent with the non-diagnostic disclaimer invariant.

### Literature search results for the integrator (arXiv and OpenAlex, 2026-10-22)
Candidates found online. None are in `academic_resources/` yet. Per Section 31, download the PDF into `academic_resources/` and read it before citing.

| Candidate | Source | Relevance to integrator |
| :--- | :--- | :--- |
| Mun & El-Yacoubi, "Profiling Handwriting-Process Deviations in Developmental Dysgraphia" (2026), arXiv 2609.15435 | arXiv | Reports a multi-domain deviation profile with bootstrap uncertainty and no single diagnostic label. Supports presenting separate risk indices as screening profiles. |
| Robaa et al., "Multimodal Ensemble with Conditional Feature Fusion for Dysgraphia Diagnosis" (2024), arXiv 2408.13754 | arXiv | Precedent for fusing multiple data streams; relevant to the learned-fusion future work. |
| Andrade-Arenas & Yactayo-Arias, "Expert system for diagnosing learning disorders in children" (2024), doi 10.11591/ijece.v14i3.pp2965-2975 | OpenAlex | Rule-based expert system for learning disorders, 21 simulated cases. Precedent for transparent rule-based screening. Abstract does not state fuzzy logic. |
| Zolna et al., "The Dynamics of Handwriting Improves the Automated Diagnosis of Dysgraphia" (2019), arXiv 1906.07576 | arXiv | Online-handwriting RNN precedent. |

Gap: no paper was found that applies fuzzy logic to handwriting-based dyslexia or dysgraphia screening, and none supports the 0.40/0.40/0.20 weights. The weights remain heuristic.

### Verified findings from the four downloaded PDFs (read 2026-10-22)
Correction: arXiv 2408.13754 is by Kunhoth, Al Maadeed, Saleh, and Akbari (Qatar University). The earlier attribution to "Robaa et al." was wrong and came from a different search result. Use the PDF's author list.

| Paper (file) | Verified content | Use in integrator |
| :--- | :--- | :--- |
| Mun & El-Yacoubi, 2026 (`2609.15435v1.pdf`) | 12-axis deviation profile on 257 children. States that no classifier is trained, results are uncertainty-aware deviation scores rather than a diagnostic label, and "neither a binary label nor a single aggregate deviation score can substitute for the profile". Output is marked "Hypothesis-generating, not a diagnosis". | Supports reporting two separate indices (R_dysgraphia, R_dyslexia) as a screening profile and the non-diagnostic framing. Also a caution against reducing results to one scalar. Their domain scores are normative z-scores with bootstrap CIs; our weighted sum is not. |
| Kunhoth et al., 2024 (`2408.13754v1.pdf`) | Compares early feature fusion, soft-voted late fusion, and a conditional fusion method that applies feature fusion only when the confidence difference falls below a threshold. Runs a sensitivity analysis over thresholds 0.10 to 0.30 and reports performance stable across the range (best 88.8% accuracy on pseudowords). | Precedent for (a) threshold-gated decision logic and (b) reporting a threshold sensitivity analysis. Supports adding our own weight and cutoff sensitivity check. |
| Andrade-Arenas & Yactayo-Arias, 2024 (`34869-69960-1-PB.pdf`) | Rule-based expert system built on if/then rules applied cumulatively to symptom inputs. 21 simulated cases: accuracy 95%, precision 100%, sensitivity 93%, specificity 100%. Authors note the use of simulated cases as a limitation. | Precedent for transparent rule-based screening logic in learning-disorder tools. It is not a source for fuzzy logic or for weights. |
| Zolna et al., 2019 (`1906.07576v1.pdf`) | Online-handwriting RNN on tablet data for dysgraphia; reports identifying more than 90% of children diagnosed by the BHK test. | Background for the kinematic stream only. Not relevant to the integrator weights. |

Remaining gap: none of the four papers supplies weights or a cutoff for combining orthographic, reversal, and latency components. The 0.40 / 0.40 / 0.20 weights and the 50% threshold stay labeled as heuristics.


## 33. Monte Carlo Parameter Sensitivity Protocol, Balanced Four-Quadrant Boundary Cohorts, and Seed Reproducibility

### Context and Problem
Our multi-attribute clinical risk integrator employs expert-informed heuristic weights ($w_{\text{spell}} = 0.40, w_{\text{rev}} = 0.40, w_{\text{lat}} = 0.20$) and a screening threshold ($\theta = 50\%$). Because these parameters are not fitted via supervised learning over a massive clinical cohort, reviewers will naturally probe whether screening classifications are fragile or sensitive to arbitrary magic numbers.

### Methodological Protocol (Kunhoth et al., 2024, Table 4)
To demonstrate parameter robustness, we implement a Monte Carlo parameter sensitivity analysis script (`scripts/eval_integrator_sensitivity.py`) that systematically perturbs weights ($w \pm 0.10$) and sweeps decision thresholds ($\theta \in [0.40, 0.60]$).

### 1. Balanced Four-Quadrant Boundary Cohort (`n_samples = 400`)
The 400 samples represent a balanced, controlled stress-test cohort spanning the four DSM-5 clinical quadrants (100 samples per quadrant) designed to stress-test boundary classifications:
1. **Typical (100 samples):** Low kinematic tremor ($K \in [10, 42]\%$), low spelling error ($E \le 0.25$), zero reversals, typical latency ($L \le 0.25$).
2. **Isolated Motor Dysgraphia (100 samples):** High kinematic tremor ($K \in [58, 95]\%$), low spelling error ($E \le 0.30$), zero reversals, typical latency ($L \le 0.30$).
3. **Isolated Dyslexia (100 samples):** Intact motor kinematics ($K \in [15, 44]\%$), elevated spelling errors ($E \in [0.40, 0.90]$), frequent mirror reversals ($p_{\text{rev}} \ge 0.50$), and prolonged working-memory latency ($L \in [0.35, 1.0]$).
4. **Comorbid SLD (100 samples):** Impaired motor kinematics and elevated orthographic/reversal errors simultaneously.

### 2. Deterministic Reproducibility (`seed = 42`)
In scientific computing and benchmark publications, setting a fixed pseudo-random number generator seed (e.g. `np.random.seed(42)`) is mandatory for bitwise reproducibility:
- Prevents random fluctuation across test runs (guaranteeing exact concordance outputs: 97.00%, 99.75%, 94.50%).
- Provides an exact scientific audit trail for external researchers and journal reviewers reproducing the paper's code.

### 3. Empirical Results
- **Threshold Stability ($\theta \in [0.45, 0.60]$):** Concordance $\ge 94.5\%$ (97.0% at $\theta = 0.45$, 99.75% at $\theta = 0.55$).
- **Weight Perturbations ($w \pm 0.10$):** Concordance $\ge 97.0\%$ across all configurations (Orthographic emphasis, Reversal emphasis, Latency balanced, and Equal linguistic).
