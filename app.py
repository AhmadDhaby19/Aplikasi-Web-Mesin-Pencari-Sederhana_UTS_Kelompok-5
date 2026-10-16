"""Aplikasi web mesin pencari sederhana: VSM + TF-IDF.

Jalankan dengan:  py app.py   lalu buka http://127.0.0.1:5000
Set BUILD_INDEKS=1 untuk memaksa indeksasi ulang dari CSV.
"""

import csv
import datetime
import io
import math
import os
import pickle
import time
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request

from engine import SearchIndex, load_documents
from engine import preprocessing
from engine.preprocessing import clean, preprocess as proses_teks

IS_VERCEL = os.environ.get("VERCEL") == "1"
ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("DATASET") or ROOT / "data" / "dataset.csv")
CACHE_INDEKS = ROOT / "data" / "indeks_cache.pkl"
CACHE_STEM = ROOT / "data" / "stem_cache.json"
LOG_PENCARIAN_DEFAULT = ROOT / "data" / "pencarian.log"
LOG_PENCARIAN = Path("/tmp/pencarian.log") if IS_VERCEL else LOG_PENCARIAN_DEFAULT
PER_HALAMAN = 10
PER_HALAMAN_KATALOG = 20
PER_HALAMAN_KOSAKATA = 30

CONTOH_KUERI = [
    "pemanasan global",
    "vaksinasi anak",
    "pupuk organik",
    "kemacetan lalu lintas",
]

app = Flask(__name__)
preprocessing.muat_cache_stem(CACHE_STEM)
WIB = datetime.timezone(datetime.timedelta(hours=7))


def ambil_contoh_kueri(target_index: SearchIndex | None = None) -> list[str]:
    target = target_index or index
    bawaan = [
        "pemanasan global",
        "vaksinasi anak",
        "pupuk organik",
        "kemacetan lalu lintas",
    ]
    cocok = [k for k in bawaan if target.search(k)["total"] > 0]
    if len(cocok) >= 3:
        return cocok
    frasa_kandidat = [
        "pejalan kaki",
        "belok kanan",
        "ruas jalan",
        "tabrakan depan",
        "lalu lintas",
        "simpang jalan",
    ]
    hasil = list(cocok)
    for f in frasa_kandidat:
        if f not in hasil and target.search(f)["total"] > 0:
            hasil.append(f)
        if len(hasil) >= 4:
            break
    if len(hasil) < 4:
        for t, _ in target.df.most_common(20):
            if len(t) >= 4 and t not in hasil:
                hasil.append(t)
            if len(hasil) >= 4:
                break
    return hasil[:4] if hasil else bawaan


def catat_log_pencarian(kueri: str, kategori: str | None, jumlah_cocok: int, durasi_ms: float, ip: str) -> None:
    try:
        waktu = datetime.datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
        kat = kategori or "Semua"
        baris = f"[{waktu}] q=\"{kueri}\" kat=\"{kat}\" cocok={jumlah_cocok} durasi={durasi_ms:.2f}ms ip={ip}\n"
        LOG_PENCARIAN.parent.mkdir(parents=True, exist_ok=True)
        if IS_VERCEL and not LOG_PENCARIAN.exists() and LOG_PENCARIAN_DEFAULT.exists():
            try:
                import shutil
                shutil.copyfile(LOG_PENCARIAN_DEFAULT, LOG_PENCARIAN)
            except Exception:
                pass
        with open(LOG_PENCARIAN, "a", encoding="utf-8") as f:
            f.write(baris)
            f.flush()
    except Exception:
        pass


