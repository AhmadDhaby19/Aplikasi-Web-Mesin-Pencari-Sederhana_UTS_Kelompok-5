"""Pembaca dataset CSV dengan pemetaan kolom yang fleksibel.

File dari asisten praktikum bisa memakai nama kolom berbeda (text/document/
dokumen, category/kategori, dst). Jika kolom teks tidak dikenali, kolom dengan
rata-rata isi terpanjang dipakai sebagai dokumen.
"""

import csv


ID_KOL = ("id", "no", "dokumen_id", "id_dokumen", "nomor", "kode")
JUDUL_KOL = (
    "judul", "title", "judul_dokumen", "nama", "heading",
    "tipe_laka_lantas", "tipe_laka", "tipe", "peristiwa", "kasus", "kejadian",
    "topik", "subjek", "keterangan",
)
TEKS_KOL = (
    "dokumen", "text", "teks", "isi", "content", "article", "body",
    "document", "naskah", "berita", "desc", "description", "tipe_laka_lantas",
)
KATEGORI_KOL = (
    "kategori", "category", "label", "topik", "kelas", "class",
    "polres", "polda", "wilayah", "daerah",
)


def _deteksi_delimiter(fh) -> str:
    pos = fh.tell()
    cuplikan = fh.read(4096)
    fh.seek(pos)
    try:
        return csv.Sniffer().sniff(cuplikan).delimiter
    except Exception:
        pertama = cuplikan.split("\n")[0] if cuplikan else ""
        return max((";", ",", "\t", "|"), key=lambda d: pertama.count(d))


def _pilih(peta: dict, kandidat: tuple) -> str | None:
    for nama in kandidat:
        if nama in peta:
            return peta[nama]
    return None


def load_documents(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        delim = _deteksi_delimiter(fh)
        pembaca = csv.DictReader(fh, delimiter=delim)
        if not pembaca.fieldnames:
            raise ValueError(f"{path} tidak punya baris judul kolom")
        peta = {kol.strip().lower(): kol for kol in pembaca.fieldnames}
        kol_id = _pilih(peta, ID_KOL)
        kol_judul = _pilih(peta, JUDUL_KOL)
        kol_teks = _pilih(peta, TEKS_KOL)
        kol_kategori = _pilih(peta, KATEGORI_KOL)

        baris = list(pembaca)

    if not baris:
        raise ValueError(f"{path} berisi 0 baris data")
    if kol_teks is None:
        terpanjang = max(
            pembaca.fieldnames,
            key=lambda kol: sum(len((b.get(kol) or "")) for b in baris[:20]),
        )
        kol_teks = terpanjang

    hasil = []
    for i, b in enumerate(baris, start=1):
        teks = (b.get(kol_teks) or "").strip()
        if not teks:
            continue
        judul_mentah = (b.get(kol_judul) or "").strip() if kol_judul else ""
        if not judul_mentah:
            baris_pertama = teks.split("\n")[0].strip()
            judul_mentah = (baris_pertama[:75] + "…") if len(baris_pertama) > 75 else baris_pertama
        hasil.append(
            {
                "id": (b.get(kol_id) or i).strip() if kol_id else i,
                "judul": judul_mentah or f"Dokumen #{i}",
                "kategori": (b.get(kol_kategori) or "").strip() if kol_kategori else "",
                "dokumen": teks,
            }
        )
    if not hasil:
        raise ValueError(f"Semua baris di {path} kosong pada kolom {kol_teks}")
    return hasil
