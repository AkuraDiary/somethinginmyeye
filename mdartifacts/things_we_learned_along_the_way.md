# Things We Learned Along the Way 🧠

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
