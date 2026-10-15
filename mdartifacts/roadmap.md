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
- [x] **Academic Archive Consolidation:** Consolidate all 38 reference PDFs into `academic_resources/`.

---

### Phase 2: Dual-Stream SLD Screening Prototype (Current Workstream)
- [x] **Differential Framework Architecture:**
  - Stream 1: Bi-LSTM kinematic inference evaluating motor dysgraphia instability.
  - Stream 2: Orthographic trajectory decoder evaluating spelling distance and mirror reversals.
  - Stream 3: Initiation latency tracking working memory hesitation (> 1500 ms).
- [x] **Tablet Canvas & Ergonomics:**
  - Lock root viewport to eliminate pull-to-refresh reloads (`html, body { position: fixed; overflow: hidden; }`).
  - Implement tactile on-screen vertical touch scrollbar for seamless navigation on touchscreens.
  - Replace academic and engineering jargon with clean, neutral labels.
- [x] **Decoupled Workflow:**
  - Isolate stroke-to-text transcription from backend model inference (`Transcribe Text` vs `Run Assessment`).
- [ ] **Universal Reversal Detection Refinement:**
  - Resolve reciprocal pair ambiguity: ensure valid standalone letters (`b`, `d`, `p`, `q`) in free-flow writing are not falsely flagged as mirror reversals without a target prompt.
  - Calibrate horizontal reflection test to prevent `M` vs `N` confusion caused by multi-stroke trajectories.
  - Solidify non-character chiral mirror detection (`N` -> `И`, `S` -> `Ƨ`, `E` -> `Ǝ`, `3` -> `Ɛ`).

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
