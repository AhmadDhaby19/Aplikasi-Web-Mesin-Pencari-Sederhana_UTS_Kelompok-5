"""Mesin Vector Space Model: pembobotan TF-IDF dan perangkingan cosine.

Rumus yang dipakai:
  tf(t,d)  = 1 + log10(f(t,d))
  idf(t)   = log10(N / df(t))
  bobot    = tf x idf, lalu dinormalkan supaya panjang vektor = 1
  cos(q,d) = jumlah bobot q[t] * bobot d[t]  (vektor sudah ternormalkan)
"""

import math
import time
from collections import Counter, defaultdict

from .preprocessing import (
    NAMA_STEMMER,
    bukan_stopword,
    case_fold,
    clean,
    preprocess,
    stem_word,
)


class SearchIndex:
    def __init__(self, documents: list[dict]):
        self.documents = documents
        self.stats: dict = {}
        mulai = time.perf_counter()
        self._build()
        self.stats["build_ms"] = (time.perf_counter() - mulai) * 1000

    def _build(self) -> None:
        judul_kata = [case_fold(clean(d.get("judul", ""))).split() for d in self.documents]
        isi_kata = [case_fold(clean(d["dokumen"])).split() for d in self.documents]
        judul_stem = [[stem_word(w) for w in ks] for ks in judul_kata]
        isi_stem = [[stem_word(w) for w in ks] for ks in isi_kata]

        self.kata_stem = isi_stem
        per_dokumen = [
            [s for w, s in zip(jk + ik, js + is_) if bukan_stopword(w)]
            for jk, ik, js, is_ in zip(judul_kata, isi_kata, judul_stem, isi_stem)
        ]
        self.vocab = {t for tokens in per_dokumen for t in tokens}
        n = len(self.documents)

        self.tf: list[Counter] = []
        self.df: Counter = Counter()
        self.cf: Counter = Counter()
        for tokens in per_dokumen:
            hitung = Counter(tokens)
            self.tf.append(hitung)
            self.df.update(hitung.keys())
            self.cf.update(hitung)

        # df = N membuat idf 0, jadi term itu sengaja tidak dibobotkan
        self.idf = {t: math.log10(n / df) for t, df in self.df.items() if df < n}

        self.doc_vectors: list[dict[str, float]] = []
        self.postings: dict[str, set[int]] = defaultdict(set)
        for idx, hitung in enumerate(self.tf):
            bobot = {
                t: (1 + math.log10(f)) * self.idf[t]
                for t, f in hitung.items()
                if t in self.idf
            }
            panjang = math.sqrt(sum(w * w for w in bobot.values()))
            if panjang:
                bobot = {t: w / panjang for t, w in bobot.items()}
                for t in bobot:
                    self.postings[t].add(idx)
            self.doc_vectors.append(bobot)
        self.doc_id_map = {str(d["id"]): (idx, d) for idx, d in enumerate(self.documents)}

        kategori = Counter(d.get("kategori") or "Tanpa kategori" for d in self.documents)
        total_token = sum(sum(c.values()) for c in self.tf)
        self.stats.update(
            {
                "jumlah_dokumen": n,
                "jumlah_term": len(self.vocab),
                "jumlah_token": total_token,
                "rata_token": total_token / n if n else 0,
                "jumlah_kategori": len(kategori),
                "kategori": kategori.most_common(),
                "jumlah_kosakata_dibobot": len(self.idf),
                "stemmer": NAMA_STEMMER,
            }
        )

    def preprocess_kueri(self, query: str) -> dict:
        hasil = preprocess(query)
        hasil["tidak_dikenal"] = [t for t in hasil["tokens"] if t not in self.idf]
        return hasil

    def search(self, query: str, kategori: str | None = None) -> dict:
        """Skorkan seluruh dokumen, urutkan dari cosine tertinggi."""
        mulai = time.perf_counter()
        kueri = self.preprocess_kueri(query)
        hitung = Counter(kueri["tokens"])

        bobot = {
            t: (1 + math.log10(f)) * self.idf[t]
            for t, f in hitung.items()
            if t in self.idf
        }
        panjang = math.sqrt(sum(w * w for w in bobot.values()))
        if panjang:
            bobot = {t: w / panjang for t, w in bobot.items()}

        skor = []
        if bobot:
            kandidat: set[int] = set()
            for t in bobot:
                kandidat.update(self.postings.get(t, ()))
            if kategori:
                kat_lower = kategori.lower()
                kandidat = {
                    idx for idx in kandidat
                    if (self.documents[idx].get("kategori") or "").lower() == kat_lower
                }
            for idx in kandidat:
                vec = self.doc_vectors[idx]
                nilai = sum(w * vec.get(t, 0.0) for t, w in bobot.items())
                if nilai > 0:
                    skor.append((idx, nilai))
            skor.sort(key=lambda x: (-x[1], x[0]))

        tabel_kueri = [
            {
                "term": t,
                "tf": hitung[t],
                "df": self.df[t],
                "idf": self.idf[t],
                "bobot": bobot[t],
            }
            for t in sorted(bobot, key=lambda x: -bobot[x])
        ]

        return {
            "kueri": kueri,
            "hitung_kueri": hitung,
            "bobot_kueri": dict(sorted(bobot.items(), key=lambda kv: -kv[1])),
            "tabel_kueri": tabel_kueri,
            "kategori": kategori,
            "total": len(skor),
            "skor": skor,
            "hasil": [
                {"idx": idx, "dokumen": self.documents[idx], "skor": nilai}
                for idx, nilai in skor
            ],
            "ambil_ms": (time.perf_counter() - mulai) * 1000,
        }

    def rincian_matriks(self, idx: int, bobot_kueri: dict, hitung_kueri: Counter) -> list[dict]:
        vec = self.doc_vectors[idx]
        return [
            {
                "term": t,
                "tf_q": hitung_kueri[t],
                "w_q": w_q,
                "tf_d": self.tf[idx][t],
                "w_d": vec.get(t, 0.0),
                "dot": w_q * vec.get(t, 0.0),
            }
            for t, w_q in sorted(bobot_kueri.items(), key=lambda kv: -kv[1])
        ]

    def cuplikan(self, idx: int, tokens_kueri: set, panjang: int = 42) -> list[tuple[str, bool]]:
        """Potongan teks dokumen dengan penanda kata yang cocok dengan kueri."""
        kata = clean(self.documents[idx]["dokumen"]).split()
        tanda = [s in tokens_kueri for s in self.kata_stem[idx]]
        mulai = next((i for i, cocok in enumerate(tanda) if cocok), 0)
        akhir = min(len(kata), mulai + panjang)
        segmen: list[tuple[str, bool]] = []
        if mulai > 0:
            segmen.append(("...", False))
        segmen.extend(zip(kata[mulai:akhir], tanda[mulai:akhir]))
        if akhir < len(kata):
            segmen.append(("...", False))
        return segmen

    def bobot_dokumen(self, idx: int, batas: int = 15) -> list[dict]:
        vec = self.doc_vectors[idx]
        urut = sorted(vec.items(), key=lambda kv: -kv[1])[:batas]
        return [
            {"term": t, "tf": self.tf[idx][t], "df": self.df[t],
             "idf": self.idf[t], "bobot": w}
            for t, w in urut
        ]

    def cari_dokumen(self, doc_id: str) -> tuple[int, dict] | None:
        return self.doc_id_map.get(str(doc_id))

    def ringkasan_kosakata(self, filter_teks: str = "", urut_oleh: str = "df", arah: str = "desc") -> list[dict]:
        cf = getattr(self, "cf", None)
        if cf is None:
            cf = Counter()
            for hitung in self.tf:
                cf.update(hitung)
            self.cf = cf
        hasil = []
        q = filter_teks.strip().lower()
        for t in self.vocab:
            if q and q not in t:
                continue
            hasil.append({
                "term": t,
                "cf": cf.get(t, 0),
                "df": self.df.get(t, 0),
                "idf": self.idf.get(t, 0.0),
            })
        balik = arah == "desc"
        if urut_oleh == "term":
            hasil.sort(key=lambda x: x["term"], reverse=not balik)
        elif urut_oleh == "cf":
            hasil.sort(key=lambda x: (x["cf"], x["term"]), reverse=balik)
        elif urut_oleh == "idf":
            hasil.sort(key=lambda x: (x["idf"], x["term"]), reverse=balik)
        else:
            hasil.sort(key=lambda x: (x["df"], x["term"]), reverse=balik)
        return hasil