def baca_log_pencarian(batas: int = 100) -> list[dict]:
    baris_log = []
    log_file = LOG_PENCARIAN
    if not log_file.exists():
        if IS_VERCEL and LOG_PENCARIAN_DEFAULT.exists():
            log_file = LOG_PENCARIAN_DEFAULT
        else:
            return baris_log
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        import re
        for line in reversed(lines[-batas:]):
            line = line.strip()
            if not line:
                continue
            waktu = line[1:20] if line.startswith("[") and len(line) >= 20 else ""
            sisa = line[22:] if len(line) >= 22 else line
            mq = re.search(r'q="([^"]*)"', sisa)
            mkat = re.search(r'kat="([^"]*)"', sisa)
            mcocok = re.search(r'cocok=(\d+)', sisa)
            mdur = re.search(r'durasi=([\d\.]+ms)', sisa)
            baris_log.append({
                "waktu": waktu,
                "kueri": mq.group(1) if mq else "",
                "kategori": mkat.group(1) if mkat else "Semua",
                "cocok": mcocok.group(1) if mcocok else "0",
                "durasi": mdur.group(1) if mdur else "-",
                "raw": line,
            })
    except Exception:
        pass
    return baris_log


def _tanda(path: Path) -> dict:
    st = path.stat()
    return {"path": str(path.resolve()), "mtime": st.st_mtime_ns, "size": st.st_size}


def muat_indeks() -> SearchIndex:
    """Bangun indeks dari CSV, simpan ke pickle supaya start berikutnya cepat."""
    is_vercel = os.environ.get("VERCEL") == "1"

    if not is_vercel and os.environ.get("BUILD_INDEKS") == "1":
        CACHE_INDEKS.unlink(missing_ok=True)

    tanda_data = _tanda(DATA) if DATA.exists() else {}
    if CACHE_INDEKS.exists():
        try:
            t0 = time.perf_counter()
            with open(CACHE_INDEKS, "rb") as fh:
                tersimpan = pickle.load(fh)
            tanda_tersimpan = tersimpan.get("tanda", {})
            if (
                is_vercel
                or tanda_tersimpan == tanda_data
                or (tanda_data and tanda_tersimpan.get("size") == tanda_data.get("size"))
            ):
                indeks = tersimpan["indeks"]
                indeks.stats["dari_cache"] = True
                indeks.stats["muat_ms"] = (time.perf_counter() - t0) * 1000
                return indeks
        except Exception:
            pass  # cache rusak atau tak terbaca: bangun ulang

    indeks = SearchIndex(load_documents(str(DATA)))
    indeks.stats["dari_cache"] = False
    try:
        with open(CACHE_INDEKS, "wb") as fh:
            pickle.dump({"tanda": tanda_data, "indeks": indeks}, fh)
        preprocessing.simpan_cache_stem(CACHE_STEM)
    except Exception:
        pass
    return indeks


index = muat_indeks()


