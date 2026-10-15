"""Membuat data/dataset.csv: 1000 dokumen contoh berbahasa Indonesia.

Dipakai karena file CSV asisten praktikum belum tersedia. Struktur kolom
(id, judul, kategori, dokumen) sengaja dibuat umum sehingga file asisten
tinggal menggantikan dataset.csv tanpa mengubah kode aplikasi.
"""

import csv
import random
from pathlib import Path

SEED = 42
TOTAL = 1000
OUT = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"

CATEGORIES = {
    "Teknologi": {
        "keywords": [
            "kecerdasan buatan", "machine learning", "internet of things", "cloud computing",
            "aplikasi mobile", "keamanan siber", "basis data", "jaringan komputer",
            "robotika", "blockchain", "pengembangan perangkat lunak", "kecerdasan artifisial",
            "server", "algoritma", "pemrograman", "komputasi awan", "sensor", "robot",
            "data besar", "automasi",
        ],
        "sentences": [
            "Penerapan {k1} semakin luas di berbagai sektor industri di Indonesia.",
            "Para peneliti menguji {k1} untuk meningkatkan efisiensi {k2} pada skala produksi.",
            "Sistem {k1} membutuhkan {k2} yang stabil agar dapat berjalan optimal.",
            "Pengembang perangkat lunak mengintegrasikan {k1} ke dalam {k2} milik perusahaan.",
            "Biaya pemeliharaan {k1} masih menjadi tantangan bagi institusi kecil.",
            "Pelatihan {k1} dirancang agar mahasiswa memahami dasar {k2} sebelum magang.",
            "Kecepatan {k2} menentukan kualitas layanan yang diterima pengguna akhir.",
            "Perusahaan rintisan membangun {k1} untuk menjawab kebutuhan {k2} di kota kecil.",
            "Studi tahun 2023 mencatat pertumbuhan pengguna {k1} mencapai 25 persen.",
            "Tim teknis melakukan audit {k1} setiap bulan untuk mencegah kesalahan {k2}.",
            "Dokumentasi {k1} ditulis lengkap agar mudah dipelihara oleh tim berikutnya.",
            "Integrasi {k1} dengan {k2} mengurangi waktu proses hingga separuh.",
            "Komputasi awan memungkinkan {k1} diakses dari berbagai perangkat.",
            "Standar {k2} menjadi acuan sebelum {k1} dipasang di lingkungan produksi.",
        ],
        "titles": [
            "Implementasi {k1} untuk {k2}",
            "Evaluasi {k1} pada sistem {k2}",
            "Rancang bangun {k1} berbasis {k2}",
            "Optimalisasi {k2} dengan metode {k1}",
            "Analisis pemanfaatan {k1} di lingkungan {k2}",
        ],
    },
    "Kesehatan": {
        "keywords": [
            "vaksinasi", "gizi anak", "hipertensi", "diabetes", "pemeriksaan rutin",
            "obat tradisional", "sanitasi", "pelayanan puskesmas", "stunting",
            "kesehatan mental", "olahraga ringan", "polusi udara", "imunisasi",
            "dokter keluarga", "gaya hidup sehat", "screening", "kolesterol",
            "donor darah", "kebersihan tangan", "makanan bergizi", "penyakit jantung",
        ],
        "sentences": [
            "Program {k1} dijalankan puskesmas untuk menekan angka {k2} di wilayah pedesaan.",
            "Dokter menyarankan {k1} secara berkala sebagai bagian dari {k2}.",
            "Riset membuktikan bahwa {k1} berkaitan erat dengan penurunan risiko {k2}.",
            "Ibu hamil mendapat {k1} gratis di pelayanan {k2} terdekat.",
            "Gejala {k2} sering muncul tanpa disadari sehingga {k1} perlu dilakukan lebih awal.",
            "Petugas kesehatan mengimbau warga menjaga {k1} demi mencegah {k2}.",
            "Konsumsi makanan bergizi seimbang mendukung keberhasilan {k1}.",
            "Data tahun 2022 menunjukkan cakupan {k1} mencapai 78 persen pada lansia.",
            "Kebiasaan {k1} membantu mengendalikan {k2} tanpa pengobatan mahal.",
            "Kesadaran {k2} masih rendah di kalangan remaja sekolah.",
            "Tenaga medis mengimbau warga melakukan {k1} sebelum gejala {k2} parah.",
            "Klinik keliling membawa layanan {k1} ke daerah terpencil.",
            "Pola tidur dan {k1} memengaruhi hasil pengobatan {k2}.",
            "Pelatihan sukarela mengajarkan {k1} pertolongan pertama pada korban {k2}.",
        ],
        "titles": [
            "Hubungan {k1} dengan penurunan risiko {k2}",
            "Strategi {k1} untuk pencegahan {k2}",
            "Evaluasi program {k1} di pelayanan {k2}",
            "Peran {k1} dalam penanganan {k2}",
            "Faktor {k1} pada penderita {k2}",
        ],
    },
    "Pendidikan": {
        "keywords": [
            "literasi", "pembelajaran daring", "kurikulum", "ujian sekolah", "guru",
            "motivasi belajar", "perpustakaan sekolah", "beasiswa", "kelas digital",
            "modul ajar", "penilaian", "ekstrakurikuler", "mahasiswa", "metode mengajar",
            "buku teks", "kehadiran siswa", "rasio guru", "pendidikan inklusif",
            "praktikum", "kalender akademik",
        ],
        "sentences": [
            "Guru mengintegrasikan {k1} ke dalam {k2} untuk meningkatkan hasil belajar siswa.",
            "Sekolah menyediakan {k1} agar {k2} dapat berjalan meski jaringan terbatas.",
            "Penelitian menunjukkan {k1} berpengaruh terhadap {k2} pada siswa kelas atas.",
            "Perpustakaan sekolah menjadi pusat {k1} bagi seluruh warga sekolah.",
            "Pelatihan {k1} diberikan kepada guru sebelum {k2} diterapkan di kelas.",
            "Orang tua dilibatkan dalam program {k1} untuk mendukung {k2} di rumah.",
            "Modul ajar disusun mengikuti {k2} dan kebutuhan siswa di lapangan.",
            "Angka partisipasi {k1} naik tajam pada tahun ajaran 2024.",
            "Siswa kesulitan {k2} karena minimnya contoh latihan di {k1}.",
            "Kegiatan {k1} dilaksanakan setiap Sabtu bersama guru pendamping.",
            "Beasiswa diberikan kepada siswa berprestasi yang mengikuti {k1}.",
            "Kelas luring tetap tersedia bagi siswa yang belum memiliki {k1}.",
            "Evaluasi {k2} dilakukan tiap akhir semester dengan rubrik terbuka.",
            "Pustakawan mengajak siswa menjadikan {k1} sebagai kebiasaan harian.",
        ],
        "titles": [
            "Penerapan {k1} dalam {k2}",
            "Pengaruh {k1} terhadap {k2}",
            "Pengembangan {k1} berbasis {k2}",
            "Evaluasi {k1} pada pelaksanaan {k2}",
            "Strategi {k1} untuk meningkatkan {k2}",
        ],
    },
    "Pertanian": {
        "keywords": [
            "pupuk organik", "irigasi", "padi", "jagung", "sistem tanam",
            "hama penyakit", "benih unggul", "panen", "lahan kering", "agrikultur",
            "kompos", "rotasi tanaman", "modernisasi pertanian", "sawah", "ternak ayam",
            "budidaya ikan", "zat hara", "kelembaban tanah", "pemupukan", "teknologi tepat guna",
        ],
        "sentences": [
            "Petani beralih ke {k1} untuk menjaga kesuburan {k2} dalam jangka panjang.",
            "Sistem {k1} yang baik menaikkan hasil {k2} pada musim tanam kedua.",
            "Balai penyuluhan mengadakan pelatihan {k1} kepada kelompok tani {k2}.",
            "Pemakaian {k1} menurunkan biaya produksi {k2} hingga sepertiga.",
            "Hama menyerang {k2} sehingga petani memperketat {k1} mingguan.",
            "Benih unggul dipilih agar {k1} tahan terhadap perubahan cuaca.",
            "Data tahun 2021 mencatat produksi {k2} naik setelah penerapan {k1}.",
            "Kelompok tani menjual {k2} langsung ke pasar tanpa perantara.",
            "Kualitas {k2} sangat ditentukan oleh timing {k1} saat panen.",
            "Peneliti menguji {k1} baru pada lahan percobaan seluas dua hektare.",
            "Pemerintah daerah mensubsidi {k1} untuk meningkatkan {k2} petani kecil.",
            "Sisa panen diolah menjadi {k1} yang berguna bagi musim berikutnya.",
            "Kelembaban {k2} dipantau tiap hari dengan alat sederhana.",
            "Program {k1} diperluas ke tiga kecamatan pada tahun berjalan.",
        ],
        "titles": [
            "Pengaruh {k1} terhadap hasil {k2}",
            "Teknik {k1} untuk peningkatan {k2}",
            "Sistem {k1} pada budidaya {k2}",
            "Efisiensi {k1} dalam produksi {k2}",
            "Inovasi {k1} di lahan {k2}",
        ],
    },
    "Ekonomi": {
        "keywords": [
            "umkm", "inflasi", "suku bunga", "ekspor", "pasar modal",
            "digitalisasi pembayaran", "daya beli", "investasi", "anggaran daerah",
            "koperasi", "rupiah", "tenaga kerja", "produk domestik bruto", "perpajakan",
            "rantai pasok", "ritel", "kredit usaha", "persaingan pasar", "uang elektronik",
            "ekonomi kreatif",
        ],
        "sentences": [
            "Kenaikan {k1} menekan {k2} rumah tangga pada kuartal pertama.",
            "Pelaku {k2} beralih ke {k1} untuk memperluas jangkauan pembeli.",
            "Bank sentral menahan {k1} agar {k2} tetap terkendali.",
            "Peneliti mencatat {k1} tumbuh 4,5 persen tahun ini.",
            "Pelaku usaha kecil mengajukan {k1} untuk modal {k2}.",
            "Program {k1} menyerap tenaga kerja baru di kawasan industri.",
            "Nilai {k2} bergerak mengikuti kebijakan {k1} pemerintah.",
            "Koperasi mengedukasi anggota tentang {k1} dan pengelolaan {k2}.",
            "Persaingan {k1} mendorong penurunan harga barang konsumsi.",
            "Investasi asing masuk ke sektor {k2} sepanjang tahun.",
            "Transaksi {k1} mencatat rekor baru pada musim liburan.",
            "Anggaran {k2} dialokasikan untuk infrastruktur dan pelatihan kerja.",
            "Daya beli {k2} pulih setelah subsidi {k1} dibagikan.",
            "Pelatihan {k1} membantu pelaku usaha mengelola {k2} lebih rapi.",
        ],
        "titles": [
            "Dampak {k1} terhadap {k2}",
            "Analisis {k1} pada sektor {k2}",
            "Peran {k1} dalam {k2}",
            "Tren {k1} dan pengaruhnya pada {k2}",
            "Kebijakan {k1} untuk {k2}",
        ],
    },
    "Lingkungan": {
        "keywords": [
            "pemanasan global", "sampah plastik", "daur ulang", "deforestasi",
            "kualitas udara", "sungai", "energi terbarukan", "konservasi",
            "emisi karbon", "banjir", "penghijauan", "ekosistem", "iklim",
            "resapan air", "taman kota", "polusi", "sumber daya air", "hutan kota",
            "jaringan hijau", "limbah industri",
        ],
        "sentences": [
            "Pemerintah menargetkan penurunan {k1} melalui program {k2} di kawasan kota.",
            "Warga diajak memilah {k1} sejak dari rumah sebagai bagian dari {k2}.",
            "Kondisi {k2} memburuk akibat pembuangan {k1} yang tidak terkelola.",
            "Peneliti memantau {k1} menggunakan sensor di enam titik {k2}.",
            "Aksi {k1} melibatkan relawan dan siswa sekolah dasar.",
            "Data tahun 2020 menunjukkan {k2} berkurang 12 persen dalam satu dekade.",
            "Kampanye {k1} menekan penggunaan kantong sekali pakai di pasar tradisional.",
            "Restorasi {k1} dilakukan bersama lembaga swadaya masyarakat.",
            "Taman kota berfungsi sebagai {k1} saat hujan deras turun.",
            "Emisi dari kendaraan bermotor menjadi penyumbang {k1} terbesar di kota.",
            "Komunitas warga menanam pohon untuk menjaga {k2} di bantaran sungai.",
            "Pabrik diwajibkan mengolah {k1} sebelum dibuang ke lingkungan.",
            "Kualitas {k2} diperiksa tiap bulan oleh dinas terkait.",
            "Pemanfaatan {k1} mengurangi ketergantungan pada bahan bakar fosil.",
        ],
        "titles": [
            "Strategi {k1} untuk menjaga {k2}",
            "Analisis {k1} terhadap kondisi {k2}",
            "Program {k1} di kawasan {k2}",
            "Evaluasi {k1} dalam pengelolaan {k2}",
            "Peran warga dalam {k1} dan {k2}",
        ],
    },
    "Olahraga": {
        "keywords": [
            "latihan kardio", "tim sepak bola", "gizi atlet", "cedera lutut",
            "kebugaran jasmani", "kompetisi daerah", "pelatih", "renang",
            "daya tahan", "pemanasan", "atlet muda", "fisioterapi", "senam",
            "persiapan pertandingan", "rekrutmen pemain", "akademi olahraga",
            "keseimbangan tubuh", "seragam tim", "jeda pertandingan", "peluncuran air",
        ],
        "sentences": [
            "Pelatih menyusun program {k1} untuk meningkatkan {k2} pemain sebelum kompetisi.",
            "Atlet muda menjalani {k1} sebagai persiapan menghadapi {k2}.",
            "Klub menyiapkan {k1} agar {k2} para pemain tetap terjaga.",
            "Cedera {k1} sering terjadi bila pemanasan dilewati sebelum {k2}.",
            "Gizi atlet diatur tim medis selama masa {k1}.",
            "Tim tuan rumah menang tiga kosong pada {k1} pekan lalu.",
            "Pelatih menekankan {k1} sebelum sesi {k2} dimulai.",
            "Pusat latihan menyediakan {k1} untuk siswa sekolah menengah.",
            "Data menunjukkan {k1} menaikkan {k2} atlet dalam delapan minggu.",
            "Panitia menetapkan jadwal {k1} di gedung olahraga daerah.",
            "Fisioterapi membantu pemain pulih dari {k1} akibat {k2} berat.",
            "Klub membuka {k1} umum sebagai bagian dari program {k2}.",
            "Atlet menjaga {k1} selama masa persiapan {k2}.",
            "Keputusan wasit pada {k1} menuai diskusi penonton.",
        ],
        "titles": [
            "Program {k1} untuk peningkatan {k2}",
            "Efektivitas {k1} pada atlet {k2}",
            "Persiapan {k1} menjelang {k2}",
            "Pengaruh {k1} terhadap {k2}",
            "Metode {k1} dalam pembinaan {k2}",
        ],
    },
    "Seni Budaya": {
        "keywords": [
            "tari tradisional", "batik", "musik gamelan", "seni rupa", "teater",
            "festival budaya", "arsitektur tradisional", "sastra", "dolanan anak",
            "ukiran kayu", "puisi", "film dokumenter", "rakyat", "cagar budaya",
            "topeng", "kerajinan tangan", "adat istiadat", "bahasa daerah",
            "pertunjukan", "galeri seni",
        ],
        "sentences": [
            "Komunitas seni mempertahankan {k1} agar tetap dikenal generasi muda.",
            "Festival {k1} menampilkan karya {k2} dari sepuluh kabupaten.",
            "Pelukis menggabungkan {k1} dengan gaya {k2} dalam pameran tunggal.",
            "Sanggar {k1} dibuka setiap sore bagi warga yang ingin belajar.",
            "Peneliti merekam {k1} sebelum penutup usia para maestro.",
            "Kurator menyusun {k1} bertema {k2} di galeri daerah.",
            "Perlindungan {k1} didorong lewat peraturan {k2} tingkat kota.",
            "Gamelan dimainkan sebagai pengiring {k1} pada acara adat.",
            "Anak-anak diajarkan {k1} lewat permainan tradisional setiap Sabtu.",
            "Pemerintah kota mengalokasikan dana untuk pemeliharaan {k1}.",
            "Karya {k1} dipamerkan di gedung kesenian sepanjang bulan ini.",
            "Paduan suara membawakan {k1} dalam pembukaan {k2}.",
            "Mesin modern mulai menggantikan kerajinan {k1} buatan tangan.",
            "Sekolah kesenian merekrut siswa baru untuk kelas {k1}.",
        ],
        "titles": [
            "Pelestarian {k1} melalui {k2}",
            "Kreativitas {k1} dalam wadah {k2}",
            "Peran {k1} pada {k2}",
            "Inovasi {k1} berbasis {k2}",
            "Dokumentasi {k1} di era {k2}",
        ],
    },
    "Transportasi": {
        "keywords": [
            "angkutan umum", "kemacetan", "sepeda motor", "jalan tol", "pelabuhan",
            "kereta commuter", "bandara", "logistik", "lalu lintas", "bus kota",
            "keselamatan jalan", "transportasi online", "jembatan", "truk barang",
            "pejalan kaki", "parkir", "rute angkutan", "sistem transit", "sepeda kota",
            "bahan bakar",
        ],
        "sentences": [
            "Dinas perhubungan menambah {k1} untuk mengurangi {k2} di jam sibuk.",
            "Penumpang {k1} meningkat setelah tarif {k2} disesuaikan.",
            "Proyek {k1} menyelesaikan titik {k2} yang lama menghambat arus.",
            "Warga diminta memanfaatkan {k1} ketika {k2} melanda kota.",
            "Operator menyiapkan {k1} tambahan saat musim mudik tiba.",
            "Keselamatan {k1} diperiksa setiap enam bulan oleh petugas.",
            "Aplikasi {k1} membantu penumpang merencanakan perjalanan hemat {k2}.",
            "Pemerintah mengkaji rute {k1} baru untuk kawasan {k2}.",
            "Truk logistik dibatasi masuk pusat kota demi {k1}.",
            "Sensor {k1} merekam volume kendaraan setiap lima menit.",
            "Pejalan kaki mendapat jalur khusus di sepanjang {k1}.",
            "Keterlambatan {k1} menurun setelah sistem {k2} diperbarui.",
            "Anggaran {k2} dipakai memperbaiki ruas jalan yang rusak.",
            "Warga mengeluh {k1} macet total setiap hujan deras.",
        ],
        "titles": [
            "Analisis {k1} terhadap {k2}",
            "Solusi {k1} untuk mengurangi {k2}",
            "Evaluasi {k1} pada koridor {k2}",
            "Perencanaan {k1} di kawasan {k2}",
            "Dampak {k1} terhadap {k2} perkotaan",
        ],
    },
    "Kuliner": {
        "keywords": [
            "pangan lokal", "rempah", "makanan fermentasi", "higienitas", "kuliner tradisional",
            "bahan pengawet", "gula", "kandungan gizi", "warung", "catering",
            "pangan olahan", "bumbu dapur", "keamanan pangan", "resep turun temurun",
            "kemasan", "distribusi pangan", "standar higienis", "jajanan pasar",
            "bahan baku", "nutrisi",
        ],
        "sentences": [
            "Warung tradisional menjaga resep {k1} turun temurun dari nenek moyang.",
            "Pedagang {k1} memperhatikan {k1} agar tahan lama tanpa pengawet berlebih.",
            "Peneliti menganalisis {k1} pada {k2} yang dijual di pasar tradisional.",
            "Pelatihan {k1} diberikan kepada pelaku usaha {k2} skala rumahan.",
            "Konsumen makin peduli {k1} saat membeli {k2} kemasan.",
            "Dinas kesehatan mengecek {k1} di {k2} menjelang lebaran.",
            "Produksi {k1} meningkat dua kali lipat pada musim liburan.",
            "Pengolahan {k1} memakai {k2} yang aman bagi penderita alergi.",
            "Kemasan {k1} didesain agar {k2} tetap terjaga selama pengiriman.",
            "Pelaku usaha kecil memasarkan {k1} lewat pesan antar.",
            "Data tahun 2023 mencatat {k1} naik 18 persen di kota ini.",
            "Standar {k1} dirujuk sebelum {k2} dibuka untuk umum.",
            "Bahan baku {k1} disuplai petani setempat setiap pagi.",
            "Jajanan pasar {k1} menjadi ikon wisata kuliner daerah.",
        ],
        "titles": [
            "Pengaruh {k1} terhadap {k2}",
            "Standar {k1} pada produksi {k2}",
            "Inovasi {k1} dalam {k2}",
            "Kualitas {k1} di pasar {k2}",
            "Strategi {k1} untuk {k2}",
        ],
    },
}

