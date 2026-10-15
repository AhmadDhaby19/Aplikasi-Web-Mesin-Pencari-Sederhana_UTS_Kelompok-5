"""Pipeline pra-proses teks untuk kueri dan dokumen.

Urutan tahap: cleaning -> case folding -> tokenizing -> stopword removal ->
stemming. Semua teks (dokumen saat indeksasi, kueri saat pencarian) melewati
fungsi yang sama supaya bentuk katanya selalu seragam.
"""

import re
from functools import lru_cache

try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

    _SASTRAWI = StemmerFactory().create_stemmer()
    NAMA_STEMMER = "Sastrawi"
except Exception:  # Sastrawi opsional; aplikasi tetap jalan tanpanya
    _SASTRAWI = None
    NAMA_STEMMER = "rule-based"

_URL = re.compile(r"https?://\S+|www\.\S+")
_TAG = re.compile(r"<[^>]+>")
_NON_HURUF = re.compile(r"[^a-zA-Z\s]")
_SPASI = re.compile(r"\s+")

STOPWORDS = frozenset(
    """
    ada adalah adanya adapun agak agar akan aku amat anda
    antar antara antaranya apa apabila apakah apalagi asal asalkan atas
    atau bagaimana bahkan bahwa bahwasanya baik bakal bakalan balik banyak
    barangkali bawah beberapa begini begitu begitulah beliau belum belumlah benar
    berapa bersama bicara bila bisa boleh buat bukan cukup cuma
    dahulu dalam dan dapat dari demi demikian dengan di dia
    dibuat didapat dijadikan dikecualikan dimana dini dipakai diperlukan engkau entah
    entahlah era guna gunanya hal hampir hanya harus haruslah hendak
    hingga ia ialah ini inikah itu itulah iya jadi jangan
    janganlah jarang jika juga justru kah kalau kalau-kalau kami kamu
    kapan karena katanya kau ke kecuali keluar kembali kenapa ketika
    kita kurang lagi lah lain lainnya lalu lazimnya lebih lumayan
    macam maka makanya makin malah malahan mana mana-mana masalah masih
    masing masing-masing mau mencegah mengapa mengenai menit menjadi mereka meskipun
    mesti mirip misal misalkan mungkin nah namun oleh pada padahal
    paling pantas para pasti per perihal perlu perlukan pertama-tama pihak
    pukul pula pun punya saja sambil sampai sana sangat saya
    sebab sebagian sebaiknya sebanyak sebelah sebelum sebelumnya sedang sedangkan segala
    seharusnya sehingga sejak sekali sekaligus seketika sekitar selain selaku selalu
    selama seluruh semakin sementara semoga semua sendiri seolah seorang seperti
    serta sesuai sesudah setelah setiap setidaknya siapa sini situ suatu
    sudah supaya tadi tak tampak tanpa tapi telah tentang terdapat
    terhadap ternyata tersebut tetapi tiap tiap-tiap tiba tidak toh untuk
    wajib waktu walau walau-walau walaupun ya yaitu yang
    """.split()
)

POSSESSIVES = ("nya", "ku", "mu")
SUFFIXES = ("kan", "an", "i")
PREFIXES = (
    "penge", "menge", "memp", "meng", "meny", "peng", "pem", "pen", "per",
    "pel", "bel", "ber", "ter", "men", "mem", "ke", "se", "di", "pe", "me",
)


def clean(text: str) -> str:
    """Buang URL, tag HTML, angka, dan tanda baca; sisakan huruf dan spasi."""
    text = _URL.sub(" ", text)
    text = _TAG.sub(" ", text)
    text = _NON_HURUF.sub(" ", text)
    return _SPASI.sub(" ", text).strip()


def case_fold(text: str) -> str:
    return text.lower()


def tokenize(text: str) -> list[str]:
    return text.split()


def bukan_stopword(token: str) -> bool:
    return len(token) > 1 and token not in STOPWORDS


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if bukan_stopword(t)]


def _kandidat_sufiks(word: str) -> list[str]:
    hasil, kerja = [], word
    for suf in POSSESSIVES:
        if kerja.endswith(suf) and len(kerja) - len(suf) >= 4:
            kerja = kerja[: -len(suf)]
            hasil.append(kerja)
    for suf in SUFFIXES:
        if kerja.endswith(suf) and len(kerja) - len(suf) >= 4:
            kerja = kerja[: -len(suf)]
            hasil.append(kerja)
    return hasil


def _kandidat_prefiks(word: str) -> list[str]:
    hasil = []
    for pre in PREFIXES:
        if word.startswith(pre) and len(word) - len(pre) >= 3:
            hasil.append(word[len(pre):])
            break
    return hasil


def _stem_tanpa_sastrawi(word: str) -> str:
    for kandidat in _kandidat_sufiks(word) + [word]:
        akar = _kandidat_prefiks(kandidat)
        if akar:
            return akar[0]
    return word


@lru_cache(maxsize=50000)
def stem_word(word: str) -> str:
    if len(word) < 5 or not word.isalpha():
        return word
    if word in _TOKO_STEM:
        return _TOKO_STEM[word]
    if "-" in word:
        kiri, _, kanan = word.partition("-")
        if kiri and kiri == kanan:
            word = kiri
    hasil = _SASTRAWI.stem(word) if _SASTRAWI is not None else _stem_tanpa_sastrawi(word)
    _TOKO_STEM[word] = hasil
    return hasil


def stem_tokens(tokens: list[str]) -> list[str]:
    return [stem_word(t) for t in tokens]


_TOKO_STEM: dict[str, str] = {}


def muat_cache_stem(path) -> None:
    """Muat hasil stemming dari file supaya kueri pertama tidak menunggu."""
    global _TOKO_STEM
    try:
        import json

        with open(path, encoding="utf-8") as fh:
            _TOKO_STEM = json.load(fh)
    except (OSError, ValueError):
        _TOKO_STEM = {}


def simpan_cache_stem(path) -> bool:
    if not _TOKO_STEM:
        return False
    import json

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(_TOKO_STEM, fh, ensure_ascii=False, indent=0, sort_keys=True)
    return True


def preprocess(teks: str) -> dict:
    """Jalankan lima tahap, kembalikan keluaran tiap tahap untuk ditampilkan."""
    bersih = clean(teks)
    huruf_kecil = case_fold(bersih)
    token = tokenize(huruf_kecil)
    tanpa_stop = remove_stopwords(token)
    di_stem = stem_tokens(tanpa_stop)
    return {
        "tahap": [
            {"nama": "Cleaning", "jenis": "teks", "isi": bersih,
             "jumlah": f"{len(bersih)} karakter"},
            {"nama": "Case Folding", "jenis": "teks", "isi": huruf_kecil,
             "jumlah": f"{len(huruf_kecil)} karakter"},
            {"nama": "Tokenizing", "jenis": "token", "isi": token,
             "jumlah": f"{len(token)} token"},
            {"nama": "Stopword Removal", "jenis": "token", "isi": tanpa_stop,
             "jumlah": f"{len(tanpa_stop)} token, {len(token) - len(tanpa_stop)} stopword dihapus"},
            {"nama": "Stemming", "jenis": "token", "isi": di_stem,
             "jumlah": f"{len(di_stem)} token, stemmer {NAMA_STEMMER}"},
        ],
        "tokens": di_stem,
    }