def angka(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def desimal(x, p: int = 4) -> str:
    return f"{x:.{p}f}".replace(".", ",")


def durasi(ms: float) -> str:
    return f"{ms / 1000:.1f}".replace(".", ",") + " dtk" if ms >= 1000 else f"{ms:.0f} ms"


app.jinja_env.filters["angka"] = angka
app.jinja_env.filters["desimal"] = desimal
app.jinja_env.filters["durasi"] = durasi


@app.context_processor
def konteks_umum():
    return {
        "is_vercel": IS_VERCEL,
        "stat_dasar": {
            "jumlah_dokumen": index.stats["jumlah_dokumen"],
            "jumlah_term": index.stats["jumlah_term"],
        },
        "daftar_kategori": [k for k, _ in index.stats["kategori"]],
        "nav_aktif": {
            "beranda": request.endpoint == "beranda",
            "katalog": request.endpoint == "katalog_dokumen",
            "kosakata": request.endpoint == "halaman_kosakata",
            "riwayat": request.endpoint == "halaman_riwayat",
            "upload": request.endpoint == "halaman_upload",
            "preprocess": request.endpoint == "halaman_preprocess",
        },
    }


@app.route("/")
def beranda():
    contoh = ambil_contoh_kueri(index)
    return render_template(
        "beranda.html",
        stats=index.stats,
        contoh=contoh,
        placeholder_kueri=contoh[0] if contoh else "kata kunci pencarian",
    )


@app.route("/search")
def cari():
    q = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip() or None
    try:
        hal = max(1, int(request.args.get("halaman", "1")))
    except ValueError:
        hal = 1

    if not q:
        return render_template("hasil.html", q="", kosong=True, kategori_aktif=kategori or "")

    r = index.search(q, kategori=kategori)
    catat_log_pencarian(q, kategori, r["total"], r["ambil_ms"], request.remote_addr or "127.0.0.1")

    # Hitung histogram distribusi skor
    rentang_skor = [
        {"label": ">= 0,40", "min": 0.40, "max": 1.01},
        {"label": "0,30 - 0,39", "min": 0.30, "max": 0.40},
        {"label": "0,20 - 0,29", "min": 0.20, "max": 0.30},
        {"label": "0,10 - 0,19", "min": 0.10, "max": 0.20},
        {"label": "< 0,10", "min": 0.00, "max": 0.10},
    ]
    distribusi = []
    maks_cacah = 0
    for b in rentang_skor:
        cacah = sum(1 for _, s in r["skor"] if b["min"] <= s < b["max"])
        distribusi.append({"label": b["label"], "jumlah": cacah})
        if cacah > maks_cacah:
            maks_cacah = cacah
    for d in distribusi:
        d["tinggi"] = round(d["jumlah"] / maks_cacah * 100, 1) if maks_cacah else 0
        d["persen"] = round(d["jumlah"] / r["total"] * 100, 1) if r["total"] else 0

    maks_hal = max(1, math.ceil(r["total"] / PER_HALAMAN))
    hal = min(hal, maks_hal)
    offset = (hal - 1) * PER_HALAMAN
    potongan = r["hasil"][offset: offset + PER_HALAMAN]

    tokens = set(r["kueri"]["tokens"])
    for h in potongan:
        h["cuplikan"] = index.cuplikan(h["idx"], tokens)
        h["matriks"] = index.rincian_matriks(h["idx"], r["bobot_kueri"], r["hitung_kueri"])

    jendela = sorted(
        {1, maks_hal, hal - 1, hal, hal + 1} & set(range(1, maks_hal + 1))
    )
    berkas_jendela: list = []
    for i, h in enumerate(jendela):
        if i and h - jendela[i - 1] > 1:
            berkas_jendela.append("…")
        berkas_jendela.append(h)

    return render_template(
        "hasil.html",
        q=q,
        kosong=False,
        r=r,
        hasil=potongan,
        kategori_aktif=kategori or "",
        hal=hal,
        maks_hal=maks_hal,
        jendela=berkas_jendela,
        offset=offset,
        tertinggi=potongan[0]["skor"] if potongan else 0.0,
        distribusi_skor=distribusi,
        jumlah_dokumen=index.stats["jumlah_dokumen"],
    )


@app.route("/preprocess", methods=["GET", "POST"])
def halaman_preprocess():
    if request.method == "POST":
        teks = request.form.get("teks", "")
        if not teks.strip():
            return render_template(
                "preprocess.html",
                teks="",
                hasil=None,
                galat="Teks masih kosong. Tempel atau ketik dokumen pada kotak di atas.",
            )
        cuplikan = clean(teks)[:35] or teks[:35]
        catat_log_pencarian(
            f"Pra-proses: {cuplikan}",
            "Demo",
            1,
            0.0,
            request.remote_addr or "127.0.0.1",
        )
        return render_template(
            "preprocess.html", teks=teks, hasil=proses_teks(teks), galat=None
        )
    return render_template("preprocess.html", teks="", hasil=None, galat=None)


@app.route("/upload", methods=["GET", "POST"])
def halaman_upload():
    global index
    pesan_sukses = None
    pesan_galat = None

    if request.method == "POST":
        if IS_VERCEL:
            pesan_galat = (
                "Mode Serverless Cloud (Vercel): Lingkungan cloud bersifat ephemeral & read-only, "
                "sehingga berkas CSV baru tidak dapat disimpan secara permanen di server Vercel. "
                "Untuk mengganti korpus dokumen, silakan perbarui berkas data/dataset.csv pada repository GitHub "
                "atau jalankan aplikasi di komputer lokal (py app.py)."
            )
        else:
            berkas = request.files.get("berkas")
            if not berkas or not berkas.filename:
                pesan_galat = "Pilih berkas CSV terlebih dahulu."
            elif not berkas.filename.lower().endswith(".csv"):
                pesan_galat = "Format berkas harus berekstensi .csv."
            else:
                temp_path = ROOT / "data" / "temp_upload.csv"
                try:
                    berkas.save(str(temp_path))
                    docs_uji = load_documents(str(temp_path))
                    if len(docs_uji) == 0:
                        temp_path.unlink(missing_ok=True)
                        pesan_galat = "Berkas CSV tidak memuat baris dokumen yang valid."
                    else:
                        if DATA.exists():
                            backup_path = ROOT / "data" / "dataset_backup.csv"
                            if backup_path.exists():
                                backup_path.unlink(missing_ok=True)
                            DATA.replace(backup_path)
                        temp_path.replace(DATA)

                        CACHE_INDEKS.unlink(missing_ok=True)
                        t0 = time.perf_counter()
                        index = muat_indeks()
                        durasi_bangun = (time.perf_counter() - t0) * 1000

                        pesan_sukses = (
                            f"Berhasil mengunggah dan mengindeks {len(index.documents):,} dokumen "
                            f"({len(index.vocab):,} lexicon unik) dalam {durasi_bangun:.1f} ms."
                        )
                except Exception as e:
                    if temp_path.exists():
                        temp_path.unlink(missing_ok=True)
                    pesan_galat = f"Gagal memproses berkas CSV: {str(e)}"

    st = DATA.stat() if DATA.exists() else None
    info_dataset = {
        "nama": DATA.name,
        "ukuran_kb": round(st.st_size / 1024, 1) if st else 0,
        "jumlah_dokumen": len(index.documents),
        "jumlah_term": len(index.vocab),
        "terakhir_diubah": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)) if st else "-",
    }
    sampel_dokumen = index.documents[:10] if pesan_sukses else None
    top_lexicon = index.ringkasan_kosakata(urut_oleh="df", arah="desc")[:10] if pesan_sukses else None
    kategori_sebaran = index.stats.get("kategori", []) if pesan_sukses else None

    return render_template(
        "upload.html",
        info=info_dataset,
        sukses=pesan_sukses,
        galat=pesan_galat,
        sampel_dokumen=sampel_dokumen,
        top_lexicon=top_lexicon,
        kategori_sebaran=kategori_sebaran,
    )


