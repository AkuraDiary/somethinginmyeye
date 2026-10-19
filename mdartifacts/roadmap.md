# Elkinematics Project Roadmap: Dual-Stream SLD Screening & Academic Publication

This document serves as the centralized roadmap for engineering milestones, scientific validation, and publication deliverables for the **Elkinematics** project.

---

## Target Milestones & Timeline Overview

| Milestone | Target Window | Primary Focus | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1: Architecture Centralization** | August - October 14, 2026 | Kinematic pipeline, model consolidation, config centralization | **Completed** |
| **Phase 2: Dual-Stream SLD Screening Prototype** | October 15 - 18, 2026 | Transparent stroke coder, reflection reversal detection, tablet UI | **In Progress** |
| **Phase 3: Statistical Validation & Benchmarking** | October 19 - 22, 2026 | Hold-out train and validation evaluation, disfluency significance tests (NIV/Jerk/Latency) | **Upcoming** |
| **Phase 4: IEEE Conference Submission** | October 23 - 26, 2026 | Final manuscript polish, figure rendering, Word compilation | **Hard Deadline: Oct 26** |
| **Phase 5: Journal Expansion (JISEBI)** | Post-Conference (Q4 2026) | Full IMRaD expansion, pediatric dataset scaling, on-device TFLite | **Planned** |

---

## Detailed Phase Breakdown

### Phase 1: Kinematic Foundation & Centralized Architecture (Completed)
- [x] **8 Standard Kinematic Features:** Enforce canonical feature vector `[delta_x, delta_y, pressure, tiltX, tiltY, velocity, acceleration, jerk]` with `latency` as secondary scalar.
- [x] **Model Centralization:** Consolidate all neural architectures (V0 Baseline CNN, V1 CNN+XAI, V2 Bi-LSTM) into `scripts/model_builder.py`.
- [x] **Configuration Centralization:** Consolidate all hyperparameters, sequence limits (`MAX_TIMESTEPS=500`), and paths into `scripts/config.py`.
- [x] **Experimentation Playground:** Establish `playground.ipynb` as the sole staging and research ground.
- [x] **Automated Observability:** Implement centralized SQLite ledger (`agents/logs/ledger.db`) with lifecycle syncer.
- [x] **Academic Archive Consolidation:** Consolidate all 48 reference PDFs (including the 10 clinical/engineering studies added on October 19, 2026) into `academic_resources/`.

---

### Phase 2: Dual-Stream SLD Screening Prototype (Current Workstream)
- [x] **Differential Framework Architecture:**
  - Stream 1: Bi-LSTM kinematic inference evaluating motor dysgraphia instability.
  - Stream 2: Orthographic trajectory decoder evaluating spelling distance, letter migrations, and mirror reversals.
  - Stream 3: Initiation latency and intra-word in-air pause tracking working memory and graphomotor loop hesitation (> 1500 ms).
- [x] **In-House Dual-Head Isolated Reversal & Kinematic Classifier (`dual_head_reversal.onnx`):**
  - Head 1: 62-class alphanumeric character identity recognition ($73.73\%$ top-1, $>90\%$ top-3).
  - Head 2: Clinical orthographic reversal classifier ($0.9982$ ROC-AUC, $98.5\%$ binary accuracy).
  - WebAssembly runtime integration in browser via ONNX Runtime Web (`ort.min.js`).
- [x] **Tablet Canvas & Ergonomics:**
  - Lock root viewport to eliminate pull-to-refresh reloads (`html, body { position: fixed; overflow: hidden; }`).
  - Implement tactile on-screen vertical touch scrollbar for seamless navigation on touchscreens.
  - Replace academic and engineering jargon with clean, neutral labels.
- [x] **Model Transparency & Diagnostics Interface:**
  - Dedicated on-canvas multi-color bounding boxes showing exact character clusters (`C#1, C#2, ...`).
  - Dedicated diagnostic drawer exposing raw cluster dimensions, tensor shape `(1, 64, 8)`, Head 1 character identity + top-3 confidence rankings, Head 2 reversal score ($p_{\text{rev}}$), and resolved output glyph.
  - Clear canvas lifecycle synchronization (wiping bounding boxes, diagnostic drawer, and cached clusters).
- [x] **Dual-Track Hybrid Resolver Standard:**
  - Google Digital Ink provides global lexical context, while the In-House ONNX Head 2 acts as the clinical reversal arbitrator.
  - If Head 2 flags a reversal ($p_{\text{rev}} \ge 0.50$), the resolver overrides the lexical engine with canonical mirror glyphs (`ᗡ`, `ꓭ`, `Ǝ`, `И`).
