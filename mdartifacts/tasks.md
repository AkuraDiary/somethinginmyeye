# 📝 Daftar Tugas (Task List)

File ini digunakan untuk mencatat rencana perbaikan, pembaruan, dan tugas-tugas yang akan dikerjakan secara berurutan dari yang paling mendesak (Prioritas Tinggi) hingga masa depan (Prioritas Rendah).

## Always Running (Immediate / Actionable)
- [ ] **Pengumpulan Data (Data Collection):** Kumpulkan dataset sesuai dengan protokol 5 ronde per orang menggunakan web app yang sudah live. Target: 200 sampel (100 Normal, 100 Dyslexic-Acted).

## Prioritas Tinggi (Immediate / Actionable)
- [ ] **Capture Fitur Pen Tilt (UI):** Modifikasi event listener `pointermove` di `index.html` untuk menangkap `event.tiltX` dan `event.tiltY` lalu menyimpannya ke dalam array data yang dikirim ke server (sebagai indikator *Pen Grip*).
- [ ] **Ekspansi Fitur Preprocessing (Python):** Update file `preprocess.py` (atau script pemrosesan) untuk menghitung 5 fitur baru menggunakan Pandas: `Delta_X`, `Delta_Y`, `Acceleration`, dan `Jerk`. Ubah `FEATURES = 3` menjadi `FEATURES = 8` di `config.py`.
- [X] **Perekaman Metrik "Latency":** Tambahkan tombol "Start" di UI. Hitung waktu (delta) antara klik "Start" dengan sentuhan pen pertama (`pointerdown`). Kirim angka ini ke Flask sebagai fitur Latency.
- [ ] **Restrukturisasi Form Pengumpulan Data:** Modifikasi form input dengan tambahan input nama anotator dan klasifikasi input data (test / validation) di `index.html` agar lebih terstruktur sehingga data masuk ke setiap folder anotator (orang yang input data) sesuai dengan klasifikasi data yang dipilih (test & validation).


## Prioritas Menengah (Next ML Upgrades)
- [ ] **Upgrade ke Bidirectional LSTM:** Setelah 200 data terkumpul, ganti layer `Conv1D` di Jupyter Notebook dengan layer `Bidirectional(LSTM)` agar AI memiliki "ingatan" jangka panjang terhadap ritme menulis user.
- [ ] **Implementasi Time-Distributed Heatmap:** Pastikan output layer menggunakan `TimeDistributed(Dense(1))` agar AI memberikan probabilitas error per milidetik.
- [ ] **Validasi Statistik:** Lakukan uji beda (misal: T-Test atau Mann-Whitney U Test) pada fitur kinematics untuk melihat signifikansi perbedaan antara kelas Normal dan Dyslexia.

## Prioritas Rendah / Masa Depan (Complex / Misc)

- [ ] **Arsitektur Dual-Stream (Two-Headed Network):** Gabungkan model LSTM (membaca ritme/CSV) dengan model 2D-CNN (membaca bentuk spasial/PNG) menjadi satu AI holistik.
- [ ] **OOD Autoencoder (The Bouncer):** Buat sistem filter untuk menolak gambar coret-coretan (scribbles) sebelum masuk ke AI utama.
- [ ] **Semantic Analysis (Hindari Transformer Auto-correct):** Implementasi OCR di masa depan dengan peringatan keras: jangan gunakan Transformer standar yang memiliki fitur auto-correct ejaan.