@app.route("/dokumen")
def katalog_dokumen():
    kat = request.args.get("kategori", "").strip() or None
    cari_teks = request.args.get("q", "").strip()
    try:
        hal = max(1, int(request.args.get("halaman", "1")))
    except ValueError:
        hal = 1

    docs = index.documents
    if kat:
        kat_lower = kat.lower()
        docs = [d for d in docs if (d.get("kategori") or "").lower() == kat_lower]
    if cari_teks:
        q_lower = cari_teks.lower()
        docs = [
            d for d in docs
            if q_lower in d.get("judul", "").lower() or q_lower in d.get("dokumen", "").lower()
        ]

    total = len(docs)
    maks_hal = max(1, math.ceil(total / PER_HALAMAN_KATALOG))
    hal = min(hal, maks_hal)
    offset = (hal - 1) * PER_HALAMAN_KATALOG
    potongan = docs[offset: offset + PER_HALAMAN_KATALOG]

    jendela = sorted(
        {1, maks_hal, hal - 1, hal, hal + 1} & set(range(1, maks_hal + 1))
    )
    berkas_jendela: list = []
    for i, h in enumerate(jendela):
        if i and h - jendela[i - 1] > 1:
            berkas_jendela.append("…")
        berkas_jendela.append(h)

    return render_template(
        "katalog.html",
        docs=potongan,
        total=total,
        kategori_aktif=kat or "",
        q=cari_teks,
        hal=hal,
        maks_hal=maks_hal,
        jendela=berkas_jendela,
        offset=offset,
        total_semua=len(index.documents),
    )


