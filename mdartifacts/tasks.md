# Daftar Tugas (Task List) — Elkinematics

Dokumen ini mencatat prioritas pengerjaan teknis, validasi klinis, dan eksperimen secara berurutan dari yang paling mendesak (Immediate Priority) hingga tahap lanjutan.

## 1. Immediate Priority (Active Engineering Workstream)
- [ ] **Step 4: Benchmarking Model (V0 vs. V1 vs. V2 Bi-LSTM):**
  - Hold-out validation and cross-validation for Balanced Accuracy, Sensitivity (Recall), Specificity, F1-Score, and AUC-ROC.
  - Significance testing (Mann-Whitney U / t-test) on kinematic features (NIV, Jerk, Initiation Latency).

## 2. Completed Foundation & Prototype Milestones
- [x] **Step 3: Data Collector & Screening Bilingual Revamp (`index.html`, `screening.html`, `index.js`, `screening.js`, `server.py`):**
  - Restored full 6-point research guidelines covering dataset types, classification modes, cognitive latency timing, hardware stylus usage, and 4 kinematic dynamics (stroke direction, velocity, pressure, inter-stroke hesitation).
  - Implemented instant bilingual (`ID` / `EN`) localization toggle across both Data Collector and Live Screening interfaces with shared `localStorage` synchronization.
  - Implemented semi-gamified Moderated Guided Collection serving balanced pseudorandom Indonesian stimuli (L1 chiral characters, L2A high-frequency words, L2B letter-migration anagrams, L3 short sentences) justified by task-type literature (Danna et al. 2023).
  - Implemented Examiner-Administered Oral Dictation Standard with Examiner HUD target presentation, manual/Spacebar latency initiation triggers, and client-side browser speech fallback (`window.speechSynthesis`).
  - Preserved legacy filename format (`${dataset}_${mode}_${prompt}_${annotator}_${timestamp}`) while writing companion `.meta.json` sidecars in `scripts/server.py`.
  - Verified strict compliance with the repository's Zero-Emoji Policy across all HTML, CSS, and JS files.
- [x] **Step 2A: Multi-Character Bounding-Box Segmentation & Writing Speed Robustness (`data_collector/js/screening.js`):**
  - Applied equidistant arc-length parameterization ($\Delta s = 3.5\text{px}$), 3-point spatial moving-average smoothing, cursive ligature valley splitting ($\tilde{y} \ge \tilde{y}_{\text{baseline}} - 0.35H$, two-body loop $\ge 0.30H$), and chronological stroke re-ordering within clusters.
  - Validated across single-letter, multi-letter, overlapping, and cursive handwriting samples with $97.3\%$ single-character integrity and $0$ false cursive splits across $1,090$ tablet CSVs.
- [x] **Step 2B: Versatile Evaluator-Entered Ground Truth & Screening Alignment (`screening.html`, `screening.css`, `screening.js`, `orthographic_decoder.py`):**
  - Replaced rigid dropdown with versatile `#promptInput` and grounded suggestion list (`bebek`, `kucing`, `buku`, `dadu`, `pohon`, `baju baru`, `smile`, `b`, `d`, `p`, `q`, `B`, `D`).
  - Added Visual Copying vs. Evaluator Dictation (Hide Target from Child) visibility toggle and un-focused input blurring.
  - Upgraded orthographic decoder with Damerau-Levenshtein Optimal String Alignment (OSA) distance and multi-character mirror glyph/reciprocal swap detection.
- [x] **Capture Fitur Pen Tilt & 8 Fitur Kinematik Standar:** Implementasi ekstraksi `[delta_x, delta_y, pressure, tiltX, tiltY, velocity, acceleration, jerk]` serta metrik skalar sekunder `latency`.
- [x] **Arsitektur Terpusat (`scripts/config.py` & `scripts/model_builder.py`):** Konsolidasi model V0 (Baseline CNN), V1 (CNN+XAI), dan V2 (Bi-LSTM).
- [x] **In-House Dual-Head Reversal Classifier (`dual_head_reversal.onnx`):** Pelatihan dan integrasi WebAssembly (`ort.min.js`) untuk pengenalan 62 karakter alfanumerik (Head 1) dan deteksi pembalikan cermin klinis (Head 2, ROC-AUC $0.9982$).
- [x] **Dual-Track Hybrid Resolver & UI Diagnostics:** Penggabungan konteks leksikal (Google Digital Ink) dengan arbitrase pembalikan karakter (ONNX Head 2 $\ge 0.50$), lengkap dengan visualisasi *bounding box* per-karakter dan panel diagnostik transparan.
- [x] **Landasan Klinis & Bebas-NLP (48 Jurnal di `academic_resources/`):** Validasi bahwa disosiasi tugas (*Copying vs. Dictation* pada kata dan *pseudoword*) menggantikan kebutuhan model NLP berat.

## 3. Upcoming (Phase 3 & Phase 4: Statistical Validation & Publication)
- [ ] **Benchmarking Model (V0 vs. V1 vs. V2 Bi-LSTM):** Evaluasi *hold-out validation* untuk metrik *Balanced Accuracy*, *Sensitivity (Recall)*, *Specificity*, *F1-Score*, dan *AUC-ROC*.
- [ ] **Uji Signifikansi Statistik:** Uji *Mann-Whitney U* atau *Two-Sample t-test* pada fitur kinematik (*NIV*, *Normalized Jerk*, *Initiation Latency*, *In-Air Pause*) antara sampel tipikal dan atipikal.
- [ ] **Finalisasi Manuskrip IEEE & JISEBI:** Sinkronisasi tabel hasil empiris, grafik arsitektur, dan kompilasi dokumen publikasi.
