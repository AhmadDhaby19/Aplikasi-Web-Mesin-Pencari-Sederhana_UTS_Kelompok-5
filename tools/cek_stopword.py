"""Audit: kata fungsi bahasa Indonesia mana yang hilang dari STOPWORDS."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.preprocessing import STOPWORDS  # noqa: E402

# Kata fungsi (kata kerja bantu, preposisi, konjungsi, pronomina) menurut
# daftar stopword umum pemrosesan bahasa Indonesia.
KATA_FUNGSI = """
yang di ke dari dan atau ini itu dengan untuk pada adalah akan telah sudah
sedang masih juga saja pun lah kah tidak bukan tanpa karena jika bila agar
supaya sehingga maka namun tetapi tapi serta bahkan walaupun meskipun walau
sementara sedangkan seperti seolah sebab demi hingga sampai sejak sebelum
sesudah setelah antara dalam atas bawah oleh tentang hampir lebih kurang
sangat amat paling cukup semua seluruh sebagian banyak beberapa tiap setiap
masing lain lainnya para segala siapa apa mana bagaimana mengapa kenapa kapan
dimana aku saya kamu kau engkau ia dia beliau kami kita mereka anda sendiri
sini sana situ begitu begini demikian ya iya nah entah mungkin bisa dapat
boleh harus perlu wajib jadi menjadi ada terdapat punya bahwa tiap-tiap
masing-masing sejak demi per antar sambil guna gunanya seharusnya sebaiknya
adapun bakal bakalan entahlah barangkali setidaknya paling tidak
""".split()

hilang = sorted({k for k in KATA_FUNGSI if k not in STOPWORDS})
print(f"kata fungsi dicek : {len(set(KATA_FUNGSI))}")
print(f"hilang dari STOPWORDS ({len(hilang)}):")
print("  " + " ".join(hilang))

# Kebalikannya: entri STOPWORDS yang jelas bukan kata fungsi Indonesia
CURIGA = ["between", "tirto", "dalah", "meni", "pengenalan", "mahu", "pur-pura"]
ada = [k for k in CURIGA if k in STOPWORDS]
print(f"\nentri mencurigakan di STOPWORDS ({len(ada)}): {' '.join(ada) or 'tidak ada'}")
