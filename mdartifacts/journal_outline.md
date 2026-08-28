# JOURNAL OUTLINE (JISEBI 2024 Compliant)
**Title:** Prototyping an Early Dysgraphia Screening System Using Explainable AI Approach Through Handwriting Kinematics

> [!IMPORTANT] 
> **JISEBI 2024 Golden Rules:**
> - **Format:** IMRaD (Introduction, Methods, Results, Discussion, Conclusion).
> - **Word Count:** 3000 - 6000 words.
> - **Language:** Grammatically correct American English.
> - **References:** Minimum 20 references using IEEE style (via Mendeley).

## 1. ABSTRACT
*(Must be 150-300 words, structured exactly with these prefixes)*
* **Background:** Keterlambatan deteksi Disgrafia karena kurangnya alat skrining awal yang objektif.
* **Objective:** Membangun purwarupa sistem berbasis web yang ringan (*lightweight*) dan transparan (*explainable*).
* **Methods:** Rapid Application Development (RAD) untuk membangun Bidirectional LSTM berbasis Kinematika (kecepatan, tekanan, jeda) dengan *TimeDistributed layer* sebagai jembatan *Explainable AI*.
* **Results:** Akurasi validasi 95.95% pada 302 sampel, mengatasi *Shortcut Learning* (Data Leakage) yang ditemukan pada arsitektur konvensional.
* **Conclusion:** Kinematika murni (tanpa visi komputer) dapat digunakan untuk skrining awal yang *lightweight* dan sangat akurat jika dipadukan dengan desain arsitektur yang tepat.

## 2. INTRODUCTION
> [!WARNING]
> **JISEBI Rule:** Must cite at least **6 recent papers** closely related to the title here to prove the Research Gap.
* Latar belakang pentingnya deteksi dini hambatan menulis (Disgrafia).
* Masalah pada proses asesmen manual (subjektif dan memakan waktu).
* **Research Gap (The 6 Papers):** Kutip paper seperti Yuri Pamungkas dll. Tunjukkan kelemahan mereka (Terlalu berat/computationally expensive, dan AI yang bersifat Black Box).
* **Tujuan/Kontribusi:** Membangun purwarupa web end-to-end (RAD) yang menutupi *gap* tersebut.

## 3. LITERATURE REVIEW (Optional but Recommended)
* Referensi paper terkait *Kinematic parameters* (Suarez-Coalla, Sindhu).
* Teori *Cognitive Load* dan Hubungan Jeda Motorik (Latency & Jerk) dengan kesulitan memori kerja (*working memory*).

## 4. METHODS
> [!NOTE]
> **JISEBI Rule:** Procedure must be written chronologically. Do not introduce interpretation/opinion here.
* **4.1. Rapid Application Development (RAD):** Iterasi purwarupa V0 (Baseline) -> V1 (CNN) -> V2 (LSTM).
* **4.2. Data Collection & Preprocessing:** Web Canvas System (302 sampel). Z-Score Normalization untuk mencegah *Dead Neurons*.
* **4.3. Feature Engineering:** Ekstraksi "Golden 8 Features".
* **4.4. System Architecture:** Dual-Input Bidirectional LSTM model.
* **4.5. Explainable AI Integration:** Mekanisme *TimeDistributed* menjadi UI *Heatmap* visual.

## 5. RESULTS
> [!NOTE]
> **JISEBI Rule:** Pure, unbiased results presented first without interpretation.
* **5.1. Learning Curves:** Grafik *Train vs Validation (Loss & Accuracy)* untuk membuktikan model tidak mengalami *overfitting* selama proses iterasi *training*.
* **5.2. Confusion Matrix:** Metrik performa evaluasi klinis (TP, TN, FP, FN) pada skenario klasifikasi biner untuk memastikan minimnya salah diagnosa (*False Negatives*).
* **5.3. ROC Curve & AUC:** Bukti kuantitatif yang mengukur kemampuan diskriminatif model dalam memisahkan pola tulisan normal dan disgrafia di berbagai ambang batas (*threshold*).

## 6. DISCUSSION
> [!NOTE]
> **JISEBI Rule:** Interpret the results. Compare with other studies. Acknowledge limitations.
* **6.1. Qualitative XAI Results (Visual Evaluation):** Interpretasi visual dari antarmuka purwarupa (`screening.html`). Memberikan bukti perbedaan visual *Heatmap* pada tulisan normal (bersih) dibandingkan dengan tulisan disgrafia (titik merah).
* **6.2. Analysis of Shortcut Learning (The Padding Trap):** Interpretasi kritis mengapa V0 dibuang meski mendapat akurasi 99%. Penjelasan matematis tentang *Data Leakage* akibat efek *Zero-Padding*.
* **6.3. Lightweight vs Heavy:** Bandingkan efisiensi model sistem kita dibandingkan model *Computer Vision/Transformer* dari penelitian sebelumnya.
* **6.4. Limitations (Threats to Validity):** Sistem saat ini baru mendeteksi hambatan motorik (Disgrafia), belum memvalidasi semantik kebenaran ejaan (Disleksia murni).

## 7. CONCLUSION
* Ringkasan eksplisit menjawab pertanyaan penelitian (berhasil membuat purwarupa).
* Rekomendasi/Future Work (Membangun Multi-stream NLP architecture di masa depan).

## 8. MANDATORY JISEBI STATEMENTS (Must be filled at the end of the manuscript)
* **Author Contributions:** (Use CRediT taxonomy: Conceptualization, Methodology, Software, etc.)
* **Funding:** (State any grants or "This research received no specific grant...").
* **Conflicts of Interest:** (e.g., "The authors declare no conflict of interest.")
* **Data Availability:** (Explanation of dataset accessibility or privacy restriction).
* **Informed Consent:** (e.g., "Informed consent was obtained from all subjects...").
