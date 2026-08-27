# 📝 Daftar Tugas (Task List)

File ini digunakan untuk mencatat rencana perbaikan, pembaruan, dan tugas-tugas yang akan dikerjakan selanjutnya pada project ini.

## 🛠️ UI & Pengumpulan Data (index.html)
- [ ] **Restrukturisasi Form Pengumpulan Data:** Modifikasi form input di `index.html` agar lebih terstruktur untuk protokol eksperimen 5 ronde. Tambahkan elemen-elemen berikut:
  - Dropdown **Nama Subject / Anotator** (misal: Seta, Stevan, dsb)
  - Dropdown **Huruf yang Ditulis** (A - Z)
  - Dropdown **Ronde** (1 - 5)
  - *Goal:* Agar format penamaan file otomatis tersimpan rapi menjadi `[Mode]_[Nama]_[Huruf]_Ronde[X]_[Timestamp]` untuk mempermudah validasi *User-Independent*.

## 🧠 Dataset & Machine Learning
- [ ] **Pengumpulan Data:** Kumpulkan dataset sesuai dengan protokol (5 ronde A-Z per orang). Pastikan subjek untuk folder `train` berbeda secara fisik dengan subjek di folder `test`.
- [ ] **Validasi Statistik:** Lakukan uji beda (misal: T-Test atau Mann-Whitney U Test) pada fitur kinematics untuk melihat signifikansi perbedaan antara kelas Normal dan Dyslexia (Tidak menggunakan Cohen's Kappa).

---
*Tambahkan tugas baru di atas jika ada rencana lain.*
