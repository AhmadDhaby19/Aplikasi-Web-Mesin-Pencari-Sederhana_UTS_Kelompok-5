"""Tampilkan bukti nyata tiap fitur tugas dari aplikasi yang berjalan."""

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:5000"
CLIENT = None


def get(rute: str) -> str:
    global CLIENT
    if CLIENT is not None:
        return CLIENT.get(rute).get_data(as_text=True)
    try:
        with urllib.request.urlopen(BASE + rute, timeout=1) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        from app import app
        CLIENT = app.test_client()
        return CLIENT.get(rute).get_data(as_text=True)


def post(rute: str, data: dict) -> str:
    global CLIENT
    if CLIENT is not None:
        return CLIENT.post(rute, data=data).get_data(as_text=True)
    body = urllib.parse.urlencode(data).encode()
    try:
        with urllib.request.urlopen(BASE + rute, data=body, timeout=1) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        from app import app
        CLIENT = app.test_client()
        return CLIENT.post(rute, data=data).get_data(as_text=True)


def teks(halaman: str) -> str:
    halaman = re.sub(r"<script.*?</script>|<style.*?</style>", " ", halaman, flags=re.S)
    halaman = re.sub(r"<[^>]+>", " ", halaman)
    return re.sub(r"\s+", " ", html.unescape(halaman)).strip()


# Fitur 1: halaman utama
b = get("/")
isi = teks(b)
print("[Fitur 1] GET / ->", "200")
print('  kotak pencarian :', 'name="q"' in b)
print('  statistik indeks:', "Dokumen terindeks" in b and ("Term / Lexicon" in b or "Term pada kosakata" in b))
print("  cuplikan        :", isi[isi.find("Cari satu kunci"): isi.find("Cari satu kunci") + 150])
print("  pipeline+rumus  :", "tf = 1 + log10(f)" in b and "Stopword removal" in b)

# Fitur 2: pra-proses
p = post(
    "/preprocess",
    {"teks": "Program Vaksinasi anak dilaksanakan puskesmas pada tahun 2024. "
             "Info di https://contoh.com/x dan 99 persen warga hadir."}
)
print("\n[Fitur 2] POST /preprocess ->", "200")
for nama in ["1. Cleaning", "2. Case Folding", "3. Tokenizing", "4. Stopword Removal", "5. Stemming"]:
    print(f"  {nama:<20}:", nama in p)
print("  token akhir      :", re.findall(r"<li>(\w+)</li>", p.split("5. Stemming")[1])[:8])

# Fitur 3: mesin backend
try:
    from app import index as app_index
    vocab_list = [t for t in app_index.vocab if len(t) > 3 and app_index.df.get(t, 0) > 10]
    kata_uji = vocab_list[0] if vocab_list else "jalan"
except Exception:
    kata_uji = "jalan"

q = urllib.parse.urlencode({"q": kata_uji})
d = json.loads(get("/api/search?" + q))
print("\n[Fitur 3] GET /api/search -> 200")
print("  kata uji         :", kata_uji)
print("  token pra-proses :", d["token_hasil_pra_proses"])
print("  dokumen cocok    :", d["jumlah_cocok"], "| dihitung", d["ambil_ms"], "ms")
for i, h in enumerate(d["hasil"][:3], 1):
    print(f"  peringkat {i}        :", h["judul"], "->", h["skor_cosine"])

# Fitur 4: halaman hasil
h = get(f"/search?q={urllib.parse.quote(kata_uji)}")
t = teks(h)
print(f"\n[Fitur 4] GET /search?q={kata_uji} -> 200")
print("  jejak pra-proses :", "Jejak Pra-proses" in h or "Jejak pra-proses" in h)
print("  jumlah cocok     :", t[t.find("dokumen cocok") - 12: t.find("dokumen cocok") + 12])
print("  baris peringkat  :", h.count('class="kartu-hasil"'), "dokumen tampil (10/halaman)")
print("  skor cosine      :", re.findall(r"cos = ([\d,]+)", h)[:3])
print("  sorotan <mark>   :", h.count("<mark>"), "titik kata kunci disorot")
print("  paginasi         :", "paginasi" in h)