SHARED_SENTENCES = [
    "Data dikumpulkan dari berbagai sumber yang tersedia selama periode penelitian.",
    "Program ini mendapat dukungan pemerintah daerah dan lembaga terkait.",
    "Masyarakat berperan aktif dalam pelaksanaan kegiatan di lapangan.",
    "Hasil pengamatan dilaporkan secara berkala kepada pihak berwenang.",
    "Setiap perubahan dicatat untuk keperluan evaluasi berikutnya.",
    "Kolaborasi antarinstansi mempercepat penyelesaian masalah yang dihadapi.",
    "Anggaran kegiatan dialokasikan mengikuti prioritas tahun berjalan.",
    "Petugas lapangan melakukan wawancara langsung dengan narasumber terpilih.",
]


def fill(template: str, rng: random.Random, keywords: list[str]) -> str:
    k1, k2 = rng.sample(keywords, 2)
    return template.format(k1=k1, k2=k2)


def build_row(rng: random.Random, index: int) -> dict:
    category = list(CATEGORIES)[index % len(CATEGORIES)]
    spec = CATEGORIES[category]
    keywords = spec["keywords"]

    sentences = rng.sample(spec["sentences"], 7)
    sentences += rng.sample(SHARED_SENTENCES, 2)
    rng.shuffle(sentences)
    text = " ".join(fill(s, rng, keywords) for s in sentences)

    title = fill(rng.choice(spec["titles"]), rng, keywords)
    return {
        "id": index + 1,
        "judul": title,
        "kategori": category,
        "dokumen": text,
    }


def main() -> None:
    rng = random.Random(SEED)
    rows = [build_row(rng, i) for i in range(TOTAL)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "judul", "kategori", "dokumen"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} dokumen ditulis ke {OUT}")


if __name__ == "__main__":
    main()