- [x] **Clinical Grounding & 2D Task Dissociation Standard (Oct 19 Literature Synthesis):**
  - Established evidence-based screening scope: Motor Dysgraphia, Spatial Dysgraphia, and Dyslexic Dysgraphia (Dysorthographia) via **Visual Copying vs. Auditory Dictation** dissociation (Chung et al., 2020; Andrade et al., 2015; Daniel et al., 2025).
  - Replaced heavy open-ended NLP with **Closed-Lexicon 2D Task Design** (Murnani et al., 2025; Fallah et al., 2025; Patil et al., 2024).
- [ ] **Step 2A (Immediate Priority): Multi-Character Bounding-Box Segmentation & Writing Speed Robustness:**
  - *Why It Must Come First:* Even in Task Levels 2 and 3 (Words, Pseudowords, and Sentences), children may flip individual characters within a multi-letter word. Accurate per-character bounding-box segmentation is required so Track 2 (`dual_head_reversal.onnx`) can inspect every letter inside a word alongside whole-word orthographic checks.
  - *The Challenge:* Character bounding boxes and ligature valley detection are currently sensitive to writing speed fluctuations (fast continuous strokes vs. hesitant/slow or scattered pediatric print).
  - *Engineering Action:* Refine `segmentIntoCharacterClusters()` in `data_collector/js/screening.js` using velocity-invariant spatial geometry—calibrating arc-length resampling ($ds$), horizontal overlap/gap thresholds, Curvature Maxima ($\kappa_{\text{extrema}}$), and Vertical Projection Profiling (histogram troughs) so letters separate cleanly regardless of writing speed.
- [ ] **Step 2B (Next): Align Screening Flow with 2D Task Protocol:**
  - **Level 1 (Isolated Letters & Shapes - Copying/Recall):** Single-letter visuomotor automaticity and chiral reversal check.
  - **Level 2 (Real Words, Pseudowords, & Migration Anagrams - Visual Copying vs. Audio Dictation):** Dissociate Motor/Spatial Dysgraphia from Dyslexic Dysgraphia using Bi-LSTM kinematics, pre-writing latency, intra-word in-air pauses, Damerau-Levenshtein edit distance (omissions, substitutions, letter migrations like *smile* $\to$ *slime*), AND per-character ONNX reversal detection on segmented letters.
  - **Level 3 (Fixed Short Sentences - Copying/Dictation):** Sustained graphomotor endurance, word/character spacing variance, baseline drift, Word Error Rate (WER), and embedded character reversal detection.

---

### Phase 3: Empirical Benchmarking & Statistical Validation (Upcoming)
- [ ] **Model Comparison Benchmark:**
  - Execute strict hold-out train and validation evaluation comparing V0 (CNN), V1 (CNN+XAI), and V2 (Bi-LSTM).
  - Compute balanced accuracy, sensitivity (recall), specificity, F1-score, and AUC-ROC on the unseen hold-out validation set.
- [ ] **Statistical Significance Testing:**
  - Perform Mann-Whitney U tests or two-sample t-tests on kinematic features between typical and atypical samples.
  - Quantify significance of NIV (Number of Inversions of Velocity), normalized jerk, and initiation latency differences.
- [ ] **Explainable AI Validation:**
  - Verify that TimeDistributed attention / activation maps accurately flag micro-hesitation segments on canvas coordinates.

---

### Phase 4: IEEE Conference Manuscript Finalization (Submission Deadline: October 26, 2026)
- [ ] **Manuscript Synchronization:**
  - Synchronize empirical results, tables, and confusion matrices into `le-conference-dyslexia/conference_paper.md`.
  - Format according to strict IEEE 2-column conference standards.
  - Verify minimum 20 peer-reviewed citations drawn from `academic_resources/`.
- [ ] **Submission Artifact Compilation:**
  - Compile final publication-ready Microsoft Word document (`le-conference-dyslexia/elkinematics-conference.docx`) via `scripts/build_conference_docx.py`.
  - Verify high-resolution figure exports (system architecture, dual-stream pipeline, kinematic heatmaps).

---

### Phase 5: Extended Journal Expansion (JISEBI 2026)
- [ ] **Expanded Clinical Dataset:** Scale clinical data collection to 300+ multi-round handwriting trials.
- [ ] **IMRaD Manuscript Expansion:** Expand conference findings into a full 3,000–6,000 word journal article adhering to JISEBI author guidelines.
- [ ] **Edge Deployment:** Deploy quantized model (`models/elkinematicliteV2.tflite`) for real-time, low-resource tablet deployment without cloud dependencies.
