# Diskusi & FAQ: Fitur Kinematik vs Dimensi Spasial (Width, Height, Pressure)

Dokumen ini merangkum diskusi teknis mengenai perbedaan antara fitur trajectory, dimensi bounding box (Width/Height), dan peran tekanan (Pressure) dalam evaluasi disleksia menggunakan data deret waktu (time-series).

---

### Q1: Mengapa `Delta_X` dan `Delta_Y` sempat dilabeli sebagai Width dan Height? Bukankah itu menghitung trajectory?
**A:** Pemahamanmu 100% benar. Melabeli `Delta_X` dan `Delta_Y` sebagai *Stroke Width* dan *Stroke Height* adalah kesalahan terminologi.
* **Fakta Matematis:** `Delta_X` dan `Delta_Y` sebenarnya adalah **Horizontal/Vertical Displacement** (Perpindahan Arah/Trajectory). Rumusnya adalah selisih antar frame: `x_t - x_{t-1}`.
* **Fungsi:** Fitur ini krusial karena memberitahu AI *ke arah mana* pena bergerak pada milidetik tertentu (membentuk lingkaran vs garis lurus). Jadi, datanya tetap sangat dibutuhkan AI, hanya saja sebutannya harus direvisi menjadi Displacement/Trajectory, bukan Width/Height.

### Q2: Lalu bagaimana dengan Stroke Width dan Height yang sebenarnya? Apakah kita bisa mendapatkannya dari data CSV saat ini, atau harus menggunakan Computer Vision (CV) pada gambar?
**A:** Kita bisa **100% mengekstraknya secara matematis dari data koordinat (CSV)** tanpa menggunakan Computer Vision sama sekali. 
Dalam analisis time-series, kita memiliki data `X` dan `Y` di setiap milidetik. Kita hanya perlu mencari titik ekstrem dari koordinat tersebut saat pena menyentuh layar (`touching == 1`).

### Q3: Tapi untuk mendapatkan Width dan Height dari *setiap goresan (individual stroke)* yang terpisah, bukankah Computer Vision lebih akurat dan bisa dipercaya?
**A:** Justru **sebaliknya**. Untuk isolasi goresan individu, data Kinematik (CSV) jauh lebih superior dibandingkan CV.
* **Masalah pada CV (The Overlap Problem):** Pada tulisan sambung (cursive) atau goresan yang menumpuk, CV pada gambar statis (PNG) hanya melihat gumpalan pixel hitam. CV tidak tahu kapan goresan pertama berakhir dan goresan kedua dimulai.
* **Keunggulan Kinematik (Dimensi Waktu):** Data kita memiliki variabel `Time` dan status `touching` (Pen-down/Pen-up). Tidak peduli seberapa banyak goresan menumpuk di pixel yang sama, dataset kita tahu pasti bahwa sebuah *stroke* adalah rentang waktu dari saat `touching` berubah menjadi 1 hingga kembali menjadi 0. Ini membuat segmentasi goresan matematis kita akurat 100%.

### Q4: Apa rumus kalkulasi untuk mendapatkan Stroke Width dan Stroke Height tersebut?
**A:** Rumusnya menggunakan logika **Bounding Box** spasial untuk setiap segmen goresan (di mana pena terus menyentuh layar):
* **Stroke Width:** $X_{Max} - X_{Min}$
* **Stroke Height:** $Y_{Max} - Y_{Min}$

*(Logika di Pandas: Mengelompokkan data berdasarkan event pen-down (`stroke_id`), lalu menjalankan fungsi `x.max() - x.min()` pada setiap grup).*

### Q5: Bagaimana dengan Pressure? Bukankah kita menggunakan Pressure untuk menghitung/mendapatkan Stroke Width dan Height?
**A:** **Sama sekali tidak.** Kita harus memisahkan perhitungan ukuran spasial (Jarak) dengan ketebalan visual (Gaya/Force).
* Jika kita membahas ketebalan visual tinta di layar Apple Pencil, itu memang bergantung pada Pressure.
* Namun, dalam Kinematik, "Stroke Width" berarti **seberapa jauh tangan bergerak secara spasial**.
* **Analogi:** Jika tangan bergerak sejauh 100 pixel ke kanan, maka Width = 100. Jika anak menekan layar dengan sangat keras (High Pressure) saat melakukan itu, tangan tersebut *tetap hanya bergerak sejauh 100 pixel*. 
* Jika kita memasukkan unsur Pressure ke dalam rumus spasial (misal: Jarak * Pressure), hasil matematisnya akan membohongi AI mengenai jarak fisik sebenarnya yang ditempuh oleh tangan.

### Q6: Jadi apakah kita tidak menggunakan Pressure sama sekali?
**A:** **Kita tetap menggunakannya secara terpisah!** `Pressure` tetap menjadi salah satu dari "Golden 8 Features" utama yang masuk ke AI (Bi-LSTM). 
* **Ukuran Spasial (Width/Height)** memberitahu AI tentang Jarak dan Inkonsistensi Proporsi Huruf.
* **Pressure** memberitahu AI tentang *Force* (Ketegangan Otot, Stres Kognitif, dan Keraguan/Hesitation).
AI akan menerima kedua stream data ini secara terpisah dan murni, lalu dengan cerdas mencari korelasi di antara keduanya (misal: "Goresan ini sangat lebar, tapi digambar dengan sangat lambat dan pressure yang melonjak drastis = Anomali Disleksia").
