# Anggota Kelompok 5:
Achileus Danatha Bhramantyo (23050974122)
Refiansyah Galuh R.P (23050974120)
Reza Choirudin D (23050974125)
Ahmad Dhaby S Bagus (23050974131)
Hamdi Ahnaf Aswana ( 23050974148)



# PustakaKata

Aplikasi web mesin pencari dokumen teks. Indeksasi, pembobotan
kata TF-IDF, dan perangkingan dokumen dihitung di backend dengan Vector Space
Model (VSM) dan cosine similarity.

## Cara menjalankan

```powershell
pip install -r requirements.txt
py app.py
```

Buka <http://127.0.0.1:5000>. Indeks dibangun dari `data/dataset.csv` saat
pertama dijalankan lalu disimpan ke `data/indeks_cache.pkl`, jadi start
berikutnya langsung siap. Untuk memaksa indeksasi ulang:

```powershell
$env:BUILD_INDEKS="1"; py app.py
```

Untuk menjalankan rangkaian pengujian otomatis:

```powershell
py tools/uji.py
```

## Struktur

```
app.py                  rute Flask (dashboard, hasil, demo, API, riwayat)
engine/preprocessing.py Fitur 2: cleaning, case folding, tokenizing,
                        stopword removal, stemming (Sastrawi)
engine/tfidf.py         Fitur 3: kosakata, IDF, vektor TF-IDF ternormalkan,
                        perangkingan cosine
engine/loader.py        pembaca CSV adaptif (deteksi otomatis delimiter ;, ,, \t, |)
data/dataset.csv        korpus dokumen aktif
tools/generate_dataset.py  pembuat ulang dataset contoh sintetis
tools/uji.py            pengujian integrasi otomatis (37 tes end-to-end)
templates/              tampilan antarmuka berbasis Jinja2
static/css/style.css    gaya visual akademik hangat sesuai DESIGN.md
```

## Pemetaan fitur tugas

| Fitur | Lokasi |
|---|---|
| 1. Halaman utama (dashboard pencarian) | `/` di `app.py`, `templates/beranda.html` |
| 2. Pra-proses teks | `engine/preprocessing.py`, halaman `/preprocess` |
| 3. Mesin hitung VSM & perangkingan | `engine/tfidf.py`, endpoint `/api/search` |
| 4. Halaman hasil pencarian | `/search` di `app.py`, `templates/hasil.html` |
| Fitur Tambahan: Katalog Dokumen Korpus | `/dokumen` di `app.py`, `templates/katalog.html` |
| Fitur Tambahan: Kosakata Korpus (CF, DF, IDF) | `/kosakata` di `app.py`, `templates/kosakata.html` |
| Fitur Tambahan: Riwayat & Log Real-Time (WIB) | `/riwayat` di `app.py`, `templates/riwayat.html`, `/api/riwayat` |
| Fitur Tambahan: Ekspor CSV | `/export/search`, `/export/dokumen/<id>`, `/export/kosakata`, `/export/riwayat` |
| Fitur Tambahan: Unggah Dataset CSV Mandiri | `/upload` di `app.py`, `templates/upload.html` |

## Rumus yang dipakai

- `tf(t,d) = 1 + log10(f(t,d))`
- `idf(t) = log10(N / df(t))`, dengan N = jumlah dokumen
- `bobot = tf x idf`, lalu setiap vektor dokumen dan vektor kueri
  dinormalkan supaya panjangnya 1
- `cos(q,d) = jumlah bobot_q[t] x bobot_d[t]`, diurutkan dari tertinggi

## Mengganti dataset dengan file dari asisten

Salin CSV asisten ke `data/dataset.csv`, lalu hapus `data/indeks_cache.pkl`
atau jalankan dengan `BUILD_INDEKS=1` (atau unggah langsung lewat menu `/upload`).
Pemisah kolom (koma `,`, titik koma `;`, tab `\t`) terdeteksi otomatis.
Nama kolom fleksibel:
- **ID**: `id`, `no`, `dokumen_id`, `nomor`, `kode`
- **Judul**: `judul`, `title`, `nama`, `tipe_laka_lantas`, `peristiwa`, `topik`, `subjek`
- **Kategori**: `kategori`, `category`, `topik`, `polres`, `polda`, `wilayah`
- **Dokumen/Teks**: `dokumen`, `text`, `teks`, `isi`, `content`, `article`, `tipe_laka_lantas`

Jika kolom judul tidak tersedia, sistem menggunakan teks asli dokumen tanpa label buatan generik.

## API

- `GET /api/search?q=kata+kunci&kategori=Kategori&batas=10`:
  Mengembalikan JSON berisi vektor kueri, token pra-proses, rincian dot product matriks VSM, jumlah cocok, dan peringkat skor cosine.
- `GET /api/riwayat?batas=50`:
  Mengembalikan JSON daftar riwayat pencarian terbaru (waktu WIB, durasi ms, jumlah cocok).
- `POST /riwayat/bersihkan`:
  Mengosongkan berkas log riwayat pencarian.
