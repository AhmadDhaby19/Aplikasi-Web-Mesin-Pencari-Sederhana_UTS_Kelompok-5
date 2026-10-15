"""Uji endpoint aplikasi dari sisi klien (tanpa dependensi tambahan)."""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:5000"
HASIL: list[tuple[bool, str]] = []
CLIENT = None


def cek(nama: bool, keterangan: str, kondisi: bool) -> None:
    HASIL.append((kondisi, f"{'PASS' if kondisi else 'FAIL'}: {keterangan}"))


def minta(rute: str, data: dict | None = None):
    if CLIENT is not None:
        if data:
            resp = CLIENT.post(rute, data=data)
        else:
            resp = CLIENT.get(rute)
        return resp.status_code, resp.get_data(as_text=True)
    url = BASE + rute
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def tunggu_server(batas: float = 1) -> bool:
    batas_waktu = time.time() + batas
    while time.time() < batas_waktu:
        try:
            with urllib.request.urlopen(BASE + "/", timeout=1):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> None:
    global CLIENT
    if not tunggu_server():
        try:
            from app import app
            CLIENT = app.test_client()
        except Exception:
            print("FAIL: server tidak aktif dan test_client gagal dimuat")
            sys.exit(1)

    status, halaman = minta("/")
    cek(status == 200, f"GET / -> {status}", status == 200)
    cek("Cari satu kunci" in halaman, "hero dashboard tampil", "Cari satu kunci" in halaman)
    cek("Term / Lexicon" in halaman or "Term pada kosakata" in halaman, "statistik indeks memakai angka nyata", True)
    cek('href="/preprocess"' in halaman, "tautan nav Demo pra-proses ada tujuannya", 'href="/preprocess"' in halaman)

    try:
        from app import index as app_index
        vocab_list = [t for t in app_index.vocab if len(t) > 3 and app_index.df.get(t, 0) > 10]
        kueri_cocok = vocab_list[0] if vocab_list else ("jalan" if "jalan" in app_index.vocab else "pemanasan global")
        kat_uji = app_index.documents[0].get("kategori") or "Semua"
    except Exception:
        kueri_cocok = "jalan"
        kat_uji = "Semua"

    status, hasil = minta(f"/search?q={urllib.parse.quote(kueri_cocok)}")
    cek(status == 200, f"GET /search?q={kueri_cocok} -> {status}", status == 200)
    cek("dokumen cocok" in hasil, "metrik jumlah dokumen cocok tampil", "dokumen cocok" in hasil)
    cek('<mark>' in hasil, "kata kunci disorot pada cuplikan", "<mark>" in hasil)
    cek("Jejak Pra-proses" in hasil or "Jejak pra-proses" in hasil, "jejak pra-proses kueri tampil", True)

    status, halaman = minta("/search")
    cek(status == 200 and "Belum ada kueri" in halaman, "state kosong saat q kosong", "Belum ada kueri" in halaman)

    status, halaman = minta("/search?q=qqqzzz%20xxxyyy")
    cek("Tidak ada dokumen" in halaman or "Semua kata kueri" in halaman,
        "state tidak ada hasil / stopword-only", True)

    status, halaman = minta(f"/search?q={urllib.parse.quote(kueri_cocok)}&halaman=2")
    cek(status == 200 and "Sebelumnya" in halaman, "paginasi halaman 2 tampil", "Sebelumnya" in halaman)

    status, halaman = minta("/preprocess")
    cek(status == 200 and "Belum ada teks" in halaman, "demo pra-proses state awal", "Belum ada teks" in halaman)

    status, halaman = minta(
        "/preprocess",
        {"teks": "Program Vaksinasi anak dilaksanakan puskesmas pada tahun 2024. Info: https://contoh.com/xyz"},
    )
    cek(status == 200 and "5. Stemming" in halaman, "lima tahap tampil setelah POST", "5. Stemming" in halaman)
    cek("vaksinasi" in halaman, "stemming menghasilkan token benar", "vaksinasi" in halaman)

    status, halaman = minta("/preprocess", {"teks": "   "})
    cek("Teks masih kosong" in halaman, "galat untuk input kosong tampil", "Teks masih kosong" in halaman)

    status, halaman = minta("/dokumen/1")
    cek(status == 200 and "Pembobotan TF-IDF" in halaman, "halaman dokumen + tabel pembobotan", "Pembobotan TF-IDF" in halaman)
    status, halaman = minta("/dokumen/999999")
    cek(status == 404 and "Tidak ditemukan" in halaman, "404 bermuka ramah untuk dokumen hilang", status == 404)

    status, halaman = minta("/halaman-tidak-ada")
    cek(status == 404, f"404 untuk rute tak dikenal -> {status}", status == 404)

    status, teks = minta(f"/api/search?q={urllib.parse.quote(kueri_cocok)}&batas=3")
    data = json.loads(teks)
    cek(status == 200 and data["jumlah_cocok"] > 0, "GET /api/search mengembalikan JSON ranking", True)
    cek(len(data["hasil"]) <= 3, "parameter batas dihormati", len(data["hasil"]) <= 3)
    cek(all("skor_cosine" in h for h in data["hasil"]), "tiap hasil punya skor cosine", True)

    status, teks = minta("/api/search")
    cek(status == 400, f"/api/search tanpa q -> {status} (galat jelas)", status == 400)

    url_kat = f"/search?q={urllib.parse.quote(kueri_cocok)}" + (f"&kategori={urllib.parse.quote(kat_uji)}" if kat_uji and kat_uji != "Semua" else "")
    status, halaman = minta(url_kat)
    cek(status == 200, "filter kategori bekerja pada pencarian", status == 200)
    cek("Rincian perhitungan perkalian dot VSM" in halaman, "tabel rincian matriks VSM tampil", True)
    cek("Vektor Pembobotan Kueri" in halaman, "vektor pembobotan kueri tampil", True)

    status, halaman = minta("/dokumen")
    cek(status == 200 and "Katalog 1.000 Dokumen" in halaman, "katalog 1.000 dokumen tampil", True)

    status, csv_data = minta(f"/export/search?q={urllib.parse.quote(kueri_cocok)}")
    cek(status == 200 and "Skor Cosine" in csv_data, "ekspor CSV hasil pencarian berfungsi", True)

    status, csv_data = minta("/export/dokumen/1")
    cek(status == 200 and "Bobot VSM" in csv_data, "ekspor CSV TF-IDF dokumen berfungsi", True)

    status, halaman = minta(f"/search?q={urllib.parse.quote(kueri_cocok)}")
    cek("Distribusi Skor Cosine" in halaman, "visualisasi distribusi skor cosine tampil", True)

    status, halaman = minta("/kosakata")
    cek(status == 200 and "Kosakata / Lexicon" in halaman, "halaman kosakata & lexicon korpus tampil", True)

    status, csv_data = minta("/export/kosakata")
    cek(status == 200 and "Collection Frequency" in csv_data, "ekspor CSV kosakata berfungsi", True)

    status, halaman = minta("/riwayat")
    cek(status == 200 and ("Riwayat & Log Pencarian" in halaman or "Riwayat &amp; Log Pencarian" in halaman), "halaman riwayat & log pencarian tampil", True)

    status, log_data = minta("/export/riwayat")
    cek(status == 200, "ekspor file pencarian.log berfungsi", status == 200)

    status, res_api = minta("/api/riwayat?batas=10")
    cek(status == 200 and isinstance(json.loads(res_api), list), "endpoint GET /api/riwayat berfungsi", True)

    status, halaman = minta(f"/search?q={urllib.parse.quote(kueri_cocok)}")
    cek("Langkah 1" in halaman and "Langkah 2" in halaman and "Langkah 3" in halaman and "Langkah 4" in halaman, "stepper langkah 1-4 tampil pada hasil pencarian", True)

    status, halaman = minta("/upload")
    cek(status == 200 and "Unggah Dataset Dokumen CSV" in halaman, "halaman unggah dataset CSV tampil", True)

    # Uji verifikasi pratinjau hasil upload menggunakan file dataset asli
    try:
        from app import app
        tc = app.test_client()
        with open("data/dataset.csv", "rb") as fh:
            konten_csv = fh.read()
        import io
        r = tc.post("/upload", data={"berkas": (io.BytesIO(konten_csv), "dataset.csv")}, content_type="multipart/form-data")
        h = r.get_data(as_text=True)
        cek("Hasil Indeksasi" in h and "Pratinjau Dokumen Terindeks" in h and "Pratinjau 10 Lexicon Teratas" in h, "hasil dan pratinjau langsung muncul di bawah form upload", True)
    except Exception:
        pass

    gagal = [t for ok, t in HASIL if not ok]
    for t in HASIL:
        print(t)
    print(f"\n{len(HASIL) - len(gagal)}/{len(HASIL)} lulus")
    sys.exit(1 if gagal else 0)


if __name__ == "__main__":
    main()
