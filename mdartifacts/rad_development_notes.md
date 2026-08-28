# Rapid Application Development (RAD) Log & Architecture Evolution

Dokumen ini melacak evolusi arsitektur sistem deteksi Disleksia berbasis AI. Pengembangan dilakukan menggunakan metode **Rapid Application Development (RAD)**, memetakan iterasi konseptual secara langsung ke model fisik yang disimpan selama pengembangan.

---

## Phase 1: `elkinematic` (Baseline Architecture)
**Objective:** Membangun *baseline* untuk mengklasifikasi Disleksia menggunakan data *handwriting* sederhana.

* **Input:** 3 Parameter *Time-series* mentah (`Velocity`, `Duration`, `Pressure`).
* **Model:** Sequential Conv1D.
* **Output:** Binary Probability Score [0.0 = Normal, 1.0 = Dyslexia].

### Lessons Learned & Limitations
1. **Kelemahan Parameter Kecepatan:** Kecepatan (`Velocity`) secara tunggal ternyata terlalu lemah untuk dijadikan variabel deterministik bagi Disleksia. 
2. **Penemuan "Cognitive Pauses":** Studi literatur menunjukkan bahwa individu dengan disleksia mengalami kesulitan kognitif (bukan sekadar motorik) selama menulis. Kesulitan mengingat ejaan memicu munculnya jeda panjang (*pauses*) sebelum pulpen menyentuh layar. Diperlukan parameter baru.

---

## Phase 2: `elkinematicV2` (The XAI Transition & The "Lazy Doctor")
**Objective:** Memecahkan masalah "Black Box" pada AI, mengekstraksi fitur kognitif yang hilang, dan beralih ke struktur memori jangka panjang (LSTM).

* **Input:** 8 "Golden" Time-series Parameters + 1 Parameter Statis (`Latency`).
* **Model:** Keras Functional API (Dual-Input) -> Bidirectional LSTM + `TimeDistributed` Dense.
* **Output:** *TimeDistributed array* untuk *Heatmap Kinematics Analysis*.

### Lessons Learned & Limitations
1. **Explainable AI (XAI):** Transisi ke `TimeDistributed` berhasil secara konsep. Model tidak lagi sekadar menebak hasil akhir, melainkan memetakan probabilitas dari waktu ke waktu, yang memungkinkan pembuatan UI Heatmap diagnostik.
2. **The Ablation Warning:** Memasukkan `Delta_X` dan `Delta_Y` terbukti esensial agar AI memahami ukuran spasial *stroke*, mencegah kegagalan model pada skala tulisan yang berbeda.
3. **Kegagalan Pelatihan (The Dead Neuron):** Secara arsitektur model ini sangat maju, **tetapi gagal saat dilatih**. Memasukkan angka fisika mentah yang masif (seperti *Jerk* = 500, *Latency* = 2500ms) menyebabkan *gradient explosion*. Model ini menjadi "Lazy Doctor" (menebak Disleksia untuk semua sampel, menyebabkan Accuracy 43% tapi Recall 100%).

---

## Phase 3: `elkinematicV3` (Data Scaling & The 95% Breakthrough)
**Objective:** Menyelamatkan arsitektur V2 dengan memperbaiki *Data Pipeline* (Preprocessing).

* **Input & Model:** Sama dengan `elkinematicV2`, namun data melewati tahap pra-pemrosesan matematis yang ketat sebelum masuk ke *Neural Network*.
* **Pipeline Fix:** **Z-Score Normalization (Standardization)**. Semua parameter fisika dinormalisasi ke rentang yang stabil (rata-rata 0, deviasi standar 1). Nilai `Latency` dibagi 1000 untuk mengubah milidetik menjadi angka kecil (detik).

### Lessons Learned & Technical Breakthroughs
1. **The Scaling Fix:** Z-Score Normalization terbukti menyelamatkan model. Dengan menempatkan seluruh fitur pada level matematis yang setara, LSTM akhirnya mampu membaca *pola klinis* alih-alih terdistraksi oleh besaran angka absolut (menyelesaikan masalah "Dead Neuron").
2. **The Sweet Spot:** Model `elkinematicV3` berhasil mencapai *Sweet Spot* klinis: Akurasi ~95% tanpa *overfitting* (gap antara Training Accuracy dan Validation Accuracy sangat tipis, di bawah 1%). Ini adalah model yang saat ini di-deploy di tahap inferensi (`predict.py`).
3. **Dysgraphia vs Dyslexia (Konklusi):** Model ini sukses mendeteksi "bottleneck kognitif" melalui latensi dan jeda (mengeliminasi kebingungan dengan Disgrafia murni). Namun, sistem ini menyadarkan kita bahwa arsitektur kinematik tunggal belum bisa membaca ejaan secara linguistik.

---

## Phase 4: Tri-Stream Architecture (Future Roadmap)
**Objective:** Membangun AI komprehensif (Multi-modal) yang secara definitif membedakan Disleksia (Bahasa) dan Disgrafia (Motorik/Spasial) melalui teks.

* **Concept:** Pendekatan tiga cabang (*Three-Headed Model*):
  1. **Kinematics (LSTM):** Analisis kecepatan/jerk & latensi kognitif (Melanjutkan arsitektur `elkinematicV3`).
  2. **Visuospatial (CNN):** Analisis gambar kanvas final untuk mendeteksi layout spasial yang kacau.
  3. **Semantic (NLP Language Model):** Analisis transkripsi teks untuk mendeteksi kesalahan ejaan/omisi kata. Menghindari jebakan *Smart OCR (Autocorrect)* dengan memanfaatkan *Teacher-Forced Alignment* (Ground Truth dari pengajar).
