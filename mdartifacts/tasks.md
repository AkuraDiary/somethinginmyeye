# Daftar Tugas (Task List) — Elkinematics

Dokumen ini mencatat prioritas pengerjaan teknis, validasi klinis, dan eksperimen secara berurutan dari yang paling mendesak (Immediate Priority) hingga tahap lanjutan.

## 1. Immediate Priority (Active Engineering Workstream)
- [ ] **Step 2A: Multi-Character Bounding-Box Segmentation & Writing Speed Robustness (`data_collector/js/screening.js`):**
  - Kalibrasi `segmentIntoCharacterClusters()` agar pemisahan huruf (bounding box) tidak terpengaruh fluktuasi kecepatan menulis (cepat/menyambung vs lambat/ragu-ragu).
  - Uji dan terapkan parameterisasi panjang busur (*arc-length resampling* $ds$), *Curvature Maxima* ($\kappa_{\text{extrema}}$), dan *Vertical Projection Profiling* (histogram troughs).
  - Pastikan setiap huruf di dalam kata/pseudoword/kalimat dapat dipisahkan secara akurat sehingga model `dual_head_reversal.onnx` (Track 2) tetap dapat mendeteksi huruf terbalik (*flipped/reversed character*) di tengah kata pada Task Level 2 dan Level 3.
- [ ] **Step 2B: Penyelarasan Alur Screening dengan Protokol 2D Task Design (`screening.html` & `screening.js`):**
  - **Task Level 1 (Isolated Letters & Shapes - Copying/Recall):** Uji otomatisitas visuomotor dan deteksi huruf terbalik (`b/d`, `p/q`, `B/D`, `E`, `S`, `N`).
  - **Task Level 2 (Real Words, Pseudowords, & Migration Words - Visual Copying vs. Audio Dictation):** Disosiasi antara *Motor/Spatial Dysgraphia* dan *Dyslexic Dysgraphia (Dysorthographia)* menggunakan fitur kinematik Bi-LSTM, *Initial Latency*, *In-Air Pauses*, evaluasi ejaan/migrasi huruf (*Damerau-Levenshtein edit distance*), serta deteksi huruf terbalik per-segmen (ONNX Track 2).
  - **Task Level 3 (Fixed Short Sentences - Copying/Dictation):** Evaluasi ketahanan grafomotorik, konsistensi jarak antar-kata/huruf, kemiringan *baseline*, *Word Error Rate (WER)*, serta deteksi huruf terbalik di dalam kalimat.

## 2. Completed Foundation & Prototype Milestones
- [x] **Capture Fitur Pen Tilt & 8 Fitur Kinematik Standar:** Implementasi ekstraksi `[delta_x, delta_y, pressure, tiltX, tiltY, velocity, acceleration, jerk]` serta metrik skalar sekunder `latency`.
- [x] **Arsitektur Terpusat (`scripts/config.py` & `scripts/model_builder.py`):** Konsolidasi model V0 (Baseline CNN), V1 (CNN+XAI), dan V2 (Bi-LSTM).
- [x] **In-House Dual-Head Reversal Classifier (`dual_head_reversal.onnx`):** Pelatihan dan integrasi WebAssembly (`ort.min.js`) untuk pengenalan 62 karakter alfanumerik (Head 1) dan deteksi pembalikan cermin klinis (Head 2, ROC-AUC $0.9982$).
- [x] **Dual-Track Hybrid Resolver & UI Diagnostics:** Penggabungan konteks leksikal (Google Digital Ink) dengan arbitrase pembalikan karakter (ONNX Head 2 $\ge 0.50$), lengkap dengan visualisasi *bounding box* per-karakter dan panel diagnostik transparan.
- [x] **Landasan Klinis & Bebas-NLP (48 Jurnal di `academic_resources/`):** Validasi bahwa disosiasi tugas (*Copying vs. Dictation* pada kata dan *pseudoword*) menggantikan kebutuhan model NLP berat.

## 3. Upcoming (Phase 3 & Phase 4: Statistical Validation & Publication)
- [ ] **Benchmarking Model (V0 vs. V1 vs. V2 Bi-LSTM):** Evaluasi *hold-out validation* untuk metrik *Balanced Accuracy*, *Sensitivity (Recall)*, *Specificity*, *F1-Score*, dan *AUC-ROC*.
- [ ] **Uji Signifikansi Statistik:** Uji *Mann-Whitney U* atau *Two-Sample t-test* pada fitur kinematik (*NIV*, *Normalized Jerk*, *Initiation Latency*, *In-Air Pause*) antara sampel tipikal dan atipikal.
- [ ] **Finalisasi Manuskrip IEEE & JISEBI:** Sinkronisasi tabel hasil empiris, grafik arsitektur, dan kompilasi dokumen publikasi.