@app.route("/dokumen/<doc_id>")
def dokumen(doc_id):
    temu = index.cari_dokumen(doc_id)
    if temu is None:
        abort(404)
    idx, d = temu
    catat_log_pencarian(
        f"Dokumen #{doc_id}: {d.get('judul', '')[:35]}",
        d.get("kategori") or "Semua",
        1,
        0.0,
        request.remote_addr or "127.0.0.1",
    )
    return render_template(
        "dokumen.html",
        d=d,
        bobot=index.bobot_dokumen(idx),
        jumlah_dokumen=index.stats["jumlah_dokumen"],
    )


@app.route("/export/search")
def export_search():
    q = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip() or None
    if not q:
        abort(400)
    r = index.search(q, kategori=kategori)

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "Peringkat", "ID Dokumen", "Judul", "Kategori", "Skor Cosine",
        "Rincian Dot Product (Term: wq * wd = dot)"
    ])
    for rank, h in enumerate(r["hasil"], start=1):
        matriks = index.rincian_matriks(h["idx"], r["bobot_kueri"], r["hitung_kueri"])
        rincian_str = "; ".join(
            f"{m['term']}: {m['w_q']:.4f} * {m['w_d']:.4f} = {m['dot']:.4f}"
            for m in matriks if m["dot"] > 0
        )
        writer.writerow([
            rank,
            h["dokumen"]["id"],
            h["dokumen"]["judul"],
            h["dokumen"]["kategori"],
            f"{h['skor']:.6f}".replace(".", ","),
            rincian_str,
        ])

    csv_data = "\ufeff" + out.getvalue()
    nama_bersih = clean(q).replace(" ", "_")[:30] or "pencarian"
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="vsm_{nama_bersih}.csv"'},
    )


@app.route("/export/dokumen/<doc_id>")
def export_dokumen(doc_id):
    temu = index.cari_dokumen(doc_id)
    if temu is None:
        abort(404)
    idx, d = temu
    bobot = index.bobot_dokumen(idx, batas=len(index.tf[idx]))

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Term", "tf (frekuensi)", "df (dokumen)", "idf", "Bobot VSM (L2)"])
    for b in bobot:
        writer.writerow([
            b["term"],
            b["tf"],
            b["df"],
            f"{b['idf']:.6f}".replace(".", ","),
            f"{b['bobot']:.6f}".replace(".", ","),
        ])

    csv_data = "\ufeff" + out.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="tfidf_dokumen_{doc_id}.csv"'},
    )


@app.route("/kosakata")
def halaman_kosakata():
    q = request.args.get("q", "").strip()
    urut = request.args.get("urut", "df").strip()
    arah = request.args.get("arah", "desc").strip()
    try:
        hal = max(1, int(request.args.get("halaman", "1")))
    except ValueError:
        hal = 1

    semua = index.ringkasan_kosakata(filter_teks=q, urut_oleh=urut, arah=arah)
    total = len(semua)
    maks_hal = max(1, math.ceil(total / PER_HALAMAN_KOSAKATA))
    hal = min(hal, maks_hal)
    offset = (hal - 1) * PER_HALAMAN_KOSAKATA
    potongan = semua[offset: offset + PER_HALAMAN_KOSAKATA]

    jendela = sorted(
        {1, maks_hal, hal - 1, hal, hal + 1} & set(range(1, maks_hal + 1))
    )
    berkas_jendela: list = []
    for i, h in enumerate(jendela):
        if i and h - jendela[i - 1] > 1:
            berkas_jendela.append("…")
        berkas_jendela.append(h)

    return render_template(
        "kosakata.html",
        terms=potongan,
        total=total,
        total_kosakata=len(index.vocab),
        q=q,
        urut=urut,
        arah=arah,
        hal=hal,
        maks_hal=maks_hal,
        jendela=berkas_jendela,
        offset=offset,
        jumlah_dokumen=index.stats["jumlah_dokumen"],
    )


@app.route("/export/kosakata")
def export_kosakata():
    q = request.args.get("q", "").strip()
    urut = request.args.get("urut", "df").strip()
    arah = request.args.get("arah", "desc").strip()
    semua = index.ringkasan_kosakata(filter_teks=q, urut_oleh=urut, arah=arah)

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Term", "Collection Frequency (CF)", "Document Frequency (DF)", "IDF"])
    for t in semua:
        writer.writerow([
            t["term"],
            t["cf"],
            t["df"],
            f"{t['idf']:.6f}".replace(".", ","),
        ])

    csv_data = "\ufeff" + out.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="kosakata_korpus.csv"'},
    )


