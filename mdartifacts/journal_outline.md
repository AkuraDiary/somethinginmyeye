# JOURNAL OUTLINE
**Title:** Prototyping an Early Dysgraphia Screening System Using Explainable AI Approach Through Handwriting Kinematics

## 1. ABSTRACT
* **Background:** Keterlambatan deteksi Disgrafia karena kurangnya alat skrining awal yang objektif.
* **Problem:** Model AI medis saat ini terlalu berat (Transformer/Vision) dan bersifat *Black Box* sehingga tidak dipercaya oleh guru/klinisi.
* **Methodology:** Menggunakan metode *Rapid Application Development* (RAD) untuk membangun purwarupa aplikasi web ringan (*Lightweight*).
* **Proposed Solution:** Membangun *Bidirectional LSTM* berbasis murni Kinematika (kecepatan, tekanan, jeda) yang dilengkapi *TimeDistributed layer* untuk menghasilkan *Explainable AI* (Visual Heatmap).
* **Results:** Mencapai akurasi validasi 95.95% dan Recall 92.94% pada 302 sampel, mengungguli arsitektur CNN konvensional yang terbukti terjebak dalam *Shortcut Learning*.

## 2. INTRODUCTION (Pendahuluan)
* Latar belakang pentingnya deteksi dini hambatan menulis (Disgrafia).
* Masalah pada proses asesmen manual (subjektif dan memakan waktu).
* Tantangan AI konvensional: Terlalu berat (*computationally expensive*) dan tidak bisa menjelaskan keputusannya (*Black Box*).
* **Tujuan Penelitian:** Membangun purwarupa sistem berbasis web (*end-to-end*) yang ringan dan transparan menggunakan pendekatan RAD.

## 3. RELATED WORKS (Penelitian Terkait / SOTA)
* Referensi paper terkait *Kinematic parameters* (Suarez-Coalla, Sindhu).
* Perbandingan langsung dengan paper Yuri Pamungkas (ITS). Jelaskan posisi penelitian ini: **Lightweight vs Heavy Transformer**, dan **Pure Kinematics vs Computer Vision**.

## 4. METHODOLOGY (Metodologi Penelitian)
* **4.1. Rapid Application Development (RAD) Lifecycle:** Penjelasan iterasi purwarupa.
* **4.2. Data Collection (Web Canvas System):** Bagaimana aplikasi mengumpulkan data sumbu X, Y, Waktu, dan Tekanan (302 sampel).
* **4.3. Feature Engineering:** Ekstraksi "Golden 8 Features" dan perlunya penyamaan skala (*Z-Score Normalization*).
* **4.4. System Architecture:** Desain *Universal Pipeline* dan *Dual-Input Model* (Kinematics Sequence + Latency).
* **4.5. Explainable AI (XAI) Integration:** Mekanisme *TimeDistributed* untuk menerjemahkan matriks probabilitas kembali menjadi titik *Heatmap* visual di antarmuka HTML.

## 5. RESULTS & DISCUSSION (Hasil dan Pembahasan)
* **5.1. Model Performance (The Leaderboard):** Tabel perbandingan evaluasi V0 (Baseline), V1 (CNN), dan V2 (LSTM). Tampilkan angka 95.95%.
* **5.2. Analysis of Shortcut Learning (The Padding Trap):** Bukti kritis mengapa V0 dibuang meski mendapat 99%, karena fenomena *Data Leakage* akibat *Flattening* dan *Zero-Padding*.
* **5.3. Prototype UI Evaluation:** Tangkapan layar (*Screenshot*) aplikasi `screening.html`. Menunjukkan antarmuka pengguna yang responsif dan bagaimana *Heatmap* bekerja secara *real-time*.

## 6. CONCLUSION & FUTURE WORK
* **Conclusion:** Prototyping berhasil membuktikan bahwa sistem skrining Disgrafia yang ringan (*lightweight*) dan *explainable* dapat dibangun menggunakan murni parameter kinematik.
* **Future Work (Roadmap):** Rencana untuk mengembangkan ke arsitektur *Multi-Stream* (menambahkan NLP) untuk secara definitif membedakan Disleksia (Kesalahan Ejaan) dari Disgrafia (Eksekusi Motorik).
