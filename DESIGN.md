# DESIGN.md: Mesin Pencari Dokumen VSM + TF-IDF

Arah visual yang dipilih pemilik proyek: **akademik hangat, terang**. Nuansa katalog
perpustakaan / jurnal ilmiah, bukan startup teknologi.

## Identitas

Produk: aplikasi web mesin pencari sederhana untuk tugas praktikum, mengindeks 1000
dokumen, memeringkat dengan Vector Space Model + TF-IDF. Nama tampilan: **PustakaKata**
(tekstual, bukan logo gambar). Karakternya: tenang, teliti, seperti kartu katalog dan
halaman jurnal yang dibaca lama-lama tanpa lelah.

## Dials

`ENERGY 1 / RHYTHM 2 / MOTION 1`

- ENERGY 1: sapaan lewat tipografi dan ruang kosong, bukan warna berteriak.
- RHYTHM 2: komposisi tiap bagian berbeda-beda (strip statistik, rantai pipeline,
  daftar peringkat), bukan grid kartu identik berulang.
- MOTION 1: hanya hover/focus state dan transisi kecil; tidak ada animasi berulang.

## Palet (maks 2-3 warna inti + 1 aksen)

| Peran | Nilai | Alasan |
|---|---|---|
| Kertas (latar) | `#F4EDE1` | kertas hangat, dasar identitas "cetak" |
| Kartu/permukaan | `#FBF7EF` | permukaan sedikit lebih terang dari kertas |
| Tinta (teks) | `#241D17` | cokelat sangat tua, kontras tinggi di atas kertas |
| Garis | `#D9CEBC` | pemisah netral, tidak menghitam |
| Aksen bata | `#A6402A` | satu aksen: tombol Cari, tautan, bar skor, focus ring |

Netral (putih `#FFFFFF`, abu-abu) tidak dihitung sebagai warna inti. Tidak ada gradien,
glow, glassmorphism, atau pola latar.

## Tema

Tetap **terang** tanpa toggle: identitas halaman kertas tidak cocok dengan mode gelap,
dan arah yang dipilih pemilik memang "terang". Alasan ini dicatat di sini sebagai
keputusan sadar (R-21), bukan kelalaian.

## Tipografi

- Judul: `Georgia, 'Times New Roman', serif`: nuansa jurnal cetak, tersedia offline
  di Windows tanpa unduh font.
- Teks isi: `system-ui, 'Segoe UI', sans-serif`: keterbacaan layar.
- Angka & bobot: `'Consolas', monospace`: angka tabular agar deret TF-IDF sejajar.
- Tidak ada heading monospace raksasa, tidak ada label uppercase ber-tracking lebar.

## Struktur halaman (RHYTHM 2)

1. **Beranda**: satu titik fokus (kotak pencarian) → strip statistik indeks (angka
   nyata dari index) → rantai 5 tahap pra-proses + rumus VSM/TF-IDF → tautan ke demo.
2. **Hasil pencarian**: bar pencarian ringkas → jejak pra-proses kueri → daftar
   peringkat dengan bar skor cosine → status kosong / tidak ada hasil.
3. **Demo pra-proses**: satu kolom textarea + blok tiap tahap beserta jumlah token.
4. **Detail dokumen**: teks penuh + tabel pembobotan 15 term teratas (angka nyata).

## Ikon & aset

Tanpa pustaka ikon dan tanpa gambar dekoratif. Penanda visual hanya yang membawa
informasi: nomor peringkat, bar skor, penanda `<mark>` pada kata kunci.

## Motion

Hover/focus saja. Satu transisi fungsional: tombol submit berubah menjadi
"Mencari..." / "Memproses..." selama request berjalan (loading state nyata).