@app.route("/riwayat")
def halaman_riwayat():
    baris_log = baca_log_pencarian(100)
    return render_template(
        "riwayat.html",
        riwayat=baris_log,
        total_catatan=len(baris_log),
    )


@app.route("/riwayat/bersihkan", methods=["POST"])
def bersihkan_riwayat():
    try:
        LOG_PENCARIAN.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PENCARIAN, "w", encoding="utf-8") as f:
            f.write("")
    except Exception:
        pass
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"sukses": True})
    return render_template(
        "riwayat.html",
        riwayat=[],
        total_catatan=0,
        sukses="Riwayat pencarian berhasil dibersihkan.",
    )


@app.route("/api/riwayat")
def api_riwayat():
    try:
        batas = min(100, max(1, int(request.args.get("batas", "50"))))
    except ValueError:
        batas = 50
    return jsonify(baca_log_pencarian(batas))


@app.route("/api/riwayat/catat", methods=["POST"])
def api_catat_riwayat():
    try:
        data = request.get_json(silent=True) or request.form
        kueri = (data.get("kueri") or "").strip()
        kategori = data.get("kategori") or "Semua"
        cocok = int(data.get("cocok", 1))
        durasi_str = str(data.get("durasi_ms", "0.0")).replace("ms", "").strip()
        durasi_ms = float(durasi_str) if durasi_str else 0.0
        if kueri:
            catat_log_pencarian(kueri, kategori, cocok, durasi_ms, request.remote_addr or "127.0.0.1")
            return jsonify({"sukses": True})
    except Exception:
        pass
    return jsonify({"sukses": False}), 400


@app.route("/export/riwayat")
def export_riwayat():
    log_file = LOG_PENCARIAN
    if not log_file.exists():
        if IS_VERCEL and LOG_PENCARIAN_DEFAULT.exists():
            log_file = LOG_PENCARIAN_DEFAULT
    if not log_file.exists():
        isi = ""
    else:
        with open(log_file, "r", encoding="utf-8") as f:
            isi = f.read()
    return Response(
        isi,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="pencarian.log"'},
    )


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip() or None
    if not q:
        return jsonify({"galat": "Parameter q wajib diisi"}), 400
    try:
        batas = min(50, max(1, int(request.args.get("batas", "10"))))
    except ValueError:
        batas = 10

    r = index.search(q, kategori=kategori)
    catat_log_pencarian(q, kategori, r["total"], r["ambil_ms"], request.remote_addr or "127.0.0.1")
    return jsonify(
        {
            "kueri": q,
            "kategori_filter": kategori,
            "token_hasil_pra_proses": r["kueri"]["tokens"],
            "term_di_luar_kosakata": r["kueri"]["tidak_dikenal"],
            "jumlah_cocok": r["total"],
            "ambil_ms": round(r["ambil_ms"], 2),
            "vektor_kueri": r["tabel_kueri"],
            "hasil": [
                {
                    "id": h["dokumen"]["id"],
                    "judul": h["dokumen"]["judul"],
                    "kategori": h["dokumen"]["kategori"],
                    "skor_cosine": round(h["skor"], 6),
                    "rincian_matriks": index.rincian_matriks(h["idx"], r["bobot_kueri"], r["hitung_kueri"]),
                }
                for h in r["hasil"][:batas]
            ],
        }
    )


@app.errorhandler(404)
def tidak_ditemukan(_e):
    return (
        render_template(
            "galat.html",
            kode=404,
            judul="Tidak ditemukan",
            pesan="Halaman atau dokumen yang Anda tuju tidak ada di indeks.",
        ),
        404,
    )


@app.errorhandler(500)
def galat_server(_e):
    return (
        render_template(
            "galat.html",
            kode=500,
            judul="Galat server",
            pesan="Permintaan gagal diproses. Coba lagi, atau muat ulang halaman beranda.",
        ),
        500,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
